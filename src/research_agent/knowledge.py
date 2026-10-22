"""Experimental, append-only argumentative knowledge. No financial truth engine."""
from __future__ import annotations

from contextlib import closing
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any

from jsonschema import Draft202012Validator
from .workspace import Workspace

STRING = {"type": "string", "minLength": 1, "maxLength": 16000}
REF = {"type": "object", "properties": {"id": STRING, "revision": {"type": "integer", "minimum": 1}},
       "required": ["id", "revision"], "additionalProperties": False}
KINDS = ("assessment", "hypothesis", "argument", "evidence", "relation")


def object_schema(properties: dict[str, Any]) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


DATA = {
    "assessment": object_schema({"judgment": STRING, "scope": STRING, "references": {"type": "array", "items": REF}}),
    "hypothesis": object_schema({"proposition": STRING, "status": STRING, "references": {"type": "array", "items": REF}}),
    "argument": object_schema({"premises": {"type": "array", "items": REF, "minItems": 1},
                               "inference": STRING, "conclusion": REF}),
    "evidence": object_schema({"observation": STRING, "source": STRING, "date": {"type": ["string", "null"]},
                               "period": {"type": ["string", "null"]}, "currency": {"type": ["string", "null"]},
                               "units": {"type": ["string", "null"]}}),
    "relation": object_schema({"source": REF, "target": REF,
                               "relation": {"type": "string", "enum": ["supports", "objects", "depends_on"]}}),
}
CHANGE = {"anyOf": [object_schema({"id": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_-]{0,79}$"},
    "kind": {"type": "string", "enum": [kind]}, "expected_revision": {"type": "integer", "minimum": 0},
    "retired": {"type": "boolean"}, "reason": STRING, "data": schema}) for kind, schema in DATA.items()]}


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


class KnowledgeStore:
    def __init__(self, path: Path, workspace: Workspace) -> None:
        Workspace._check_links(path)
        self.path, self.workspace = path.absolute(), workspace
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as db:
            if db.execute("PRAGMA user_version").fetchone()[0] not in {0, 1}:
                raise ValueError("Unsupported argumentative schema version")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS revisions (
                    id TEXT NOT NULL, revision INTEGER NOT NULL, kind TEXT NOT NULL,
                    retired INTEGER NOT NULL, reason TEXT NOT NULL, run TEXT NOT NULL,
                    created_at TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(id, revision));
                CREATE TABLE IF NOT EXISTS impacts (
                    id TEXT NOT NULL, revision INTEGER NOT NULL, cause TEXT NOT NULL,
                    cause_revision INTEGER NOT NULL, run TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS immutable_update BEFORE UPDATE ON revisions
                    BEGIN SELECT RAISE(ABORT, 'Immutable revision'); END;
                CREATE TRIGGER IF NOT EXISTS immutable_delete BEFORE DELETE ON revisions
                    BEGIN SELECT RAISE(ABORT, 'Immutable revision'); END;
                PRAGMA user_version=1;
            """)

    def connect(self) -> sqlite3.Connection:
        Workspace._check_links(self.path)
        db = sqlite3.connect(self.path, timeout=2)
        db.row_factory = sqlite3.Row
        return db

    @staticmethod
    def decode(row: sqlite3.Row) -> dict[str, Any]:
        return {**dict(row), "retired": bool(row["retired"]), "data": json.loads(row["data"])}

    def heads(self, db: sqlite3.Connection) -> dict[str, dict[str, Any]]:
        return {r["id"]: self.decode(r) for r in db.execute(
            "SELECT r.* FROM revisions r JOIN (SELECT id, MAX(revision) v FROM revisions GROUP BY id) h "
            "ON r.id=h.id AND r.revision=h.v ORDER BY r.id")}

    def read(self, id: str, revision: int = 0) -> dict[str, Any]:
        with closing(self.connect()) as db:
            row = db.execute("SELECT * FROM revisions WHERE id=? AND (?=0 OR revision=?) ORDER BY revision DESC LIMIT 1",
                             (id, revision, revision)).fetchone()
            if row is None:
                raise ValueError("Unknown element or revision")
            result = self.decode(row)
            result["pending_review"] = [dict(r) for r in db.execute(
                "SELECT * FROM impacts WHERE id=? AND revision=?", (id, result["revision"]))]
            return result

    def query(self, kind: str = "", text: str = "", offset: int = 0, limit: int = 20) -> dict[str, Any]:
        if kind not in ("", *KINDS) or offset < 0 or not 1 <= limit <= 50:
            raise ValueError("Invalid query window or kind")
        with closing(self.connect()) as db:
            rows = [r for r in self.heads(db).values() if not r["retired"] and (not kind or r["kind"] == kind)
                    and (text.casefold() in r["id"].casefold() or text.casefold() in dumps(r["data"]).casefold())]
        return {"items": [self.read(r["id"]) for r in rows[offset:offset+limit]],
                "next_offset": offset+limit if offset+limit < len(rows) else None}

    def history(self, id: str, offset: int = 0, limit: int = 20) -> dict[str, Any]:
        if offset < 0 or not 1 <= limit <= 50:
            raise ValueError("Invalid history window")
        with closing(self.connect()) as db:
            rows = list(db.execute("SELECT * FROM revisions WHERE id=? ORDER BY revision LIMIT ? OFFSET ?", (id, limit+1, offset)))
        return {"items": [self.decode(r) for r in rows[:limit]], "next_offset": offset+limit if len(rows) > limit else None}

    @staticmethod
    def dependencies(heads: dict[str, dict[str, Any]], *, impact: bool = False) -> dict[str, set[str]]:
        # premise -> argument -> conclusion; depends_on is dependent -> foundation.
        edges: dict[str, set[str]] = {id: set() for id in heads}
        for id, row in heads.items():
            if row["retired"]:
                continue
            data, kind = row["data"], row["kind"]
            if kind in {"assessment", "hypothesis"}:
                for ref in data["references"]:
                    edges[ref["id"]].add(id)
            elif kind == "argument":
                for ref in data["premises"]:
                    edges[ref["id"]].add(id)
                edges[id].add(data["conclusion"]["id"])
            elif kind == "relation":
                source, target = data["source"]["id"], data["target"]["id"]
                if impact:
                    edges[source].add(id)
                    edges[target].add(id)
                if data["relation"] == "depends_on":
                    edges[target].add(source)
                elif impact:
                    edges[source].add(target)
                # Support/objection identifies possible impact, not formal entailment.
        return edges

    @staticmethod
    def reachable(edges: dict[str, set[str]], id: str) -> list[str]:
        visited: set[str] = set()
        todo = list(edges.get(id, ()))
        while todo:
            next_id = todo.pop()
            if next_id not in visited and next_id != id:
                visited.add(next_id)
                todo.extend(edges.get(next_id, ()))
        return sorted(visited)

    def impact(self, id: str) -> dict[str, Any]:
        with closing(self.connect()) as db:
            heads = self.heads(db)
            if id not in heads:
                raise ValueError("Unknown element")
            return {"affected": self.reachable(self.dependencies(heads, impact=True), id)}

    def apply(self, changes: list[dict[str, Any]], run: str) -> dict[str, Any]:
        Draft202012Validator({"type": "array", "items": CHANGE, "minItems": 1, "maxItems": 50}).validate(changes)
        if len({c["id"] for c in changes}) != len(changes):
            raise ValueError("Duplicate element in batch")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            old = self.heads(db)
            heads = dict(old)
            for c in changes:
                previous = old.get(c["id"])
                version = previous["revision"] if previous else 0
                if version != c["expected_revision"]:
                    raise ValueError(f"Stale revision for {c['id']}: expected {c['expected_revision']}, current {version}. "
                                     "Use knowledge_read with this id and revision=0; reconsider the batch using the current revision. "
                                     "expected_revision=0 only creates a missing element. No changes in this batch were saved.")
                if previous and previous["kind"] != c["kind"]:
                    raise ValueError(f"Cannot change kind of {c['id']} from {previous['kind']} to {c['kind']}. "
                                     "Use knowledge_read with this id and revision=0. No changes in this batch were saved.")
                if c["retired"] and previous is None:
                    raise ValueError("Cannot retire a missing element")
                if c["retired"] and previous is not None and c["data"] != previous["data"]:
                    raise ValueError("Retirement must preserve the previous content")
                heads[c["id"]] = {"id": c["id"], "revision": version+1, "kind": c["kind"], "retired": c["retired"],
                    "reason": c["reason"], "run": run, "created_at": datetime.now(timezone.utc).isoformat(), "data": c["data"]}
            for c in changes:
                row = heads[c["id"]]
                if row["retired"]:
                    continue
                data, kind = row["data"], row["kind"]
                refs = data.get("references", data.get("premises", []))
                if kind == "argument":
                    refs = [*refs, data["conclusion"]]
                if kind == "relation":
                    refs = [data["source"], data["target"]]
                for ref in refs:
                    referenced = heads.get(ref["id"])
                    existing = db.execute("SELECT 1 FROM revisions WHERE id=? AND revision=?", (ref["id"], ref["revision"])).fetchone()
                    if referenced is None or (referenced["revision"] != ref["revision"] and existing is None):
                        raise ValueError("Unknown referenced revision")
                    if referenced["retired"]:
                        raise ValueError("New foundations cannot reference a retired element")
                if kind == "argument" and heads[data["conclusion"]["id"]]["kind"] not in {"hypothesis", "assessment"}:
                    raise ValueError("Argument conclusion must be a hypothesis or assessment")
                if kind == "relation" and any(heads[data[end]["id"]]["kind"] == "relation" for end in ("source", "target")):
                    raise ValueError("Relations connect knowledge elements, not relations")
                if kind == "evidence":
                    source = data["source"]
                    path, separator, locator = source.partition("#")
                    if not separator or not locator.strip() or not path.startswith(("entradas/", "materiales/")) or not self.workspace.path(path).is_file():
                        raise ValueError("Evidence needs an existing source path and a #locator")
            edges = self.dependencies(heads)
            # Topological check without recursion; objects/supports may coexist.
            incoming = dict.fromkeys(edges, 0)
            for targets in edges.values():
                for target in targets:
                    incoming[target] += 1
            todo = [id for id, count in incoming.items() if count == 0]
            count = 0
            while todo:
                id = todo.pop()
                count += 1
                for target in edges[id]:
                    incoming[target] -= 1
                    if incoming[target] == 0:
                        todo.append(target)
            if count != len(edges):
                raise ValueError("Circular foundation dependency")
            affected = set()
            # Include old paths: removing a relationship must still invalidate its former dependents.
            old_edges = self.dependencies(old, impact=True)
            impact_edges = self.dependencies(heads, impact=True)
            for c in changes:
                row = heads[c["id"]]
                db.execute("INSERT INTO revisions VALUES (?,?,?,?,?,?,?,?)", (row["id"], row["revision"], row["kind"],
                    row["retired"], row["reason"], run, row["created_at"], dumps(row["data"])))
            for c in changes:
                targets = (set(self.reachable(impact_edges, c["id"])) | set(self.reachable(old_edges, c["id"]))) if c["id"] in old else set()
                relation_changed = c["kind"] == "relation" and (c["id"] not in old or c["retired"] != old[c["id"]]["retired"] or
                    c["data"]["relation"] != old[c["id"]]["data"]["relation"] or
                    any(c["data"][key]["id"] != old[c["id"]]["data"][key]["id"] for key in ("source", "target")))
                if relation_changed:
                    if c["id"] in old:
                        targets.add(old[c["id"]]["data"]["target"]["id"])
                    targets.add(c["data"]["target"]["id"])
                    if c["data"]["relation"] == "depends_on":
                        targets.add(c["data"]["source"]["id"])
                if c["kind"] == "argument":
                    targets.add(c["data"]["conclusion"]["id"])
                    if c["id"] in old:
                        targets.add(old[c["id"]]["data"]["conclusion"]["id"])
                # Mark foundations downstream of added/removed arguments or relations too.
                for target in list(targets):
                    targets.update(self.reachable(impact_edges, target))
                for target in sorted(targets):
                    if heads[target]["retired"]:
                        continue
                    affected.add(target)
                    db.execute("INSERT INTO impacts VALUES (?,?,?,?,?)", (target, heads[target]["revision"], c["id"],
                                                                         heads[c["id"]]["revision"], run))
                data = c["data"]
                pinned = data.get("references", data.get("premises", []))
                if c["kind"] == "relation":
                    pinned = [data["source"], data["target"]]
                if not c["retired"]:
                    for ref in pinned:
                        if ref["revision"] != heads[ref["id"]]["revision"]:
                            affected.add(c["id"])
                            db.execute("INSERT INTO impacts VALUES (?,?,?,?,?)", (c["id"], heads[c["id"]]["revision"],
                                ref["id"], heads[ref["id"]]["revision"], run))
            return {"updated": [{"id": c["id"], "revision": heads[c["id"]]["revision"]} for c in changes],
                    "pending_review": sorted(affected)}

    def export(self) -> dict[str, Any]:
        with closing(self.connect()) as db:
            return {"schema_version": "argumentative-v1", "revisions": [self.decode(r) for r in db.execute(
                "SELECT * FROM revisions ORDER BY id, revision")], "impacts": [dict(r) for r in db.execute(
                    "SELECT * FROM impacts ORDER BY id, revision, cause, cause_revision, run")]}

    def capture(self, directory: Path, phase: str) -> dict[str, Any]:
        target = directory / f"conocimiento-{phase}.sqlite"
        with closing(self.connect()) as source, closing(sqlite3.connect(target)) as dest:
            source.backup(dest)
        copied = KnowledgeStore(target, self.workspace)
        logical = directory / f"conocimiento-{phase}.json"
        logical.write_text(dumps(copied.export()), encoding="utf-8")
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (target, logical)}


def verify_capture(directory: Path) -> None:
    try:
        _verify_capture(directory)
    except (sqlite3.Error, KeyError, TypeError) as exc:
        raise ValueError(f"Invalid knowledge capture: {type(exc).__name__}") from exc


def _verify_capture(directory: Path) -> None:
    """Verify both physical recovery and the independent logical export, read-only."""
    for phase in ("inicial", "final"):
        Workspace._check_links(directory / f"conocimiento-{phase}-hashes.json")
        hashes = json.loads((directory / f"conocimiento-{phase}-hashes.json").read_text(encoding="utf-8"))
        expected = {f"conocimiento-{phase}.{suffix}" for suffix in ("sqlite", "json")}
        if set(hashes) != expected:
            raise ValueError("Incomplete knowledge capture")
        for name, digest in hashes.items():
            path = directory / name
            Workspace._check_links(path)
            if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise ValueError("Knowledge capture hash mismatch")
        source = directory / f"conocimiento-{phase}.sqlite"
        with closing(sqlite3.connect(source.as_uri()+"?mode=ro", uri=True)) as db:
            db.row_factory = sqlite3.Row
            if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Corrupt knowledge database")
            logical = {"schema_version": "argumentative-v1", "revisions": [KnowledgeStore.decode(r) for r in db.execute(
                "SELECT * FROM revisions ORDER BY id, revision")], "impacts": [dict(r) for r in db.execute(
                    "SELECT * FROM impacts ORDER BY id, revision, cause, cause_revision, run")]}
        if logical != json.loads((directory / f"conocimiento-{phase}.json").read_text(encoding="utf-8")):
            raise ValueError("Physical/logical knowledge mismatch")


def register_knowledge(registry: Any, store: KnowledgeStore) -> None:
    async def apply(changes: list[dict[str, Any]]) -> dict[str, Any]:
        # No await/thread between validation and commit: cancellation cannot leave a late writer.
        assert registry.recorder.current is not None
        return store.apply(changes, registry.recorder.current.name)

    async def query(kind: str, text: str, offset: int, limit: int) -> dict[str, Any]:
        return store.query(kind, text, offset, limit)

    async def read(id: str, revision: int) -> dict[str, Any]:
        return store.read(id, revision)

    async def history(id: str, offset: int, limit: int) -> dict[str, Any]:
        return store.history(id, offset, limit)

    async def impact(id: str) -> dict[str, Any]:
        return store.impact(id)

    window = {"offset": {"type": "integer", "minimum": 0}, "limit": {"type": "integer", "minimum": 1, "maximum": 50}}
    registry.register("knowledge_query", "Find current active knowledge by case-insensitive literal substring in ID or content, not semantic search. "
                      "Use a short term, or text='' to list a kind; follow next_offset. An empty result is not proof of absence. "
                      "For a known ID use knowledge_read(id, revision=0).",
        {"kind": {"type": "string", "enum": ["", *KINDS]}, "text": {"type": "string"}, **window}, query)
    registry.register("knowledge_read", "Retrieve directly by exact ID, including pending review causes; revision=0 reads current. "
                      "Prefer this when the index or a previous result gives an ID, even if knowledge_query returned empty.",
        {"id": STRING, "revision": {"type": "integer", "minimum": 0}}, read)
    registry.register("knowledge_history", "Read immutable revisions and reasons.", {"id": STRING, **window}, history)
    registry.register("knowledge_impact", "Find potentially affected dependents; this does not change judgments.", {"id": STRING}, impact)
    registry.register("knowledge_apply", "Atomically create/revise/retire typed knowledge; expected_revision=0 creates only a missing ID. "
                      "On revision conflict, no part of the batch is saved: use knowledge_read(id, revision=0), reconsider and retry with the current revision. "
                      "Preserve source metadata; review affected foundations.",
        {"changes": {"type": "array", "items": CHANGE, "minItems": 1, "maxItems": 50}}, apply)
    registry.consolidation_tools = registry.consolidation_tools | frozenset({"knowledge_query", "knowledge_read",
        "knowledge_history", "knowledge_impact", "knowledge_apply"})
    registry.recorder.knowledge = store
