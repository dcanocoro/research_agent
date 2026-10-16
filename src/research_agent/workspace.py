from __future__ import annotations
from typing import Any
"""Bounded Markdown workspace; artifacts and instructions live elsewhere."""
import hashlib
import os
from pathlib import Path


class Workspace:
    def __init__(self, root: Path) -> None:
        self.root = root.absolute()
        self._check_links(self.root)
        self.root.mkdir(parents=True, exist_ok=True)
        for name in ("memory", "notes", "reports"):
            self.path(name).mkdir(exist_ok=True)

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
        target = self.path(path)
        if target.suffix.lower() != ".md":
            raise ValueError("Only Markdown writes are allowed.")
        if len(content.encode("utf-8")) > 128 * 1024:
            raise ValueError("Markdown exceeds the write limit.")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"path": path, "bytes": target.stat().st_size,
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}

    def search_files(self, query: str, path: str = ".") -> dict[str, Any]:
        matches = []
        for directory, children, files in os.walk(self.path(path), followlinks=False):
            for child in children:
                self._check_links(Path(directory) / child)
            for name in sorted(files):
                file = Path(directory) / name
                self._check_links(file)
                if file.suffix.lower() != ".md":
                    continue
                with file.open(encoding="utf-8") as stream:
                    for line, text in enumerate(stream, 1):
                        if query.casefold() in text.casefold():
                            matches.append({"path": file.relative_to(self.root).as_posix(), "line": line, "text": text[:1000]})
                            if len(matches) >= 50:
                                return {"matches": matches, "limited": True}
        return {"matches": matches, "limited": False}

    def snapshot(self) -> dict[str, str]:
        result = {}
        for directory, children, files in os.walk(self.root, followlinks=False):
            for child in children:
                self._check_links(Path(directory) / child)
            for name in files:
                path = Path(directory) / name
                self._check_links(path)
                if path.suffix.lower() == ".md":
                    result[path.relative_to(self.root).as_posix()] = path.read_text(encoding="utf-8")
        return result
