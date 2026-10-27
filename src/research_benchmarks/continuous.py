"""Offline preparation of the manual continuous pilot; never launches providers."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from importlib.metadata import distribution
import json
from pathlib import Path
import shutil
import sys
from typing import Any, cast

from research_agent.agent import AgentA
from research_agent.context_budget import ByteCounter
from research_agent.continuous import POLICY, context_seed
from research_agent.contracts import AgentRequest, ContinuousConfig
from research_agent.experiments import disjoint, prepare_experiment, validate_mandate
from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder
from research_agent.simulation.state import Simulator, read, save
from research_agent.simulation.tools import activation_message, register_simulation
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from .longitudinal import digest, freeze_files, preflight, runtime_identity


def installed_identity() -> dict[str, Any]:
    identity = runtime_identity()
    origin = json.loads(distribution("findata").read_text("direct_url.json") or "{}")
    # Installation provenance, not a new verification of the original wheel archive.
    return {**identity, "findata_recorded_wheel_sha256":
            origin.get("archive_info", {}).get("hashes", {}).get("sha256")}


def initial_budget(root: Path, profile: dict[str, Any]) -> dict[str, int]:
    """Use the runtime seed and schemas without constructing a client or DB engine."""
    space = Workspace(root / "agente/estado", create=False)
    registry = ToolRegistry(RunRecorder(root / "agente/ejecuciones"))
    register_files(registry, space)
    simulator = Simulator(root / "simulador")
    register_simulation(registry, simulator, None)  # Web is disabled in this pilot.
    agent = AgentA(cast(Any, None), registry, space, registry.recorder,
                   configuration={**profile, "simulated_date": str(simulator.today)})
    message = activation_message(simulator, (root / "peticion.md").read_text(encoding="utf-8"), "usuario")
    request = AgentRequest(message, "agente", "cli", mandate=(root / "mandato.md").read_text(encoding="utf-8"),
                           metadata={"simulated_date": str(simulator.today), "activation_kind": "usuario"})
    paths = sorted((root / "agente/instrucciones").glob("*.md"), key=lambda p: (p.name != "agente.md", p.name))
    system = "\n\n".join(p.read_text(encoding="utf-8") for p in paths) + "\n\n" + POLICY
    return ByteCounter().measure(system, context_seed(agent, request, "initial"), registry.specs(), profile["max_output_tokens"])


def prepare(root: Path, definition: Path, source_data: Path) -> None:
    root, definition, source_data = root.absolute(), definition.absolute(), source_data.absolute()
    for path in (root, definition, source_data):
        Workspace._check_links(path)
    disjoint(root, definition)
    disjoint(root, source_data)
    config = read(definition / "scenario.json")
    if config["schema_version"] != "continuous-pilot-v1" or config["allow_web"] is not False or config["start"] != config["end"]:
        raise ValueError("Expected fixed-date continuous pilot with web disabled.")
    continuous = ContinuousConfig(**config["continuous"])
    if any(value is None for value in (continuous.max_llm_calls, continuous.max_tool_calls, continuous.timeout_seconds)):
        raise ValueError("The pilot requires finite global call, tool and time limits.")
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
    root.mkdir(parents=True, exist_ok=False)
    for name in ("scenario.json", "mandato.md", "peticion.md", "rubrica.md"):
        shutil.copyfile(definition / name, root / name)
    prepare_experiment(root / "agente", new=True, deliberative=True)
    Simulator.create(root / "simulador", config, data)
    # Preserve the original bytes as well as their semantic content and provenance.
    shutil.copyfile(source_data, root / "simulador/data.json")
    size = initial_budget(root, identity["profile"])
    if size["budgeted_bytes"] + 2048 >= continuous.consolidation_threshold_bytes:
        raise ValueError("Initial protected context plus startup margin does not fit below threshold.")
    save(root / "preflight.json", {**report, "initial_budget": size, "startup_margin_bytes": 2048,
                                   "provider_checked": False, "campaign_executed": False})
    command = [sys.executable, "-m", "research_agent", (root / "peticion.md").read_text(encoding="utf-8"),
               "--experiment", str(root / "agente"), "--continue", "--run-name", "piloto",
               "--simulation", str(root / "simulador"), "--mandate", str(root / "mandato.md"), "--continuous",
               "--context-bytes", str(continuous.max_context_bytes),
               "--consolidation-bytes", str(continuous.consolidation_threshold_bytes),
               "--max-calls", str(continuous.max_llm_calls), "--max-tools", str(continuous.max_tool_calls),
               "--continuous-timeout-seconds", str(continuous.timeout_seconds)]
    save(root / "command.json", command)
    save(root / "preparacion.json", {"runtime": identity, "source_dataset_sha256": digest(source_data),
                                     "byte_policy": ByteCounter().metadata, "continuous": asdict(continuous),
                                     "files": freeze_files(root)})


def check(root: Path) -> None:
    """Refuse changed inputs/runtime or reuse of an already attempted pilot."""
    root = root.absolute()
    Workspace._check_links(root)
    manifest = read(root / "preparacion.json")
    actual = freeze_files(root)
    actual.pop("preparacion.json", None)
    if actual != manifest["files"]:
        raise ValueError("Prepared pilot changed or has already run; preserve it and prepare a fresh destination.")
    if installed_identity() != manifest["runtime"]:
        raise ValueError("Runtime changed after preparation; prepare a fresh destination.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    create = sub.add_parser("prepare")
    create.add_argument("output", type=Path)
    create.add_argument("--definition", type=Path, default=Path("benchmarks/contexto-continuo-v1"))
    create.add_argument("--source-data", type=Path, required=True)
    verify = sub.add_parser("check")
    verify.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.operation == "prepare":
            prepare(args.output, args.definition, args.source_data)
        check(args.output)
    except (ValueError, OSError, KeyError) as exc:
        parser.exit(2, f"continuous pilot: {exc}\n")
    print(f"READY (offline; provider not checked): {args.output.absolute()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
