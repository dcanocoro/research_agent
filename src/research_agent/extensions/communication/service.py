"""Run-local publication and snapshots from already captured observations."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from research_agent.observability.recording import encoded
from research_agent.storage.transactions import atomic_bytes


def references(events: list[dict[str, Any]], cutoff: int) -> set[str]:
    refs = set()
    for event in events[:cutoff]:
        if event["event"] in {"lab.tool.completed", "lab.material.saved", "lab.file.written"}:
            refs.add(f"event:{event['sequence']}")
            for key in ("artifact_ref", "path"):
                if isinstance(event.get(key), str):
                    refs.add(event[key])
    return refs


class PublicationService:
    def __init__(self, recorder: Any, mode: str, callback: Any = None) -> None:
        self.recorder, self.mode, self.callback = recorder, mode, callback
        self.exchange = 0
        self.last_exchange = -5
        self.updates: list[dict[str, Any]] = []
        self.last_cutoff = 0

    def publish(self, message: str, evidence_refs: list[str] | None, cutoff: int,
                allowed_refs: set[str] | None = None) -> dict[str, Any]:
        if not isinstance(message, str) or not message.strip() or len(message) > 600:
            raise ValueError("Progress message must contain 1–600 characters")
        message = message.strip()
        refs = [] if evidence_refs is None else evidence_refs
        if not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs):
            raise ValueError("Invalid evidence references")
        available = references(self.recorder.events, cutoff) if allowed_refs is None else allowed_refs
        if not set(refs) <= available:
            raise ValueError("Evidence unavailable at observation cutoff")
        if self.exchange - self.last_exchange < 5:
            raise ValueError("Progress publication rate limit")
        if self.updates and self.updates[-1]["message"] == message:
            raise ValueError("Duplicate progress message")
        update = {"id": str(uuid4()), "run_id": self.recorder_run_id,
                  "mode": self.mode, "source": "react" if self.mode == "hook" else "external",
                  "created_at": datetime.now(timezone.utc).isoformat(), "message": message,
                  "evidence_refs": refs, "event_cutoff": cutoff}
        assert self.recorder.current is not None
        path = self.recorder.current / "comunicacion/publicaciones.jsonl"
        previous = path.read_bytes() if path.exists() else b""
        atomic_bytes(path, previous + encoded(update) + b"\n")
        self.updates.append(update)
        self.last_exchange, self.last_cutoff = self.exchange, cutoff
        self.record("lab.communication.published", **update)
        if self.callback is not None:
            try:
                self.callback(dict(update))
            except Exception as exc:
                self.record("lab.communication.display_failed", error_type=type(exc).__name__)
        return {"published": True, "id": update["id"]}

    def record(self, name: str, **fields: Any) -> None:
        try:
            self.recorder.event(name, **fields)
        except Exception as exc:
            self.recorder.capture_errors.append({"operation": "communication_event", "error_type": type(exc).__name__})

    @property
    def recorder_run_id(self) -> str:
        assert self.recorder.current is not None
        return json.loads((self.recorder.current / "manifiesto.json").read_bytes())["run_id"]


def snapshot(service: PublicationService, request: str, phase: str) -> dict[str, Any]:
    recorder = service.recorder
    cutoff = len(recorder.events)
    value: dict[str, Any] = {"run_id": service.recorder_run_id, "request": request,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "event_cutoff": cutoff, "phase": phase, "exchange": service.exchange,
        "previous_updates": [{k: v for k, v in update.items() if k != "evidence_refs"}
                             for update in service.updates[-1:]],
        "previous_update_refs_omitted": len(service.updates[-1]["evidence_refs"]) if service.updates else 0,
        "activity": [], "evidence_refs": [],
        "omitted_events": 0, "omitted_result_excerpts": 0, "request_truncated": False}
    # Bound even pathological requests; mark the omission rather than silently truncating.
    while len(encoded(value)) > 32600:
        value["request"] = value["request"][:len(value["request"]) // 2]
        value["request_truncated"] = True
    events = [e for e in recorder.events[service.last_cutoff:cutoff]
              if e["event"] in {"lab.tool.started", "lab.tool.completed", "lab.tool.failed",
                                "lab.file.written", "lab.material.saved", "lab.phase.changed"}
              and e.get("tool_name") != "publish_progress"]
    available_refs = references(recorder.events, cutoff)
    for index, event in enumerate(reversed(events)):
        item = dict(event)
        ref = event.get("artifact_ref")
        if ref and event["event"] == "lab.tool.completed":
            # Registry delivery is captured under the completed event's sequence.
            # This also works for material refs without reading mutable workspace files.
            path = recorder.current / "trazas" / f"herramienta-{event['sequence']:04d}.json"
            if path.is_file() and path.stat().st_size <= 8192:
                trace = json.loads(path.read_bytes())
                result = trace.get("result", {})
                if result.get("artifact_ref") == ref and len(encoded(result)) <= 4096:
                    item["result"] = result
                else:
                    value["omitted_result_excerpts"] += 1
            else:
                value["omitted_result_excerpts"] += 1
        new_refs = {f"event:{event['sequence']}"}
        new_refs.update(event[k] for k in ("artifact_ref", "path") if isinstance(event.get(k), str))
        candidate = {**value, "activity": [item, *value["activity"]],
                     "evidence_refs": sorted(set(value["evidence_refs"]) | new_refs),
                     "omitted_events": len(events) - index - 1}
        candidate["evidence_refs"] = sorted(set(candidate["evidence_refs"]) & available_refs)
        if len(encoded(candidate)) > 32600:
            value["omitted_events"] = len(events) - index
            break
        value = candidate
    return json.loads(encoded(value))
