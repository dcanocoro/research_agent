"""Historical activations, private simulator inputs, and recoverable sequential execution."""
from __future__ import annotations

from dataclasses import asdict, replace
from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Callable
from uuid import uuid4

from research_agent.contracts import AgentLimits
from research_agent.experiments import disjoint, experiment_lock, prepare_experiment, validate_mandate, deliberative_context, instruction_bundle
from research_agent.simulation.state import Simulator, positive, read, save
from research_agent.workspace import Workspace
from .catalog import identifier, mapping, read_yaml, text
from .evidence import inspect_run
from .report import persist
from .runner import launch, execute
from .storage import create, load, dependencies, digest, freeze_files


def load_scenario(path: Path) -> dict[str, Any]:
    Workspace._check_links(path)
    raw = mapping(read_yaml(path), {"schema_version", "id", "start", "end", "universe", "initial_cash",
                                  "max_positions", "annual_lag_days", "messages", "limits", "price_review"})
    if raw["schema_version"] != "longitudinal-v1":
        raise ValueError("Expected longitudinal-v1.")
    identifier(raw["id"])
    start, end = date.fromisoformat(str(raw["start"])), date.fromisoformat(str(raw["end"]))
    if start > end or start.day != 1:
        raise ValueError("Start must be a first of month before end.")
    if not isinstance(raw["universe"], list) or not raw["universe"]:
        raise ValueError("Expected nonempty universe.")
    universe = []
    seen = set()
    for item in raw["universe"]:
        item = mapping(item, {"symbol", "name"})
        symbol = text(item["symbol"]).upper()
        if symbol in seen or not all(c.isalnum() or c in ".-" for c in symbol):
            raise ValueError("Duplicate or invalid symbol.")
        seen.add(symbol)
        universe.append({"symbol": symbol, "name": text(item["name"])})
    if type(raw["max_positions"]) is not int or not 1 <= raw["max_positions"] <= len(universe):
        raise ValueError("Invalid maximum positions.")
    if type(raw["annual_lag_days"]) is not int or raw["annual_lag_days"] < 0:
        raise ValueError("Invalid annual availability lag.")
    limits = AgentLimits(**mapping(raw["limits"], set(asdict(AgentLimits()))))
    messages = {}
    if not isinstance(raw["messages"], dict):
        raise ValueError("Expected dated messages.")
    for key, value in raw["messages"].items():
        when = date.fromisoformat(str(key))
        if not start <= when <= end:
            raise ValueError("Message outside scenario.")
        messages[when.isoformat()] = text(value)
    review = mapping(raw["price_review"], {"status", "basis", "evidence"})
    if review["status"] not in {"pending", "approved"} or review["basis"] not in {"unadjusted", "adjusted", "synthetic"}:
        raise ValueError("Invalid price review.")
    text(review["evidence"])
    return {**raw, "start": str(start), "end": str(end), "universe": universe,
            "initial_cash": str(positive(raw["initial_cash"])), "messages": messages,
            "limits": asdict(limits)}


def activations(config: dict[str, Any]) -> list[dict[str, str]]:
    current = date.fromisoformat(config["start"])
    dates = set(config["messages"])
    while str(current) <= config["end"]:
        dates.add(str(current))
        current = date(current.year + (current.month == 12), current.month % 12 + 1, 1)
    return [{"id": f"activation-{i:04d}", "date": when,
             "kind": "usuario" if when in config["messages"] else "temporal",
             "message": config["messages"].get(when, "")}
            for i, when in enumerate(sorted(dates), 1)]


def activation_mandate(config: dict[str, Any], when: str) -> str:
    mandate = "\n\n".join(f"## Mensaje del usuario â€” {day}\n\n{message}"
                            for day, message in sorted(config["messages"].items()) if day <= when)
    validate_mandate(mandate)
    return mandate


def export_data(config: dict[str, Any]) -> dict[str, Any]:
    from findata.settings import settings
    from findata.read.historical import dataset
    from sqlalchemy import create_engine, text as sql
    from sqlalchemy.orm import Session
    engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 10})
    try:
        with Session(engine) as session:
            session.execute(sql("SET TRANSACTION READ ONLY"))
            session.execute(sql("SET LOCAL statement_timeout = '30000'"))
            result = dataset(session, [c["symbol"] for c in config["universe"]],
                             date.fromisoformat(config["start"]), date.fromisoformat(config["end"]))
            session.rollback()
            return result
    finally:
        engine.dispose()


def preflight(config: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    from findata.read.historical import available_facts
    problems, coverage = [], []
    if config["price_review"]["status"] != "approved" or config["price_review"]["basis"] != data["price_basis"]:
        problems.append("Price adjustments/corporate actions have not been reviewed for this dataset.")
    expected = {c["symbol"] for c in config["universe"]}
    if any(r["symbol"] not in expected for r in [*data["prices"], *data["facts"]]):
        problems.append("Dataset contains symbols outside the scenario.")
    keys = [(r["symbol"], r["date"]) for r in data["prices"]]
    if len(keys) != len(set(keys)):
        problems.append("Ambiguous price series: duplicate symbol/date.")
    for company in config["universe"]:
        symbol = company["symbol"]
        prices = sorted((r for r in data["prices"] if r["symbol"] == symbol), key=lambda r: r["date"])
        facts = [r for r in data["facts"] if r["symbol"] == symbol]
        available = available_facts(facts, date.fromisoformat(config["start"]), config["annual_lag_days"])
        issues = []
        if not available:
            issues.append("No available initial fundamentals")
        if any(r.get("currency") != "USD" for r in facts):
            issues.append("Non-USD or unknown fundamental currency")
        for row in prices:
            positive(row["close"])
            date.fromisoformat(row["date"])
        if not prices:
            issues.append("No prices")
        else:
            for activation in [*activations(config), {"date": config["end"]}]:
                prior = [p for p in prices if p["date"] <= activation["date"]]
                if not prior or (date.fromisoformat(activation["date"]) - date.fromisoformat(prior[-1]["date"])).days > 7:
                    issues.append("Missing or stale price at activation/end")
                    break
        coverage.append({"symbol": symbol, "prices": len(prices), "facts": len(facts),
                         "available_initial_facts": len(available), "issues": issues})
        problems.extend(f"{symbol}: {issue}" for issue in issues)
    return {"ready": not problems, "problems": problems, "coverage": coverage,
            "price_review": config["price_review"], "annual_lag_days": config["annual_lag_days"],
            "limitations": data.get("limitations", [])}


def runtime_identity() -> dict[str, Any]:
    import research_agent
    import research_campaigns
    from findata.settings import settings
    from infra.llm_factory import configured_profile
    import infra
    import findata
    import runtime_contracts
    result: dict[str, Any] = {"profile": asdict(replace(configured_profile(settings, "planner"), name="lab")),
                              "dependencies": dependencies(), "python": sys.version, "source": {}}
    for module in (research_agent, research_campaigns, infra, findata, runtime_contracts):
        assert module.__file__ is not None
        package = Path(module.__file__).parent
        result["source"][module.__name__] = {str(p.relative_to(package)): digest(p)
                                              for p in sorted(package.rglob("*")) if p.suffix in {".py", ".md"}}
    return result


def run_campaign(campaign: Path, *, scenario: Path | None = None, data: dict[str, Any] | None = None,
                 condition: str | None = None,
                 instructions_dir: Path | None = None,
                 state_tools: str | None = None,
                 launcher: Callable[[list[str], Path, Path], int] = launch,
                 identity: Callable[[], dict[str, Any]] = runtime_identity) -> int:
    campaign = campaign.absolute()
    Workspace._check_links(campaign)
    import research_agent
    disjoint(campaign, Path(research_agent.__file__).parent)
    disjoint(campaign, Path(__file__).parent)
    if condition not in {None, "baseline", "deliberative"}:
        raise ValueError("Unknown experimental condition.")
    if state_tools not in {None, "legacy", "v5"} or (scenario is None and state_tools is not None):
        raise ValueError("State tools profile applies only when creating a campaign.")
    if scenario is None and condition is not None:
        raise ValueError("Resume uses its frozen condition; do not supply condition.")
    if instructions_dir is not None:
        if scenario is None:
            raise ValueError("Resume uses frozen instructions; do not supply instructions_dir.")
        disjoint(campaign, instructions_dir)
        instruction_bundle(instructions_dir, deliberative=condition == "deliberative")
    if scenario is not None:
        config = load_scenario(scenario)
        condition = condition or "baseline"
        if condition == "deliberative":
            for activation in activations(config):
                activation_mandate(config, activation["date"])
        disjoint(campaign, scenario)
        record = create(campaign, scenario.parent, "historical", config["id"],
                        [scenario, *scenario.parent.glob("*.md")],
                        deliberative=condition == "deliberative", instructions_dir=instructions_dir,
                        state_tools=state_tools or "v5")
        record.update(config=config, condition=condition, limits=config["limits"], runtime=identity(),
                      instructions_sha256=freeze_files(campaign / "instrucciones"),
                      progress={"next": 0, "active": None, "finished": False})
        persist(campaign, record)
    if scenario is None:
        load(campaign)  # Reject unsupported captures before creating control directories.
    (campaign / "recuperacion").mkdir(exist_ok=True)
    with experiment_lock(campaign / "recuperacion"):
        record = load(campaign)
        if record["mode"] != "historical":
            raise ValueError("Only historical campaigns support resume.")
        config = record["config"]
        condition = record["condition"]
        if condition not in {"baseline", "deliberative"}:
            raise ValueError("Unknown frozen experimental condition.")
        frozen_runtime = record["runtime"]
        if frozen_runtime != identity():
            raise ValueError("Runtime/model configuration changed; resume requires frozen configuration.")
        if record["instructions_sha256"] != freeze_files(campaign / "instrucciones"):
            raise ValueError("Instructions changed; resume refused.")
        simulator_root = campaign / "simulador"
        if not simulator_root.exists():
            source = data if data is not None else export_data(config)
            report = preflight(config, source)
            record["preflight"] = report
            persist(campaign, record)
            if not report["ready"]:
                record.update(status="blocked", stop_reason="dataset_preflight_failed")
                persist(campaign, record)
                return 1
            staging = campaign / ("simulator-setup-" + uuid4().hex)
            Simulator.create(staging, config, source)
            staging.rename(simulator_root)
        actual = {"definition": freeze_files(campaign / "definicion"), "data": digest(simulator_root / "data.json"),
                  "simulator_config": digest(simulator_root / "config.json"), "condition": condition,
                  "config": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
                  "state_tools_config": digest(campaign / "herramientas.json") if (campaign / "herramientas.json").exists() else None}
        if "frozen_inputs" not in record:
            if record["progress"]["next"] != 0 or record["sessions"]:
                raise ValueError("Missing frozen inputs for a previously started campaign.")
            record["frozen_inputs"] = actual
        if record["frozen_inputs"] != actual:
            raise ValueError("Frozen scenario/data/limits changed.")
        progress = record["progress"]
        if progress["finished"]:
            return 0
        schedule = activations(config)
        experiment = campaign
        attempts_root = campaign / "recuperacion"
        attempts_root.mkdir(exist_ok=True)

        def commit() -> None:
            persist(campaign, record)

        def prepare_mandate(when: str) -> None:
            if condition == "deliberative":
                mandate_path = experiment / "mandato.md"
                Workspace._check_links(mandate_path)
                mandate_path.write_text(activation_mandate(config, when), encoding="utf-8")

        def inspect_attempt(attempt: dict[str, Any]) -> bool:
            directory = attempts_root / attempt["id"]
            runs = sorted(p.name for p in (experiment / "ejecuciones").iterdir() if p.is_dir()
                          and p.name not in attempt["runs_before"])
            if len(runs) != 1:
                return False
            details = inspect_run(campaign, experiment / "ejecuciones" / runs[0], frozen_runtime)
            manifest = {}
            if condition == "deliberative" or "profile" in frozen_runtime:
                try:
                    manifest = read(experiment / "ejecuciones" / runs[0] / "manifiesto.json")
                except (OSError, ValueError):
                    details["capture_errors"].append({"error": "Child manifest unavailable"})
                    details["capture_complete"] = False
            if condition == "deliberative":
                expected_context = deliberative_context(Workspace(directory / "checkpoint-state", create=False),
                    activation_mandate(config, attempt["activation"]["date"]))
                if manifest.get("condition") != condition or manifest.get("persistent_context") != expected_context:
                    details["capture_errors"].append({"error": "Child persistent context differs from activation/checkpoint"})
                    details["capture_complete"] = False
            attempt.update(details)
            if attempt.get("returncode", 0) != 0 or details.get("agent_status") != "completed" or not details.get("capture_complete"):
                return False
            attempt.update(status="completed", run=runs[0])
            return True

        def restore(attempt: dict[str, Any]) -> None:
            directory = attempts_root / attempt["id"]
            # Keep the failed memory (including original materials) for audit. No recursive deletion.
            state = experiment / "estado"
            backup = directory / ("failed-state-" + uuid4().hex)
            if state.exists():
                assert state.resolve().is_relative_to(campaign.resolve())
                assert backup.resolve().is_relative_to(campaign.resolve())
                state.rename(backup)
            shutil.copytree(directory / "checkpoint-state", state)
            save(simulator_root / "state.json", read(directory / "simulator-before.json"))
            attempt["status"] = "interrupted"
            progress["active"] = None
            commit()

        active = progress["active"]
        if active is not None:
            attempt = record["sessions"][active]
            prepare_mandate(attempt["activation"]["date"])
            if inspect_attempt(attempt):
                progress["next"] += 1
                progress["active"] = None
                commit()
            else:
                restore(attempt)
        while progress["next"] < len(schedule):
            activation = schedule[progress["next"]]
            prepare_mandate(activation["date"])
            simulator = Simulator(simulator_root)
            simulator.advance(date.fromisoformat(activation["date"]))
            number = len(record["sessions"]) + 1
            # A crash while preparing a checkpoint can leave an unlaunched directory.
            # Preserve it and choose a fresh name on resume.
            while (attempts_root / f"{activation['id']}-attempt-{number:04d}").exists():
                number += 1
            attempt_id = f"{activation['id']}-attempt-{number:04d}"
            directory = attempts_root / attempt_id
            directory.mkdir()
            shutil.copytree(experiment / "estado", directory / "checkpoint-state")
            save(directory / "simulator-before.json", simulator.state)
            attempt = {"id": attempt_id, "activation": activation, "status": "running",
                       "runs_before": [p.name for p in (experiment / "ejecuciones").iterdir() if p.is_dir()]}
            progress["active"] = len(record["sessions"])
            record["sessions"].append(attempt)
            commit()
            command = [sys.executable, "-m", "research_agent", activation["message"], "--experiment", str(experiment),
                       "--continue", "--run-name", attempt_id, "--conversation", activation["id"],
                       "--simulation", str(simulator_root), "--activation-kind", activation["kind"],
                       "--limits", str(campaign / "campaign.json")]
            if condition == "deliberative":
                command.extend(["--mandate", str(experiment / "mandato.md")])
            execute(campaign, experiment, record, attempt, command, launcher=launcher)
            if attempt["status"] != "completed" or not inspect_attempt(attempt):
                if attempt["status"] == "completed":
                    attempt["status"] = "failed"
                record["status"] = attempt["status"]
                commit()
                return 1
            progress["next"] += 1
            progress["active"] = None
            commit()
        simulator = Simulator(simulator_root)
        simulator.advance(date.fromisoformat(config["end"]), finish=True)
        record.update(status="completed", stop_reason="all_activations_completed")
        progress["finished"] = True
        commit()
        return 0

