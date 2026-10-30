"""V5 schemas and recoverable package contracts; one effective tool registry."""
from importlib.resources import files
from typing import Any

from ..state_tools import StateOperations
from ..tools import ToolRegistry
from ..workspace import Workspace


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
    operations: dict[str, Any] = {"type": "array", "minItems": 1, "items": {
        "type": "object", "properties": {
            "kind": {"type": "string", "enum": ["replace", "insert_before", "insert_after"]},
            "target": {"type": "string", "minLength": 1}, "content": string},
        "required": ["kind", "target", "content"], "additionalProperties": False}}
    common = {"purpose": purpose}
    read = {"selector": selector, "expected_sha256": nullable_string, "cursor": nullable_string}
    company = {"symbol": {"type": "string", "minLength": 1, "maxLength": 80},
               "dimension": {"type": "string", "enum": ["modelo", "valoracion", "evaluacion"]}}

    def add(name: str, description: str, properties: dict[str, Any], mutation: bool = False) -> None:
        registry.register(name, description, {**common, **properties}, getattr(state, name),
                          execution="inline", consolidation=True, mutation=mutation, bounded=True)
        group = "company" if "company" in name else "state"
        registry.contracts[name] = {"version": "state-tools-v6.1", "text": files("research_agent").joinpath(
            f"state_contracts/{group}.md").read_text(encoding="utf-8")}

    add("inspect_state", "Map a file (ATX headings) or inventory a directory. Versioned, paginated; no quality inference.",
        {"path": string, "cursor": nullable_string})
    add("read_state", "Read full file with lines,start=1,end=null; bytes start at 0, sections at heading line. First version/cursor=null; continuations require sha256.",
        {"path": string, **read})
    add("search_state", "Literal case-insensitive file/directory search ordered by path,line. Use context_lines=2 (0..8); cursor=null initially.",
        {"path": string, "query": {"type": "string", "minLength": 1},
         "context_lines": {"type": "integer", "minimum": 0, "maximum": 8}, "cursor": nullable_string})
    add("create_state", "Create an absent state file with explicit content; never replace. Original materiales/ remain read-only.",
        {"path": string, "content": string}, True)
    add("edit_state", "Apply exact replacements/anchored insertions against expected_sha256. Each target must be unique; atomic per file.",
        {"path": string, "expected_sha256": {"type": "string", "minLength": 64, "maxLength": 64}, "operations": operations}, True)
    add("inspect_company", "Inventory preserved company dimensions, ATX headings and explicit IDs; absent does not mean unresearched.",
        {"symbol": company["symbol"], "cursor": nullable_string})
    add("read_company_document", "Read a company dimension using either a selector or unique heading ID; set the unused argument to null.",
        {**company, **read, "selector": {**selector, "type": ["object", "null"]}, "identifier": nullable_string})
    add("update_company_document", "Create/edit one dimension; preserves unique IDs and populated bodies. Returns changed sections and literal warnings, not economic validation.",
        {**company, "action": {"type": "string", "enum": ["create", "edit"]},
         "content": nullable_string, "expected_sha256": nullable_string,
         "operations": {**operations, "type": ["array", "null"]}, "reason": purpose,
         "source_refs": {"type": "array", "items": string}}, True)

    def describe_state_tools(tool: str) -> dict[str, Any]:
        available = {spec.name for spec in registry.specs(registry.active_names)}
        if tool not in registry.contracts or tool not in available:
            raise ValueError("unavailable_contract: choose an available state/company tool.")
        return {"tool": tool, **registry.contracts[tool]}

    registry.contracts["describe_state_tools"] = {"version": "state-tools-v6.1", "text": files("research_agent").joinpath(
        "state_contracts/state.md").read_text(encoding="utf-8")}
    registry.register("describe_state_tools", "Optionally read the versioned contract and examples for an available state/company tool.",
                      {"tool": {"type": "string", "enum": list(registry.contracts)}}, describe_state_tools,
                      execution="inline", consolidation=True, bounded=True)
