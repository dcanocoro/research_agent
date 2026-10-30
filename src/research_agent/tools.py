from __future__ import annotations
"""Schema-validated dispatch, automatic materials, and bounded result delivery."""
import asyncio
import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal
from jsonschema import Draft202012Validator
from runtime_contracts.llm import ResponseFunctionCall, ToolResult, ToolSpec
from .contracts import StateSummary, serializable
from .recording import RunRecorder, encoded
from .workspace import Workspace
from .advances import RecoveryRequired


def mutation_receipt(value: Any) -> dict[str, Any]:
    return {key: value[key] for key in ("path", "bytes", "sha256", "previous_sha256", "applied", "operation", "operations_applied") if key in value}


@dataclass(frozen=True)
class RegisteredTool:
    spec: ToolSpec
    function: Callable[..., Any]
    validator: Draft202012Validator
    execution: Literal["inline", "thread", "async"]
    material: bool
    consolidation: bool
    mutation: bool
    bounded: bool


class ToolRegistry:
    def __init__(self, recorder: RunRecorder) -> None:
        self.recorder = recorder
        self._tools: dict[str, RegisteredTool] = {}
        self.workspace: Workspace | None = None
        self.files_written: list[str] = []
        self.materials: list[str] = []
        self.contracts: dict[str, Any] = {}
        self.active_names: frozenset[str] | None = None

    def reset(self) -> None:
        self.files_written, self.materials = [], []

    def summary(self) -> StateSummary:
        return StateSummary(tuple(dict.fromkeys(self.files_written)), tuple(self.materials), tuple(self.recorder.capture_errors))

    def register(self, name: str, description: str, properties: dict[str, Any], function: Callable[..., Any], *,
                 execution: Literal["inline", "thread", "async"] = "thread",
                 material: bool = False, consolidation: bool = False,
                 mutation: bool = False, bounded: bool = False) -> None:
        if name in self._tools:
            raise ValueError("Duplicate tool.")
        schema = {"type": "object", "properties": properties,
                  "required": list(properties), "additionalProperties": False}
        Draft202012Validator.check_schema(schema)
        self._tools[name] = RegisteredTool(ToolSpec(name, description, schema), function,
                                          Draft202012Validator(schema), execution, material, consolidation, mutation, bounded)

    @property
    def consolidation_tools(self) -> frozenset[str]:
        return frozenset(name for name, tool in self._tools.items() if tool.consolidation)

    def is_mutation(self, name: str) -> bool:
        return name in self._tools and self._tools[name].mutation

    def is_material(self, name: str) -> bool:
        return name in self._tools and self._tools[name].material

    def specs(self, allowed_names: frozenset[str] | None = None) -> list[ToolSpec]:
        return [tool.spec for name, tool in self._tools.items() if allowed_names is None or name in allowed_names]

    def _material(self, name: str, value: Any) -> str | None:
        if not self._tools[name].material or self.workspace is None:
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
        capturing = False
        mutation_result = None
        previous_names, self.active_names = self.active_names, allowed_names
        try:
            if allowed_names is not None and call.name not in allowed_names:
                raise ValueError("Tool is unavailable in this execution phase.")
            if call.name not in self._tools:
                raise ValueError("Unknown tool.")
            tool = self._tools[call.name]
            tool.validator.validate(call.arguments)
            if tool.execution == "async":
                value = await tool.function(**call.arguments)
            elif tool.execution == "inline":
                # File operations finish synchronously: a timed-out thread must not mutate a closed run.
                value = tool.function(**call.arguments)
            else:
                value = await asyncio.to_thread(tool.function, **call.arguments)
            value = serializable(value)
            if tool.mutation:
                receipts = value.get("files", [value])
                mutation_result = {"files": [mutation_receipt(v) for v in receipts]} if "files" in value else mutation_receipt(value)
                self.files_written.extend(v["path"] for v in receipts)
            capturing = True
            if tool.mutation:
                assert mutation_result is not None
                for receipt in mutation_result.get("files", [mutation_result]):
                    self.recorder.event("lab.file.written", call_id=call.call_id, tool_name=call.name, **receipt)
            artifact = self.recorder.artifact(value)
            material = self._material(call.name, value)
            reference = material or artifact
            if len(encoded(value)) > 32768 and not tool.bounded and call.name not in {"read_artifact", "read_file"}:
                value = {"artifact_ref": reference, "limited": True,
                         "message": "Result stored in full. Use read_artifact or read_file with byte pagination."}
            if tool.bounded and isinstance(value, dict) and isinstance(value.get("diff"), str) and len(value["diff"]) > 3000:
                value = {**value, "diff": value["diff"][:3000], "diff_partial": True,
                         "diff_recovery": "read_artifact for the complete diff"}
            payload = {"ok": True, "value": value, "artifact_ref": reference}
            if material:
                assert self.workspace is not None
                payload["material_ref"] = material
                self.recorder.event("lab.material.saved", path=material, tool_name=call.name,
                                    arguments=call.arguments, sha256=hashlib.sha256(self.workspace.path(material).read_bytes()).hexdigest())
            self.recorder.event("lab.tool.completed", call_id=call.call_id, tool_name=call.name, artifact_ref=reference)
            if tool.bounded and len(encoded(payload)) > 32768:
                payload = {"ok": True, "value": {"limited": True, "recovery": "read_artifact with byte pagination",
                           "mutation": mutation_result}, "artifact_ref": reference}
        except RecoveryRequired as exc:
            self.recorder.event("lab.tool.failed", call_id=call.call_id, tool_name=call.name,
                                error_type="RecoveryRequired", message=str(exc), fatal=True)
            raise
        except asyncio.CancelledError:
            self.recorder.event("lab.tool.failed", call_id=call.call_id, tool_name=call.name, error_type="cancelled")
            raise
        except Exception as exc:
            payload = {"ok": False, "error_type": type(exc).__name__}
            if mutation_result is not None:
                payload.update(applied=True, mutation=mutation_result,
                               message="Change applied; capture failed. Inspect current version before retrying.")
            if isinstance(exc, ValueError) and type(exc) is ValueError:
                payload["message"] = str(exc)[:500]
            if capturing:
                self.recorder.capture_errors.append({"operation": "tool_capture", "error_type": type(exc).__name__})
            try:
                self.recorder.event("lab.tool.failed", call_id=call.call_id, tool_name=call.name, **payload)
            except OSError:
                self.recorder.capture_errors.append({"operation": "tool_event", "error_type": "OSError"})
        finally:
            self.active_names = previous_names
        try:
            self.recorder.save(f"trazas/herramienta-{len(self.recorder.events):04d}.json", {"call": call, "result": payload})
        except Exception as exc:
            self.recorder.capture_errors.append({"operation": "tool_trace", "error_type": type(exc).__name__})
            payload["capture_failed"] = True
            if mutation_result is not None:
                payload.update(applied=True, mutation=mutation_result)
        return ToolResult(call.call_id, call.name, payload)
