"""Explicit prepare/run/report entry point. Preparation never constructs services."""
from dataclasses import asdict, replace
from importlib import import_module
from pathlib import Path
from time import monotonic
import argparse
import asyncio
import hashlib
import json
import random
import shutil
import sys

from research_agent.observability.recording import encoded

CONDITIONS = ("V0", "V1", "V2")


def save(path, value):
    from research_agent.storage.transactions import atomic_bytes
    atomic_bytes(path, encoded(value))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fingerprints():
    result = {}
    for name in ("research_agent", "research_campaigns", "infra", "runtime_contracts", "findata"):
        root = Path(import_module(name).__file__).parent
        entries = [(p.relative_to(root).as_posix(), digest(p)) for p in sorted(root.rglob("*"))
                   if p.is_file() and p.suffix in {".py", ".md", ".json"}]
        result[name] = hashlib.sha256(encoded(entries)).hexdigest()
    return result


def validate(definition):
    cases = json.loads((definition / "cases.json").read_bytes())
    if len(cases) != 12 or len({c["id"] for c in cases}) != 12:
        raise ValueError("Expected twelve distinct cases")
    for case in cases:
        if (not case["id"].isalnum() or case["group"] not in {"simple", "intermediate", "open"}
                or not all(isinstance(case[k], str) and case[k].strip()
                           for k in ("request", "corpus", "rubric"))):
            raise ValueError("Invalid case")
    for group in ("simple", "intermediate", "open"):
        if sum(c["group"] == group for c in cases) != 4:
            raise ValueError("Expected four cases per group")
    for name in ("self-control.md", "checkpoint.md", "common.md", "rubric.md"):
        if not (definition / name).read_text(encoding="utf-8").strip():
            raise ValueError("Empty instructions")
    return cases


def prepare(definition, output, repetitions):
    cases = validate(definition)
    if repetitions < 1:
        raise ValueError("Repetitions must be positive")
    # Validate before creating a destination. Never merge into an existing campaign.
    hashes = fingerprints()
    output.mkdir(parents=True, exist_ok=False)
    shutil.copytree(definition, output / "definition")
    jobs = []
    rng = random.Random(1729)
    for repeat in range(1, repetitions + 1):
        ordered = list(cases)
        rng.shuffle(ordered)
        for case in ordered:
            conditions = list(CONDITIONS)
            rng.shuffle(conditions)
            jobs.extend({"id": f'{case["id"]}-{repeat:02d}-{condition}', "case": case["id"],
                         "repeat": repeat, "condition": condition} for condition in conditions)
    frozen = {p.relative_to(output / "definition").as_posix(): digest(p)
              for p in sorted((output / "definition").rglob("*")) if p.is_file()}
    save(output / "campaign.json", {"schema_version": "termination-v1", "status": "prepared",
         "repetitions": repetitions, "seed": 1729, "code_sha256": hashes,
         "definition_sha256": frozen, "jobs": jobs,
         "limits": {"max_llm_calls": 18, "max_tool_calls": 30, "timeout_seconds": 600,
                    "finalization_seconds": 45, "max_context_bytes": 262144},
         "profile": None, "tools": "local-state-and-arithmetic", "remote_data": False})
    report(output)


def verify(output):
    campaign = json.loads((output / "campaign.json").read_bytes())
    if campaign["schema_version"] != "termination-v1" or campaign["code_sha256"] != fingerprints():
        raise ValueError("Code/wheel changed: prepare a new campaign; do not overwrite evidence")
    actual = {p.relative_to(output / "definition").as_posix(): digest(p)
              for p in sorted((output / "definition").rglob("*")) if p.is_file()}
    if actual != campaign["definition_sha256"]:
        raise ValueError("Frozen definition changed")
    validate(output / "definition")
    return campaign


async def run_job(output, campaign, job, case, factory, profile):
    from research_agent.agent import AgentA
    from research_agent.contracts import AgentLimits, AgentRequest
    from research_agent.core.execution import execute
    from research_agent.core.tools import ToolRegistry
    from research_agent.storage.workspace import Workspace
    from research_agent.observability.recording import RunRecorder
    from research_agent.capabilities.state.files import register_files
    from research_agent.composition.provider_errors import TRUNCATED_RESPONSE_ERRORS
    from research_campaigns.termination.policy import TerminationPolicy

    destination = output / "jobs" / job["id"]
    destination.mkdir(parents=True, exist_ok=False)
    save(destination / "job.json", {**job, "status": "started"})
    started = monotonic()
    try:
        space = Workspace(destination / "estado")
        space.path("materiales/corpus.md").write_text(case["corpus"], encoding="utf-8")
        space.path("indice.md").write_text(
            "# Corpus del encargo\n\nFuente sintética congelada: materiales/corpus.md.\n", encoding="utf-8")
        recorder = RunRecorder(destination / "ejecuciones", run_name=job["id"])
        tools = ToolRegistry(recorder)
        register_files(tools, space)
        definition = output / "definition"
        instructions = [definition / "common.md",
                        Path(import_module("research_agent").__file__).parent / "instructions/financial_research.md"]
        if job["condition"] != "V0":
            instructions.append(definition / "self-control.md")
        agent = AgentA(factory.conversation(profile), tools, space, recorder,
                       AgentLimits(**campaign["limits"]), instructions=tuple(instructions),
                       configuration={**asdict(profile), "code_sha256": campaign["code_sha256"],
                                      "termination_experiment": job,
                                      "tool_profile": campaign["tools"], "remote_data": False})
        agent.truncated_response_errors = TRUNCATED_RESPONSE_ERRORS
        checkpoint_profile = replace(profile, name=profile.name + "-checkpoint")
        agent.configuration["checkpoint_profile"] = asdict(checkpoint_profile) if job["condition"] == "V2" else None
        request = AgentRequest(case["request"], job["id"], job["id"], metadata={
            "experiment": "termination-v1", "condition": job["condition"], "case": job["case"]})
        policy = TerminationPolicy(agent, request,
            evaluator=factory.conversation(checkpoint_profile) if job["condition"] == "V2" else None,
            evaluator_prompt=(definition / "checkpoint.md").read_text(encoding="utf-8"))
        result = await execute(policy)
        save(destination / "job.json", {**job, "status": result.status,
             "stop_reason": result.stop_reason, "llm_calls": result.llm_calls,
             "calls_by_phase": result.llm_calls_by_phase, "tool_calls": result.tool_calls,
             "elapsed_seconds": monotonic() - started,
             "cost": None, "tokens": None, "usage_note": "Consultar trazas del proveedor; no estimado",
             "run": str(recorder.current.relative_to(destination)),
             "capture_errors": result.state.capture_errors})
    except asyncio.CancelledError:
        save(destination / "job.json", {**job, "status": "cancelled", "elapsed_seconds": monotonic() - started})
        raise
    except Exception as exc:
        save(destination / "job.json", {**job, "status": "failed", "error_type": type(exc).__name__,
                                       "elapsed_seconds": monotonic() - started})


async def run(output, case_ids=(), conditions=()):
    campaign = verify(output)  # All validation before constructing clients.
    cases = {c["id"]: c for c in validate(output / "definition")}
    if set(case_ids) - cases.keys() or set(conditions) - set(CONDITIONS):
        raise ValueError("Unknown case/condition")
    selected = [j for j in campaign["jobs"] if (not case_ids or j["case"] in case_ids)
                and (not conditions or j["condition"] in conditions)
                and not (output / "jobs" / j["id"]).exists()]
    if not selected:
        return True
    from findata.settings import settings
    from infra.llm_factory import LLMFactory, configured_profile
    profile = replace(configured_profile(settings, "planner"), name="lab")
    effective = json.loads(encoded(asdict(profile)))
    if campaign["profile"] is not None and campaign["profile"] != effective:
        raise ValueError("LLM profile changed: prepare a new campaign")
    campaign["profile"] = effective
    campaign["status"] = "started"
    save(output / "campaign.json", campaign)
    factory = LLMFactory(settings)
    try:
        for job in selected:
            print(job["id"], flush=True)
            await run_job(output, campaign, job, cases[job["case"]], factory, profile)
            report(output)
    finally:
        await factory.aclose()
        statuses = [json.loads(path.read_bytes())["status"] if path.exists() else "pending"
                    for j in campaign["jobs"] for path in [output / "jobs" / j["id"] / "job.json"]]
        campaign["status"] = ("completed" if all(s == "completed" for s in statuses) else
                              "partial" if "pending" in statuses else "finished_incomplete")
        save(output / "campaign.json", campaign)
        report(output)
    return all(json.loads((output / "jobs" / j["id"] / "job.json").read_bytes())["status"] == "completed"
               for j in selected)


def report(output):
    campaign = json.loads((output / "campaign.json").read_bytes())
    rows = []
    blind = output / "review" / "answers"
    blind.mkdir(parents=True, exist_ok=True)
    mapping = []
    cases = {c["id"]: c for c in validate(output / "definition")}
    review_order = list(campaign["jobs"])
    random.Random(2718).shuffle(review_order)
    for number, job in enumerate(review_order, 1):
        label = f"R{number:03d}"
        mapping.append({"blind_id": label, **job})
        root = output / "jobs" / job["id"]
        path = root / "job.json"
        record = json.loads(path.read_bytes()) if path.exists() else {"status": "pending"}
        rows.append({**job, **record, "blind_id": label})
        if record.get("run"):
            answer = root / record["run"] / "respuesta.md"
            if answer.exists():
                (blind / f"{label}.md").write_bytes(answer.read_bytes())
                case = cases[job["case"]]
                save(blind / f"{label}.json", {"blind_id": label, "request": case["request"],
                     "corpus": case["corpus"], "rubric": case["rubric"],
                     "answer": answer.read_text(encoding="utf-8")})
    save(output / "review" / "mapping-private.json", mapping)
    save(output / "summary.json", rows)
    lines = ["# Terminación ReAct — campaña", "",
             f'Estado de campaña: {campaign["status"]}. Los resultados operativos no son una evaluación semántica.', "",
             "Respuestas para revisión ciega en review/answers; no entregar mapping-private.json al juez.", "",
             "Coste y tokens desconocidos hasta extraerlos de las trazas. No se imputan ceros.", "",
             "| Ejecución | Estado | Cierre | LLM total | Herramientas | Segundos |",
             "|---|---|---|---:|---:|---:|"]
    for row in sorted(rows, key=lambda r: r["id"]):
        lines.append(f'| {row["id"]} | {row["status"]} | {row.get("stop_reason", "—")} | '
                     f'{row.get("llm_calls", "—")} | {row.get("tool_calls", "—")} | '
                     f'{round(row["elapsed_seconds"], 2) if "elapsed_seconds" in row else "—"} |')
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("validate", "prepare", "run", "report"))
    parser.add_argument("--definition", type=Path, default=Path("campaigns/terminacion"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--condition", choices=CONDITIONS, action="append", default=[])
    args = parser.parse_args(argv)
    try:
        if args.action == "validate":
            validate(args.definition)
        else:
            if args.output is None:
                parser.error("--output is required")
            output = args.output.resolve()
            from research_agent.experiments.store import disjoint
            disjoint(output, args.definition.resolve())
            disjoint(output, Path(__file__).parents[2])
            if args.action == "prepare":
                prepare(args.definition, output, args.repetitions)
            elif args.action == "report":
                report(output)
            else:
                # One process owns campaign state; an interrupted attempt is retained.
                lock = output / ".termination.lock"
                with lock.open("x", encoding="utf-8") as stream:
                    stream.write("termination campaign running\n")
                try:
                    successful = asyncio.run(run(output, args.case, args.condition))
                finally:
                    lock.unlink()
                if not successful:
                    return 1
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 130
