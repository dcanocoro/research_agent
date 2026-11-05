"""Small, removable E2 policies. Declarations are claims, never semantic certificates."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Any

from research_agent.storage.transactions import atomic_bytes
from research_agent.observability.recording import encoded
from research_agent.storage.workspace import Workspace

from importlib.resources import files

_DEFINITION = json.loads(files("research_agent").joinpath("regimes/continuous/identity.json").read_bytes())
POLICY: dict[str, Any] = _DEFINITION["policy"]
INSTRUCTION = _DEFINITION["instruction"]


def identity() -> dict[str, Any]:
    return {"policy": POLICY, "instruction": INSTRUCTION, "policies": [p.__name__ for p in POLICIES]}


def freeze_runtime(root: Path) -> None:
    path = root / "runtime.json"
    Workspace._check_links(path)
    with path.open("xb") as stream:
        stream.write(encoded(identity()))


def validate_runtime(root: Path) -> None:
    path = root / "runtime.json"
    Workspace._check_links(path)
    if not path.is_file() or json.loads(path.read_bytes()) != identity():
        raise ValueError(
            "Incompatible continuous runtime: use previous code or an explicitly authorized migration."
        )


@dataclass(frozen=True)
class Intervention:
    kind: str
    reason: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeState:
    researcher_calls: int = 0
    last_evaluation_call: int = 0
    evaluation_requested: bool = False
    assessment_sha: str | None = None  # Read historical state; no active assessment-path mechanism.
    references: dict[str, dict[str, Any]] = field(default_factory=dict)
    declarations: list[dict[str, Any]] = field(default_factory=list)
    notified: set[str] = field(default_factory=set)
    evaluated_versions: dict[str, str] = field(default_factory=dict)
    feedback: dict[str, Any] | None = None
    observer: dict[str, Any] = field(default_factory=dict)
    unhandled_text: bool = False
    closing_notified: bool = False

    def refresh(self, workspace: Workspace) -> None:
        for declaration in self.declarations:
            stale = False
            for document in declaration["documents"]:
                try:
                    stale |= workspace.read_version(document["path"])[1] != document["sha256"]
                except (OSError, ValueError):
                    stale = True
            if stale:
                declaration["stale"] = True
                for ref in declaration["references"]:
                    if (
                        ref in self.references
                        and self.references[ref].get("declaration") == declaration["receipt"]
                    ):
                        self.references[ref]["disposition"] = "unknown"

    def pending(self) -> list[dict[str, Any]]:
        return [
            {"reference": ref, **value}
            for ref, value in self.references.items()
            if value["disposition"] in {"unknown", "pending"}
        ]

    def view(self) -> dict[str, Any]:
        items = self.pending()
        result: dict[str, Any] = {
            "pending": [],
            "pending_count": len(items),
            "unhandled_text": self.unhandled_text,
            "semantic_validity_assessed": False,
        }
        for item in items:
            if len(encoded({**result, "pending": [*result["pending"], item]})) > 4096:
                break
            result["pending"].append(item)
        result["omitted"] = len(items) - len(result["pending"])
        return result

    def save(self, path: Path, workspace: Workspace, mandate: str) -> None:
        data = {
            **self.__dict__,
            "notified": sorted(self.notified),
            "version": POLICY["version"],
            "workspace": str(workspace.root.resolve()),
            "mandate_sha256": hashlib.sha256(mandate.encode()).hexdigest(),
        }
        atomic_bytes(path, encoded(data))


def recover_state(runs: Path, current: Path, workspace: Workspace, mandate: str) -> RuntimeState:
    for path in sorted(runs.glob("*/runtime/estado.json"), key=lambda p: p.stat().st_mtime_ns, reverse=True):
        if path.parent.parent == current:
            continue
        Workspace._check_links(path)
        data = json.loads(path.read_bytes())
        if (
            data.pop("version", None) != POLICY["version"]
            or data.pop("workspace", None) != str(workspace.root.resolve())
            or data.pop("mandate_sha256", None) != hashlib.sha256(mandate.encode()).hexdigest()
        ):
            continue
        data["notified"] = set(data["notified"])
        state = RuntimeState(**data)
        state.closing_notified = False
        state.refresh(workspace)
        return state
    return RuntimeState()


def evaluation_policy(state: RuntimeState, workspace: Workspace) -> list[Intervention]:
    elapsed = state.researcher_calls - state.last_evaluation_call
    if elapsed >= POLICY["evaluation_backstop"] or (
        state.evaluation_requested and elapsed >= POLICY["evaluation_spacing"]
    ):
        return [Intervention("evaluate", "event" if state.evaluation_requested else "backstop")]
    return []


def reconciliation_policy(state: RuntimeState, workspace: Workspace) -> list[Intervention]:
    state.refresh(workspace)
    proposals = []
    pending = state.view()
    if pending["pending_count"]:
        proposals.append(Intervention("notice", "pending_integration", pending))
    for path, version in state.evaluated_versions.items():
        try:
            current = workspace.read_version(path)[1]
        except (OSError, ValueError):
            current = "missing"
        if current != version:
            proposals.append(
                Intervention(
                    "notice",
                    "review_outdated",
                    {
                        "path": path,
                        "reviewed_sha256": version,
                        "current_sha256": current,
                        "note": "La revisión corresponde a una versión anterior; valora su impacto.",
                    },
                )
            )
    if state.feedback:
        proposals.append(Intervention("notice", "evaluation_feedback", state.feedback))
    return proposals


POLICIES = (evaluation_policy, reconciliation_policy)


def inspect_policies(
    state: RuntimeState, workspace: Workspace
) -> list[Intervention]:
    return [proposal for policy in POLICIES for proposal in policy(state, workspace)]


def register_report(registry: Any, state: RuntimeState, workspace: Workspace) -> None:
    string = {"type": "string"}

    def report(
        kind: str, references: list[str], disposition: str, documents: list[dict[str, str]], reason: str
    ) -> dict[str, Any]:
        if not reason.strip() or len(encoded([references, documents, reason])) > 8192:
            raise ValueError("Supply a brief reason and a report of at most 8 KiB.")
        if disposition == "integrated" and (not documents or not references):
            raise ValueError("Integration requires references and current documents.")
        for ref in references:
            if ref.startswith(("archivo/", "materiales/")):
                registry.recorder.read_artifact(ref, max_bytes=1)
            else:
                path, _, identifier = ref.partition("#")
                raw, _ = workspace.read_version(path)
                if identifier:
                    from research_agent.capabilities.state.operations import headings

                    if sum(h["id"] == identifier for h in headings(raw)) != 1:
                        raise ValueError("missing_or_ambiguous_id")
        for document in documents:
            if workspace.read_version(document["path"])[1] != document["sha256"]:
                raise ValueError("version_conflict: " + document["path"])
        declaration = {
            "kind": kind,
            "references": references,
            "disposition": disposition,
            "documents": documents,
            "reason": reason,
            "stale": False,
            "source": "researcher",
            "semantic_validity_assessed": False,
        }
        # Persist the declaration receipt before changing operational memory.
        ref = registry.recorder.artifact(declaration)
        for reference in references:
            state.references[reference] = {"disposition": disposition, "declaration": ref}
        state.declarations.append({**declaration, "receipt": ref})
        if kind in {"milestone", "blocker"}:
            state.evaluation_requested = True
        if kind == "checkpoint":
            state.unhandled_text = False
        return {**declaration, "receipt": ref}

    registry.register(
        "report_work",
        "Report a milestone/blocker or reference treatment; optional, no knowledge writes or semantic certification.",
        {
            "kind": {"type": "string", "enum": ["milestone", "blocker", "checkpoint", "reconciliation"]},
            "references": {"type": "array", "items": string, "maxItems": 20},
            "disposition": {"type": "string", "enum": ["pending", "integrated", "irrelevant"]},
            "documents": {
                "type": "array",
                "maxItems": 5,
                "items": {
                    "type": "object",
                    "properties": {"path": string, "sha256": string},
                    "required": ["path", "sha256"],
                    "additionalProperties": False,
                },
            },
            "reason": {"type": "string", "minLength": 1},
        },
        report,
        execution="inline",
        bounded=True,
    )


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")).hexdigest()
