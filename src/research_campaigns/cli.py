"""Validate, execute, resume and review local research campaigns."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from research_agent.simulation.state import read
from research_agent.workspace import Workspace
from .catalog import load_suite
from .storage import digest, load


def definition(root: Path) -> tuple[str, Path]:
    Workspace._check_links(root)
    candidates = [root / name for name in ("suite.yaml", "scenario.yaml", "scenario.json") if (root / name).is_file()]
    if len(candidates) != 1:
        raise ValueError("Definition requires exactly one suite.yaml, scenario.yaml or scenario.json.")
    path = candidates[0]
    return {"suite.yaml": "suite", "scenario.yaml": "historical", "scenario.json": "continuous"}[path.name], path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    for name in ("validate", "run"):
        command = sub.add_parser(name)
        command.add_argument("definition", type=Path)
        command.add_argument("--data", type=Path)
        if name == "run":
            command.add_argument("--output", type=Path, required=True)
            command.add_argument("--case")
            command.add_argument("--condition", choices=["baseline", "deliberative"])
            command.add_argument("--instructions-dir", type=Path)
            command.add_argument("--state-tools", choices=["legacy", "v5"], default="v5")
    for name in ("resume", "report"):
        sub.add_parser(name).add_argument("campaign", type=Path)
    progress = sub.add_parser("progress", help="Observe a native run offline; no semantic score or provider calls.")
    progress.add_argument("run", type=Path)
    progress.add_argument("--checks", type=Path)
    progress.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.operation == "progress":
            from .progress import save_report
            save_report(args.run, args.output or args.run / "progreso-v6.json", args.checks)
            return 0
        if args.operation in {"resume", "report"}:
            record = load(args.campaign)
            if args.operation == "report":
                from .report import report
                report(args.campaign, record)
                return 0
            if record["mode"] != "historical":
                raise ValueError("Only historical campaigns support resume.")
            from .longitudinal import run_campaign
            return run_campaign(args.campaign)
        mode, path = definition(args.definition)
        config: dict[str, Any] = {}
        if mode == "suite":
            suite = load_suite(args.definition)
            if args.data is not None:
                raise ValueError("--data does not apply to document suites.")
        elif mode == "historical":
            from .longitudinal import load_scenario, preflight
            config = load_scenario(path)
        else:
            from .continuous import validate
            config = validate(args.definition)
            from .longitudinal import preflight
        if args.operation == "validate":
            if args.data:
                if mode == "continuous" and digest(args.data) != config["dataset_sha256"]:
                    raise ValueError("Frozen source dataset hash mismatch.")
                result = preflight(config, read(args.data))
                if not result["ready"]:
                    raise ValueError(f"Dataset preflight failed: {result['problems']}")
            print(f"valid: {mode}" + (f"; cases={len(suite.cases)}; sessions={sum(len(c.sessions) for c in suite.cases)}" if mode == "suite" else ""))
            return 0
        if mode != "historical" and (args.condition is not None or args.instructions_dir is not None):
            raise ValueError("--condition and --instructions-dir apply only to historical campaigns.")
        if mode != "suite" and args.case is not None:
            raise ValueError("--case applies only to document suites.")
        if mode == "suite":
            from .suite import run_suite
            return run_suite(suite, args.output, args.case, state_tools=args.state_tools)[1]
        if mode == "historical":
            from .longitudinal import run_campaign
            return run_campaign(args.output, scenario=path, data=read(args.data) if args.data else None,
                                condition=args.condition, instructions_dir=args.instructions_dir, state_tools=args.state_tools)
        if args.data is None:
            raise ValueError("Continuous campaigns require a local --data dataset.")
        from .continuous import run_campaign as run_continuous
        return run_continuous(args.output, args.definition, args.data, state_tools=args.state_tools)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    except KeyboardInterrupt:
        return 1
    return 2
