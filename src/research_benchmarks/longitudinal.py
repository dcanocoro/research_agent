"""Historical activations, private simulator inputs, and recoverable sequential execution."""
from __future__ import annotations

import argparse
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
from research_agent.experiments import disjoint, experiment_lock, prepare_experiment, validate_mandate, deliberative_context
from research_agent.simulation.state import Simulator, positive, read, save
from research_agent.workspace import Workspace
from .catalog import identifier, mapping, read_yaml, text
from .evidence import inspect_run
from .runner import dependencies, launch


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    mandate = "\n\n".join(f"## Mensaje del usuario — {day}\n\n{message}"
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
    import research_benchmarks
    from findata.settings import settings
    from infra.llm_factory import configured_profile
    import infra
    import findata
    import runtime_contracts
    result: dict[str, Any] = {"profile": asdict(replace(configured_profile(settings, "planner"), name="lab")),
                              "dependencies": dependencies(), "python": sys.version, "source": {}}
    for module in (research_agent, research_benchmarks, infra, findata, runtime_contracts):
        assert module.__file__ is not None
        package = Path(module.__file__).parent
        result["source"][module.__name__] = {str(p.relative_to(package)): digest(p)
                                              for p in sorted(package.rglob("*")) if p.suffix in {".py", ".md"}}
    return result


def freeze_files(root: Path) -> dict[str, str]:
    return {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob("*")) if p.is_file()}


def run_campaign(campaign: Path, *, scenario: Path | None = None, data: dict[str, Any] | None = None,
                 condition: str | None = None,
                 launcher: Callable[[list[str], Path, Path], int] = launch,
                 identity: Callable[[], dict[str, Any]] = runtime_identity) -> int:
    campaign = campaign.absolute()
    Workspace._check_links(campaign)
    import research_agent
    disjoint(campaign, Path(research_agent.__file__).parent)
    disjoint(campaign, Path(__file__).parent)
    if condition not in {None, "baseline", "deliberative"}:
        raise ValueError("Unknown experimental condition.")
    if scenario is None and condition is not None:
        raise ValueError("Resume uses its frozen condition; do not supply condition.")
    if scenario is not None:
        config = load_scenario(scenario)
        condition = condition or "baseline"
        if condition == "deliberative":
            for activation in activations(config):
                activation_mandate(config, activation["date"])
        disjoint(campaign, scenario)
        campaign.mkdir(parents=True, exist_ok=False)
        (campaign / "definiciones").mkdir()
        save(campaign / "definiciones/scenario.json", config)
        save(campaign / "runtime.json", identity())
        save(campaign / "limits.json", config["limits"])
        save(campaign / "condition.json", {"condition": condition})
        save(campaign / "progress.json", {"next": 0, "active": None, "attempts": [], "finished": False})
        prepare_experiment(campaign / "agente", new=True, deliberative=condition == "deliberative")
        save(campaign / "instructions.json", freeze_files(campaign / "agente/instrucciones"))
    with experiment_lock(campaign):
        config = read(campaign / "definiciones/scenario.json")
        condition_path = campaign / "condition.json"
        condition = read(condition_path)["condition"] if condition_path.exists() else "baseline"
        if condition not in {"baseline", "deliberative"}:
            raise ValueError("Unknown frozen experimental condition.")
        frozen_runtime = read(campaign / "runtime.json")
        if frozen_runtime != identity():
            raise ValueError("Runtime/model configuration changed; resume requires frozen configuration.")
        if read(campaign / "instructions.json") != freeze_files(campaign / "agente/instrucciones"):
            raise ValueError("Instructions changed; resume refused.")
        simulator_root = campaign / "simulador"
        if not simulator_root.exists():
            source = data if data is not None else export_data(config)
            report = preflight(config, source)
            save(campaign / "preflight.json", report)
            if not report["ready"]:
                save(campaign / "blocked-data.json", source)
                return 1
            staging = campaign / ("simulator-setup-" + uuid4().hex)
            Simulator.create(staging, config, source)
            staging.rename(simulator_root)
        actual = {"config": digest(campaign / "definiciones/scenario.json"), "data": digest(simulator_root / "data.json"),
                  "simulator_config": digest(simulator_root / "config.json"), "limits": digest(campaign / "limits.json")}
        if condition_path.exists():
            actual["condition"] = digest(condition_path)
        if not (campaign / "frozen-inputs.json").exists():
            initial_progress = read(campaign / "progress.json")
            if initial_progress["next"] != 0 or initial_progress["attempts"]:
                raise ValueError("Missing frozen inputs for a previously started campaign.")
            save(campaign / "frozen-inputs.json", actual)
        frozen = read(campaign / "frozen-inputs.json")
        if frozen != actual:
            raise ValueError("Frozen scenario/data/limits changed.")
        progress = read(campaign / "progress.json")
        if progress["finished"]:
            return 0
        schedule = activations(config)
        experiment = campaign / "agente"
        attempts_root = campaign / "intentos"
        attempts_root.mkdir(exist_ok=True)

        def persist() -> None:
            save(campaign / "progress.json", progress)

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
            details, rows = inspect_run(campaign, experiment / "ejecuciones" / runs[0], config["id"], attempt["activation"]["id"])
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
            if "profile" in frozen_runtime:
                effective = manifest.get("configuration", {})
                if any(effective.get(key) != value for key, value in frozen_runtime["profile"].items()):
                    details["capture_errors"].append({"error": "Child model/profile differs from frozen runtime"})
                    details["capture_complete"] = False
                for package in ("research_agent", "infra", "findata", "runtime_contracts"):
                    expected = hashlib.sha256(repr(list(frozen_runtime["source"][package].items())).encode()).hexdigest()
                    if effective.get("code_sha256", {}).get(package) != expected:
                        details["capture_errors"].append({"error": f"Child source differs from frozen runtime: {package}"})
                        details["capture_complete"] = False
            save(directory / "capture.json", details)
            save(directory / "steps.json", rows)
            if details.get("agent_status") != "completed" or not details.get("capture_complete"):
                return False
            save(directory / "simulator-after.json", read(simulator_root / "state.json"))
            save(directory / "memory-after.json", freeze_files(experiment / "estado"))
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
            persist()

        active = progress["active"]
        if active is not None:
            attempt = progress["attempts"][active]
            prepare_mandate(attempt["activation"]["date"])
            if inspect_attempt(attempt):
                progress["next"] += 1
                progress["active"] = None
                persist()
            else:
                restore(attempt)
        while progress["next"] < len(schedule):
            activation = schedule[progress["next"]]
            prepare_mandate(activation["date"])
            simulator = Simulator(simulator_root)
            simulator.advance(date.fromisoformat(activation["date"]))
            number = len(progress["attempts"]) + 1
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
            progress["active"] = len(progress["attempts"])
            progress["attempts"].append(attempt)
            persist()
            command = [sys.executable, "-m", "research_agent", activation["message"], "--experiment", str(experiment),
                       "--continue", "--run-name", attempt_id, "--conversation", activation["id"],
                       "--simulation", str(simulator_root), "--activation-kind", activation["kind"],
                       "--limits", str(campaign / "limits.json")]
            if condition == "deliberative":
                command.extend(["--mandate", str(experiment / "mandato.md")])
            save(directory / "command.json", command)
            print(f"{activation['date']} {activation['kind']} {attempt_id}", flush=True)
            try:
                attempt["returncode"] = launcher(command, directory / "stdout.txt", directory / "stderr.txt")
                complete = inspect_attempt(attempt)
                if attempt["returncode"] != 0 or not complete:
                    attempt["status"] = "failed"
                    persist()
                    return 1
            except KeyboardInterrupt:
                attempt["status"] = "interrupted"
                persist()
                return 1
            except Exception:
                attempt["status"] = "failed"
                persist()
                raise
            progress["next"] += 1
            progress["active"] = None
            persist()
        simulator = Simulator(simulator_root)
        simulator.advance(date.fromisoformat(config["end"]), finish=True)
        save(campaign / "portfolio-final.json", simulator.get())
        save(campaign / "history-final.json", simulator.history())
        save(campaign / "communications.json", simulator.state["notifications"])
        progress["finished"] = True
        persist()
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("scenario", type=Path)
    pre = sub.add_parser("preflight")
    pre.add_argument("scenario", type=Path)
    pre.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("scenario", type=Path)
    run.add_argument("--output", type=Path, required=True, help="New campaign directory")
    run.add_argument("--data", type=Path, help="Explicit controlled dataset; otherwise export Findata read-only")
    run.add_argument("--condition", choices=["baseline", "deliberative"], default="baseline")
    resume = sub.add_parser("resume")
    resume.add_argument("campaign", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.operation == "validate":
            config = load_scenario(args.scenario)
            print(f"valid: {config['id']}; companies={len(config['universe'])}; activations={len(activations(config))}")
            return 0
        if args.operation == "preflight":
            config = load_scenario(args.scenario)
            args.output.mkdir(parents=True, exist_ok=False)
            source = export_data(config)
            save(args.output / "data.json", source)
            report = preflight(config, source)
            save(args.output / "preflight.json", report)
            print(f"ready={report['ready']}; report={args.output / 'preflight.json'}")
            return 0 if report["ready"] else 1
        if args.operation == "resume":
            return run_campaign(args.campaign)
        return run_campaign(args.output, scenario=args.scenario, data=read(args.data) if args.data else None,
                            condition=args.condition)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f"longitudinal: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("longitudinal: interrupted; available checkpoints and attempts are preserved", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
