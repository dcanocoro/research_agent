from typing import Any
from pathlib import Path
from dataclasses import asdict
from importlib.resources import files
import hashlib
import json
from research_agent.contracts import AgentRequest
from research_agent.storage.workspace import Workspace
from research_agent.experiments.store import disjoint
from research_agent.composition.metadata import effective_extensions
from research_agent.composition.metadata import objective_policy
from research_agent.composition.metadata import closing_metadata

def prepare_run(
    self: Any,
    request: AgentRequest,
    run_id: str,
    interaction_id: str,
    persistent: dict[str, Any] | None = None,
) -> str:
    from research_agent.storage.transactions import recover

    recover(self.workspace, self.journal_root)
    instructions = (*self.instructions, *request.instructions)
    protected = [Path(str(files("research_agent"))), *instructions]
    disjoint(self.workspace.root, self.recorder.root)
    for path in protected:
        disjoint(self.workspace.root, path)
        disjoint(self.recorder.root, path)
    self.tools.reset()
    self.run_id = run_id
    base = (
        files("research_agent")
        .joinpath("extensions/knowledge_agent/prompts/agent.md" if self.role == "B" else "instructions/agent.md")
        .read_text(encoding="utf-8")
    )
    prompts = {str(p): p.read_text(encoding="utf-8") for p in instructions}
    if self.recorder.experiment is None:
        if self.role != "B" or not any((p.name == "agente-conocimiento.md" for p in instructions)):
            prompts = {"knowledge_agent.md" if self.role == "B" else "agent_a.md": base, **prompts}
        if not any((p.name in {"herramientas-estado.md", "state_tools.md"} for p in instructions)):
            prompts["state_tools.md"] = (
                files("research_agent").joinpath("capabilities/state/instructions.md").read_text(encoding="utf-8")
            )
        if persistent is not None and (not any((p.name == "deliberacion.md" for p in instructions))):
            prompts["deliberation.md"] = (
                files("research_agent").joinpath("extensions/deliberation/instructions.md").read_text(encoding="utf-8")
            )
    elif persistent is not None and (not any((p.name == "deliberacion.md" for p in instructions))):
        raise ValueError("Deliberative experiment requires instrucciones/deliberacion.md.")
    if self.knowledge is not None:
        root = self.recorder.experiment
        guide = (
            (root / "instrucciones/delegacion-conocimiento.md").read_text(encoding="utf-8")
            if root
            else files("research_agent")
            .joinpath("extensions/knowledge_agent/prompts/delegation.md")
            .read_text(encoding="utf-8")
        )
        prompts["knowledge_delegation.md"] = guide
    system = "\n\n".join(prompts.values())
    review_policy = None
    checkpoint_policy = None
    state_tools_configuration = None
    if self.recorder.experiment is not None:
        profile_path = self.recorder.experiment / "herramientas.json"
        Workspace._check_links(profile_path)
        if profile_path.exists():
            state_tools_configuration = json.loads(profile_path.read_bytes())
    if request.continuous is not None:
        from research_agent.regimes.continuous.checkpoints import CHECKPOINT_POLICY
        from research_agent.regimes.continuous.policy import REVIEW_POLICY
        from research_agent.regimes.continuous.control import identity as runtime_identity

        review_policy = REVIEW_POLICY if request.continuous.general_review and not request.progress else None
        checkpoint_policy = CHECKPOINT_POLICY
    self.recorder.start(
        run_id,
        {
            "run_id": run_id,
            "interaction_id": interaction_id,
            "role": self.role,
            "extensions": effective_extensions(self, request),
            "parent_run_id": self.configuration.get("parent_run_id"),
            "conversation_id": request.conversation_id,
            "workspace_id": request.workspace_id,
            "workspace_fingerprint": hashlib.sha256(str(self.workspace.root.resolve()).encode()).hexdigest(),
            "limits": asdict(self.limits),
            "configuration": self.configuration,
            "metadata": request.metadata,
            "condition": "deliberative" if persistent is not None else "baseline",
            "continuous": asdict(request.continuous) if request.continuous is not None else None,
            "review_policy": review_policy,
            "general_review": {
                "requested": request.continuous.general_review if request.continuous else None,
                "effective": bool(request.continuous and request.continuous.general_review and not request.progress),
            },
            "external_review_policy": (
                review_policy if request.continuous and request.continuous.general_review and not request.progress else None
            ),
            "runtime_control": runtime_identity() if request.continuous else None,
            "objective": (
                {"definition": request.objective.definition(), "sha256": request.objective.sha256}
                if request.objective
                else None
            ),
            "objective_evaluation_policy": objective_policy(request),
            "progress_step_calls": request.progress_step_calls if request.progress else None,
            "knowledge_checkpoint_policy": checkpoint_policy,
            "persistent_context": persistent,
            "closing_policy": (closing_metadata(self, request)),
            "prompts": {
                k: {"sha256": hashlib.sha256(v.encode()).hexdigest(), "text": v} for k, v in prompts.items()
            },
            "state_contracts": self.tools.contracts,
            "state_tools_configuration": state_tools_configuration,
            "tools": self.tools.specs(),
        },
    )
    if self.recorder.contract_changes:
        notice = "State tool contracts changed since the previous run: " + ", ".join(
            self.recorder.contract_changes
        )
        system += (
            "\n\n" + notice + ". Consult current contracts before relying on prior instrumental knowledge."
        )
        self.recorder.event("lab.state_contracts.changed", tools=self.recorder.contract_changes)
    return system
