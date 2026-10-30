from ..workspace import Workspace
from ..tools import ToolRegistry


def register_files(registry: ToolRegistry, workspace: Workspace, *, state_tools: str = "legacy") -> None:
    if state_tools not in {"legacy", "v5"}:
        raise ValueError("Unknown state tools profile.")
    registry.workspace = workspace
    registry.recorder.workspace = workspace
    string = {"type": "string"}
    window = {"offset": {"type": "integer", "minimum": 0},
              "max_bytes": {"type": "integer", "minimum": 4, "maximum": 32768}}
    registry.register("list_files", "List workspace files and directories.", {"path": string}, workspace.list_files, execution="inline", consolidation=True)
    registry.register("read_file", "Read UTF-8 text; byte pagination, follow next_offset.", {"path": string, **window}, workspace.read_file, execution="inline", consolidation=True)
    registry.register("search_files", "Find literal text in state Markdown, JSON, TXT and CSV.", {"query": string, "path": string}, workspace.search_files, execution="inline", consolidation=True)
    registry.register("write_file", "Write UTF-8 Markdown, JSON, TXT or CSV. Original materiales/ are read-only.", {"path": string, "content": string}, workspace.write_file, execution="inline", consolidation=True, mutation=True)
    registry.register("write_markdown", "Write or replace a workspace Markdown file.", {"path": string, "content": string}, workspace.write_markdown, execution="inline", consolidation=True, mutation=True)
    registry.register("read_artifact", "Read a full stored tool result as JSON text with byte pagination.",
                      {"reference": string, **window}, registry.recorder.read_artifact, execution="inline", consolidation=True)
    registry.register("calculate", "Deterministic arithmetic with explicit inputs and source references. Ratios are fractions; multiply by 100 for percent.",
        {"operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
         "left": {"type": "number"}, "right": {"type": "number"},
         "source_refs": {"type": "array", "items": {"type": "string"}}}, calculate, material=True)
    from ..advances import register_advance
    register_advance(registry, workspace)
    if state_tools == "v5":
        from .state_tools import register_state_tools
        register_state_tools(registry, workspace)


def calculate(operation: str, left: float, right: float, source_refs: list[str]) -> dict[str, object]:
    import math
    import operator
    functions = {"add": operator.add, "subtract": operator.sub, "multiply": operator.mul, "divide": operator.truediv}
    if not math.isfinite(left) or not math.isfinite(right) or operation not in functions:
        raise ValueError("Calculation requires finite numbers and a supported operation.")
    if operation == "divide" and right == 0:
        raise ValueError("Division requires a nonzero denominator.")
    result = functions[operation](left, right)
    if not math.isfinite(result):
        raise ValueError("Calculation produced a non-finite value.")
    return {"formula_version": "arithmetic-v1", "operation": operation, "left": left, "right": right,
            "result": result, "source_refs": source_refs}
