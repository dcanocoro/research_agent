from collections.abc import Iterator
from typing import Any
"""Scoped local capture using the existing LLM payload writer."""
import json
import logging
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone


@contextmanager
def capture_traces(root: Path) -> Iterator[list[dict[str, Any]]]:
    from findata.settings import settings
    from infra.adapters import llm_trace
    root.mkdir(parents=True, exist_ok=True)
    previous_mode, previous_archive = settings.LLM_TRACE_MODE, llm_trace._archive_directory
    events: list[dict[str, Any]] = []

    class Capture(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            fields = getattr(record, "json_fields", None)
            if isinstance(fields, dict):
                # Snapshot before callers can mutate a logging payload.
                value = json.loads(json.dumps(fields, default=str))
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
        llm_trace.configure_local_archive(root / "llm")
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
