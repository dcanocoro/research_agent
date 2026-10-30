"""Recoverable batches of state edits. Journals never belong to editable memory."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

from .recording import encoded
from .workspace import Workspace


class RecoveryRequired(RuntimeError):
    """Stop the run: a transaction cannot safely be restored."""


def atomic_bytes(path: Path, raw: bytes) -> None:
    Workspace._check_links(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def restore(workspace: Workspace, journal: Path, data: dict[str, Any]) -> None:
    # Preflight the entire set before touching anything, including after a crash.
    for item in data['changes']:
        path = workspace.path(item['path'])
        current = path.read_bytes() if path.exists() else None
        if current not in (None if item['before'] is None else item['before'].encode('utf-8'),
                           item['after'].encode('utf-8')):
            raise RecoveryRequired('External edit conflicts with transaction recovery: ' + item['path'])
    for item in reversed(data['changes']):
        path = workspace.path(item['path'])
        if item['before'] is None:
            path.unlink(missing_ok=True)
        else:
            atomic_bytes(path, item['before'].encode('utf-8'))
    data['status'] = 'restored'
    atomic_bytes(journal, encoded(data))


def recover(workspace: Workspace, runs: Path) -> None:
    root = runs / 'transacciones'
    Workspace._check_links(root)
    if not root.exists():
        return
    with workspace.mutation_lock:
        for journal in sorted(root.glob('*.json')):
            Workspace._check_links(journal)
            data = json.loads(journal.read_bytes())
            if data.get('workspace') != str(workspace.root.resolve()):
                continue
            if data['status'] == 'pending':
                try:
                    restore(workspace, journal, data)
                except Exception as exc:
                    raise RecoveryRequired('Unfinished transaction requires recovery: ' + str(journal)) from exc


def record_advance(workspace: Workspace, runs: Path, changes: list[dict[str, Any]],
                   reason: str, source_refs: list[str]) -> dict[str, Any]:
    if not reason.strip() or not 1 <= len(changes) <= 5:
        raise ValueError('Supply a reason and one to five changes.')
    with workspace.mutation_lock:
        recover(workspace, runs)
        prepared = []
        names: set[str] = set()
        for change in changes:
            path = change['path']
            key = str(workspace.path(path).resolve()).casefold()
            if key in names:
                raise ValueError('duplicate_path')
            names.add(key)
            before: str | None = None
            if change['action'] == 'create':
                if change['expected_sha256'] is not None or change['operations'] is not None or change['content'] is None:
                    raise ValueError('invalid_create')
                after = change['content']
            elif change['action'] == 'edit':
                if change['content'] is not None or not change['operations']:
                    raise ValueError('invalid_edit')
                raw, version = workspace.read_version(path)
                if version != change['expected_sha256']:
                    raise ValueError('version_conflict: ' + path)
                before = after = raw.decode('utf-8')
                for operation in change['operations']:
                    target, content, kind = operation['target'], operation['content'], operation['kind']
                    if not target or len(list(re.finditer('(?=' + re.escape(target) + ')', after))) != 1:
                        raise ValueError('ambiguous_target')
                    if kind not in {'replace', 'insert_before', 'insert_after'}:
                        raise ValueError('invalid_edit')
                    replacement = content if kind == 'replace' else content + target if kind == 'insert_before' else target + content
                    after = after.replace(target, replacement, 1)
            else:
                raise ValueError('invalid_action')
            workspace.validate_publish(path, after.encode('utf-8'), create=change['action'] == 'create')
            prepared.append({'path': path, 'before': before, 'after': after})
        journal = runs / 'transacciones' / (str(uuid4()) + '.json')
        data = {'workspace': str(workspace.root.resolve()), 'status': 'pending', 'changes': prepared}
        atomic_bytes(journal, encoded(data))
        receipts = []
        try:
            for item in prepared:
                previous = None if item['before'] is None else hashlib.sha256(item['before'].encode('utf-8')).hexdigest()
                value = workspace.publish(item['path'], item['after'].encode('utf-8'),
                                          create=item['before'] is None, expected_sha256=previous)
                receipts.append({**value, 'previous_sha256': previous, 'applied': True,
                                 'excerpt': item['after'].encode('utf-8')[:1200].decode('utf-8', errors='ignore'),
                                 'partial': len(item['after'].encode('utf-8')) > 1200})
            data['status'] = 'committed'
            atomic_bytes(journal, encoded(data))
        except Exception:
            try:
                restore(workspace, journal, data)
            except Exception as exc:
                raise RecoveryRequired('Transaction rollback failed: ' + str(journal)) from exc
            raise
        return {'applied': True, 'operation': 'record_research_advance', 'files': receipts,
                'reason': reason, 'source_refs': source_refs, 'semantic_validity_assessed': False}


def register_advance(registry: Any, workspace: Workspace) -> None:
    string = {"type": "string"}
    nullable = {"type": ["string", "null"]}
    operation = {"type": "object", "properties": {
        "kind": {"type": "string", "enum": ["replace", "insert_before", "insert_after"]},
        "target": {"type": "string", "minLength": 1}, "content": string},
        "required": ["kind", "target", "content"], "additionalProperties": False}
    change = {"type": "object", "properties": {"path": string,
        "action": {"type": "string", "enum": ["create", "edit"]},
        "content": nullable, "expected_sha256": nullable,
        "operations": {"type": ["array", "null"], "minItems": 1, "items": operation}},
        "required": ["path", "action", "content", "expected_sha256", "operations"],
        "additionalProperties": False}
    def apply(changes: list[dict[str, Any]], reason: str, source_refs: list[str]) -> dict[str, Any]:
        return record_advance(workspace, registry.recorder.root, changes, reason, source_refs)
    registry.register("record_research_advance", "Save one coherent advance across 1-5 files; versions and V6 integrity checked; recoverable batch, no semantic certification.",
        {"changes": {"type": "array", "minItems": 1, "maxItems": 5, "items": change},
         "reason": {"type": "string", "minLength": 1}, "source_refs": {"type": "array", "items": string}},
        apply, execution="inline", consolidation=True, mutation=True, bounded=True)
    registry.contracts["record_research_advance"] = {"version": "state-tools-v7.1",
        "text": "Create: content supplied, operations and expected_sha256 null. Edit: content null, exact operations and current expected_sha256 supplied. All changes validate before publishing; recovery journal outside state. Readers/editors external to this process are not isolated. No deletions. Evidence references are not semantically validated."}
