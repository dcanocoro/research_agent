"""Prepare files, run the existing CLI in fresh processes, collect native evidence."""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from importlib import metadata
import os
from pathlib import Path
import shutil
import subprocess
import sys
from time import monotonic
from typing import Callable
from uuid import uuid4

from .catalog import Suite, load_suite
from .evidence import digest, extract, inspect_run, save
from research_agent.contracts import AgentLimits
from research_agent.experiments import disjoint, git_state, prepare_experiment
from research_agent.workspace import Workspace
import research_agent


def launch(command: list[str], stdout: Path, stderr: Path) -> int:
    """No shell, no output parsing. Let Ctrl+C reach the child before forcing exit."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    with stdout.open("wb") as out, stderr.open("wb") as err:
        child = subprocess.Popen(command, stdout=out, stderr=err, env=env)
        try:
            return child.wait()
        except KeyboardInterrupt:
            try:
                child.wait(timeout=5)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            raise


def dependencies() -> dict[str, object]:
    result: dict[str, object] = {}
    for name in ("research-agent", "findata", "PyYAML"):
        try:
            dist = metadata.distribution(name)
            record = dist.read_text("RECORD")
            import hashlib
            result[name] = {"version": dist.version, "record_sha256": hashlib.sha256(record.encode()).hexdigest() if record else None}
        except metadata.PackageNotFoundError:
            result[name] = {"version": None, "record_sha256": None}
    return result


def run_suite(suite: Suite, output: Path, selected: str | None = None, *,
              launcher: Callable[[list[str], Path, Path], int] = launch,
              compact: bool = True, condition: str = "A0", profile: dict | None = None) -> tuple[Path, int]:
    if condition not in {"A0", "A1"}:
        raise ValueError("Expected A0 or A1")
    if suite.execution is not None:
        required = {"provider", "model", "reasoning_effort", "max_output_tokens"}
        if profile is None or set(profile) != required or any(not isinstance(profile[k], str) or not profile[k] for k in ("provider", "model")) or profile["provider"] not in {"openai", "gemini"} or (profile["reasoning_effort"] is not None and not isinstance(profile["reasoning_effort"], str)) or type(profile["max_output_tokens"]) is not int or profile["max_output_tokens"] < 1:
            raise ValueError("Controlled run requires explicit provider, model, reasoning_effort and max_output_tokens profile")
    mode = "argumentative" if condition == "A1" else "markdown"
    cases = [case for case in suite.cases if selected is None or case.id == selected]
    if not cases:
        raise ValueError(f"Unknown case: {selected}")
    output = output.absolute()
    Workspace._check_links(output)
    disjoint(output, suite.root)
    disjoint(output, Path(__file__).parent)
    agent_source = Path(research_agent.__file__).parent
    disjoint(output, agent_source)
    output.mkdir(parents=True, exist_ok=True)
    campaign = output / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{uuid4().hex[:8]}"
    campaign.mkdir()
    print(f"campaign={campaign}", flush=True)
    frozen = campaign / "definiciones"
    for source in suite.files():
        target = frozen / source.relative_to(suite.root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    suite = load_suite(frozen)
    cases = [case for case in suite.cases if selected is None or case.id == selected]
    manifest = {"schema_version": "benchmark-run-v1", "suite_id": suite.id,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "python": {"executable": sys.executable, "version": sys.version},
                "code_git": git_state(Path(__file__).resolve().parents[2]),
                "source_sha256": {f"{package.name}/{p.relative_to(package).as_posix()}": digest(p)
                                  for package in (agent_source, Path(__file__).parent)
                                  for p in sorted(package.rglob("*")) if p.suffix in {".py", ".md"}},
                "dependencies": dependencies(), "limits": (suite.execution or {}).get("limits", asdict(AgentLimits())),
                "environment": (suite.execution or {}).get("tool_profile", "live-tools-with-prepared-stimuli"),
                "condition": condition, "execution": suite.execution, "profile": profile, "cases": [c.id for c in cases],
                "definitions_sha256": {p.relative_to(campaign).as_posix(): digest(p) for p in suite.files()},
                "configuration_source": "Per-run manifiesto.json contains effective profile, prompts and code hashes; no environment dump."}
    save(campaign / "manifiesto.json", manifest)
    records: list[dict] = []
    (campaign / "casos").mkdir()
    (campaign / "sesiones").mkdir()
    interrupted = False

    def summary() -> None:
        performed = [r for r in records if r["status"] != "not_executed"]
        save(campaign / "resumen.json", {
            "suite_id": suite.id, "interrupted": interrupted,
            "sessions_expected": sum(len(c.sessions) for c in cases),
            "sessions_attempted": len(performed),
            "sessions_completed": sum(r["status"] == "completed" for r in records),
            "operational_complete": len(records) == sum(len(c.sessions) for c in cases) and all(r["status"] == "completed" for r in records),
            "llm_calls": sum(r["llm_calls"] for r in performed) if performed and all(isinstance(r.get("llm_calls"), int) for r in performed) else None,
            "tool_calls": sum(r["tool_calls"] for r in performed) if performed and all(isinstance(r.get("tool_calls"), int) for r in performed) else None,
            "sessions": records,
            "semantic_review": "pending", "investment_quality": "not_evaluated"})

    summary()
    for case in cases:
        experiment = campaign / "casos" / case.id
        blocked = interrupted
        preparation_error: str | None = None
        try:
            prompts = prepare_experiment(experiment, new=True, knowledge_mode=mode,
                                         tool_profile=(suite.execution or {}).get("tool_profile", "live"))
            initial = case.sessions[0]
            index = case.context + "\n\nEntradas disponibles:\n" + "".join(f"- {p.target}\n" for p in initial.publish)
            Workspace(experiment / "estado").write_file("indice.md", index)
            save(experiment / "instrucciones-efectivas.json", {
                p.relative_to(experiment).as_posix(): {"sha256": digest(p), "text": p.read_text(encoding="utf-8")}
                for p in prompts})
        except (OSError, ValueError) as exc:
            blocked = True
            preparation_error = type(exc).__name__
        else:
            preparation_error = None
        published: dict[str, str] = {}
        for session in case.sessions:
            record: dict = {"case_id": case.id, "session_id": session.id, "message": session.message,
                            "status": "not_executed", "run_directory": None, "llm_calls": None,
                            "tool_calls": None, "capture_errors": [], "capture_complete": False}
            record_path = campaign / "sesiones" / f"{case.id}-{session.id}.json"
            if blocked:
                record["reason"] = preparation_error or ("campaign_interrupted" if interrupted else "previous_session_failed")
                records.append(record)
                save(record_path, record)
                summary()
                continue
            prefix = campaign / "sesiones" / f"{case.id}-{session.id}"
            stdout, stderr = Path(str(prefix) + ".stdout.txt"), Path(str(prefix) + ".stderr.txt")
            command = [sys.executable, "-m", "research_agent", session.message,
                       "--experiment", str(experiment), "--continue", "--run-name", session.id,
                       "--conversation", f"{case.id}-{session.id}"]
            runtime: dict = {"document_paths": session.document_paths, "document_limit": session.document_limit}
            if suite.execution is not None:
                runtime["limits"] = suite.execution["limits"]
            if profile is not None:
                runtime["profile"] = profile
            runtime_dir = campaign / "definiciones/runtime"
            runtime_dir.mkdir(exist_ok=True)
            runtime_path = runtime_dir / f"{case.id}-{session.id}.json"
            save(runtime_path, runtime)
            manifest["definitions_sha256"][runtime_path.relative_to(campaign).as_posix()] = digest(runtime_path)
            command.extend(["--runtime-config", str(runtime_path)])
            record.update(status="running", command=command, stdout=stdout.relative_to(campaign).as_posix(),
                          stderr=stderr.relative_to(campaign).as_posix(),
                          started_at=datetime.now(timezone.utc).isoformat())
            records.append(record)
            save(record_path, record)
            summary()
            before = set((experiment / "ejecuciones").iterdir())
            start = monotonic()
            try:
                stdout.touch(exist_ok=False)
                stderr.touch(exist_ok=False)
                for publication in session.publish:
                    target = Workspace(experiment / "estado", create=False).path(publication.target)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as stream:
                        stream.write(publication.source.read_bytes())
                    published[publication.target] = digest(publication.source)
                print(f"{case.id}/{session.id}: running", flush=True)
                record["returncode"] = launcher(command, stdout, stderr)
            except KeyboardInterrupt:
                interrupted = True
                record["error"] = "KeyboardInterrupt"
            except (OSError, ValueError) as exc:
                record["error"] = type(exc).__name__
            finally:
                record["elapsed_seconds"] = round(monotonic() - start, 3)
                new_runs = sorted(set((experiment / "ejecuciones").iterdir()) - before)
                if len(new_runs) == 1 and new_runs[0].is_dir():
                    details, _ = inspect_run(campaign, new_runs[0], case.id, session.id)
                    record.update(details)
                else:
                    record["capture_errors"].append({"error": "Expected exactly one native run", "found": len(new_runs)})
                modifications = []
                for name, expected in published.items():
                    try:
                        actual: str | None = digest(Workspace(experiment / "estado", create=False).path(name))
                    except (OSError, ValueError):
                        actual = None
                    if actual != expected:
                        modifications.append({"path": name, "expected_sha256": expected, "actual_sha256": actual})
                record["input_modifications"] = modifications
                record["published_sha256"] = dict(published)
                record["status"] = ("interrupted" if interrupted else "completed" if record.get("returncode") == 0
                                    and record.get("agent_status") == "completed" and record["capture_complete"] else "failed")
                if case.id == "G2":
                    record["failure_recovery_review"] = ("pending" if record.get("document_tool_failure_observed")
                                                          else "not_observed" if record["capture_complete"] else "unknown_capture_incomplete")
                blocked = record["status"] != "completed"
                save(record_path, record)
                summary()
                extract(campaign)
                print(f"{case.id}/{session.id}: {record['status']}", flush=True)
    summary()
    extract(campaign)
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    save(campaign / "manifiesto.json", manifest)
    if compact:
        from .archive import compact_campaign
        compact_campaign(campaign)
        extract(campaign)
        import json
        return campaign, 0 if json.loads((campaign / "resumen.json").read_text(encoding="utf-8"))["operational_complete"] else 1
    return campaign, 0 if all(r["status"] == "completed" for r in records) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    validate = sub.add_parser("validate", help="Validate all definitions without constructing services")
    validate.add_argument("suite", type=Path)
    run = sub.add_parser("run", help="Run the existing agent with real tools")
    run.add_argument("suite", type=Path)
    run.add_argument("--output", type=Path, default=Path("artifacts/benchmark"))
    run.add_argument("--case")
    run.add_argument("--condition", choices=("A0", "A1"), default="A0")
    run.add_argument("--profile", type=Path, help="JSON provider/model/reasoning_effort/max_output_tokens")
    regenerate = sub.add_parser("extract", help="Regenerate pasos.jsonl from native evidence, without providers")
    regenerate.add_argument("campaign", type=Path)
    compact = sub.add_parser("compact", help="Export an existing campaign to a separate compact archive")
    compact.add_argument("campaign", type=Path)
    compact.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.operation == "compact":
            from .archive import export_campaign
            print(export_campaign(args.campaign, args.output))
            return 0
        if args.operation == "extract":
            extract(args.campaign.absolute())
            return 0
        suite = load_suite(args.suite)
        if args.operation == "validate":
            print(f"valid: {suite.id}; cases={len(suite.cases)}; sessions={sum(len(c.sessions) for c in suite.cases)}")
            return 0
        try:
            import json
            profile = json.loads(args.profile.read_text(encoding="utf-8")) if args.profile else None
            _, code = run_suite(suite, args.output, args.case, condition=args.condition, profile=profile)
            return code
        except OSError as exc:
            print(f"benchmark: execution/archive error: {type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
