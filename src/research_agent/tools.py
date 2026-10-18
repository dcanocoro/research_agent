from __future__ import annotations
"""Simple function dispatch with the same schemas shown to the model."""
import asyncio
import inspect
from pathlib import Path
from collections.abc import Callable
from typing import Any
from jsonschema import Draft202012Validator
from runtime_contracts.llm import ResponseFunctionCall, ToolResult, ToolSpec
from .contracts import PersistenceResult, serializable
from .recording import RunRecorder, encoded


class ToolRegistry:
    def __init__(self, recorder: RunRecorder) -> None:
        self.recorder = recorder
        self._tools: dict[str, tuple[ToolSpec, Callable[..., Any]]] = {}
        self.state_readers: dict[str, Callable[[], Any]] = {}
        self.protected_roots: list[Path] = []
        self.consolidation_tools: frozenset[str] | None = None
        self.publication_reader: Callable[[str], list[dict[str, str]]] | None = None

    def persistence(self, run_id: str, response_delivered: bool = False) -> PersistenceResult | None:
        if self.publication_reader is None:
            return None
        try:
            revisions = tuple(self.publication_reader(run_id))
            return PersistenceResult("confirmed" if revisions else "unconfirmed", revisions, response_delivered)
        except Exception as exc:
            return PersistenceResult("verification_failed", (), response_delivered, type(exc).__name__)

    def snapshot_state(self) -> dict[str, Any]:
        result = {}
        for name, reader in self.state_readers.items():
            try:
                result[name] = reader()
            except Exception as exc:
                result[name] = {"capture_error": type(exc).__name__}
        return result

    def register(self, name: str, description: str, properties: dict[str, Any], function: Callable[..., Any]) -> None:
        if name in self._tools:
            raise ValueError("Duplicate tool.")
        schema = {"type": "object", "properties": properties,
                  "required": list(properties), "additionalProperties": False}
        Draft202012Validator.check_schema(schema)
        self._tools[name] = (ToolSpec(name, description, schema), function)

    def specs(self, allowed_names: frozenset[str] | None = None) -> list[ToolSpec]:
        return [spec for spec, _ in self._tools.values() if allowed_names is None or spec.name in allowed_names]

    async def execute(self, call: ResponseFunctionCall, *, allowed_names: frozenset[str] | None = None) -> ToolResult:
        self.recorder.event("lab.tool.started", call_id=call.call_id, tool_name=call.name, arguments=call.arguments)
        try:
            if allowed_names is not None and call.name not in allowed_names:
                raise ValueError("Tool is unavailable in this execution phase.")
            if call.name not in self._tools:
                raise ValueError("Unknown tool.")
            spec, function = self._tools[call.name]
            Draft202012Validator(spec.parameters).validate(call.arguments)
            if inspect.iscoroutinefunction(function):
                value = await function(**call.arguments)
            else:
                value = await asyncio.to_thread(function, **call.arguments)
            value = serializable(value)
            reference = self.recorder.artifact(value)
            if len(encoded(value)) > 32768 and call.name not in {"read_artifact", "read_file"}:
                value = {"artifact_ref": reference, "limited": True,
                         "message": "Result stored in full. Use read_artifact with byte pagination."}
            payload = {"ok": True, "value": value, "artifact_ref": reference}
            self.recorder.event("lab.tool.completed", call_id=call.call_id, tool_name=call.name, artifact_ref=reference)
            if call.name == "write_markdown":
                self.recorder.event("lab.file.written", **value)
        except asyncio.CancelledError:
            self.recorder.event("lab.tool.failed", call_id=call.call_id, tool_name=call.name, error_type="cancelled")
            raise
        except Exception as exc:
            # Provider exception strings may contain secrets; expose category only.
            payload = {"ok": False, "error_type": type(exc).__name__}
            if isinstance(exc, ValueError) and type(exc) is ValueError:
                payload["message"] = str(exc)[:500]
            self.recorder.event("lab.tool.failed", call_id=call.call_id, tool_name=call.name, **payload)
        import hashlib
        safe_id = hashlib.sha256(call.call_id.encode()).hexdigest()
        self.recorder.save(f"tools/{len(self.recorder.events):04d}-{safe_id}.json", {"call": call, "result": payload})
        return ToolResult(call.call_id, call.name, payload)
