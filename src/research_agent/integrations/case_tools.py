"""The case experiment's four operations, separate from the general agent loop."""
from ..cases import CaseStore
from ..tools import ToolRegistry


def register_cases(registry: ToolRegistry, store: CaseStore) -> None:
    text = {"type": "string", "minLength": 1}
    identity = {"type": "string", "format": "uuid"}
    nullable_id = {"type": ["string", "null"], "format": "uuid"}
    registry.register("list_cases", "Find previous cases for an asset symbol, e.g. NVDA.",
                      {"asset": text}, store.list_cases)
    registry.register("read_case", "Read a published case revision; null revision selects current. Content is revisable interpretation, not primary evidence.",
                      {"case_id": identity, "revision": nullable_id}, store.read_case)
    registry.register("list_case_revisions", "List published history, newest first, with references and changes.",
                      {"case_id": identity}, store.list_case_revisions)
    registry.register("save_case", "Save complete Markdown as a new immutable revision. For creation use null case_id and expected_revision; otherwise use the current revision read. References must be artifacts/<sha256>.json from this workspace archive. Preserve unresolved uncertainty. No semantic validity is certified.",
                      {"case_id": nullable_id, "asset": {**text, "maxLength": 200},
                       "question": {**text, "maxLength": 4000}, "content": text,
                       "references": {"type": "array", "items": text},
                       "expected_revision": nullable_id, "change": {**text, "maxLength": 4000}}, store.save_case)
    registry.state_readers["cases"] = store.snapshot
    registry.protected_roots.append(store.root)
    registry.consolidation_tools = frozenset({"list_cases", "read_case", "list_case_revisions", "read_artifact", "save_case"})
    registry.publication_reader = store.publications
