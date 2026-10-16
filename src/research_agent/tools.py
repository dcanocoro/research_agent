from __future__ import annotations
"""Simple function dispatch with the same schemas shown to the model."""
import asyncio
import inspect
from collections.abc import Callable
from typing import Any
from jsonschema import Draft202012Validator
from runtime_contracts.llm import ResponseFunctionCall, ToolResult, ToolSpec
from .contracts import serializable
from .recording import RunRecorder, encoded


class ToolRegistry:
    def __init__(self, recorder: RunRecorder) -> None:
        self.recorder = recorder
        self._tools: dict[str, tuple[ToolSpec, Callable[..., Any]]] = {}

    def register(self, name: str, description: str, properties: dict[str, Any], function: Callable[..., Any]) -> None:
        if name in self._tools:
            raise ValueError("Duplicate tool.")
        schema = {"type": "object", "properties": properties,
                  "required": list(properties), "additionalProperties": False}
        Draft202012Validator.check_schema(schema)
        self._tools[name] = (ToolSpec(name, description, schema), function)

    def specs(self) -> list[ToolSpec]:
        return [spec for spec, _ in self._tools.values()]

    async def execute(self, call: ResponseFunctionCall) -> ToolResult:
        self.recorder.event("lab.tool.started", call_id=call.call_id, tool_name=call.name, arguments=call.arguments)
        try:
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
