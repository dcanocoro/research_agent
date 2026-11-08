"""Experimental policy outside the agent package, using its existing engine."""
from collections import Counter
from dataclasses import replace
from time import monotonic
import asyncio
import json

from runtime_contracts.llm import ConversationContext, ConversationMessage
from research_agent.core.execution import Action, ModelCall, interact
from research_agent.observability.recording import encoded
from research_agent.regimes.bounded.policy import BoundedPolicy


class TerminationPolicy(BoundedPolicy):
    def __init__(self, agent, request, *, evaluator=None, evaluator_prompt=""):
        if request.continuous or request.progress or request.mandate or agent.knowledge:
            raise ValueError("Termination experiment requires plain bounded A")
        super().__init__(agent, request)
        self.evaluator = evaluator
        self.evaluator_prompt = evaluator_prompt
        self.checked = set()
        self.checkpoint_calls = 0
        self.requested_finish = False
        self.phase_counts = Counter()
        self.trace_checkpoint = False

    async def prepare(self):
        # Plain bounded preparation, with only the observability context adapted to
        # the installed shared wheel. No global patch or change to AgentA's tracer.
        from research_campaigns.termination.tracing import capture
        recorder = self.agent.recorder
        recorder.event("lab.run.started", **self.request.metadata)
        self.captured = self.captures.enter_context(capture(recorder.current / "trazas", metadata=lambda: {
            "experiment_role": "checkpoint" if self.trace_checkpoint else "A",
            "experiment_phase": "checkpoint" if self.trace_checkpoint else self.phase,
        }))
        recorder.text("peticion.md", self.request.message)
        recorder.save("estado-inicial.json", recorder.snapshot(self.agent.workspace))
        index = self.agent.workspace.path("indice.md")
        memory = self.agent.workspace.read_file("indice.md", max_bytes=8192) if index.exists() else {"text": ""}
        self.agent.history.append(ConversationContext({"memory_index": memory}))
        self.agent.history.append(ConversationMessage("user", self.request.message))

    async def next_step(self):
        # Review only after a complete model/tool exchange. Never delay dispatch.
        if (self.evaluator is not None and not self.done and self.pending_tool is None
                and self.phase == "research" and self.calls in {6, 12}
                and self.calls not in self.checked):
            self.checked.add(self.calls)
            # Apply ordinary closing limits before considering a review.
            self.remaining = self.deadline - monotonic()
            self.size = len(encoded({"system": self.system, "input": self.agent.history,
                                     "tools": self.agent.tools.specs()}))
            self.select_phase()
            if self.phase == "research":
                return Action(self.checkpoint)
        step = await super().next_step()
        if isinstance(step, ModelCall):
            self.phase_counts[self.phase] += 1
        return step

    async def checkpoint(self):
        number = self.calls
        prefix = f"terminacion/checkpoint-{number:02d}"
        # Full visible history, no rubric, no future information, no hidden reasoning.
        packet = {"request": self.request.message, "agent_calls": number,
                  "conversation": self.agent.history}
        self.agent.recorder.save(prefix + "-input.json", packet)
        seconds = min(30.0, self.deadline - monotonic() - self.agent.limits.finalization_seconds)
        if seconds <= 0:
            self.agent.recorder.save(prefix + ".json", {"outcome": "skipped", "cause": "closing_reserve"})
            return
        started = monotonic()
        self.checkpoint_calls += 1  # Attempts, including invalid responses/timeouts.
        self.trace_checkpoint = True
        report = {"outcome": "failed", "decision": "CONTINUE"}
        try:
            turn = await interact(self.evaluator, ModelCall(
                self.evaluator_prompt,
                [ConversationMessage("user", encoded(packet).decode("utf-8"))],
                [], seconds, False, options={"max_tokens": 1500},
            ))
            self.agent.recorder.save(prefix + "-response.json", turn)
            value = json.loads(turn.text)
            if (turn.function_call is not None or not isinstance(value, dict)
                    or set(value) != {"decision", "reason"}
                    or value["decision"] not in {"CONTINUE", "REQUEST_FINISH"}
                    or not isinstance(value["reason"], str) or not value["reason"].strip()
                    or len(value["reason"]) > 2000):
                raise ValueError("Invalid termination checkpoint")
            report = {"outcome": "valid", **value}
        except asyncio.CancelledError:
            report["cause"] = "cancelled"
            raise
        except Exception as exc:
            report["cause"] = type(exc).__name__
        finally:
            self.trace_checkpoint = False
            report["elapsed_seconds"] = monotonic() - started
            self.agent.recorder.save(prefix + ".json", report)
            self.agent.recorder.event("experiment.termination.checkpoint", agent_calls=number, **report)
        if report["outcome"] == "valid" and report["decision"] == "REQUEST_FINISH":
            self.requested_finish = True
            self.transition("response", "early_answer")
            # Do not expose the evaluator's rationale as evidence or financial advice.
            self.agent.history.append(ConversationMessage(
                "user", "Experimental runtime checkpoint requests a final answer now. "
                "Tools are disabled. Answer the original request using the evidence already available; "
                "state material limitations and unfinished work. This is a runtime control, not new evidence."
            ))

    def text_response(self, turn):
        super().text_response(turn)
        if self.requested_finish and self.answer is not None:
            self.reason = "checkpoint_requested_finish"

    async def finalize(self, error):
        result = await super().finalize(error)
        result = replace(result, llm_calls=result.llm_calls + self.checkpoint_calls,
                         llm_calls_by_phase={**self.phase_counts, "checkpoint": self.checkpoint_calls},
                         llm_calls_by_role={"A": result.llm_calls, "checkpoint": self.checkpoint_calls})
        # Native lab.run terminal event reports A's budget. This experiment event and
        # resultado.json explicitly account for the additional evaluator calls.
        self.agent.recorder.save("resultado.json", result)
        self.agent.recorder.event("experiment.termination.completed", total_llm_calls=result.llm_calls,
                                  agent_llm_calls=self.calls, checkpoint_calls=self.checkpoint_calls,
                                  stop_reason=result.stop_reason)
        return result
