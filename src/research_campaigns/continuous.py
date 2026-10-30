"""Prepare a fixed-date pilot offline, then launch the native continuous agent."""
from __future__ import annotations

from dataclasses import asdict
from importlib.metadata import distribution
import json
from pathlib import Path
import shutil
import sys
from typing import Any, cast

from research_agent.agent import AgentA
from research_agent.context_budget import ByteCounter
from research_agent.continuous import CHECKPOINT_POLICY, POLICY, REVIEW_POLICY, context_seed
from research_agent.contracts import AgentRequest, ContinuousConfig
from research_agent.experiments import disjoint, validate_mandate
from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder
from research_agent.simulation.state import Simulator, read
from research_agent.simulation.tools import activation_message, register_simulation
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from research_agent.state_profiles import state_profile
from .longitudinal import preflight, runtime_identity
from .storage import create, load, digest, freeze_files
from .report import persist
from .runner import launch, execute


def installed_identity() -> dict[str, Any]:
    identity = runtime_identity()
    origin = json.loads(distribution("findata").read_text("direct_url.json") or "{}")
    # Installation provenance, not a new verification of the original wheel archive.
    return {**identity, "findata_recorded_wheel_sha256":
            origin.get("archive_info", {}).get("hashes", {}).get("sha256")}


def initial_budget(root: Path, profile: dict[str, Any]) -> dict[str, int]:
    """Use the runtime seed and schemas without constructing a client or DB engine."""
    space = Workspace(root / "estado", create=False)
    registry = ToolRegistry(RunRecorder(root / "ejecuciones"))
    register_files(registry, space, state_tools=state_profile(root))
    simulator = Simulator(root / "simulador")
    register_simulation(registry, simulator, None)  # Web is disabled in this pilot.
    agent = AgentA(cast(Any, None), registry, space, registry.recorder,
                   configuration={**profile, "simulated_date": str(simulator.today)})
    message = activation_message(simulator, (root / "definicion/peticion.md").read_text(encoding="utf-8"), "usuario")
    request = AgentRequest(message, "agente", "cli", mandate=(root / "definicion/mandato.md").read_text(encoding="utf-8"),
                           metadata={"simulated_date": str(simulator.today), "activation_kind": "usuario"})
    paths = sorted((root / "instrucciones").glob("*.md"), key=lambda p: (p.name != "agente.md", p.name))
    system = "\n\n".join(p.read_text(encoding="utf-8") for p in paths) + "\n\n" + POLICY
    return ByteCounter().measure(system, context_seed(agent, request, "initial"), registry.specs(), profile["max_output_tokens"])



def validate(definition: Path) -> dict[str, Any]:
    config = read(definition / "scenario.json")
    if config["schema_version"] != "continuous-pilot-v1" or config["allow_web"] is not False or config["start"] != config["end"]:
        raise ValueError("Expected fixed-date continuous pilot with web disabled.")
    continuous = ContinuousConfig(**config["continuous"])
    if any(value is None for value in (continuous.max_llm_calls, continuous.max_tool_calls, continuous.timeout_seconds)):
        raise ValueError("The pilot requires finite global call, tool and time limits.")
    validate_mandate((definition / "mandato.md").read_text(encoding="utf-8"))
    for name in ("peticion.md", "rubrica.md"):
        if not (definition / name).read_text(encoding="utf-8").strip():
            raise ValueError(f"Nonempty {name} required.")
    return config

def prepare(root: Path, definition: Path, source_data: Path, *, state_tools: str = "v5") -> None:
    root, definition, source_data = root.absolute(), definition.absolute(), source_data.absolute()
    for path in (root, definition, source_data):
        Workspace._check_links(path)
    disjoint(root, definition)
    disjoint(root, source_data)
    config = validate(definition)
    continuous = ContinuousConfig(**config["continuous"])
    if digest(source_data) != config["dataset_sha256"]:
        raise ValueError("Frozen source dataset hash mismatch.")
    data = read(source_data)
    report = preflight(config, data)  # Pure validation of the supplied local dataset.
    if not report["ready"]:
        raise ValueError(f"Dataset preflight failed: {report['problems']}")
    identity = installed_identity()
    if any(identity["profile"].get(k) != v for k, v in config["expected_profile"].items()):
        raise ValueError("Configured model/profile differs from scenario; no automatic substitution.")
    validate_mandate((definition / "mandato.md").read_text(encoding="utf-8"))
    record = create(root, definition, "continuous", config["id"],
                    [definition / name for name in ("scenario.json", "mandato.md", "peticion.md", "rubrica.md")],
                    deliberative=True, state_tools=state_tools)
    persist(root, record)
    Simulator.create(root / "simulador", config, data)
    # Preserve the original bytes as well as their semantic content and provenance.
    shutil.copyfile(source_data, root / "simulador/data.json")
    size = initial_budget(root, identity["profile"])
    if size["budgeted_bytes"] + 2048 >= continuous.consolidation_threshold_bytes:
        raise ValueError("Initial protected context plus startup margin does not fit below threshold.")
    record.update(runtime=identity, limits=asdict(continuous), condition="deliberative", review_policy=REVIEW_POLICY,
                  knowledge_checkpoint_policy=CHECKPOINT_POLICY,
                  preflight={**report, "initial_budget": size, "startup_margin_bytes": 2048,
                             "provider_checked": False, "campaign_executed": False})
    command = [sys.executable, "-m", "research_agent", (root / "definicion/peticion.md").read_text(encoding="utf-8"),
               "--experiment", str(root), "--continue", "--run-name", "piloto",
               "--simulation", str(root / "simulador"), "--mandate", str(root / "definicion/mandato.md"), "--continuous",
               "--context-bytes", str(continuous.max_context_bytes),
               "--consolidation-bytes", str(continuous.consolidation_threshold_bytes),
               "--max-calls", str(continuous.max_llm_calls), "--max-tools", str(continuous.max_tool_calls),
               "--continuous-timeout-seconds", str(continuous.timeout_seconds)]
    frozen_files = {path.relative_to(root).as_posix(): digest(path)
                         for name in ("definicion", "instrucciones", "estado", "simulador")
                         for path in (root / name).rglob("*") if path.is_file()}
    frozen_files["herramientas.json"] = digest(root / "herramientas.json")
    record.update(command=command, byte_policy=ByteCounter().metadata, files=frozen_files)
    persist(root, record)


def check(root: Path) -> None:
    """Refuse changed inputs/runtime or reuse of an already attempted pilot."""
    root = root.absolute()
    Workspace._check_links(root)
    manifest = load(root)
    actual = freeze_files(root)
    actual.pop("campaign.json", None)
    actual.pop("README.md", None)
    actual.pop(".gitignore", None)
    if actual != manifest["files"]:
        raise ValueError("Prepared pilot changed or has already run; preserve it and prepare a fresh destination.")
    if installed_identity() != manifest["runtime"]:
        raise ValueError("Runtime changed after preparation; prepare a fresh destination.")



def run_campaign(root: Path, definition: Path, source_data: Path, *, launcher=launch, state_tools: str = "v5") -> int:
    root = root.absolute()
    prepare(root, definition, source_data, state_tools=state_tools)
    check(root)
    record = load(root)
    session = {"id": "piloto", "message": (root / "definicion/peticion.md").read_text(encoding="utf-8")}
    record["sessions"].append(session)
    execute(root, root, record, session, record.pop("command"), launcher=launcher)
    return 0 if session["status"] == "completed" else 1
