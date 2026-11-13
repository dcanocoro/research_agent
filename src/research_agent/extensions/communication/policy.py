"""Policy decoration, temporary request instructions and an isolated live observer."""
from __future__ import annotations

import asyncio
import hashlib
import json
from dataclasses import asdict, replace
from time import monotonic
from typing import Any

from runtime_contracts.llm import ConversationMessage, ResponseTurn
from runtime_contracts.execution import bind_run_context
from research_agent.core.execution import ModelCall, ToolCall, interact
from research_agent.core.context_budget import ContextConfigurationError
from research_agent.observability.recording import encoded
from research_agent.observability.tracing import capture_traces
from research_agent.extensions.communication.configuration import CommunicationConfig
from research_agent.extensions.communication.prompts import PERMANENT, REMINDER, COMMUNICATOR
from research_agent.extensions.communication.service import PublicationService, snapshot


class HookController:
    def __init__(self) -> None:
        self.since_publication = 0
        self.retired_at = -5
        self.remaining = 0
        self.identifier = 0

    def before(self, exchange: int) -> bool:
        if not self.remaining and self.since_publication >= 6 and exchange - self.retired_at >= 5:
            self.identifier += 1
            self.remaining = 3
            return True
        return False

    def retire(self, exchange: int) -> None:
        self.remaining = 0
        self.retired_at = exchange


class CommunicationPolicy:
    def __init__(self, base: Any, config: CommunicationConfig, client: Any = None,
                 callback: Any = None) -> None:
        self.base, self.agent = base, base.agent
        self.context, self.interaction = base.context, base.interaction
        self.research = getattr(base, "base", base)
        self.config, self.client = config, client
        self.service = PublicationService(self.agent.recorder, config.mode, callback)
        self.hook = HookController()
        self.step: Any = None
        self.eligible = False
        self.pending_publication = False
        self.awaiting_tool = False
        self.task: asyncio.Task | None = None
        self.pending: dict[str, Any] | None = None
        self.closed = False
        self.phase = "research"
        self.phase_generation = 0
        self.calls = 0
        self.errors = 0
        self.duration = 0.0
        self.expiring = False
        self.input_tokens: list[int | None] = []
        self.output_tokens: list[int | None] = []

    def event(self, kind: str, **fields: Any) -> None:
        self.service.record("lab.communication." + kind, run_id=self.context.run_id, **fields)

    async def prepare(self) -> None:
        await self.base.prepare()
        recorder = self.agent.recorder
        if self.config.mode == "hook":
            self.agent.tools.register("publish_progress", "Publish a brief, evidence-backed progress update to the user.",
                {"message": {"type": "string", "minLength": 1, "maxLength": 600},
                 "evidence_refs": {"type": ["array", "null"], "items": {"type": "string"}}},
                self.publish, execution="inline", consolidation=True)
        prompts = {"permanent": PERMANENT, "reminder": REMINDER} if self.config.mode == "hook" else {"communicator": COMMUNICATOR}
        config = {**asdict(self.config), "prompts": prompts,
                  "policy": {"interval_exchanges": 6, "publication_spacing": 5,
                             "window_calls": 3, "cooldown_exchanges": 5,
                             "snapshot_bytes": 32768, "communicator_max_output_tokens": 1000},
                  "prompt_hashes": {k: hashlib.sha256(v.encode()).hexdigest() for k, v in prompts.items()}}
        if self.config.mode == "hook":
            config["tool"] = next(spec for spec in self.agent.tools.specs() if spec.name == "publish_progress")
        recorder.save("comunicacion/configuracion.json", config)
        manifest = json.loads((recorder.current / "manifiesto.json").read_bytes())
        manifest["communication"] = config
        recorder.save("manifiesto.json", manifest)

    def publish(self, message: str, evidence_refs: list[str] | None) -> dict[str, Any]:
        try:
            result = self.service.publish(message, evidence_refs, len(self.agent.recorder.events))
        except Exception as exc:
            self.event("publication_failed", error_type=type(exc).__name__)
            raise
        active = bool(self.hook.remaining or self.expiring)
        self.event("hook.publication", reminder_active=active, hook_id=self.hook.identifier)
        self.hook.since_publication = 0
        if active:
            self.event("hook.completed", hook_id=self.hook.identifier)
        self.hook.retire(self.service.exchange)
        self.expiring = False
        return result

    def current_phase(self, step: Any) -> str:
        if getattr(self.base, "operation", "") in {"closing", "evaluator", "objective_generation"}:
            return self.base.operation
        if isinstance(step, ModelCall) and not step.allow_tools:
            return "closing"
        if getattr(self.research, "checkpoint_active", False):
            return "checkpoint"
        return getattr(self.research, "phase", "research")

    def is_research_call(self, step: Any) -> bool:
        return (isinstance(step, ModelCall) and step.allow_tools and self.phase == "research"
                and getattr(self.research, "operation", "") == "model"
                and (self.base is self.research or self.base.operation == "researcher"))

    async def next_step(self) -> Any:
        # The engine can discard a truncated response without calling receive.
        if self.expiring and not self.awaiting_tool:
            self.expire()
        step = await self.base.next_step()
        phase = self.current_phase(step)
        if phase != self.phase:
            self.phase_generation += 1
            self.event("phase", previous=self.phase, phase=phase)
            self.phase = phase
        if step is None or phase in {"closing", "response"}:
            await self.stop()
        if phase != "research" and (self.hook.remaining or self.expiring):
            self.event("hook.cancelled", hook_id=self.hook.identifier, phase=phase)
            self.hook.retire(self.service.exchange)
            self.expiring = False
        self.step = step
        if isinstance(step, ModelCall):
            self.eligible = self.is_research_call(step)
            self.pending_publication = False
            self.awaiting_tool = False
            if self.config.mode == "hook" and self.eligible:
                if self.hook.before(self.service.exchange):
                    self.event("hook.activated", hook_id=self.hook.identifier)
                if self.hook.remaining:
                    self.event("hook.inserted", hook_id=self.hook.identifier, remaining=self.hook.remaining,
                               instruction=REMINDER, researcher_call=self.research.calls)
                    self.hook.remaining -= 1
                    self.expiring = self.hook.remaining == 0
                else:
                    self.expiring = False
                system = step.system + "\n\n" + PERMANENT
                if self.hook.remaining or self.expiring:
                    system += "\n\n" + REMINDER
                step = replace(step, system=system)
            elif self.config.mode == "hook" and step.allow_tools:
                # Consolidation retains the tool and its permanent usage guide only.
                step = replace(step, system=step.system + "\n\n" + PERMANENT)
            if self.config.mode == "hook" and step.allow_tools:
                self.check_size(step)
        # Give the independent task a scheduling opportunity without awaiting inference.
        await asyncio.sleep(0)
        return step

    def check_size(self, step: ModelCall) -> None:
        if self.research.request.continuous is not None:
            size = self.research.counter.measure(step.system, step.items, step.tools, self.research.output_tokens)["budgeted_bytes"]
            limit = self.research.config.max_context_bytes
        else:
            size = len(encoded({"system": step.system, "input": step.items, "tools": step.tools}))
            limit = self.agent.limits.max_context_bytes
        if size > limit:
            raise ContextConfigurationError("communication_context_too_large")

    async def receive(self, value: Any) -> None:
        await self.base.receive(value)
        if not self.eligible:
            return
        if isinstance(self.step, ModelCall) and isinstance(value, ResponseTurn):
            if value.function_call is not None:
                self.pending_publication = value.function_call.name == "publish_progress"
                self.awaiting_tool = True
                return  # complete the exchange only after the tool result
            self.complete_exchange()
        elif isinstance(self.step, ToolCall):
            self.awaiting_tool = False
            if not self.pending_publication:
                self.complete_exchange()
            else:
                self.expire()
            self.eligible = False
        elif isinstance(value, BaseException):
            self.expire()

    def expire(self) -> None:
        if getattr(self, "expiring", False):
            self.event("hook.expired", hook_id=self.hook.identifier)
            self.hook.retire(self.service.exchange)
            self.expiring = False

    def complete_exchange(self) -> None:
        self.service.exchange += 1
        self.hook.since_publication += 1
        self.expire()
        if (self.config.mode == "communicator" and not self.closed
                and self.service.exchange % 6 == 0):
            try:
                replaced_pending = self.pending is not None
                self.pending = snapshot(self.service, self.base.request.message, self.phase)
                self.pending["phase_generation"] = self.phase_generation
                self.event("observation.queued", exchange=self.service.exchange,
                           event_cutoff=self.pending["event_cutoff"], replaced_pending=replaced_pending)
            except Exception as exc:
                self.errors += 1
                self.event("snapshot.failed", error_type=type(exc).__name__)
                return
            if self.task is None or self.task.done():
                self.task = asyncio.create_task(self.observe())

    async def observe(self) -> None:
        while self.pending is not None and not self.closed:
            view, self.pending = self.pending, None
            if self.calls >= self.config.max_calls:
                self.event("budget_exhausted")
                return
            call_number = self.calls + 1
            stem = f"comunicacion/observacion-{call_number:04d}"
            started = monotonic()
            sent = False
            traces: list[dict[str, Any]] = []
            try:
                self.agent.recorder.save(stem + "-input.json", view)
                # Independent attribution; never inherit the researcher's managed budget.
                context = replace(self.context, run_id=f"{self.context.run_id}:communication:{call_number}",
                                  component="communicator", deadline=None)
                with bind_run_context(context):
                    with capture_traces(self.agent.recorder.current / "comunicacion" / f"trazas-{call_number:04d}") as traces:
                        self.calls += 1
                        sent = True
                        self.event("model.started", call=call_number, parent_run_id=self.context.run_id,
                                   component_run_id=context.run_id, event_cutoff=view["event_cutoff"])
                        turn = await interact(self.client, ModelCall(COMMUNICATOR,
                            [ConversationMessage("user", encoded(view).decode())], [],
                            self.config.timeout_seconds, False, options={"max_tokens": 1000}))
                if turn.function_call is not None:
                    raise ValueError("Communicator cannot call tools")
                self.agent.recorder.save(stem + ".json", {"text": turn.text, "status": "received"})
                decision = json.loads(turn.text)
                self.validate_decision(decision)
                self.agent.recorder.save(stem + ".json", {"text": turn.text, "decision": decision, "status": "validated"})
                if self.closed or view["phase_generation"] != self.phase_generation:
                    self.event("discarded", reason="stale_phase", call=self.calls)
                elif decision["publish"]:
                    self.service.publish(decision["message"], decision["evidence_refs"],
                                         view["event_cutoff"], set(view["evidence_refs"]))
                else:
                    self.event("no_publication", call=self.calls)
            except asyncio.CancelledError:
                self.event("model.cancelled", call=self.calls)
                raise
            except Exception as exc:
                self.errors += 1
                self.event("model.failed", call=self.calls, error_type=type(exc).__name__)
            finally:
                elapsed = monotonic() - started
                self.duration += elapsed
                usage = [e for e in traces if e.get("event") == "engine.llm_call"]
                input_tokens = self.known_sum([e.get("input_tokens") for e in usage]) if usage else None
                output_tokens = self.known_sum([e.get("output_tokens") for e in usage]) if usage else None
                if sent:
                    self.input_tokens.append(input_tokens)
                    self.output_tokens.append(output_tokens)
                self.event("model.finished", call=call_number, sent=sent, duration_seconds=elapsed,
                           input_tokens=input_tokens, output_tokens=output_tokens, cost=None)

    @staticmethod
    def known_sum(values: list[int | None]) -> int | None:
        if any(type(v) is not int for v in values):
            return None
        return sum(v for v in values if v is not None)

    @staticmethod
    def validate_decision(value: Any) -> None:
        if not isinstance(value, dict) or set(value) != {"publish", "message", "evidence_refs"}:
            raise ValueError("Invalid communication decision")
        if type(value["publish"]) is not bool or not isinstance(value["evidence_refs"], list):
            raise ValueError("Invalid communication decision types")
        if any(not isinstance(ref, str) for ref in value["evidence_refs"]):
            raise ValueError("Invalid references")
        if value["publish"]:
            if not isinstance(value["message"], str) or not value["message"].strip() or len(value["message"]) > 600:
                raise ValueError("Invalid progress message")
        elif value["message"] is not None or value["evidence_refs"]:
            raise ValueError("Invalid no-publication decision")

    async def stop(self) -> None:
        self.closed, self.pending = True, None
        if self.task is not None:
            if not self.task.done():
                self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def finalize(self, error: BaseException | None) -> Any:
        try:
            await self.stop()
            if self.hook.remaining or self.expiring:
                self.event("hook.cancelled", hook_id=self.hook.identifier, phase="terminal")
                self.hook.retire(self.service.exchange)
                self.expiring = False
            self.agent.recorder.save("comunicacion/resumen.json", {
                "mode": self.config.mode, "llm_calls": self.calls, "errors": self.errors,
                "duration_seconds": self.duration, "input_tokens": self.known_sum(self.input_tokens),
                "output_tokens": self.known_sum(self.output_tokens),
                "cost": None, "publications": len(self.service.updates),
                "eligible_exchanges": self.service.exchange})
        except Exception as exc:
            self.agent.recorder.capture_errors.append({"operation": "communication_finalize", "error_type": type(exc).__name__})
        finally:
            if self.config.mode == "hook":
                self.agent.tools.unregister("publish_progress")
            self.service.callback = None
        return await self.base.finalize(error)
