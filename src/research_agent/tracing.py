from collections.abc import Callable, Iterator
from typing import Any
"""Scoped local capture using the existing LLM payload writer."""
import json
import logging
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone


@contextmanager
def capture_traces(root: Path, *, flat: bool = False,
                   call_metadata: Callable[[], dict[str, Any]] | None = None) -> Iterator[list[dict[str, Any]]]:
    from findata.settings import settings
    from infra.adapters import llm_trace
    root.mkdir(parents=True, exist_ok=True)
    previous_mode, previous_archive = settings.LLM_TRACE_MODE, llm_trace._archive_directory
    events: list[dict[str, Any]] = []
    payload_names: dict[str, str] = {}

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            fields = getattr(record, "json_fields", None)
            if isinstance(fields, dict):
                # Snapshot before callers can mutate a logging payload.
                value = json.loads(json.dumps(fields, default=str))
                if call_metadata is not None:
                    value.update(call_metadata())
                if flat and value.get("archive_file"):
                    original = value["archive_file"]
                    if original not in payload_names:
                        payload_names[original] = f"modelo-{len(payload_names)+1:04d}.json.gz"
                        try:
                            (root / original).rename(root / payload_names[original])
                        except OSError as exc:
                            value["archive_error"] = type(exc).__name__
                    # Rewrite the local references, retaining provider IDs inside the payload.
                    def renamed(item: Any) -> Any:
                        if isinstance(item, dict):
                            return {k: renamed(v) for k, v in item.items()}
                        if isinstance(item, list):
                            return [renamed(v) for v in item]
                        return payload_names.get(item, item) if isinstance(item, str) else item
                    value = renamed(value)
                from observability_context import current_interaction_context
                from runtime_contracts.execution import current_run_context
                interaction, run = current_interaction_context(), current_run_context()
                value.setdefault("occurred_at", datetime.fromtimestamp(record.created, timezone.utc).isoformat())
                if interaction is not None:
                    value.setdefault("interaction_id", interaction.interaction_id)
                    value.setdefault("conversation_id", interaction.conversation_id)
                if run is not None:
                    value.setdefault("run_id", run.run_id)
                events.append(value)
                with (root / "events.jsonl").open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(value, ensure_ascii=False) + "\n")

    handler = Capture()
    # Attach to actual emitting loggers once; disable propagation duplication.
    targets = [logging.getLogger("ingestion_service.llm_trace"), logging.getLogger("ingestion_service.observability")]
    levels = [logger.level for logger in targets]
    try:
        settings.LLM_TRACE_MODE = "full"
        llm_trace.configure_local_archive(root if flat else root / "llm")
        for logger in targets:
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        yield events
    finally:
        for logger, level in zip(targets, levels):
            logger.removeHandler(handler)
            logger.setLevel(level)
        settings.LLM_TRACE_MODE = previous_mode
        llm_trace._archive_directory = previous_archive
