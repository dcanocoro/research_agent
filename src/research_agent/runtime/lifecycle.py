from __future__ import annotations
from typing import Any
from dataclasses import replace
from .contracts import AgentResult
from ..experiment_store import git_state


def finish_run(self: Any, result: AgentResult, captured: list[dict[str, Any]]) -> AgentResult:

    def save(name: str, value: Any) -> str | None:
        try:
            return self.recorder.save(name, value)
        except Exception as exc:
            self.recorder.capture_errors.append({"operation": name, "error_type": type(exc).__name__})
            return None

    for event in captured:
        for field in ("archive_error", "capture_error"):
            if event.get(field):
                self.recorder.capture_errors.append(
                    {"operation": "provider_payload", "error_type": str(event[field])}
                )
    refs = [
        ref
        for ref in (
            save("conversacion.json", self.history),
            save("estado-final.json", self.recorder.snapshot(self.workspace)),
            save("git-final.json", git_state(self.recorder.experiment)),
        )
        if ref
    ]
    if result.answer is not None:
        try:
            self.recorder.text("respuesta.md", result.answer)
        except Exception as exc:
            self.recorder.capture_errors.append(
                {"operation": "answer_capture", "error_type": type(exc).__name__}
            )
    terminal = (
        "completed"
        if result.status == "completed"
        else "failed" if result.status == "failed" else "interrupted"
    )
    try:
        self.recorder.event(
            f"lab.run.{terminal}",
            status=result.status,
            stop_reason=result.stop_reason,
            llm_calls=result.llm_calls,
            tool_calls=result.tool_calls,
        )
    except Exception as exc:
        self.recorder.capture_errors.append({"operation": "terminal_event", "error_type": type(exc).__name__})
    refs = ["manifiesto.json", "estado-inicial.json", "eventos.jsonl", *refs]
    if result.answer is not None:
        refs.append("respuesta.md")
    outcome = replace(result, artifact_refs=tuple(refs), state=self.tools.summary())
    if save("resultado.json", outcome) is None:
        outcome = replace(outcome, state=self.tools.summary())
    return outcome
