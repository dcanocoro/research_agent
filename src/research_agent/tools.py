from __future__ import annotations
"""Schema-validated dispatch, automatic materials, and bounded result delivery."""
import asyncio
import hashlib
import inspect
from pathlib import Path
from collections.abc import Callable
from typing import Any
from jsonschema import Draft202012Validator
from runtime_contracts.llm import ResponseFunctionCall, ToolResult, ToolSpec
from .contracts import StateSummary, serializable
from .recording import RunRecorder, encoded
from .workspace import Workspace


class ToolRegistry:
    material_tools = frozenset({"search_companies", "read_company", "read_financials", "read_metric_trend",
                                "search_web", "read_document", "calculate"})
    consolidation_tools = frozenset({"list_files", "read_file", "search_files", "write_file", "write_markdown", "read_artifact"})

    def __init__(self, recorder: RunRecorder) -> None:
        self.recorder = recorder
        self._tools: dict[str, tuple[ToolSpec, Callable[..., Any]]] = {}
        self.workspace: Workspace | None = None
        self.files_written: list[str] = []
        self.materials: list[str] = []

    def reset(self) -> None:
        self.files_written, self.materials = [], []

    def summary(self) -> StateSummary:
        return StateSummary(tuple(dict.fromkeys(self.files_written)), tuple(self.materials), tuple(self.recorder.capture_errors))

    def register(self, name: str, description: str, properties: dict[str, Any], function: Callable[..., Any]) -> None:
        if name in self._tools:
            raise ValueError("Duplicate tool.")
        schema = {"type": "object", "properties": properties,
                  "required": list(properties), "additionalProperties": False}
        Draft202012Validator.check_schema(schema)
        self._tools[name] = (ToolSpec(name, description, schema), function)

    def specs(self, allowed_names: frozenset[str] | None = None) -> list[ToolSpec]:
        return [spec for spec, _ in self._tools.values() if allowed_names is None or spec.name in allowed_names]

    def _material(self, name: str, value: Any) -> str | None:
        if name not in self.material_tools or self.workspace is None:
            return None
        assert self.recorder.current is not None
        relative = f"materiales/{self.recorder.current.name}-{len(self.materials)+1:02d}-{name.replace('_', '-')}.json"
        path = self.workspace.path(relative)
        # Original provider output: do not replace its schema or metadata with an interpretation.
        with path.open("xb") as stream:
            stream.write(encoded(value))
        self.materials.append(relative)
        return relative

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
            elif self.workspace is not None and getattr(function, "__self__", None) is self.workspace:
                # File operations finish synchronously: a timed-out thread must not mutate a closed run.
                value = function(**call.arguments)
            else:
                value = await asyncio.to_thread(function, **call.arguments)
            value = serializable(value)
            artifact = self.recorder.artifact(value)
            material = self._material(call.name, value)
            reference = material or artifact
            if len(encoded(value)) > 32768 and call.name not in {"read_artifact", "read_file"}:
                value = {"artifact_ref": reference, "limited": True,
                         "message": "Result stored in full. Use read_artifact or read_file with byte pagination."}
            payload = {"ok": True, "value": value, "artifact_ref": reference}
            if material:
                assert self.workspace is not None
                payload["material_ref"] = material
                self.recorder.event("lab.material.saved", path=material, tool_name=call.name,
                                    arguments=call.arguments, sha256=hashlib.sha256(self.workspace.path(material).read_bytes()).hexdigest())
            self.recorder.event("lab.tool.completed", call_id=call.call_id, tool_name=call.name, artifact_ref=reference)
            if call.name in {"write_file", "write_markdown"}:
                self.files_written.append(value["path"])
                self.recorder.event("lab.file.written", **value)
        except asyncio.CancelledError:
            self.recorder.event("lab.tool.failed", call_id=call.call_id, tool_name=call.name, error_type="cancelled")
            raise
        except Exception as exc:
            payload = {"ok": False, "error_type": type(exc).__name__}
            if isinstance(exc, ValueError) and type(exc) is ValueError:
                payload["message"] = str(exc)[:500]
            if isinstance(exc, OSError):
                self.recorder.capture_errors.append({"operation": "tool_capture", "error_type": type(exc).__name__})
            self.recorder.event("lab.tool.failed", call_id=call.call_id, tool_name=call.name, **payload)
        self.recorder.save(f"trazas/herramienta-{len(self.recorder.events):04d}.json", {"call": call, "result": payload})
        return ToolResult(call.call_id, call.name, payload)
