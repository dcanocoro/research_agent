from __future__ import annotations
from typing import Any
from collections.abc import Callable
"""Bounded UTF-8 state; original materials are owned by tools."""
import hashlib
import os
import json
import tempfile
import threading
from pathlib import Path


def reject_constant(value: str) -> None:
    raise ValueError("Non-standard JSON constant.")


class Workspace:
    extensions = frozenset({".md", ".json", ".txt", ".csv"})
    _locks: dict[str, Any] = {}
    _locks_guard = threading.Lock()

    def __init__(self, root: Path, *, create: bool = True) -> None:
        self.root = root.absolute()
        # Optional domain policy supplied by the tool composition, not owned by the core.
        self.write_validator: Callable[[str, bytes], dict[str, Any]] | None = None
        with self._locks_guard:
            self.mutation_lock = self._locks.setdefault(os.path.normcase(str(self.root.resolve())), threading.RLock())
        self._check_links(self.root)
        if create:
            self.root.mkdir(parents=True, exist_ok=True)
            self.path("materiales").mkdir(exist_ok=True)

    @staticmethod
    def _check_links(path: Path) -> None:
        for candidate in (path, *path.parents):
            if candidate.is_symlink() or (candidate.exists() and
                    getattr(candidate.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("Links and junctions are not allowed in workspaces.")

    def path(self, relative: str) -> Path:
        name = Path(relative)
        if name.is_absolute() or name.drive or ".." in name.parts or ":" in relative:
            raise ValueError("Path escapes the workspace.")
        if any(part.startswith(".") for part in name.parts):
            raise ValueError("Hidden paths are not accessible.")
        for part in name.parts:
            if part.endswith((".", " ")) or part.split(".")[0].lower() in {
                "con", "prn", "aux", "nul", *(f"com{i}" for i in range(10)), *(f"lpt{i}" for i in range(10))
            }:
                raise ValueError("Invalid Windows path component.")
        if len(name.parts) > 3:
            raise ValueError("State supports at most two directory levels.")
        path = self.root / name
        self._check_links(path)
        if path.resolve() != self.root.resolve() and self.root.resolve() not in path.resolve().parents:
            raise ValueError("Path escapes the workspace.")
        return path

    def list_files(self, path: str = ".") -> dict[str, Any]:
        base = self.path(path)
        files = []
        for item in sorted(base.iterdir()):
            self._check_links(item)
            files.append({"path": item.relative_to(self.root).as_posix(), "directory": item.is_dir()})
        return {"files": files}

    def read_file(self, path: str, offset: int = 0, max_bytes: int = 32768) -> dict[str, Any]:
        if offset < 0 or not 1 <= max_bytes <= 32768:
            raise ValueError("Invalid read window.")
        source = self.path(path)
        if source.suffix.lower() not in self.extensions:
            raise ValueError("Unsupported text format.")
        with source.open("rb") as stream:
            stream.seek(offset)
            data = stream.read(max_bytes)
            # Do not split a UTF-8 code point; offsets are bytes.
            text = ""
            if data:
                for trim in range(4):
                    try:
                        chunk = data[:len(data)-trim] if trim else data
                        text = chunk.decode("utf-8")
                        break
                    except UnicodeDecodeError:
                        if trim == 3:
                            raise ValueError("File is not UTF-8, or offset is not a character boundary.") from None
                data = chunk
        next_offset = offset + len(data)
        return {"path": path, "text": text, "offset": offset,
                "next_offset": next_offset if next_offset < source.stat().st_size else None}

    def write_markdown(self, path: str, content: str) -> dict[str, Any]:
        if Path(path).suffix.lower() != ".md":
            raise ValueError("Only Markdown writes are allowed.")
        return self.write_file(path, content)

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        with self.mutation_lock:
            return self.publish(path, content.encode("utf-8"))

    def read_version(self, path: str) -> tuple[bytes, str]:
        source = self.path(path)
        if source.suffix.lower() not in self.extensions:
            raise ValueError("Unsupported text format.")
        raw = source.read_bytes()
        raw.decode("utf-8")
        return raw, hashlib.sha256(raw).hexdigest()

    def publish(self, path: str, raw: bytes, *, create: bool = False,
                expected_sha256: str | None = None) -> dict[str, Any]:
        """Caller holds mutation_lock; external editors are not isolated."""
        content = raw.decode("utf-8")
        target = self.path(path)
        if target.suffix.lower() not in self.extensions:
            raise ValueError("Allowed formats: Markdown, JSON, TXT and CSV.")
        if Path(path).parts[0].casefold() == "materiales":
            raise ValueError("Original materials are read-only for the agent.")
        if len(raw) > 128 * 1024:
            raise ValueError("File exceeds the write limit.")
        if create and target.exists():
            raise FileExistsError("State file already exists; read its version and edit instead.")
        if target.suffix.lower() == ".json":
            try:
                json.loads(content, parse_constant=reject_constant)
            except ValueError:
                raise ValueError("Invalid JSON content.") from None
        details = self.write_validator(path, raw) if self.write_validator is not None else {}
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            # Recheck immediately before publishing; this is not an external CAS.
            self.path(path)
            if expected_sha256 is not None and self.read_version(path)[1] != expected_sha256:
                raise ValueError("version_conflict: reread the current file before editing.")
            if create:
                # Same-filesystem atomic publication with no replacement, also on Windows.
                os.link(temporary, target)
            else:
                temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return {"path": path, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), **details}

    def search_files(self, query: str, path: str = ".") -> dict[str, Any]:
        matches = []
        for directory, children, files in os.walk(self.path(path), followlinks=False):
            children[:] = [child for child in children if not child.startswith(".")]
            for child in children:
                self.path((Path(directory) / child).relative_to(self.root).as_posix())
            for name in sorted(files):
                file = Path(directory) / name
                self._check_links(file)
                if file.suffix.lower() not in self.extensions:
                    continue
                self.path(file.relative_to(self.root).as_posix())
                with file.open(encoding="utf-8") as stream:
                    for line, text in enumerate(stream, 1):
                        if query.casefold() in text.casefold():
                            matches.append({"path": file.relative_to(self.root).as_posix(), "line": line, "text": text[:1000]})
                            if len(matches) >= 50:
                                return {"matches": matches, "limited": True}
        return {"matches": matches, "limited": False}

    def snapshot(self, errors: list[dict[str, str]] | None = None) -> dict[str, str]:
        result = {}
        def walk_error(exc: OSError) -> None:
            if errors is None:
                raise exc
            errors.append({"operation": "state_snapshot", "error_type": type(exc).__name__})
        for directory, children, files in os.walk(self.root, followlinks=False, onerror=walk_error):
            for child in list(children):
                try:
                    self.path((Path(directory) / child).relative_to(self.root).as_posix())
                except ValueError as exc:
                    if errors is None:
                        raise
                    children.remove(child)
                    errors.append({"operation": "state_snapshot", "path": str(child), "error_type": type(exc).__name__})
            for name in files:
                path = Path(directory) / name
                if path.suffix.lower() in self.extensions:
                    relative = path.relative_to(self.root).as_posix()
                    try:
                        self.path(relative)
                        result[relative] = path.read_text(encoding="utf-8")
                    except (ValueError, OSError) as exc:
                        if errors is None:
                            raise
                        errors.append({"operation": "state_snapshot", "path": relative, "error_type": type(exc).__name__})
        return result
