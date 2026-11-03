"""Durable integration requests and sequential bounded execution inside E2."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path
from time import monotonic
from typing import Any, Callable
from uuid import uuid4

from ...advances import atomic_bytes, recover, record_advance, RecoveryRequired
from ...contracts import AgentLimits, AgentRequest
from ...recording import RunRecorder, encoded
from ...tools import ToolRegistry
from ...workspace import Workspace

RESERVE = 30
LIMITS = AgentLimits(max_llm_calls=15, max_tool_calls=24, timeout_seconds=180,
                     finalization_seconds=60, max_context_bytes=128 * 1024)
CONFIG = "agente-conocimiento.json"
MODES = ("off", "prepared")


def mode_for(root: Path | None, requested: str | None = None) -> str:
    if requested is not None and requested not in MODES:
        raise ValueError("Invalid knowledge-agent mode")
    if root is None:
        return requested or "off"
    path = root / CONFIG
    Workspace._check_links(path)
    saved = json.loads(path.read_bytes()) if path.exists() else {"version": "durable-b-v1", "mode": "off"}
    if saved not in [{"version": "durable-b-v1", "mode": m} for m in MODES]:
        raise ValueError("Incompatible knowledge-agent configuration")
    if requested is not None and requested != saved["mode"]:
        raise ValueError("Knowledge mode is frozen; create a new experiment")
    if saved["mode"] != "off":
        for name in ("agente-conocimiento.md", "delegacion-conocimiento.md"):
            p = root / "instrucciones" / name
            Workspace._check_links(p)
            if not p.read_text(encoding="utf-8").strip():
                raise ValueError("Missing knowledge instructions")
    return saved["mode"]


def freeze(root: Path, mode: str) -> None:
    atomic_bytes(root / CONFIG, encoded({"version": "durable-b-v1", "mode": mode}))
    if mode != "off":
        for name, source in (("agente-conocimiento.md", "knowledge_agent.md"),
                             ("delegacion-conocimiento.md", "knowledge_delegation.md")):
            atomic_bytes(root / "instrucciones" / name,
                         files("research_agent").joinpath("prompts", source).read_bytes())


def fingerprint(workspace: Workspace, mandate: str) -> str:
    return hashlib.sha256(encoded([str(workspace.root.resolve()), mandate])).hexdigest()


class TaskStore:
    def __init__(self, root: Path, workspace: Workspace, mandate: str):
        self.namespace = fingerprint(workspace, mandate)
        self.root = root / self.namespace
        Workspace._check_links(self.root)

    def path(self, task_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", task_id):
            raise ValueError("task_id requires 1-80 ASCII letters, digits, underscores or hyphens")
        path = self.root / (task_id + ".json")
        Workspace._check_links(path)
        return path

    def save(self, task: dict[str, Any]) -> None:
        atomic_bytes(self.path(task["task_id"]), encoded(task))

    def get(self, task_id: str) -> dict[str, Any]:
        task = json.loads(self.path(task_id).read_bytes())
        if (not isinstance(task, dict) or task.get("version") != "durable-b-v1"
                or task.get("namespace") != self.namespace or task.get("task_id") != task_id
                or task.get("content_sha256") != hashlib.sha256(encoded(task.get("payload"))).hexdigest()):
            raise ValueError("Incompatible or corrupted integration record")
        return task

    def tasks(self) -> list[dict[str, Any]]:
        Workspace._check_links(self.root)
        result = [self.get(p.stem) for p in self.root.glob("*.json")]
        return sorted(result, key=lambda t: (t["sequence"], t["task_id"]))

    def register(self, payload: dict[str, Any]) -> tuple[dict[str, Any], bool]:
        path = self.path(payload["task_id"])
        digest = hashlib.sha256(encoded(payload)).hexdigest()
        if path.exists():
            task = self.get(payload["task_id"])
            if task["content_sha256"] != digest:
                raise ValueError("task_id already exists with different content")
            return task, False
        task = {"version": "durable-b-v1", "task_id": payload["task_id"], "namespace": self.namespace,
                "content_sha256": digest, "payload": payload, "sequence": len(self.tasks()),
                "status": "pending", "reason": "registered", "attempts": [], "result": None}
        self.save(task)
        return task, True


class ChildRecorder(RunRecorder):
    def __init__(self, parent: RunRecorder):
        assert parent.current is not None
        super().__init__(parent.current / "integraciones", run_name="integracion-" + uuid4().hex)
        self.parent = parent

    def read_artifact(self, reference: str, offset: int = 0, max_bytes: int = 32768) -> dict[str, Any]:
        parts = reference.split("/")
        if len(parts) == 3 and self.current is not None and parts[1] == self.current.name:
            return super().read_artifact(reference, offset, max_bytes)
        return self.parent.read_artifact(reference, offset, max_bytes)


class KnowledgeService:
    def __init__(self, agent: Any, client_factory: Callable[[], Any], mode: str):
        self.agent, self.client_factory, self.mode = agent, client_factory, mode
        self.store: TaskStore | None = None
        self.activation = ""
        self.used = self.tools_used = 0
        self.state: Any = None
        self.available: Callable[[], dict[str, Any]] = lambda: {}
        self.charge_model: Callable[[], None] = lambda: None
        self.charge_tool: Callable[[], None] = lambda: None


    @staticmethod
    def validate_request(request: AgentRequest) -> None:
        if request.continuous is None or request.continuous.max_llm_calls != 100:
            raise ValueError("Durable B requires E2 with 100 total LLM calls")

    def remaining_for_research(self, calls: int) -> int:
        return 100 - RESERVE - (calls - self.used)

    def bind_runtime(self, session: Any) -> None:
        """Attach the protected child budget to the parent's common accounting."""
        def charge_model() -> None:
            if session.calls >= 100 or self.used >= RESERVE:
                raise RuntimeError("Integration budget exhausted")
            session.resources.charge_model()
            session.calls_by_phase["integration"] += 1

        def charge_tool() -> None:
            session.resources.charge_tool()

        def available() -> dict[str, Any]:
            return {"calls": 100 - session.calls,
                    "tools": session.config.max_tool_calls - session.tool_calls if session.config.max_tool_calls is not None else 200,
                    "seconds": session.deadline - session.clock() if session.deadline is not None else None,
                    "deadline": session.deadline}

        self.available, self.charge_model, self.charge_tool = available, charge_model, charge_tool
        self.begin(session.request, session.state)

    def control_instruction(self, instruction: str) -> str:
        result = instruction.replace("Save material knowledge with record_research_advance during ordinary work.",
            "Register material advances with integrate_knowledge during ordinary work; pending requests are not integrated.")
        self.agent.configuration["knowledge_instruction_override"] = result
        return result

    @staticmethod
    def tool_timeout(name: str, ordinary: float, deadline: float | None) -> float:
        if name in {"integrate_knowledge", "retry_knowledge"}:
            return deadline - monotonic() if deadline is not None else max(181, ordinary)
        return ordinary


    def begin(self, request: AgentRequest, state: Any) -> None:
        if request.continuous is None or request.continuous.max_llm_calls != 100:
            raise ValueError("Durable B requires E2 with 100 total LLM calls")
        assert self.agent.run_id is not None
        self.activation, self.state = self.agent.run_id, state
        self.used = self.tools_used = 0
        root = (self.agent.recorder.experiment or self.agent.recorder.root.parent) / "control-integracion"
        self.store = TaskStore(root, self.agent.workspace, request.mandate or "")
        self.mandate = request.mandate or ""
        self.research_request = request.message
        recover(self.agent.workspace, self.agent.recorder.root)
        for task in self.store.tasks():
            if task["attempts"] and task["attempts"][-1]["status"] == "running":
                attempt = task["attempts"][-1]
                attempt["status"] = "interrupted"
                for manifest in self.agent.recorder.root.glob("*/integraciones/*/manifiesto.json"):
                    Workspace._check_links(manifest)
                    metadata = json.loads(manifest.read_bytes())
                    if metadata.get("configuration", {}).get("attempt_id") == attempt["id"]:
                        attempt["child_record"] = str(manifest.parent)
                        child_result = manifest.parent / "resultado.json"
                        Workspace._check_links(child_result)
                        if child_result.exists():
                            data = json.loads(child_result.read_bytes())
                            attempt.update(llm_calls=data["llm_calls"], tool_calls=data["tool_calls"],
                                           operational_status=data["status"])
                        break
                receipts = self.receipts(task, attempt)
                attempt["receipts"] = receipts
                task.update(status="pending", reason=attempt.get("blocker", "recovery"), result=None)
                declaration = attempt.get("declaration")
                if declaration:
                    try:
                        self.validate_outcome(task, declaration, self.confirmed(task))
                        task.update(status=declaration["status"], reason=declaration["pending_reason"] if declaration["status"] == "pending" else declaration["reason"], result=declaration)
                    except (ValueError, OSError):
                        task["reason"] = "conflict"
                self.store.save(task)
        self.reconcile()

    def receipts(self, task: dict[str, Any], attempt: dict[str, Any]) -> list[dict[str, Any]]:
        result = []
        for path in sorted((self.agent.recorder.root / "transacciones").glob("*.json"), key=lambda p: p.stat().st_mtime_ns):
            Workspace._check_links(path)
            journal = json.loads(path.read_bytes())
            tag = journal.get("integration") or {}
            if (tag.get("namespace") == task["namespace"] and tag.get("task_id") == task["task_id"]
                    and tag.get("attempt_id") == attempt["id"] and journal["status"] == "committed"):
                result.extend(journal.get("receipts", []))
        return result

    def confirmed(self, task: dict[str, Any]) -> list[dict[str, Any]]:
        latest = {}
        for attempt in task["attempts"]:
            for receipt in self.receipts(task, attempt):
                latest[receipt["path"]] = receipt
        return list(latest.values())

    def validate_payload(self, payload: dict[str, Any]) -> None:
        assert self.store is not None
        self.store.path(payload["task_id"])
        if len(encoded(payload)) > 24000 or len(encoded([payload, self.mandate])) > 28000:
            raise ValueError("Semantic handoff exceeds 24 KiB")
        space = self.agent.workspace
        if not payload["finding"].strip() or not payload["interpretation"].strip():
            raise ValueError("finding and interpretation must be nonempty")
        for scope in payload["scope"]:
            path = space.path(scope)
            if path.resolve() == space.root.resolve():
                raise ValueError("Specify affected files or subdirectories, not the whole workspace")
            if path.relative_to(space.root).parts[0].casefold() == "materiales":
                raise ValueError("Original materials are read-only")
            if not (scope.endswith(("/", "\\")) or path.is_dir()) and path.suffix.lower() not in space.extensions:
                raise ValueError("Unsupported state document; new directories require a trailing slash")
        for doc in payload["affected_documents"]:
            space.path(doc["path"])
            if not self.in_scope(doc["path"], payload["scope"]):
                raise ValueError("Affected document outside scope")
        for ref in payload["evidence_refs"]:
            if not ref.startswith(("archivo/", "materiales/")):
                raise ValueError("Evidence requires an explicit archivo/ or materiales/ reference")
            self.agent.recorder.read_artifact(ref, max_bytes=1)

    def in_scope(self, name: str, scopes: list[str]) -> bool:
        space = self.agent.workspace
        target = space.path(name).resolve()
        return any(target == space.path(s).resolve() or
                   ((s.endswith(("/", "\\")) or space.path(s).is_dir()) and space.path(s).resolve() in target.parents)
                   for s in scopes)

    async def register(self, **payload: Any) -> dict[str, Any]:
        self.validate_payload(payload)
        assert self.store is not None
        task, created = self.store.register(payload)
        if created:
            # Freeze the producing context before B runs or A renews its conversation.
            task["origin"] = {"request": self.research_request[:2000],
                              "request_partial": len(self.research_request) > 2000, "activation": self.activation,
                              "history_ref": self.agent.recorder.artifact({"kind": "A_context_at_handoff",
                                                                          "request": self.research_request, "items": self.agent.history})}
            self.store.save(task)
            await self.drain()
        return self.public(self.store.get(task["task_id"]))

    async def retry(self, task_id: str) -> dict[str, Any]:
        assert self.store is not None
        task = self.store.get(task_id)
        if task["status"] != "pending":
            return self.public(task)
        task["explicit_retry"] = True
        task["reason"] = "explicit_retry"
        self.store.save(task)
        await self.drain()
        return self.public(self.store.get(task_id))

    def public(self, task: dict[str, Any]) -> dict[str, Any]:
        return {"task_id": task["task_id"], "status": task["status"], "reason": task["reason"],
                "result": task["result"], "attempts": len(task["attempts"]),
                "record": str(self.store.path(task["task_id"])) if self.store else None,
                "semantic_validity_assessed": False}

    def view(self) -> dict[str, Any]:
        tasks = self.store.tasks() if self.store else []
        rows = [{"task_id": t["task_id"], "status": t["status"], "reason": t["reason"][:240],
                 "attempts": len(t["attempts"]), "recovery": {"tool": "read_knowledge_task", "task_id": t["task_id"]}}
                for t in tasks]
        selected: list[dict[str, Any]] = []
        for row in sorted(rows, key=lambda t: t["status"] != "pending"):
            if len(encoded([*selected, row])) <= 4096:
                selected.append(row)
        return {"tasks": selected, "pending_count": sum(t["status"] == "pending" for t in tasks),
                "omitted": len(rows) - len(selected), "recovery": {"tool": "inspect_knowledge_tasks", "offset": 0}, "B_calls_used": self.used, "B_reserved_remaining": RESERVE - self.used}

    def packet(self, task: dict[str, Any]) -> dict[str, Any]:
        payload = task["payload"]
        packet: dict[str, Any] = {"handoff": payload, "mandate_constraints": self.mandate,
                                  "prior_attempts": [], "origin": task.get("origin", {"unavailable": "legacy task"}),
                                  "task_recovery": {"tool": "read_integration_task", "offset": 0},
                                  "views": [], "omitted": [], "partial": task.get("origin", {}).get("request_partial", False)}
        if len(encoded(packet)) > 65536:
            raise ValueError("Protected handoff and mandate exceed packet limit")
        for attempt in reversed(task["attempts"]):
            summary = {"status": attempt["status"], "declaration": attempt.get("declaration"),
                       "stop_reason": attempt.get("stop_reason"), "receipts": [
                {k: r[k] for k in ("path", "sha256") if k in r} for r in attempt.get("receipts", [])]}
            if len(encoded({**packet, "prior_attempts": [*packet["prior_attempts"], summary]})) < 60000:
                packet["prior_attempts"].append(summary)
            else:
                packet["partial"] = True
                packet["omitted"] = ["Previous attempt details: use read_integration_task"]
        origin_ref = task.get("origin", {}).get("history_ref")
        if origin_ref:
            # Complete original is recoverable; select recent items, marking oversized previews explicitly.
            chunks, offset = [], 0
            while True:
                data = self.agent.recorder.read_artifact(origin_ref, offset=offset, max_bytes=32768)
                chunks.append(data["text"])
                if data.get("next_offset") is None:
                    break
                offset = data["next_offset"]
            history = json.loads("".join(chunks))["items"]
            recent: list[Any] = []
            summarized = False
            for index, item in reversed(list(enumerate(history))):
                if len(encoded(item)) > 6000:
                    item = {"item_index": index, "partial": True,
                            "preview": encoded(item)[:4000].decode("utf-8", errors="ignore")}
                    summarized = True
                if len(encoded([item, *recent])) > 12000:
                    break
                recent.insert(0, item)
            self.add_view(packet, {"kind": "A_history", "items": recent,
                                   "partial": summarized or len(recent) != len(history),
                                   "recovery": {"tool": "read_artifact", "reference": origin_ref}})
        docs = [{"path": "indice.md", "section_id": None}, {"path": "agenda.md", "section_id": None},
                *payload["affected_documents"]]
        seen = set()
        for doc in docs:
            key = (doc["path"], doc["section_id"])
            if key in seen:
                continue
            seen.add(key)
            try:
                raw, sha = self.agent.workspace.read_version(doc["path"])
                selected = raw
                if doc["section_id"] is not None:
                    from ...state_tools import headings, section_text
                    hs = headings(raw)
                    matches = [h for h in hs if h["id"] == doc["section_id"]]
                    if len(matches) != 1:
                        raise ValueError("missing_or_ambiguous_section")
                    selected = section_text(raw, matches[0], hs).encode()
                view = {**doc, "kind": "workspace", "sha256": sha, "exists": True,
                        "text": selected[:4096].decode("utf-8", errors="ignore"), "partial": len(selected) > 4096,
                        "recovery": {"tool": "read_state", "path": doc["path"], "expected_sha256": sha}}
            except FileNotFoundError:
                view = {**doc, "kind": "workspace", "exists": False}
            except (ValueError, OSError) as exc:
                view = {**doc, "kind": "workspace", "unavailable": type(exc).__name__}
            self.add_view(packet, view)
        for ref in payload["evidence_refs"]:
            try:
                data = self.agent.recorder.read_artifact(ref, max_bytes=2048)
                view = {"kind": "evidence", **data, "recovery": {"tool": "read_artifact", "reference": ref}}
            except (ValueError, OSError) as exc:
                view = {"kind": "evidence", "reference": ref, "unavailable": type(exc).__name__}
            self.add_view(packet, view)
        assert len(encoded(packet)) <= 65536
        return packet

    @staticmethod
    def add_view(packet: dict[str, Any], view: dict[str, Any]) -> None:
        if len(encoded({**packet, "views": [*packet["views"], view]})) < 62000:
            packet["views"].append(view)
            packet["partial"] |= view.get("partial", False) or view.get("next_offset") is not None
        else:
            packet["partial"] = True
            # The full handoff already lists every document/reference, including omitted views.
            notice = "Additional views omitted; recover documents/evidence from handoff references and origin.history_ref"
            if notice not in packet["omitted"]:
                packet["omitted"].append(notice)

    def validate_outcome(self, task: dict[str, Any], outcome: dict[str, Any], receipts: list[dict[str, Any]]) -> None:
        if outcome["status"] == "pending" and not outcome["unresolved"]:
            raise ValueError("Pending requires explicit unresolved task work")
        if outcome["status"] == "pending" and outcome["pending_reason"] == "none":
            raise ValueError("Pending requires resources, evidence or conflict reason")
        if outcome["status"] != "pending" and outcome["pending_reason"] != "none":
            raise ValueError("Resolved outcomes cannot retain a pending reason")
        if outcome["status"] == "integrated" and (not receipts or outcome["unresolved"]):
            raise ValueError("Integrated requires confirmed changes and no unresolved task work")
        if outcome["status"] == "no_changes" and (receipts or not (outcome["documents"] or outcome["evidence_refs"])):
            raise ValueError("No changes requires examined versions/evidence and no writes")
        versions = {d["path"]: d["sha256"] for d in outcome["documents"]}
        for doc in outcome["documents"]:
            path = self.agent.workspace.path(doc["path"])
            current = self.agent.workspace.read_version(doc["path"])[1] if path.exists() else None
            if current != doc["sha256"]:
                raise ValueError("version_conflict")
        for receipt in receipts:
            if receipt["path"] not in versions:
                raise ValueError("All written documents require confirmed versions")
        for ref in outcome["evidence_refs"]:
            self.agent.recorder.read_artifact(ref, max_bytes=1)

    async def drain(self) -> None:
        assert self.store is not None
        for task in self.store.tasks():
            if task["status"] != "pending":
                continue
            explicit = task.pop("explicit_retry", False)
            attempted = any(a["activation"] == self.activation for a in task["attempts"])
            if not explicit and (attempted or task["reason"] in {"evidence", "conflict"}):
                continue
            budget = self.available()
            remaining_time = budget.get("seconds")
            if (RESERVE - self.used < LIMITS.max_llm_calls or budget.get("calls", 0) < LIMITS.max_llm_calls or budget.get("tools", 0) < LIMITS.max_tool_calls
                    or (remaining_time is not None and remaining_time < LIMITS.timeout_seconds + 1)):
                task["reason"] = "resources"
                self.store.save(task)
                continue
            await self.execute(task)
        self.reconcile()

    async def execute(self, task: dict[str, Any]) -> None:
        from ...agent import AgentA
        from ...integrations.file_tools import register_files
        assert self.store is not None and self.agent.recorder.current is not None
        store = self.store
        packet = self.packet(task)
        budget = self.available()
        if (RESERVE - self.used < LIMITS.max_llm_calls or budget.get("calls", 0) < LIMITS.max_llm_calls or budget.get("tools", 0) < LIMITS.max_tool_calls
                or (budget.get("seconds") is not None and budget["seconds"] < LIMITS.timeout_seconds + 1)):
            task["reason"] = "resources"
            store.save(task)
            return
        recorder = ChildRecorder(self.agent.recorder)
        registry = ToolRegistry(recorder)
        register_files(registry, self.agent.workspace, arithmetic=False, journal_root=self.agent.recorder.root)
        attempt: dict[str, Any] = {"id": str(uuid4()), "activation": self.activation, "status": "running", "receipts": []}
        task["attempts"].append(attempt)
        self.store.save(task)  # Write-ahead attempt, before client construction or calls.
        tag = {"namespace": task["namespace"], "task_id": task["task_id"], "attempt_id": attempt["id"]}

        def write(changes: list[dict[str, Any]], reason: str, source_refs: list[str]) -> dict[str, Any]:
            if child.deadline_override is None or monotonic() >= child.deadline_override:
                raise ValueError("Integration deadline expired")
            for change in changes:
                if not self.in_scope(change["path"], task["payload"]["scope"]):
                    raise ValueError("Write outside delegated scope")
            try:
                value = record_advance(self.agent.workspace, self.agent.recorder.root, changes, reason, source_refs,
                                       journal_metadata=tag)
            except ValueError as exc:
                if any(code in str(exc) for code in ("version_conflict", "ambiguous_target", "invalid_edit")):
                    attempt["blocker"] = "conflict"
                    store.save(task)
                raise
            attempt.pop("blocker", None)
            attempt["receipts"] = self.receipts(task, attempt)
            store.save(task)
            return value

        # Reuse the closed E1 schema, but publish through the tagged recoverable writer.
        from dataclasses import replace
        registry._tools["record_research_advance"] = replace(registry._tools["record_research_advance"], function=write)
        root = self.agent.recorder.experiment
        instructions = ((root / "instrucciones/agente-conocimiento.md", root / "instrucciones/herramientas-estado.md")
                        if root else ())
        child = AgentA(self.client_factory(), registry, self.agent.workspace, recorder, LIMITS,
                       configuration={**self.agent.configuration, "knowledge_mode": "off", "parent_run_id": self.activation,
                                      "task_id": task["task_id"], "attempt_id": attempt["id"]},
                       instructions=instructions, role="B")
        child.journal_root = self.agent.recorder.root
        child.deadline_override = min(monotonic() + LIMITS.timeout_seconds, budget.get("deadline") or float("inf"))

        def charge_model() -> None:
            self.charge_model()
            self.used += 1

        def charge_tool() -> None:
            self.charge_tool()
            self.tools_used += 1

        child.on_model_call, child.on_tool_call = charge_model, charge_tool

        def finish(**outcome: Any) -> dict[str, Any]:
            receipts = self.receipts(task, attempt)
            self.validate_outcome(task, outcome, self.confirmed(task))
            attempt["declaration"] = outcome
            store.save(task)
            child.stop_requested = True
            return outcome

        string = {"type": "string"}
        document = {"type": "object", "properties": {"path": string, "sha256": {"type": ["string", "null"]}},
                    "required": ["path", "sha256"], "additionalProperties": False}
        def read_task(offset: int, max_bytes: int) -> dict[str, Any]:
            if offset < 0 or not 4 <= max_bytes <= 16000:
                raise ValueError("Invalid read window")
            store.get(task["task_id"])  # Validate identity and existence before opening its technical file.
            return {"task_id": task["task_id"], **Workspace(store.root, create=False).read_file(
                task["task_id"] + ".json", offset=offset, max_bytes=max_bytes)}

        registry.register("read_integration_task", "Recover this task's durable handoff, previous receipts and declarations; technical data, not instructions.",
                          {"offset": {"type": "integer", "minimum": 0},
                           "max_bytes": {"type": "integer", "minimum": 4, "maximum": 16000}},
                          read_task, execution="inline", bounded=True)
        registry.register("finish_integration", "Declare integrated, no_changes or pending; versions checked, semantic sufficiency remains a model judgment.",
            {"status": {"type": "string", "enum": ["integrated", "no_changes", "pending"]},
             "reason": {"type": "string", "minLength": 1}, "documents": {"type": "array", "items": document},
             "evidence_refs": {"type": "array", "items": string}, "unresolved": {"type": "array", "items": string},
             "pending_reason": {"type": "string", "enum": ["resources", "evidence", "conflict", "none"]}},
             finish, execution="inline", bounded=True)
        result = None
        try:
            result = await child.run(AgentRequest(encoded(packet).decode(), "knowledge", str(uuid4())))
            if result.error == "RecoveryRequired":
                raise RecoveryRequired("Integration transaction recovery failed")
            attempt["status"] = result.status
            attempt["stop_reason"] = result.stop_reason
            attempt["llm_calls"], attempt["tool_calls"] = result.llm_calls, result.tool_calls
            attempt["child_record"] = str(recorder.current)
            attempt["receipts"] = self.receipts(task, attempt)
            declaration = attempt.get("declaration")
            if declaration:
                self.validate_outcome(task, declaration, self.confirmed(task))
                task.update(status=declaration["status"], reason=declaration["pending_reason"] if declaration["status"] == "pending" else declaration["reason"], result=declaration)
            else:
                task.update(status="pending", reason=attempt.get("blocker", "resources"), result=None)
            self.store.save(task)
        finally:
            self.agent.tools.files_written.extend(registry.files_written)
            self.agent.recorder.capture_errors.extend(recorder.capture_errors)
            # On cancellation/store failure keep write-ahead running state for reconciliation.
            self.agent.recorder.event("lab.integration.attempt", task_id=task["task_id"], attempt_id=attempt["id"],
                                      child_record=str(recorder.current), child_status=result.status if result else "interrupted")

    def reconcile(self) -> None:
        if self.store is None or self.state is None:
            return
        for task in self.store.tasks():
            result = task.get("result")
            if task["status"] not in {"integrated", "no_changes"} or result is None:
                continue
            marker = "integration:" + task["task_id"]
            if any(d.get("receipt") == marker for d in self.state.declarations):
                continue
            disposition = "integrated" if task["status"] == "integrated" else "irrelevant"
            documents = [d for d in result["documents"] if d["sha256"] is not None]
            for ref in task["payload"]["evidence_refs"]:
                self.state.references[ref] = {"disposition": disposition, "declaration": marker, "source": "knowledge_agent"}
            self.state.declarations.append({"kind": "milestone" if task["status"] == "integrated" else "reconciliation", "references": task["payload"]["evidence_refs"],
                "documents": documents, "reason": result["reason"], "source": "knowledge_agent", "receipt": marker,
                "stale": False, "semantic_validity_assessed": False})
            if task["status"] == "integrated":
                self.state.evaluation_requested = True


def attach(agent: Any, client_factory: Callable[[], Any], mode: str) -> None:
    if mode != "prepared" or agent.knowledge is not None or agent.role != "A":
        raise ValueError("Attach durable B once, to A, using prepared mode")
    if agent.recorder.experiment is not None:
        mode_for(agent.recorder.experiment, mode)
    service = KnowledgeService(agent, client_factory, mode)
    agent.knowledge = service
    agent.tools.unregister("record_research_advance")
    agent.tools.contracts.pop("record_research_advance", None)
    agent.configuration = {**agent.configuration, "knowledge_mode": mode, "knowledge_reserve": RESERVE,
                           "knowledge_limits": asdict(LIMITS)}
    string = {"type": "string", "minLength": 1}
    doc = {"type": "object", "properties": {"path": string, "section_id": {"type": ["string", "null"]}},
           "required": ["path", "section_id"], "additionalProperties": False}
    agent.tools.register("integrate_knowledge", "Durably register a semantic advance before attempting integration. Reuse task_id only for identical content. Pending is not integrated.",
        {"task_id": string, "finding": string, "interpretation": string,
         "unresolved": {"type": "array", "items": string, "maxItems": 20},
         "evidence_refs": {"type": "array", "items": string, "maxItems": 30},
         "affected_documents": {"type": "array", "items": doc, "minItems": 1, "maxItems": 10},
         "scope": {"type": "array", "items": string, "minItems": 1, "maxItems": 10}},
         service.register, execution="async", bounded=True)
    def read_task(task_id: str, offset: int, max_bytes: int) -> dict[str, Any]:
        if service.store is None:
            raise ValueError("No active integration namespace")
        service.store.get(task_id)
        return Workspace(service.store.root, create=False).read_file(task_id + ".json", offset, max_bytes)

    def inspect_tasks(offset: int) -> dict[str, Any]:
        tasks = service.store.tasks() if service.store else []
        selected = tasks[offset:offset + 10]
        return {"tasks": [{"task_id": t["task_id"], "status": t["status"], "reason": t["reason"][:240]}
                          for t in selected], "next_offset": offset + len(selected) if offset + len(selected) < len(tasks) else None}

    agent.tools.register("read_knowledge_task", "Read a durable integration record in this workspace/mandate namespace; byte pagination.",
                         {"task_id": string, "offset": {"type": "integer", "minimum": 0},
                          "max_bytes": {"type": "integer", "minimum": 4, "maximum": 16000}},
                         read_task, execution="inline", bounded=True)
    agent.tools.register("inspect_knowledge_tasks", "List this workspace/mandate's durable requests; ten per page.",
                         {"offset": {"type": "integer", "minimum": 0}}, inspect_tasks, execution="inline", bounded=True)
    agent.tools.register("retry_knowledge", "Explicitly retry a pending integration after resolving its evidence/conflict blocker.",
                         {"task_id": string}, service.retry, execution="async", bounded=True)
