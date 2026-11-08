"""Experiment-local bridge for installed shared trace contracts, without patching A."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import logging


@contextmanager
def capture(root, *, metadata=None):
    from infra.adapters import llm_trace
    if hasattr(llm_trace, "configure_local_archive") and hasattr(llm_trace, "_archive_directory"):
        from research_agent.observability.tracing import capture_traces
        with capture_traces(root, flat=True, call_metadata=metadata) as events:
            yield events
        return
    # Newer wheels expose context-local capture. Do not restore private globals or
    # monkey-patch the installed library to emulate its historical interface.
    from runtime_contracts.execution import current_run_context
    from observability_context import current_interaction_context
    owner = current_run_context()
    events = []
    root.mkdir(parents=True, exist_ok=True)

    class Capture(logging.Handler):
        def emit(self, record):
            active = current_run_context()
            if owner is not None and (active is None or active.run_id != owner.run_id):
                return
            fields = getattr(record, "json_fields", None)
            if not isinstance(fields, dict):
                return
            value = json.loads(json.dumps(fields, default=str))
            if metadata:
                value.update(metadata())
            value.setdefault("occurred_at", datetime.fromtimestamp(record.created, timezone.utc).isoformat())
            if active:
                value.setdefault("run_id", active.run_id)
            interaction = current_interaction_context()
            if interaction:
                value.setdefault("conversation_id", interaction.conversation_id)
                value.setdefault("interaction_id", interaction.interaction_id)
            events.append(value)
            with (root / "events.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(value, ensure_ascii=False) + "\n")

    handler = Capture()
    loggers = [logging.getLogger(name) for name in
               ("ingestion_service.llm_trace", "ingestion_service.observability")]
    levels = [logger.level for logger in loggers]
    with llm_trace.local_trace_capture(root):
        try:
            for logger in loggers:
                logger.addHandler(handler)
                logger.setLevel(logging.INFO)
            yield events
        finally:
            for logger, level in zip(loggers, levels):
                logger.removeHandler(handler)
                logger.setLevel(level)
