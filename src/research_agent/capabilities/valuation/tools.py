from __future__ import annotations

import asyncio
import json
import re
from time import monotonic
from typing import Any

from dcf_lab import ContextDocument, Evaluation, ValuationRequest, evaluate_company, load_evaluation
from dcf_lab.adapters.llm import AsyncLanguageModel, LLMReply
from dcf_lab.reporting import fingerprint, render
from dcf_lab.schemas import Model
from dcf_lab.service import seal
from research_agent.core.tool_runtime import current_tool_runtime
from research_agent.core.tools import ToolRegistry
from research_agent.observability.recording import encoded
from research_agent.storage.workspace import Workspace


class ValuationTools:
    def __init__(self, registry: ToolRegistry, workspace: Workspace, source: Any, llm: AsyncLanguageModel,
                 timeout_seconds: float = 120):
        self.registry, self.workspace, self.source, self.llm = registry, workspace, source, llm
        self.timeout_seconds = timeout_seconds

    def previous(self, reference: str | None) -> Evaluation | None:
        if reference is None:
            return None
        path = self.workspace.path(reference)
        if path.suffix != ".json" or not reference.startswith("materiales/dcf-"):
            raise ValueError("Previous evaluation must reference a DCF material")
        evaluation = load_evaluation(path)
        # Editable materials are accepted only when an identical audit copy exists
        # for this workspace in a recorded run.
        for manifest in self.registry.recorder.root.glob("*/manifiesto.json"):
            Workspace._check_links(manifest)
            metadata = json.loads(manifest.read_bytes())
            if metadata.get("workspace_fingerprint") != self.registry.recorder.workspace_fingerprint:
                continue
            audit = manifest.parent / "valoraciones" / f"{evaluation.run_id}.json"
            Workspace._check_links(audit)
            if audit.exists() and load_evaluation(audit).bundle_sha256 == evaluation.bundle_sha256:
                return evaluation
        raise ValueError("Previous evaluation has no matching workspace audit copy")

    def persist(self, evaluation: Evaluation) -> None:
        evaluation = seal(evaluation)
        recorder = self.registry.recorder
        # Write the audit copy first. Local publication is synchronous, so cancelled
        # async work cannot leave a thread writing after the run has closed.
        recorder.save(f"valoraciones/{evaluation.run_id}.json", evaluation)
        relative = f"materiales/dcf-{evaluation.run_id}.json"
        path = self.workspace.path(relative)
        from research_agent.storage.transactions import atomic_bytes
        atomic_bytes(path, encoded(evaluation))
        atomic_bytes(self.workspace.path(f"materiales/dcf-{evaluation.run_id}.md"), render(evaluation).encode("utf-8"))
        if relative not in self.registry.materials:
            self.registry.materials.append(relative)

    async def evaluate_company(self, company_id: str, knowledge_paths: list[str], previous_evaluation_ref: str | None) -> dict[str, Any]:
        runtime = current_tool_runtime.get()
        if runtime is None:
            raise RuntimeError("Valuation requires managed run resources")
        company_id = company_id.strip().upper()
        if not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,31}", company_id):
            raise ValueError("Invalid company symbol")
        if len(knowledge_paths) > 32 or len(set(knowledge_paths)) != len(knowledge_paths):
            raise ValueError("Select at most thirty-two distinct knowledge files")
        context = []
        total = 0
        for relative in knowledge_paths:
            path = self.workspace.path(relative)
            if path.suffix.lower() not in {".md", ".txt", ".json"} or not path.is_file():
                raise ValueError("Knowledge must reference existing text documents")
            if total + path.stat().st_size > 262144:
                raise ValueError("Knowledge exceeds byte budget")
            raw, digest = self.workspace.read_version(relative)
            total += len(raw)
            if total > 262144:
                raise ValueError("Knowledge exceeds byte budget")
            context.append(ContextDocument(source_ref=f"document:{digest}", name=relative, sha256=digest,
                                           version=digest, content=raw.decode("utf-8")))
        previous = self.previous(previous_evaluation_ref)
        # Only read-only data loading runs in a thread; it has finite DB timeouts
        # and cannot call an LLM or publish artifacts after cancellation.
        snapshot = await asyncio.to_thread(self.source.load, company_id.strip().upper())
        request = ValuationRequest(company_id=company_id, snapshot=snapshot, context=context,
                                   previous_evaluation=previous)
        owner = self
        evaluation_id: str | None = None

        class ManagedModel:
            @property
            def identity(self) -> dict[str, str]:
                return owner.llm.identity

            async def acomplete(self, phase: str, instructions: str, payload: dict[str, Any], schema: type[Model]) -> LLMReply:
                assert runtime is not None
                runtime.require(2 if phase == "assumptions" else 1)
                purpose = "valuation_assumptions" if phase == "assumptions" else "valuation_diagnosis"
                runtime.charge(purpose)
                started = monotonic()
                metadata = {"evaluation_id": evaluation_id, "call_id": runtime.call_id, "purpose": purpose,
                            "model": owner.llm.identity, "input_sha256": fingerprint(payload)}
                recorder = owner.registry.recorder
                stem = f"valoraciones/{evaluation_id}-{phase}"
                recorder.save(stem + "-input.json", {"instructions": instructions, "payload": payload,
                                                       "schema": schema.model_json_schema()})
                recorder.event("lab.valuation.model.started", **metadata)
                try:
                    async with asyncio.timeout(min(owner.timeout_seconds, runtime.deadline - monotonic())):
                        reply = await owner.llm.acomplete(phase, instructions, payload, schema)
                    recorder.save(stem + "-output.json", {"output": reply.output, "metadata": reply.metadata})
                    recorder.event("lab.valuation.model.completed", **metadata, duration_seconds=monotonic()-started,
                                   usage=reply.metadata.get("usage"), cost=reply.metadata.get("cost"))
                    return reply
                except BaseException as exc:
                    recorder.event("lab.valuation.model.failed", **metadata, duration_seconds=monotonic()-started,
                                   error_type=type(exc).__name__)
                    raise

        async def checkpoint(evaluation: Evaluation) -> None:
            nonlocal evaluation_id
            evaluation_id = evaluation.run_id
            self.persist(evaluation)

        try:
            evaluation = await evaluate_company(request=request, llm=ManagedModel(), on_phase=checkpoint)
        except asyncio.CancelledError as exc:
            try:
                interrupted = getattr(exc, "evaluation", None)
                if isinstance(interrupted, Evaluation):
                    self.persist(interrupted)
            except OSError as capture:
                self.registry.recorder.capture_errors.append({"operation": "valuation_capture", "error_type": type(capture).__name__})
            raise
        self.persist(evaluation)
        self.registry.recorder.event("lab.valuation.completed", evaluation_id=evaluation.run_id,
                                     call_id=runtime.call_id, status=evaluation.status,
                                     bundle_sha256=evaluation.bundle_sha256)
        return summarize(evaluation)

    def register(self) -> None:
        self.registry.register("evaluate_company",
            "Experimental DCF using stored financial data and explicitly selected knowledge files. "
            "Use [] without knowledge and null without a previous evaluation. Includes two managed specialist LLM calls; "
            "returns financial limitations and research implications, not mandatory tasks. Full bundle is readable with read_file.",
            {"company_id": {"type": "string", "minLength": 1, "maxLength": 32},
             "knowledge_paths": {"type": "array", "items": {"type": "string"}, "maxItems": 32},
             "previous_evaluation_ref": {"type": ["string", "null"]}},
            self.evaluate_company, execution="async", bounded=True, material=True)


def summarize(e: Evaluation) -> dict[str, Any]:
    assert e.snapshot is not None
    result: dict[str, Any] = {"evaluation_id": e.run_id, "status": e.status,
        "bundle_ref": f"materiales/dcf-{e.run_id}.json", "report_ref": f"materiales/dcf-{e.run_id}.md",
        "snapshot_captured_at": e.snapshot.captured_at.isoformat(),
        "price": {"value": e.snapshot.price.value, "currency": e.snapshot.price.currency,
                  "as_of": e.snapshot.price.as_of.isoformat() if e.snapshot.price.as_of else None},
        "warnings": list(e.inspection.warnings) if e.inspection else [], "issues": list(e.issues),
        "assumptions": ({"initial_revenue_growth": e.assumptions.initial_revenue_growth,
                         "target_fcff_margin": e.assumptions.target_fcff_margin} if e.assumptions else None),
        "scenarios": ({name: {key: values[key] for key in ("value_per_share", "terminal_weight") if key in values}
                      for name, values in e.calculations["scenarios"].items()} if e.calculations else None),
        "diagnosis": e.synthesis.model_dump(mode="json") if e.synthesis else None}
    if len(encoded(result)) > 8192:
        # Keep whole items only; full originals are always recoverable.
        result["omitted"] = {"diagnosis": result["diagnosis"] is not None}
        result["diagnosis"] = None
        result["limitations_ref"] = result["bundle_ref"]
    for name in ("warnings", "issues"):
        omitted = 0
        while len(encoded(result)) > 8192 and result[name]:
            result[name].pop()
            omitted += 1
        if omitted:
            result.setdefault("omitted", {})[name] = omitted
            result["limitations_ref"] = result["bundle_ref"]
    if len(encoded(result)) > 8192:
        return {"evaluation_id": e.run_id, "status": e.status, "bundle_ref": result["bundle_ref"],
                "report_ref": result["report_ref"], "limited": True,
                "message": "Read the bundle for financial results and limitations."}
    return result
