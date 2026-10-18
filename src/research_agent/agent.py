from __future__ import annotations
from typing import Any, Literal
"""Conventional bounded agent loop, preserving provider replay verbatim."""
import asyncio
import hashlib
from pathlib import Path
from dataclasses import asdict
from importlib.resources import files
from time import monotonic
from uuid import uuid4
from runtime_contracts.execution import RunContext, bind_run_context
from runtime_contracts.llm import ConversationClient, ConversationItem, ConversationMessage, ConversationContext
from observability_context import bind_interaction_context, interaction_context_for
from .contracts import AgentLimits, AgentRequest, AgentResult
from .recording import RunRecorder, encoded
from .tools import ToolRegistry
from .workspace import Workspace


class AgentA:
    def __init__(self, client: ConversationClient, tools: ToolRegistry, workspace: Workspace,
                 recorder: RunRecorder, limits: AgentLimits = AgentLimits(), configuration: dict[str, Any] | None = None,
                 instructions: tuple[Path, ...] = ()) -> None:
        self.client, self.tools, self.workspace, self.recorder = client, tools, workspace, recorder
        self.limits, self.configuration = limits, configuration or {}
        self.history: list[ConversationItem] = []
        self._conversation_id: str | None = None
        self.instructions = instructions
        if tools.publication_reader is not None:
            if tools.consolidation_tools is None:
                raise ValueError("Persistence requires an injected consolidation tool set.")
            if limits.max_llm_calls < 4 or limits.max_tool_calls < 2:
                raise ValueError("Persistence requires at least four model calls and two tools.")

    async def run(self, request: AgentRequest) -> AgentResult:
        if self._conversation_id not in (None, request.conversation_id):
            raise ValueError("An AgentA instance belongs to one conversation.")
        self._conversation_id = request.conversation_id
        instructions = (*self.instructions, *request.instructions)
        protected = [Path(str(files("research_agent"))), *instructions]
        for path in protected:
            if self.workspace.root.resolve() == path.resolve() or self.workspace.root.resolve() in path.resolve().parents:
                raise ValueError("Workspace must not contain instructions or package code.")
            for root in self.tools.protected_roots:
                a, b = root.resolve(), path.resolve()
                if a == b or a in b.parents or b in a.parents:
                    raise ValueError("State stores must be disjoint from instructions and package code.")
        run_id, interaction_id = str(uuid4()), str(uuid4())
        deadline = monotonic() + self.limits.timeout_seconds
        base = files("research_agent").joinpath("prompts/agent_a.md").read_text(encoding="utf-8")
        prompts = {"agent_a.md": base, **{str(p): p.read_text(encoding="utf-8") for p in instructions}}
        system = "\n\n".join(prompts.values())
        self.recorder.start(run_id, {"run_id": run_id, "interaction_id": interaction_id,
            "conversation_id": request.conversation_id, "workspace_id": request.workspace_id,
            "workspace_fingerprint": hashlib.sha256(str(self.workspace.root.resolve()).encode()).hexdigest(),
            "limits": asdict(self.limits), "configuration": self.configuration, "metadata": request.metadata,
            "closing_policy": {"consolidation_calls": 2, "response_calls": 1,
                               "consolidation_seconds_at_time_threshold": self.limits.finalization_seconds / 3,
                               "response_seconds": self.limits.finalization_seconds * 2 / 3,
                               "context_reserve_bytes": min(32768, self.limits.max_context_bytes // 4),
                               "consolidation_tools": sorted(self.tools.consolidation_tools or ())}
                              if self.tools.publication_reader is not None else None,
            "prompts": {k: {"sha256": hashlib.sha256(v.encode()).hexdigest(), "text": v} for k, v in prompts.items()},
            "tools": self.tools.specs()})
        calls = tool_calls = 0
        answer = error = None
        status: Literal["completed", "interrupted", "failed", "cancelled"] = "interrupted"
        reason = "budget"
        persistent = self.tools.publication_reader is not None
        phase = "research" if persistent else "vanilla"
        consolidation_calls = 0
        consolidation_deadline = deadline
        response_seconds = self.limits.finalization_seconds * 2 / 3
        draft_refs: list[str] = []

        def transition(target: str, cause: str) -> None:
            nonlocal phase, consolidation_deadline, reason
            if target == phase:
                return
            previous, phase = phase, target
            if target == "consolidation":
                # A call/context trigger may leave minutes: only reserve response time.
                # At the 45-second threshold this naturally leaves at most 15 seconds.
                consolidation_deadline = deadline - response_seconds
                text = ("Runtime consolidation: research is ending. Use only the available persistence/artifact tools "
                        "to preserve relevant advances, foundations, uncertainty and pending work. Do not begin new research. "
                        "You have at most two model calls for consolidation, then a brief final response. "
                        "Only a published revision verified from the store counts as saved.")
            else:
                text = ("Runtime final response: tools are disabled. Deliver a brief answer in the user's language, "
                        "identify what was saved and what remains unfinished. Do not repeat the full investigation. "
                        "This limit comes from the runtime, not a new human instruction.")
            if cause not in {"early_answer", "saved"}:
                reason = "context_limit" if cause == "context" else "budget"
            elif cause == "early_answer":
                reason = "answered"
            self.history.append(ConversationMessage("user", text))
            self.recorder.event("lab.phase.changed", previous_phase=previous, phase=target, cause=cause)
        context = RunContext(run_id, turn_id=interaction_id, regime="lab", component="agent_a", deadline=deadline)
        interaction = interaction_context_for(interaction_id=interaction_id, conversation_id=request.conversation_id)
        with bind_run_context(context), bind_interaction_context(interaction):
            self.recorder.event("lab.run.started", **request.metadata)
            try:
                self.recorder.save("workspace_before.json", self.workspace.snapshot())
                if self.tools.state_readers:
                    self.recorder.save("state_before.json", self.tools.snapshot_state())
                index = self.workspace.path("memory/index.md")
                memory = self.workspace.read_file("memory/index.md", max_bytes=8192) if index.exists() else {"text": ""}
                self.history.append(ConversationContext({"memory_index": memory}))
                self.history.append(ConversationMessage("user", request.message))
                while calls < self.limits.max_llm_calls:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        reason = "timeout"
                        break
                    size = len(encoded({"system": system, "input": self.history, "tools": self.tools.specs()}))
                    if persistent:
                        margin = min(32768, self.limits.max_context_bytes // 4)
                        if (remaining <= response_seconds or calls >= self.limits.max_llm_calls - 1
                                or tool_calls >= self.limits.max_tool_calls):
                            transition("response", "budget")
                        elif phase == "research" and (calls >= self.limits.max_llm_calls - 3
                                or remaining <= self.limits.finalization_seconds
                                or tool_calls >= self.limits.max_tool_calls - 2
                                or size >= self.limits.max_context_bytes - margin):
                            transition("consolidation", "context" if size >= self.limits.max_context_bytes - margin else "budget")
                        if phase == "consolidation" and (consolidation_calls >= 2 or monotonic() >= consolidation_deadline):
                            transition("response", "budget")
                        closing = phase == "response"
                        allowed = frozenset() if closing else self.tools.consolidation_tools if phase == "consolidation" else None
                        call_deadline = (deadline if closing else consolidation_deadline if phase == "consolidation"
                                         else deadline - self.limits.finalization_seconds)
                    else:
                        closing = (remaining <= self.limits.finalization_seconds
                                   or calls >= self.limits.max_llm_calls - 1
                                   or tool_calls >= self.limits.max_tool_calls
                                   or size >= self.limits.max_context_bytes - 4096)
                        allowed = frozenset() if closing else None
                        call_deadline = deadline
                        if closing:
                            reason = "context_limit" if size >= self.limits.max_context_bytes - 4096 else "budget"
                            self.history.append(ConversationMessage("user", "Execution resources are ending. Deliver the best supported answer from available evidence, state limitations and unfinished work. Do not call tools."))
                    specs = self.tools.specs(allowed)
                    publication = self.tools.persistence(run_id)
                    phase_capacity = (0 if closing else min(2 - consolidation_calls,
                                      self.limits.max_llm_calls - calls - 1) if phase == "consolidation"
                                      else self.limits.max_llm_calls - calls - (3 if persistent else 1))
                    budget = {"phase": phase, "llm_calls_available": self.limits.max_llm_calls - calls,
                              "tool_calls_available": self.limits.max_tool_calls - tool_calls,
                              "phase_tool_opportunities": max(0, min(phase_capacity, self.limits.max_tool_calls - tool_calls)),
                              "seconds_remaining": round(max(0, deadline - monotonic()), 3),
                              "phase_seconds_remaining": round(max(0, call_deadline - monotonic()), 3),
                              "persistence_status": publication.status if publication else None}
                    self.history.append(ConversationContext({"execution_budget": budget}))
                    self.recorder.event("lab.budget", **budget)
                    if len(encoded({"system": system, "input": self.history, "tools": specs})) > self.limits.max_context_bytes:
                        reason = "context_limit"
                        break
                    calls += 1
                    if phase == "consolidation":
                        consolidation_calls += 1
                    try:
                        async with asyncio.timeout(max(0.001, call_deadline - monotonic())):
                            turn = await self.client.respond(system=system, input_items=list(self.history),
                                tools=specs, allow_tools=not closing,
                                timeout=max(0.001, call_deadline - monotonic()))
                    except TimeoutError:
                        if not persistent or closing:
                            raise
                        self.recorder.event("lab.phase.timeout", phase=phase, operation="model")
                        transition("consolidation" if phase == "research" else "response", "budget")
                        continue
                    self.history.extend(turn.output_items)
                    if turn.function_call is None:
                        if turn.text.strip():
                            publication = self.tools.persistence(run_id)
                            if persistent and not closing and publication is not None and publication.status != "confirmed":
                                draft_ref = f"drafts/{calls:04d}.json"
                                self.recorder.save(draft_ref, {"text": turn.text, "phase": phase, "llm_call": calls})
                                draft_refs.append(draft_ref)
                                self.recorder.event("lab.answer.drafted", artifact_ref=draft_ref, phase=phase)
                                if phase == "research":
                                    transition("consolidation", "early_answer")
                                else:
                                    self.history.append(ConversationMessage("user", "Runtime: no publication has been confirmed. Use any remaining consolidation opportunity to save; otherwise report that limitation."))
                                continue
                            answer, status = turn.text, "completed"
                            if not closing:
                                reason = "answered"
                        else:
                            reason = "empty_response"
                        break
                    if closing:
                        reason = "tools_disabled"
                        break
                    tool_calls += 1
                    tool_time = (call_deadline - monotonic() if persistent else
                                 deadline - monotonic() - self.limits.finalization_seconds)
                    try:
                        async with asyncio.timeout(max(0.001, tool_time)):
                            result = await self.tools.execute(turn.function_call, allowed_names=allowed)
                    except TimeoutError:
                        from runtime_contracts.llm import ToolResult
                        result = ToolResult(turn.function_call.call_id, turn.function_call.name,
                                            {"ok": False, "error_type": "timeout"})
                        self.recorder.event("lab.phase.timeout", phase=phase, operation="tool")
                    self.history.append(result)
                    if phase == "consolidation":
                        after = self.tools.persistence(run_id)
                        if (after is not None and after.status == "confirmed" and
                                (publication is None or after.revisions != publication.revisions)):
                            transition("response", "saved")
            except asyncio.CancelledError:
                status, reason = "cancelled", "cancelled"
                raise
            except TimeoutError:
                reason = "timeout"
            except Exception as exc:
                status, reason, error = "failed", "operational_failure", type(exc).__name__
            finally:
                self.recorder.save("transcript.json", self.history)
                self.recorder.save("workspace_after.json", self.workspace.snapshot())
                if self.tools.state_readers:
                    self.recorder.save("state_after.json", self.tools.snapshot_state())
                outcome = AgentResult(run_id, status, answer, reason,
                    ("manifest.json", "transcript.json", "workspace_before.json", "workspace_after.json", "events.jsonl",
                     *(("state_before.json", "state_after.json") if self.tools.state_readers else ()), *draft_refs),
                    calls, tool_calls, error, self.tools.persistence(run_id, answer is not None))
                self.recorder.save("result.json", outcome)
                if answer is not None and self.recorder.current is not None:
                    (self.recorder.current / "answer.md").write_text(answer, encoding="utf-8")
                terminal = "completed" if status == "completed" else "failed" if status == "failed" else "interrupted"
                self.recorder.event(f"lab.run.{terminal}", status=status, stop_reason=reason, llm_calls=calls, tool_calls=tool_calls,
                                    persistence=outcome.persistence)
        return outcome
