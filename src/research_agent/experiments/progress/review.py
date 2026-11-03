"""Existing isolated semantic reviews, executed through the shared transport."""

from __future__ import annotations
import asyncio
from datetime import datetime, timezone
from time import monotonic
from typing import Any
from runtime_contracts.llm import ConversationContext
from .external_review import REVIEW_SYSTEM, knowledge, packet, parse_report, feedback, packet_hash
from . import objective_review
from .objectives import parse_evaluation, digest
from ...runtime.execution import ModelCall, interact


async def evaluate_objective(self: Any, label: str) -> None:
    objective = self.request.objective
    assert objective is not None and self.agent.recorder.current is not None
    timeout = (
        min(self.agent.limits.timeout_seconds, self.deadline - self.clock())
        if self.deadline is not None
        else self.agent.limits.timeout_seconds
    )
    if timeout <= 0:
        return
    current = knowledge(self.agent.workspace)
    content_sha = objective_review.content_hash(self.agent.workspace, objective, current)
    self.objective_sequence += 1
    stem = f"evaluacion-objetivo/evaluation-{self.objective_sequence:04d}"
    reference = f"{self.agent.recorder.current.name}/{stem}.json"
    previous_reference = self.objective_state.last_valid_reference
    payload = objective_review.packet(
        self.agent.workspace,
        objective,
        current,
        self.objective_state.last_review_feedback,
        self.budget(),
        self.agent.recorder.events[self.objective_event_start :],
    )
    payload["evaluation_kind"] = label
    payload["previous_valid_reference"] = previous_reference
    payload["content_sha256"] = content_sha
    packet_sha = digest(payload)
    if label == "final" and self.evaluated_packet == packet_sha and (self.final_record is not None):
        self.agent.recorder.save("evaluacion-objetivo/final.json", {**self.final_record, "reused": True})
        return
    self.agent.recorder.save(f"{stem}-input.json", payload)
    record: dict[str, Any] = {
        "id": self.objective_sequence,
        "kind": label,
        "reference": reference,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "objective_sha256": objective.sha256,
        "packet_sha256": packet_sha,
        "content_sha256": content_sha,
        "previous_valid_reference": previous_reference,
    }
    timeout = (
        min(self.agent.limits.timeout_seconds, self.deadline - self.clock())
        if self.deadline is not None
        else self.agent.limits.timeout_seconds
    )
    review_items = [ConversationContext({"objective_evaluation_packet": payload})]
    if (
        timeout <= 0
        or self.counter.measure(objective_review.SYSTEM, review_items, [], self.output_tokens)[
            "budgeted_bytes"
        ]
        > self.config.max_context_bytes
    ):
        self.objective_state.failed()
        record.update(status="skipped", reason="time_or_context_limit")
        self.objective_state.last_feedback = {
            "reference": reference,
            "status": "skipped",
            "historical": False,
            "last_valid_reference": self.objective_state.last_valid_reference,
            "notice": "Evaluación omitida: no hay nueva distancia ni se infiere falta de progreso.",
        }
        self.agent.recorder.save(f"{stem}.json", record)
        self.agent.recorder.save(
            "evaluacion-objetivo/summary.json",
            {
                "latest": record,
                "last_valid_reference": self.objective_state.last_valid_reference,
                "last_valid_report": self.objective_state.last_valid,
            },
        )
        self.agent.recorder.event("lab.objective.skipped", **record)
        if label == "final":
            self.agent.recorder.save("evaluacion-objetivo/final.json", record)
        else:
            self.append(ConversationContext({"objective_feedback": self.objective_state.last_feedback}))
        return
    self.charged("evaluator")
    call_started = self.clock()
    self.agent.recorder.event("lab.model.started", **self.active_call)
    turn = None
    try:
        turn = await interact(
            self.agent.client,
            ModelCall(
                objective_review.SYSTEM,
                review_items,
                [],
                timeout,
                False,
                {"max_tokens": self.output_tokens},
                self.resources,
            ),
        )
        if turn.function_call is not None:
            raise ValueError("objective_evaluation_tools_disabled")
        report = parse_evaluation(turn.text or "", objective)
        if objective.assessment_path and "decision_review" not in report:
            raise ValueError("Decision-oriented objective requires decision_review.")
    except asyncio.CancelledError:
        self.objective_state.failed()
        self.agent.recorder.save(f"{stem}.json", {**record, "status": "cancelled"})
        raise
    except Exception as exc:
        self.objective_state.failed()
        record.update(
            status="failed",
            error_type=type(exc).__name__,
            raw_response=turn.text if turn is not None else None,
        )
        self.objective_state.last_feedback = {
            "reference": reference,
            "status": "failed",
            "historical": False,
            "last_valid_reference": self.objective_state.last_valid_reference,
            "notice": "Evaluación fallida: no hay nueva distancia ni se infiere falta de progreso.",
        }
        self.agent.recorder.save(f"{stem}.json", record)
        self.agent.recorder.event("lab.objective.failed", **record)
        if label != "final":
            self.append(ConversationContext({"objective_feedback": self.objective_state.last_feedback}))
    else:
        details = self.objective_state.accept(report, reference)
        record.update(
            status="complete" if details["metrics"]["distance"] is not None else "partial",
            report=report,
            **details,
        )
        self.agent.recorder.save(f"{stem}.json", record)
        self.objective_state.last_feedback = objective_review.feedback(
            report, {**details, "evaluated_at": record["evaluated_at"], "status": record["status"]}, reference
        )
        self.objective_state.last_review_feedback = self.objective_state.last_feedback
        if record["status"] == "complete":
            self.objective_state.last_valid_feedback = self.objective_state.last_feedback
        self.evaluated_packet, self.final_record = (packet_sha, record)
        self.reviewed_versions = {d["path"]: d["sha256"] for d in payload["documents"] if "sha256" in d}
        self.agent.recorder.event(
            "lab.objective.evaluated", reference=reference, status=record["status"], **details
        )
        if label != "final":
            self.append(ConversationContext({"objective_feedback": self.objective_state.last_feedback}))
    finally:
        self.agent.recorder.event(
            "lab.model.finished", **self.active_call, duration_seconds=max(0, self.clock() - call_started)
        )
        self.active_call.clear()
        self.objective_event_start = len(self.agent.recorder.events)
    self.agent.recorder.save(
        "evaluacion-objetivo/summary.json",
        {
            "latest": record,
            "last_valid_reference": self.objective_state.last_valid_reference,
            "last_valid_report": self.objective_state.last_valid,
        },
    )
    if label == "final":
        self.agent.recorder.save("evaluacion-objetivo/final.json", record)


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
    if self.request.objective is not None:
        await self.evaluate_objective(label)
        self.state.feedback = self.objective_state.last_feedback
    else:
        await self.external_review(label if label == "final" else f"event-{self.calls + 1:04d}")
        self.state.feedback = self.latest_feedback
    if self.state.feedback and self.state.feedback.get("status") not in {"failed", "skipped"}:
        self.state.evaluated_versions = self.reviewed_versions
        has_findings = (
            self.state.feedback.get("blockers")
            or self.state.feedback.get("findings")
            or self.state.feedback.get("decision_review", {}).get("blockers")
        )
        if has_findings:
            ref = self.agent.recorder.artifact(self.state.feedback)
            self.state.references[ref] = {"disposition": "pending", "source": "evaluator"}
    self.agent.recorder.event("lab.intervention.applied", kind="evaluate", reason=label, **self.budget())
    self.agent.recorder.checkpoint(self.agent.workspace, "evaluation", **self.budget())
    self.persist()
