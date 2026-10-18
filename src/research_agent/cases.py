"""Local versioned case documents. Interpretation remains Markdown, not a graph."""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import os
import sys
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from .recording import RunRecorder, encoded
from .workspace import Workspace


class CaseContract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class CaseBinding(CaseContract):
    schema_version: str = "case-store-v1"
    store_id: UUID
    root: str
    workspace: str
    archive: str


class InvestmentCase(CaseContract):
    case_id: UUID
    asset: str = Field(min_length=1, max_length=200)
    question: str = Field(min_length=1, max_length=4000)
    created_at: datetime
    current_revision: UUID


class CaseRevision(CaseContract):
    revision_id: UUID
    case_id: UUID
    parent_revision: UUID | None
    created_at: datetime
    change: str = Field(min_length=1, max_length=4000)
    references: tuple[str, ...]
    run_id: UUID
    content_sha256: str


def disjoint(left: Path, right: Path) -> None:
    a, b = left.resolve(), right.resolve()
    if a == b or a in b.parents or b in a.parents:
        raise ValueError("Case store, workspace, archive and instructions must be disjoint.")


class CaseStore:
    def __init__(self, root: Path, workspace: Path, recorder: RunRecorder) -> None:
        self.root = root.absolute()
        self.workspace = workspace.resolve()
        self.recorder = recorder
        for other in (workspace, recorder.root, Path(__file__).parent):
            disjoint(root, other)
        Workspace._check_links(self.root)
        Workspace._check_links(workspace)
        Workspace._check_links(recorder.root)
        self.root.mkdir(parents=True, exist_ok=True)
        with self._lock():
            path = self._path("binding.json")
            if path.exists():
                self.binding = CaseBinding.model_validate_json(path.read_bytes())
                if (self.binding.root != str(self.root.resolve()) or
                        self.binding.workspace != str(self.workspace) or
                        self.binding.archive != str(recorder.root.resolve())):
                    raise ValueError("Case store is bound to another location, workspace or archive.")
            else:
                if any(p.name != ".lock" for p in self.root.iterdir()):
                    raise ValueError("Cannot bind a nonempty case store without binding.json.")
                self.binding = CaseBinding(store_id=uuid4(), root=str(self.root.resolve()),
                                           workspace=str(self.workspace), archive=str(recorder.root.resolve()))
                self._atomic(path, self.binding.model_dump(mode="json"))

    def _path(self, *parts: str) -> Path:
        path = self.root.joinpath(*parts)
        Workspace._check_links(path)
        if path.resolve() != self.root.resolve() and self.root.resolve() not in path.resolve().parents:
            raise ValueError("Path escapes case store.")
        return path

    @contextmanager
    def _lock(self) -> Iterator[None]:
        # OS-held locks are released on process exit; the lock file is never deleted.
        with self._path(".lock").open("a+b") as stream:
            if stream.seek(0, 2) == 0:
                stream.write(b"\0")
                stream.flush()
            stream.seek(0)
            try:
                if sys.platform == "win32":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                raise ValueError("Case store is busy; retry after the current operation finishes.") from None
            try:
                yield
            finally:
                stream.seek(0)
                if sys.platform == "win32":
                    import msvcrt
                    msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    @staticmethod
    def _atomic(path: Path, value: Any) -> None:
        # Preserve an interrupted temporary file for diagnosis, rather than hiding it.
        temporary = path.with_name(f".{path.name}.{uuid4()}.tmp")
        with temporary.open("xb") as stream:
            stream.write(encoded(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)

    @staticmethod
    def _exclusive(path: Path, data: bytes) -> None:
        with path.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())

    def _case(self, case_id: str) -> InvestmentCase:
        identity = str(UUID(case_id))
        case = InvestmentCase.model_validate_json(self._path(identity, "case.json").read_bytes())
        if str(case.case_id) != identity:
            raise ValueError("Case identity mismatch.")
        return case

    def _revision(self, case_id: UUID, revision_id: UUID) -> tuple[CaseRevision, str]:
        folder = (str(case_id), "revisions")
        revision = CaseRevision.model_validate_json(self._path(*folder, f"{revision_id}.json").read_bytes())
        if revision.case_id != case_id or revision.revision_id != revision_id:
            raise ValueError("Revision identity mismatch.")
        data = self._path(*folder, f"{revision_id}.md").read_bytes()
        if hashlib.sha256(data).hexdigest() != revision.content_sha256:
            raise ValueError("Revision content hash mismatch.")
        return revision, data.decode("utf-8")

    def _history(self, case: InvestmentCase) -> list[CaseRevision]:
        result: list[CaseRevision] = []
        seen: set[UUID] = set()
        pointer: UUID | None = case.current_revision
        while pointer is not None:
            if pointer in seen:
                raise ValueError("Revision history contains a cycle.")
            seen.add(pointer)
            revision, _ = self._revision(case.case_id, pointer)
            result.append(revision)
            pointer = revision.parent_revision
        return result

    def _record(self, action: str, case: InvestmentCase, **fields: Any) -> None:
        self.recorder.event(f"lab.case.{action}", store_id=str(self.binding.store_id),
                            case_id=str(case.case_id), current_revision=str(case.current_revision), **fields)

    def list_cases(self, asset: str) -> dict[str, Any]:
        with self._lock():
            cases = []
            for entry in sorted(self.root.iterdir()):
                if not entry.is_dir():
                    continue
                try:
                    identity = str(UUID(entry.name))
                except ValueError:
                    continue
                if self._path(identity, "case.json").exists():
                    case = self._case(identity)
                    if case.asset.casefold() == asset.strip().casefold():
                        self._history(case)
                        cases.append(case.model_dump(mode="json"))
                        self._record("listed", case)
            return {"cases": cases}

    def read_case(self, case_id: str, revision: str | None = None) -> dict[str, Any]:
        with self._lock():
            case = self._case(case_id)
            history = self._history(case)
            selected = UUID(revision) if revision else case.current_revision
            if selected not in {r.revision_id for r in history}:
                raise ValueError("Revision is not in published case history.")
            item, content = self._revision(case.case_id, selected)
            self._record("read", case, selected_revision=str(selected))
            return {"case": case.model_dump(mode="json"),
                    "revision": item.model_dump(mode="json"), "content": content}

    def list_case_revisions(self, case_id: str) -> dict[str, Any]:
        with self._lock():
            case = self._case(case_id)
            history = self._history(case)
            self._record("history_read", case)
            return {"case_id": str(case.case_id), "current_revision": str(case.current_revision),
                    "revisions": [r.model_dump(mode="json") for r in history]}

    def save_case(self, case_id: str | None, asset: str, question: str, content: str,
                  references: list[str], expected_revision: str | None, change: str) -> dict[str, Any]:
        if not content.strip() or len(content.encode("utf-8")) > 128 * 1024:
            raise ValueError("Case content must be nonempty Markdown, at most 128 KiB.")
        if self.recorder.current is None:
            raise ValueError("Saving a case requires an active run.")
        fingerprint = hashlib.sha256(str(self.workspace).encode()).hexdigest()
        if self.recorder.workspace_fingerprint != fingerprint:
            raise ValueError("Active run belongs to another workspace.")
        asset = asset.strip().upper()
        with self._lock():
            for reference in references:
                self.recorder.read_artifact(reference, max_bytes=4)
            old: InvestmentCase | None = None
            if case_id is not None:
                old = self._case(case_id)
                if expected_revision is None or UUID(expected_revision) != old.current_revision:
                    raise ValueError(f"Revision conflict; read_case again. Current revision: {old.current_revision}")
                if old.asset != asset or old.question != question:
                    raise ValueError("Asset and original question are immutable; create another case for a different question.")
                self._history(old)
            elif expected_revision is not None:
                raise ValueError("A new case requires null case_id and expected_revision.")
            now = datetime.now(timezone.utc)
            identity, revision_id = old.case_id if old else uuid4(), uuid4()
            case = InvestmentCase(case_id=identity, asset=asset, question=question,
                                  created_at=old.created_at if old else now, current_revision=revision_id)
            revision = CaseRevision(revision_id=revision_id, case_id=identity,
                                    parent_revision=old.current_revision if old else None, created_at=now,
                                    change=change, references=tuple(dict.fromkeys(references)),
                                    run_id=UUID(self.recorder.current.name),
                                    content_sha256=hashlib.sha256(content.encode("utf-8")).hexdigest())
            folder = self._path(str(identity), "revisions")
            folder.mkdir(parents=True, exist_ok=True)
            self._exclusive(self._path(str(identity), "revisions", f"{revision_id}.md"), content.encode("utf-8"))
            self._exclusive(self._path(str(identity), "revisions", f"{revision_id}.json"),
                            encoded(revision.model_dump(mode="json")))
            self._atomic(self._path(str(identity), "case.json"), case.model_dump(mode="json"))
            self._record("saved", case, previous_revision=str(old.current_revision) if old else None)
            return {"case": case.model_dump(mode="json"), "revision": revision.model_dump(mode="json")}

    def publications(self, run_id: str) -> list[dict[str, str]]:
        """Confirm this run's published revisions from disk, excluding orphan writes."""
        producer = UUID(run_id)
        revisions = []
        with self._lock():
            for entry in sorted(self.root.iterdir()):
                if not entry.is_dir():
                    continue
                try:
                    identity = str(UUID(entry.name))
                except ValueError:
                    continue
                if not self._path(identity, "case.json").exists():
                    continue
                for revision in self._history(self._case(identity)):
                    if revision.run_id == producer:
                        for reference in revision.references:
                            self.recorder.read_artifact(reference, max_bytes=4)
                        revisions.append({"case_id": identity, "revision_id": str(revision.revision_id)})
        return revisions

    def snapshot(self) -> dict[str, Any]:
        """Heads and uncommitted leftovers, not extra context injected into the LLM."""
        with self._lock():
            heads: dict[str, str] = {}
            leftovers: list[str] = []
            for entry in sorted(self.root.iterdir()):
                if not entry.is_dir():
                    if entry.suffix == ".tmp":
                        leftovers.append(entry.name)
                    continue
                try:
                    identity = str(UUID(entry.name))
                except ValueError:
                    continue
                published: set[str] = {"case.json"}
                if self._path(identity, "case.json").exists():
                    case = self._case(identity)
                    heads[identity] = str(case.current_revision)
                    for revision in self._history(case):
                        published.update({f"revisions/{revision.revision_id}.json", f"revisions/{revision.revision_id}.md"})
                for file in entry.rglob("*"):
                    self._path(*file.relative_to(self.root).parts)
                    if file.is_file() and file.relative_to(entry).as_posix() not in published:
                        leftovers.append(file.relative_to(self.root).as_posix())
            return {"store_id": str(self.binding.store_id), "heads": heads, "unpublished_files": leftovers}
