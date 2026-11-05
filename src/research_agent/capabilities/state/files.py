from pathlib import Path
from collections.abc import Callable
from typing import Any
from research_agent.storage.workspace import Workspace
from research_agent.core.tools import ToolRegistry
from research_agent.capabilities.arithmetic.tools import calculate


def register_files(registry: ToolRegistry, workspace: Workspace, *, writable: bool = True, arithmetic: bool = True,
                   journal_root: Path | None = None, write_guard: Callable[[list[dict[str, Any]]], None] | None = None) -> None:
    registry.workspace = workspace
    registry.recorder.workspace = workspace
    string = {"type": "string"}
    window = {"offset": {"type": "integer", "minimum": 0},
              "max_bytes": {"type": "integer", "minimum": 4, "maximum": 32768}}
    registry.register("list_files", "List workspace files and directories.", {"path": string}, workspace.list_files, execution="inline", consolidation=True)
    registry.register("read_file", "Read UTF-8 text; byte pagination, follow next_offset.", {"path": string, **window}, workspace.read_file, execution="inline", consolidation=True)
    registry.register("search_files", "Find literal text in state Markdown, JSON, TXT and CSV.", {"query": string, "path": string}, workspace.search_files, execution="inline", consolidation=True)
    registry.register("read_artifact", "Read a full stored tool result as JSON text with byte pagination.",
                      {"reference": string, **window}, registry.recorder.read_artifact, execution="inline", consolidation=True)
    if arithmetic:
        registry.register("calculate", "Deterministic arithmetic with explicit inputs and source references. Ratios are fractions; multiply by 100 for percent.",
            {"operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
             "left": {"type": "number"}, "right": {"type": "number"},
             "source_refs": {"type": "array", "items": {"type": "string"}}}, calculate, material=True)
    if writable:
        from research_agent.capabilities.state.advances import register_advance
        register_advance(registry, workspace, journal_root=journal_root, write_guard=write_guard)
    from research_agent.capabilities.state.tools import register_state_tools
    register_state_tools(registry, workspace)


