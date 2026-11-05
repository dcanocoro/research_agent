"""Existing isolated semantic reviews, executed through the shared transport."""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from time import monotonic
from typing import Any
from runtime_contracts.llm import ConversationContext
from research_agent.regimes.continuous.review.evaluator import REVIEW_SYSTEM
from research_agent.regimes.continuous.review.evaluator import knowledge
from research_agent.regimes.continuous.review.evaluator import packet
from research_agent.regimes.continuous.review.evaluator import parse_report
from research_agent.regimes.continuous.review.evaluator import feedback
from research_agent.regimes.continuous.review.evaluator import packet_hash
from research_agent.core.execution import ModelCall
from research_agent.core.execution import interact


async def external_review(self: Any, label: str) -> None:
    timeout = (
        min(self.agent.limits.timeout_seconds, self.deadline - self.clock())
        if self.deadline is not None
        else self.agent.limits.timeout_seconds
    )
    if timeout <= 0:
        return
    current = knowledge(self.agent.workspace)
    payload = packet(
        self.agent.workspace,
        self.mandate,
        self.review_before,
        current,
        self.budget(),
        self.agent.recorder.events[self.review_event_start :],
    )
    payload["review_kind"] = label
    payload["stop_reason"] = self.reason if label == "final" else None
    if label == "final" and self.evaluated_packet == packet_hash(payload) and (self.final_record is not None):
        self.agent.recorder.save("revision-externa/final.json", {**self.final_record, "reused": True})
        return
    self.agent.recorder.save(f"revision-externa/{label}-input.json", payload)
    timeout = (
        min(self.agent.limits.timeout_seconds, self.deadline - self.clock())
        if self.deadline is not None
        else self.agent.limits.timeout_seconds
    )
    review_items = [ConversationContext({"review_packet": payload})]
    if (
        timeout <= 0
        or self.counter.measure(REVIEW_SYSTEM, review_items, [], self.output_tokens)["budgeted_bytes"]
        > self.config.max_context_bytes
    ):
        self.latest_feedback = {
            "status": "skipped",
            "notice": "Evaluation packet does not fit; no progress judgment.",
        }
        self.agent.recorder.save(
            f"revision-externa/{label}.json",
            {"status": "skipped", "reason": "time_or_context_limit", "packet_sha256": packet_hash(payload)},
        )
        self.agent.recorder.event("lab.external_review.skipped", label=label, cause="time_or_context_limit")
        return
    self.charged("evaluator")
    call_started = self.clock()
    self.agent.recorder.event("lab.model.started", **self.active_call)
    try:
        turn = await interact(
            self.agent.client,
            ModelCall(
                REVIEW_SYSTEM,
                review_items,
                [],
                timeout,
                False,
                {"max_tokens": self.output_tokens},
                self.resources,
            ),
        )
        if turn.function_call is not None:
            raise ValueError("external_review_tools_disabled")
        report = parse_report(turn.text or "")
        self.latest_feedback = {
            **feedback(report),
            "packet_sha256": packet_hash(payload),
            "input_reference": f"revision-externa/{label}-input.json",
        }
        self.agent.recorder.save(
            f"revision-externa/{label}.json",
            {"status": "complete", "packet_sha256": packet_hash(payload), "report": report},
        )
        self.agent.recorder.event(
            "lab.external_review.completed", label=label, packet_sha256=packet_hash(payload)
        )
        self.evaluated_packet = packet_hash(payload)
        self.final_record = {"status": "complete", "packet_sha256": self.evaluated_packet, "report": report}
        self.reviewed_versions = {
            d["path"]: d["after"]["sha256"]
            for d in payload["documents"]
            if d.get("after") and "sha256" in d["after"]
        }
        if label != "final":
            self.append(ConversationContext({"external_review_feedback": self.latest_feedback}))
    except asyncio.CancelledError:
        raise
    except Exception as exc:
        self.latest_feedback = {
            "status": "failed",
            "error_type": type(exc).__name__,
            "notice": "No new semantic assessment.",
        }
        self.agent.recorder.save(
            f"revision-externa/{label}.json",
            {"status": "failed", "packet_sha256": packet_hash(payload), "error_type": type(exc).__name__},
        )
        self.agent.recorder.event("lab.external_review.failed", label=label, error_type=type(exc).__name__)
    finally:
        self.agent.recorder.event(
            "lab.model.finished", **self.active_call, duration_seconds=max(0, self.clock() - call_started)
        )
        self.active_call.clear()
        self.review_before = current
        self.review_event_start = len(self.agent.recorder.events)


async def evaluate(self: Any, label: str) -> None:
    self.state.last_evaluation_call = self.state.researcher_calls
    self.state.evaluation_requested = False
    await self.external_review(label if label == "final" else f"event-{self.calls + 1:04d}")
    self.state.feedback = self.latest_feedback
    if self.state.feedback and self.state.feedback.get("status") not in {"failed", "skipped"}:
        self.state.evaluated_versions = self.reviewed_versions
        has_findings = (
            self.state.feedback.get("blockers")
            or self.state.feedback.get("findings")
        )
        if has_findings:
            ref = self.agent.recorder.artifact(self.state.feedback)
            self.state.references[ref] = {"disposition": "pending", "source": "evaluator"}
    self.agent.recorder.event("lab.intervention.applied", kind="evaluate", reason=label, **self.budget())
    self.agent.recorder.checkpoint(self.agent.workspace, "evaluation", **self.budget())
    self.persist()
