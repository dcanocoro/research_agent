"""Offline document campaign definitions; no service construction."""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

import yaml

from research_agent.workspace import Workspace


@dataclass(frozen=True)
class Publication:
    source: Path
    target: str


@dataclass(frozen=True)
class Session:
    id: str
    message: str
    publish: tuple[Publication, ...]


@dataclass(frozen=True)
class Case:
    id: str
    title: str
    context: str
    definition: Path
    rubric: Path
    sessions: tuple[Session, ...]


@dataclass(frozen=True)
class Suite:
    root: Path
    id: str
    cases: tuple[Case, ...]

    def files(self) -> list[Path]:
        return sorted({self.root / "suite.yaml", *(c.definition for c in self.cases),
                       *(c.rubric for c in self.cases),
                       *(p.source for c in self.cases for s in c.sessions for p in s.publish)})


def identifier(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value):
        raise ValueError("Identifiers must start with a letter and use letters, digits, '_' or '-'.")
    if value.split(".")[0].casefold() in {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(10)), *(f"lpt{i}" for i in range(10))}:
        raise ValueError("Reserved Windows identifier.")
    return value


def text(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected nonempty text.")
    return value


def inside(root: Path, relative: Any) -> Path:
    name = text(relative)
    if "\\" in name or ":" in name or Path(name).is_absolute() or any(p in {"..", "."} or p.startswith(".") for p in name.split("/")):
        raise ValueError("Expected a visible relative catalog path.")
    path = root / name
    Workspace._check_links(path)
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Missing file or escaped catalog path: {name}")
    if path.suffix not in Workspace.extensions | {".yaml"}:
        raise ValueError(f"Unsupported catalog file: {name}")
    path.read_text(encoding="utf-8")
    return path


def mapping(value: Any, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(value, dict) or not required <= value.keys() or value.keys() - required - (optional or set()):
        raise ValueError(f"Expected fields {sorted(required)}; unexpected or missing fields.")
    return value


class UniqueLoader(yaml.SafeLoader):
    """Reject silent duplicate YAML keys (not just duplicate case IDs)."""


def unique_mapping(loader: UniqueLoader, node: Any) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if not isinstance(key, str) or key in result:
            raise ValueError("Duplicate or non-string YAML key.")
        result[key] = loader.construct_object(value_node)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def read_yaml(path: Path) -> Any:
    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {path.name}") from exc


def load_suite(root: Path) -> Suite:
    root = root.absolute()
    raw = mapping(read_yaml(inside(root, "suite.yaml")), {"schema_version", "id", "cases"})
    if raw["schema_version"] != "campaign-suite-v1" or not isinstance(raw["cases"], list) or not raw["cases"]:
        raise ValueError("Expected campaign-suite-v1 and a nonempty cases list.")
    cases: list[Case] = []
    case_ids: set[str] = set()
    for entry in raw["cases"]:
        definition = inside(root, entry)
        item = mapping(read_yaml(definition), {"id", "title", "context", "competencies", "difficulty", "rubric", "sessions"})
        case_id = identifier(item["id"])
        if case_id.casefold() in case_ids:
            raise ValueError(f"Duplicate case: {case_id}")
        case_ids.add(case_id.casefold())
        if not isinstance(item["competencies"], list) or not item["competencies"]:
            raise ValueError("Expected competencies list.")
        for competency in item["competencies"]:
            text(competency)
        text(item["difficulty"])
        rubric = inside(definition.parent, item["rubric"])
        if rubric.suffix != ".md":
            raise ValueError("Rubric must be Markdown.")
        if not isinstance(item["sessions"], list) or not item["sessions"]:
            raise ValueError("Expected sessions list.")
        sessions: list[Session] = []
        session_ids: set[str] = set()
        targets: set[str] = set()
        for entry_session in item["sessions"]:
            session = mapping(entry_session, {"id", "message", "publish"})
            session_id = identifier(session["id"])
            if session_id.casefold() in session_ids:
                raise ValueError(f"Duplicate session: {session_id}")
            session_ids.add(session_id.casefold())
            if not isinstance(session["publish"], dict):
                raise ValueError("publish must map workspace paths to input files.")
            publications = []
            for target, source in session["publish"].items():
                target = text(target)
                Workspace(root, create=False).path(target)
                if "\\" in target or target != Path(target).as_posix() or not target.startswith("entradas/") or Path(target).suffix not in Workspace.extensions:
                    raise ValueError("Publications must be text files under entradas/.")
                normalized = target.casefold()
                if any(normalized == old or normalized.startswith(old + "/") or old.startswith(normalized + "/") for old in targets):
                    raise ValueError(f"Publication would overwrite an earlier input: {target}")
                targets.add(normalized)
                original = inside(definition.parent, source)
                if original.suffix not in Workspace.extensions or original.stat().st_size > 128 * 1024:
                    raise ValueError("Input must be supported UTF-8 text, at most 128 KiB.")
                if original.suffix == ".json":
                    json.loads(original.read_text(encoding="utf-8"))
                publications.append(Publication(original, target))
            sessions.append(Session(session_id, text(session["message"]), tuple(publications)))
        cases.append(Case(case_id, text(item["title"]), text(item["context"]), definition, rubric, tuple(sessions)))
    return Suite(root, identifier(raw["id"]), tuple(cases))
