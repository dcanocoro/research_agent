"""Deterministic, versioned views over the existing workspace, without semantic inference."""
from __future__ import annotations

import base64
from bisect import bisect_right
import difflib
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

from .recording import encoded
from .workspace import Workspace

VIEW_BYTES = 24000  # Reserve the remainder of 32 KiB for registry metadata and escaping.
DIMENSIONS = ("modelo", "valoracion", "evaluacion")


def digest(value: Any) -> str:
    return hashlib.sha256(encoded(value)).hexdigest()


def purpose_text(purpose: str) -> None:
    if not purpose.strip():
        raise ValueError("purpose_required: provide a brief purpose.")


def headings(raw: bytes) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    fence: tuple[str, int] | None = None
    offset = 0
    for number, line in enumerate(raw.decode("utf-8").splitlines(keepends=True), 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line.rstrip("\r\n"))
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
        elif marker and not (marker[1][0] == "`" and "`" in marker[2]):
            fence = (marker[1][0], len(marker[1]))
        else:
            match = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*?)|[ \t]*)$", line.rstrip("\r\n"))
            if match:
                title = re.sub(r"[ \t]+#+[ \t]*$", "", match[2] or "")
                identifier = re.match(r"^([A-Za-z][A-Za-z0-9_-]*\d+)\b", title)
                result.append({"line": number, "offset": offset, "level": len(match[1]),
                               "title": title[:256], "title_partial": len(title) > 256,
                               "id": identifier[1] if identifier else None})
        offset += len(line.encode("utf-8"))
    return result


def section_text(raw: bytes, heading: dict[str, Any], hs: list[dict[str, Any]]) -> str:
    """The same ATX boundary used by read_state, including subsections."""
    end = next((h["offset"] for h in hs if h["line"] > heading["line"]
                and h["level"] <= heading["level"]), len(raw))
    return raw[heading["offset"]:end].decode("utf-8")


def section_has_body(text: str) -> bool:
    raw = text.encode("utf-8")
    heading_lines = {h["line"] for h in headings(raw)}
    return any(line.strip() for n, line in enumerate(text.splitlines(), 1) if n not in heading_lines)


def cursor_for(signature: str, position: int) -> str:
    return base64.urlsafe_b64encode(encoded({"signature": signature, "position": position})).decode("ascii")


def cursor_position(cursor: str | None, signature: str) -> int:
    if cursor is None:
        return 0
    try:
        value = json.loads(base64.b64decode(cursor, altchars=b"-_", validate=True))
        if value["signature"] != signature:
            raise ValueError("continuation_changed: restart with the current versions and original selectors.")
        position = value["position"]
        if type(position) is not int or position < 0:
            raise ValueError("invalid_cursor")
        return position
    except (KeyError, TypeError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid_cursor") from exc


def page(items: list[dict[str, Any]], metadata: dict[str, Any], signature: str,
         cursor: str | None, limit: int = 50) -> dict[str, Any]:
    start = cursor_position(cursor, signature)
    if start > len(items):
        raise ValueError("invalid_cursor")
    end = min(start + limit, len(items))
    while True:
        value = {**metadata, "items": items[start:end], "limited": end < len(items),
                 "continuation": cursor_for(signature, end) if end < len(items) else None}
        if len(encoded(value)) <= VIEW_BYTES:
            return value
        if end <= start + 1:
            raise ValueError("view_limit: narrow the selection.")
        end -= 1


class StateOperations:
    def __init__(self, workspace: Workspace) -> None:
        self.workspace = workspace
        workspace.write_validator = self.validate_company_write

    def validate_company_write(self, path: str, raw: bytes) -> dict[str, Any]:
        """Protect company documents across every writer in this tool composition."""
        parts = Path(path).parts
        if (len(parts) != 3 or parts[0].casefold() != "empresas"
                or parts[2].casefold() not in {f"{d}.md" for d in DIMENSIONS}):
            return {}
        # Normalize only for dispatch; Workspace still owns path validation/publication.
        self.company_path(parts[1], parts[2].casefold()[:-3])
        target = self.workspace.path(path)
        old = self.workspace.read_version(path)[0] if target.exists() else b""
        old_hs, new_hs = headings(old), headings(raw)
        old_counts = Counter(h["id"] for h in old_hs if h["id"])
        new_counts = Counter(h["id"] for h in new_hs if h["id"])
        if any(new_counts[k] == 0 for k in old_counts):
            raise ValueError("id_changed: preserve existing IDs; repair by explicit content edits.")
        if any(n > 1 for n in new_counts.values()):
            raise ValueError("duplicate_ids: each company ID must be unique before publication.")
        previous = {h["id"]: section_text(old, h, old_hs) for h in old_hs if h["id"]}
        current = {h["id"]: section_text(raw, h, new_hs) for h in new_hs if h["id"]}
        emptied = [key for key, text in previous.items() if section_has_body(text)
                   and not section_has_body(current[key])]
        if emptied:
            raise ValueError("empty_section: populated IDs would lose their recoverable body: " + ", ".join(emptied)[:300])
        changed = [key for key, text in current.items() if previous.get(key) != text]
        empty = [key for key, text in current.items() if not section_has_body(text)]
        # Literal local references only. Missing/future destinations are warnings, not financial verdicts.
        refs = sorted(set(re.findall(r"(?:empresas/[A-Za-z0-9.-]+/(?:modelo|valoracion|evaluacion)\.md)?#[A-Za-z][A-Za-z0-9_-]*\d+\b", raw.decode("utf-8"))))
        unresolved = []
        for ref in refs:
            ref_path, identifier = ref.split("#", 1)
            if not ref_path:
                ref_path = path
            try:
                ref_raw = raw if ref_path == path else self.workspace.read_version(ref_path)[0]
                count = sum(h["id"] == identifier for h in headings(ref_raw))
                status = "missing_id" if count == 0 else "ambiguous_id" if count > 1 else "resolved"
            except (OSError, ValueError):
                status = "unavailable_document"
            if status != "resolved":
                unresolved.append({"reference": ref, "status": status})
        visible_changed = [key for key in changed if len(encoded(key)) <= 512][:20]
        visible_empty = [key for key in empty if len(encoded(key)) <= 512][:20]
        visible_unresolved = [ref for ref in unresolved if len(encoded(ref)) <= 1000][:20]
        recovered = []
        for heading in new_hs:
            if heading["id"] in visible_changed:
                text = current[heading["id"]]
                recovered.append({"identifier": heading["id"], "text": text[:1200],
                                  "partial": len(text) > 1200,
                                  "selector": {"kind": "section", "start": heading["line"], "end": None}})
        details: dict[str, Any] = {"changed_ids": visible_changed, "changed_ids_omitted": len(changed) - len(visible_changed),
                   "validation": {"duplicate_ids": [], "empty_ids": visible_empty,
                                  "empty_ids_omitted": len(empty) - len(visible_empty),
                                  "unresolved_references": visible_unresolved,
                                  "unresolved_references_omitted": len(unresolved) - len(visible_unresolved),
                                  "scope": "literal structure and local ID references; no semantic or numerical certification"},
                   "recovered_sections": recovered,
                   "recovery": "Use read_company_document with identifier and returned sha256; unused selector=null. Inspect for omitted IDs."}
        while len(encoded(details)) > 18000 and recovered:
            recovered.pop()
        while len(encoded(details)) > 18000 and visible_unresolved:
            visible_unresolved.pop()
            details["validation"]["unresolved_references_omitted"] += 1
        details["recovered_sections_omitted"] = len(changed) - len(recovered)
        return details

    def _files(self, path: str) -> list[str]:
        base = self.workspace.path(path)
        if not base.exists():
            raise FileNotFoundError(path)
        if base.is_file():
            self.workspace.read_version(path)
            return [base.relative_to(self.workspace.root).as_posix()]
        result = []
        for directory, children, names in os.walk(base, followlinks=False):
            children[:] = sorted(child for child in children if not child.startswith("."))
            for name in [*children, *sorted(names)]:
                if name.startswith("."):
                    continue
                item = Path(directory) / name
                relative = item.relative_to(self.workspace.root).as_posix()
                self.workspace.path(relative)
                if item.is_file() and item.suffix.lower() in self.workspace.extensions:
                    result.append(relative)
        return sorted(result)

    def inspect_state(self, path: str, purpose: str, cursor: str | None) -> dict[str, Any]:
        purpose_text(purpose)
        paths = self._files(path)
        items: list[dict[str, Any]] = []
        versions = {}
        file_mode = self.workspace.path(path).is_file()
        for name in paths:
            raw, version = self.workspace.read_version(name)
            versions[name] = version
            items.append({"path": name, "bytes": len(raw), "sha256": version, "kind": "file"})
            if file_mode:
                items.extend({"path": name, "kind": "heading", **h} for h in headings(raw))
        signature = digest(["inspect", path, versions])
        return page(items, {"path": path, "version": signature, "structure": "ATX outside fenced code only"}, signature, cursor)

    def read_state(self, path: str, purpose: str, selector: dict[str, Any],
                   expected_sha256: str | None, cursor: str | None) -> dict[str, Any]:
        purpose_text(purpose)
        raw, version = self.workspace.read_version(path)
        if expected_sha256 is not None and expected_sha256 != version:
            raise ValueError("version_conflict: restart from the current document.")
        if cursor is not None and expected_sha256 is None:
            raise ValueError("version_required: continuation requires expected_sha256.")
        kind, start, end = selector["kind"], selector["start"], selector["end"]
        lines = raw.decode("utf-8").splitlines(keepends=True)
        offsets = [0]
        for line in lines:
            offsets.append(offsets[-1] + len(line.encode("utf-8")))
        hs = headings(raw)
        if kind == "bytes":
            if start is None or start < 0 or (end is not None and end < start):
                raise ValueError("invalid_selector: byte offsets start at zero; end is exclusive.")
            low, high = start, len(raw) if end is None else end
        elif kind == "lines":
            if start is None or start < 1 or (end is not None and end < start) or start > max(1, len(lines)):
                raise ValueError("invalid_selector: inclusive line numbers start at one.")
            low = offsets[min(start - 1, len(lines))]
            high = offsets[min(len(lines), len(lines) if end is None else end)]
        elif kind == "section":
            selected = [h for h in hs if h["line"] == start]
            if len(selected) != 1 or end is not None:
                raise ValueError("invalid_selector: section requires one heading start line and null end.")
            heading = selected[0]
            low = heading["offset"]
            high = low + len(section_text(raw, heading, hs).encode("utf-8"))
        else:
            raise ValueError("invalid_selector")
        if high > len(raw) or low > len(raw):
            raise ValueError("invalid_selector: range exceeds file.")
        try:
            raw[:low].decode("utf-8")
            raw[low:high].decode("utf-8")
        except UnicodeError as exc:
            raise ValueError("invalid_selector: byte range splits a UTF-8 character.") from exc
        signature = digest(["read", path, version, selector])
        consumed = cursor_position(cursor, signature)
        if consumed > high - low:
            raise ValueError("invalid_cursor")
        offset = low + consumed
        chunk = raw[offset:min(high, offset + 12000)]
        text = chunk.decode("utf-8", errors="ignore")
        while True:
            next_byte = offset + len(text.encode("utf-8"))
            context = [h for h in hs if h["offset"] <= offset]
            value = {"path": path, "sha256": version, "selector": selector, "text": text,
                     "offset": offset, "end_offset": next_byte, "selection_end": high,
                     "start_line": bisect_right(offsets, offset),
                     "heading": context[-1] if context else None,
                     "limited": next_byte < high,
                     "continuation": cursor_for(signature, next_byte - low) if next_byte < high else None}
            if len(encoded(value)) <= VIEW_BYTES:
                return value
            text = text[:len(text) // 2]

    def search_state(self, path: str, query: str, purpose: str, context_lines: int,
                     cursor: str | None) -> dict[str, Any]:
        purpose_text(purpose)
        if not query or not 0 <= context_lines <= 8:
            raise ValueError("invalid_search: nonempty query and 0..8 context lines required.")
        items = []
        versions = {}
        for name in self._files(path):
            raw, version = self.workspace.read_version(name)
            versions[name] = version
            lines = raw.decode("utf-8").splitlines()
            for index, text in enumerate(lines):
                if query.casefold() in text.casefold():
                    first, last = max(0, index - context_lines), min(len(lines), index + context_lines + 1)
                    fragment = "\n".join(lines[first:last])
                    # A very long line is an explicitly partial view, recoverable by read_state.
                    excerpt_start = 0
                    if len(fragment.encode("utf-8")) > 1200:
                        # Center on an actual match, including when casefold expands a character.
                        folded_position = fragment.casefold().find(query.casefold())
                        folded_count = 0
                        character = 0
                        for character, char in enumerate(fragment):
                            if folded_count >= folded_position:
                                break
                            folded_count += len(char.casefold())
                        excerpt_start = len(fragment[:max(0, character - 100)].encode("utf-8"))
                    excerpt = fragment.encode("utf-8")[excerpt_start:excerpt_start + 1200].decode("utf-8", errors="ignore")
                    items.append({"path": name, "sha256": version, "line": index + 1,
                                  "context_start_line": first + 1, "context_end_line": last,
                                  "excerpt_offset": excerpt_start,
                                  "text": excerpt, "text_partial": excerpt != fragment,
                                  "recovery": "read_state with lines selector and this sha256"})
        signature = digest(["search", path, query, context_lines, versions])
        return page(items, {"path": path, "query": query, "context_lines": context_lines,
                            "order": "path,line", "version": signature}, signature, cursor)

    def create_state(self, path: str, content: str, purpose: str) -> dict[str, Any]:
        purpose_text(purpose)
        with self.workspace.mutation_lock:
            value = self.workspace.publish(path, content.encode("utf-8"), create=True)
        return {**value, "applied": True, "previous_sha256": None, "operation": "create"}

    def edit_state(self, path: str, expected_sha256: str, operations: list[dict[str, str]],
                   purpose: str) -> dict[str, Any]:
        purpose_text(purpose)
        if not operations:
            raise ValueError("empty_edit: supply explicit operations.")
        with self.workspace.mutation_lock:
            raw, version = self.workspace.read_version(path)
            if version != expected_sha256:
                raise ValueError("version_conflict: reread the current file before editing.")
            original = raw.decode("utf-8")
            updated = original
            for operation in operations:
                target, content, kind = operation["target"], operation["content"], operation["kind"]
                # Count overlapping occurrences too.
                if not target or len(list(re.finditer(f"(?={re.escape(target)})", updated))) != 1:
                    raise ValueError("ambiguous_target: each target must occur exactly once.")
                replacement = content if kind == "replace" else content + target if kind == "insert_before" else target + content
                if kind not in {"replace", "insert_before", "insert_after"}:
                    raise ValueError("invalid_edit")
                updated = updated.replace(target, replacement, 1)
            value = self.workspace.publish(path, updated.encode("utf-8"), expected_sha256=version)
        diff = "".join(difflib.unified_diff(original.splitlines(keepends=True), updated.splitlines(keepends=True),
                                          fromfile=path, tofile=path))
        return {**value, "applied": True, "previous_sha256": version, "operation": "edit",
                "operations_applied": len(operations), "diff": diff, "diff_partial": False}

    def company_path(self, symbol: str, dimension: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*", symbol) or dimension not in DIMENSIONS:
            raise ValueError("invalid_company: use a resolved ASCII symbol and a supported dimension.")
        name = f"empresas/{symbol}/{dimension}.md"
        self.workspace.path(name)
        root = self.workspace.path("empresas")
        if root.exists() and any(p.name.casefold() == symbol.casefold() and p.name != symbol for p in root.iterdir()):
            raise ValueError("company_case_collision: use the existing symbol spelling.")
        return name

    def inspect_company(self, symbol: str, purpose: str, cursor: str | None) -> dict[str, Any]:
        purpose_text(purpose)
        items = []
        versions: dict[str, str | None] = {}
        for dimension in DIMENSIONS:
            path = self.company_path(symbol, dimension)
            exists = self.workspace.path(path).is_file()
            if not exists:
                versions[path] = None
                items.append({"path": path, "dimension": dimension, "exists": False,
                              "meaning": "not preserved; does not establish whether it was researched"})
                continue
            raw, version = self.workspace.read_version(path)
            versions[path] = version
            hs = headings(raw)
            duplicates = sorted(k for k, n in Counter(h["id"] for h in hs if h["id"]).items() if n > 1)
            items.append({"path": path, "dimension": dimension, "exists": True, "sha256": version,
                          "bytes": len(raw), "duplicate_ids": duplicates})
            items.extend({"path": path, "kind": "heading", **h} for h in hs)
        signature = digest(["company", symbol, versions])
        return page(items, {"symbol": symbol, "version": signature,
                            "structure": "ATX outside fenced code only; no semantic completeness check"}, signature, cursor)

    def read_company_document(self, symbol: str, dimension: str, purpose: str,
                              selector: dict[str, Any] | None, identifier: str | None,
                              expected_sha256: str | None, cursor: str | None) -> dict[str, Any]:
        path = self.company_path(symbol, dimension)
        if (selector is None) == (identifier is None):
            raise ValueError('invalid_selector: for an ID use identifier="H1", selector=null; for the whole file use identifier=null, selector={"kind":"lines","start":1,"end":null}.')
        if identifier is not None:
            raw, version = self.workspace.read_version(path)
            matches = [h for h in headings(raw) if h["id"] == identifier]
            if len(matches) != 1:
                raise ValueError("ambiguous_id: ID must identify exactly one heading; use line selection.")
            if expected_sha256 is not None and expected_sha256 != version:
                raise ValueError("version_conflict")
            if cursor is not None and expected_sha256 is None:
                raise ValueError("version_required")
            expected_sha256 = version
            selector = {"kind": "section", "start": matches[0]["line"], "end": None}
        assert selector is not None
        return self.read_state(path, purpose, selector, expected_sha256, cursor)

    def update_company_document(self, symbol: str, dimension: str, purpose: str, action: str,
                                content: str | None, expected_sha256: str | None,
                                operations: list[dict[str, str]] | None, reason: str,
                                source_refs: list[str]) -> dict[str, Any]:
        path = self.company_path(symbol, dimension)
        if not reason.strip():
            raise ValueError("reason_required")
        with self.workspace.mutation_lock:
            if action == "create" and content is not None and expected_sha256 is None and operations is None:
                value = self.create_state(path, content, purpose)
            elif action == "edit" and content is None and expected_sha256 is not None and operations is not None:
                value = self.edit_state(path, expected_sha256, operations, purpose)
            else:
                raise ValueError("invalid_update: create requires content; edit requires version and operations.")
        return {**value, "reason": reason, "source_refs": source_refs,
                "references_checked": False, "meaning": "text persisted, financial validity not assessed"}
