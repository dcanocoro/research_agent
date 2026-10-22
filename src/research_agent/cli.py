import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from .bootstrap import build_agent
from .contracts import AgentRequest, AgentLimits, AgentResult
from .experiments import ExperimentConfig, prepare_experiment, experiment_lock, human_name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-agent", description="Agent A: isolated experiments and persistent file state.")
    raw = sys.argv[1:] if argv is None else argv
    if any(arg.split("=")[0] in {"--case-store", "--workspace", "--runs"} for arg in raw):
        parser.error('Legacy workspace/case options were removed. Use: research-agent "MESSAGE" --experiment PATH --new --run-name NAME; then --continue. Historical stores are not migrated.')
    parser.add_argument("message")
    parser.add_argument("--experiment", type=Path, required=True)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--new", action="store_true")
    operation.add_argument("--continue", dest="continuing", action="store_true")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--conversation", default="cli")
    parser.add_argument("--instructions", type=Path, action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=300)
    parser.add_argument("--knowledge-mode", choices=("markdown", "argumentative"))
    parser.add_argument("--tool-profile", choices=("live", "closed-corpus"))
    parser.add_argument("--runtime-config", type=Path, help="Frozen benchmark runtime configuration")
    args = parser.parse_args(raw)
    run_directory: Path | None = None

    async def execute(root: Path, prompts: tuple[Path, ...], limits: AgentLimits) -> AgentResult:
        nonlocal run_directory
        mode = ExperimentConfig.load(root)
        async with build_agent(root / "estado", root / "ejecuciones", limits,
                               experiment=root, run_name=args.run_name,
                               knowledge_mode=mode.knowledge_mode, tool_profile=mode.tool_profile,
                               document_paths=tuple(runtime.get("document_paths", ())),
                               document_limit=runtime.get("document_limit"),
                               profile_overrides=runtime.get("profile")) as agent:
            result = await agent.run(AgentRequest(args.message, root.name, args.conversation, prompts))
            run_directory = agent.recorder.current
            return result
    try:
        human_name(args.run_name)
        runtime = json.loads(args.runtime_config.read_text(encoding="utf-8")) if args.runtime_config else {}
        limits = AgentLimits(**runtime["limits"]) if "limits" in runtime else AgentLimits(timeout_seconds=args.timeout_seconds)
        root = args.experiment.absolute()
        prompts = prepare_experiment(root, new=args.new, instructions=tuple(args.instructions),
                                     knowledge_mode=args.knowledge_mode, tool_profile=args.tool_profile)
        with experiment_lock(root):
            result = asyncio.run(execute(root, prompts, limits))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"research-agent: {exc}\n")
    print(result.answer or f"{result.status}: {result.stop_reason}")
    print(f"execution={run_directory}")
    print(f"run_id={result.run_id}")
    print("state=" + json.dumps(asdict(result.state), ensure_ascii=False))
    return 0 if result.status == "completed" else 1
