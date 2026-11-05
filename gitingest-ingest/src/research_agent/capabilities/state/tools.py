"""State schemas and recoverable package contracts; one effective tool registry."""
from importlib.resources import files
from typing import Any

from research_agent.capabilities.state.operations import StateOperations
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace


def register_state_tools(registry: ToolRegistry, workspace: Workspace) -> None:
    state = StateOperations(workspace)
    string = {"type": "string"}
    nullable_string = {"type": ["string", "null"]}
    purpose = {"type": "string", "minLength": 1, "maxLength": 1000}
    selector: dict[str, Any] = {"type": "object", "properties": {
        "kind": {"type": "string", "enum": ["bytes", "lines", "section"]},
        "start": {"type": "integer", "minimum": 0},
        "end": {"type": ["integer", "null"], "minimum": 0}},
        "required": ["kind", "start", "end"], "additionalProperties": False}
    common = {"purpose": purpose}
    read = {"selector": selector, "expected_sha256": nullable_string, "cursor": nullable_string}
    company = {"symbol": {"type": "string", "minLength": 1, "maxLength": 80},
               "dimension": {"type": "string", "enum": ["modelo", "valoracion", "evaluacion"]}}

    def add(name: str, description: str, properties: dict[str, Any], mutation: bool = False) -> None:
        registry.register(name, description, {**common, **properties}, getattr(state, name),
                          execution="inline", consolidation=True, mutation=mutation, bounded=True)
        group = "company" if "company" in name else "state"
        registry.contracts[name] = {"version": "state-tools-e1", "text": files("research_agent").joinpath(
            f"capabilities/state/contracts/{group}.md").read_text(encoding="utf-8")}

    add("inspect_state", "Map a file (ATX headings) or inventory a directory. Versioned, paginated; no quality inference.",
        {"path": string, "cursor": nullable_string})
    add("read_state", "Read full file with lines,start=1,end=null; bytes start at 0, sections at heading line. First version/cursor=null; continuations require sha256.",
        {"path": string, **read})
    add("search_state", "Literal case-insensitive file/directory search ordered by path,line. Use context_lines=2 (0..8); cursor=null initially.",
        {"path": string, "query": {"type": "string", "minLength": 1},
         "context_lines": {"type": "integer", "minimum": 0, "maximum": 8}, "cursor": nullable_string})
    add("inspect_company", "Inventory preserved company dimensions, ATX headings and explicit IDs; absent does not mean unresearched.",
        {"symbol": company["symbol"], "cursor": nullable_string})
    add("read_company_document", "Read a company dimension using either a selector or unique heading ID; set the unused argument to null.",
        {**company, **read, "selector": {**selector, "type": ["object", "null"]}, "identifier": nullable_string})
    def describe_state_tools(tool: str) -> dict[str, Any]:
        available = {spec.name for spec in registry.specs(registry.active_names)}
        if tool not in registry.contracts or tool not in available:
            raise ValueError("unavailable_contract: choose an available state/company tool.")
        return {"tool": tool, **registry.contracts[tool]}

    registry.contracts["describe_state_tools"] = {"version": "state-tools-e1", "text": files("research_agent").joinpath(
        "capabilities/state/contracts/state.md").read_text(encoding="utf-8")}
    registry.register("describe_state_tools", "Optionally read the versioned contract and examples for an available state/company tool.",
                      {"tool": {"type": "string", "enum": list(registry.contracts)}}, describe_state_tools,
                      execution="inline", consolidation=True, bounded=True)
