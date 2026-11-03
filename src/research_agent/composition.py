from __future__ import annotations
from typing import Any
from pathlib import Path
from dataclasses import asdict, replace
import hashlib
import json
from importlib.resources import files
from .contracts import AgentRequest
from .runtime.contracts import AgentResult
from .experiment_store import disjoint
from .workspace import Workspace


def progress_components() -> Any:
    from .experiments.progress import support

    return support


def knowledge_mode(root: Path | None, requested: str | None = None) -> str:
    """Inspect the frozen selector before importing a concrete implementation."""
    if requested not in (None, "off", "prepared"):
        raise ValueError("Invalid knowledge-agent mode")
    saved = {"version": "durable-b-v1", "mode": "off"}
    if root is not None:
        path = root / "agente-conocimiento.json"
        Workspace._check_links(path)
        if path.exists():
            saved = json.loads(path.read_bytes())
    if saved not in [{"version": "durable-b-v1", "mode": m} for m in ("off", "prepared")]:
        raise ValueError("Incompatible knowledge-agent configuration")
    if root is not None and requested is not None and requested != saved["mode"]:
        raise ValueError("Knowledge mode is frozen; create a new experiment")
    mode = requested or saved["mode"]
    if mode == "prepared":
        from .experiments.multiagent.knowledge import mode_for

        return mode_for(root, requested)
    return mode


def freeze_knowledge(root: Path, mode: str) -> None:
    if mode == "off":
        from .advances import atomic_bytes
        from .recording import encoded

        atomic_bytes(root / "agente-conocimiento.json", encoded({"version": "durable-b-v1", "mode": mode}))
    else:
        from .experiments.multiagent.knowledge import freeze

        freeze(root, mode)


def freeze_runtime_configuration(root: Path) -> None:
    """Preserve the historical frozen record without loading the E2 controller."""
    from .recording import encoded

    definition = json.loads(
        files("research_agent").joinpath("experiments/regimes/identity.json").read_bytes()
    )
    path = root / "runtime.json"
    Workspace._check_links(path)
    with path.open("xb") as stream:
        stream.write(encoded(definition))


def effective_extensions(agent: Any, request: AgentRequest) -> dict[str, str]:
    return {
        "regime": (
            "knowledge-integration"
            if agent.role == "B"
            else "continuous-e2" if request.continuous else "bounded"
        ),
        "progress": (
            ("objectives-v8" if request.objective else "general-review") if request.continuous else "off"
        ),
        "multiagent": "prepared" if agent.role == "B" or agent.knowledge is not None else "off",
    }


def prepare_run(
    self: Any,
    request: AgentRequest,
    run_id: str,
    interaction_id: str,
    persistent: dict[str, Any] | None = None,
) -> str:
    from .advances import recover

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
        .joinpath("prompts/knowledge_agent.md" if self.role == "B" else "prompts/agent_a.md")
        .read_text(encoding="utf-8")
    )
    prompts = {str(p): p.read_text(encoding="utf-8") for p in instructions}
    if self.recorder.experiment is None:
        if self.role != "B" or not any((p.name == "agente-conocimiento.md" for p in instructions)):
            prompts = {"knowledge_agent.md" if self.role == "B" else "agent_a.md": base, **prompts}
        if not any((p.name in {"herramientas-estado.md", "state_tools.md"} for p in instructions)):
            prompts["state_tools.md"] = (
                files("research_agent").joinpath("prompts/state_tools.md").read_text(encoding="utf-8")
            )
        if persistent is not None and (not any((p.name == "deliberacion.md" for p in instructions))):
            prompts["deliberation.md"] = (
                files("research_agent").joinpath("prompts/deliberation.md").read_text(encoding="utf-8")
            )
    elif persistent is not None and (not any((p.name == "deliberacion.md" for p in instructions))):
        raise ValueError("Deliberative experiment requires instrucciones/deliberacion.md.")
    if self.knowledge is not None:
        root = self.recorder.experiment
        guide = (
            (root / "instrucciones/delegacion-conocimiento.md").read_text(encoding="utf-8")
            if root
            else files("research_agent")
            .joinpath("prompts/knowledge_delegation.md")
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
        from .continuous import CHECKPOINT_POLICY, REVIEW_POLICY
        from .runtime_control import identity as runtime_identity

        review_policy = REVIEW_POLICY
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
            "external_review_policy": (
                review_policy if request.continuous and request.objective is None else None
            ),
            "runtime_control": runtime_identity() if request.continuous else None,
            "objective": (
                {"definition": request.objective.definition(), "sha256": request.objective.sha256}
                if request.objective
                else None
            ),
            "objective_evaluation_policy": objective_policy(request),
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


def objective_policy(request: AgentRequest) -> dict[str, Any] | None:
    if request.objective is None:
        return None
    from .objective_review import POLICY
    from .continuous import DECISION_DIRECTION, REVIEW_POLICY

    return (
        {
            **POLICY,
            **REVIEW_POLICY,
            "direction": DECISION_DIRECTION,
            "protected_seed_headroom_bytes": (
                16384 if request.objective and request.objective.assessment_path else 0
            ),
        }
        if request.objective is not None
        else None
    )


def closing_metadata(agent: Any, request: AgentRequest) -> dict[str, Any] | None:
    if agent.role == "B":
        from .experiments.multiagent.closing import closing_metadata as integration_metadata

        return integration_metadata(agent.limits)
    return (
        {
            "consolidation_calls": 2,
            "response_calls": 1,
            "consolidation_seconds_at_time_threshold": agent.limits.finalization_seconds / 3,
            "response_seconds": agent.limits.finalization_seconds * 2 / 3,
            "context_reserve_bytes": min(32768, agent.limits.max_context_bytes // 4),
            "consolidation_tools": sorted(agent.tools.consolidation_tools or ()),
        }
        if agent.role == "A"
        and request.continuous is None
        and (agent.limits.max_llm_calls >= 4)
        and (agent.limits.max_tool_calls >= 2)
        else None
    )
