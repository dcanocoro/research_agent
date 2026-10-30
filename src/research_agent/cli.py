import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from pathlib import Path
from .bootstrap import build_agent
from .contracts import AgentRequest, AgentLimits, AgentResult, ContinuousConfig
from .experiments import prepare_experiment, experiment_lock, human_name, disjoint, validate_mandate, deliberative_context
from .workspace import Workspace
from .state_profiles import state_profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-agent", description="Agent A: isolated experiments and persistent file state.")
    raw = sys.argv[1:] if argv is None else argv
    if any(arg.split("=")[0] in {"--knowledge-mode", "--case-store", "--workspace", "--runs"} for arg in raw):
        parser.error('Legacy workspace/case options were removed. Use: research-agent "MESSAGE" --experiment PATH --new --run-name NAME; then --continue. Historical stores are not migrated.')
    parser.add_argument("message")
    parser.add_argument("--experiment", type=Path, required=True)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--new", action="store_true")
    operation.add_argument("--continue", dest="continuing", action="store_true")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--conversation", default="cli")
    parser.add_argument("--instructions", type=Path, action="append", default=[])
    parser.add_argument("--state-tools", choices=["legacy", "v5"], help="Creation-only profile; new experiments default to v5")
    parser.add_argument("--adopt-state-tools-v5", action="store_true", help="Explicitly adopt V5 in an existing experiment")
    parser.add_argument("--mandate", type=Path, help="Trusted persistent user mandate outside state and recordings; enables deliberative condition")
    parser.add_argument("--timeout-seconds", type=float, default=300)
    parser.add_argument("--simulation", type=Path, help="Private simulator directory supplied by the longitudinal controller")
    parser.add_argument("--python", dest="python_enabled", action="store_true", help="Enable optional local Python operators (POC, not a security sandbox)")
    parser.add_argument("--activation-kind", choices=["usuario", "temporal"], default="usuario")
    parser.add_argument("--limits", type=Path, help="Frozen AgentLimits JSON or campaign record containing limits")
    parser.add_argument("--continuous", action="store_true", help="Keep A running with bounded renewable context; requires --mandate")
    parser.add_argument("--context-bytes", type=int, default=None, help="Continuous local byte budget including reserves (default 524288)")
    parser.add_argument("--consolidation-bytes", type=int, default=None, help="Continuous byte consolidation threshold including reserves (default 262144)")
    parser.add_argument("--max-calls", type=int, default=None, help="Optional research + consolidation call limit in continuous mode; periodic reviews are additional")
    parser.add_argument("--max-tools", type=int, default=None, help="Optional total tool calls in continuous mode")
    parser.add_argument("--continuous-timeout-seconds", type=float, default=None, help="Optional global continuous duration")
    args = parser.parse_args(raw)
    if (args.state_tools is not None and not args.new) or (args.adopt_state_tools_v5 and args.new):
        parser.error("--state-tools requires --new; --adopt-state-tools-v5 requires --continue.")
    continuous_options = (args.context_bytes, args.consolidation_bytes, args.max_calls, args.max_tools, args.continuous_timeout_seconds)
    if args.continuous and (args.mandate is None or args.limits is not None):
        parser.error("--continuous requires --mandate and cannot use bounded --limits; use --max-calls/--max-tools instead.")
    if not args.continuous and any(value is not None for value in continuous_options):
        parser.error("Continuous budget options require --continuous.")
    run_directory: Path | None = None

    async def execute(root: Path, prompts: tuple[Path, ...], limits: AgentLimits) -> AgentResult:
        nonlocal run_directory
        options = {"simulation": args.simulation} if args.simulation is not None else {}
        if args.python_enabled:
            options["python_enabled"] = True
        options["state_tools"] = state_profile(root)
        async with build_agent(root / "estado", root / "ejecuciones", limits,
                               experiment=root, run_name=args.run_name, **options) as agent:
            message = args.message
            metadata = {}
            if args.simulation is not None:
                from .simulation.state import Simulator
                from .simulation.tools import activation_message
                simulator = Simulator(args.simulation)
                message = activation_message(simulator, message, args.activation_kind)
                metadata = {"simulated_date": str(simulator.today), "activation_kind": args.activation_kind}
            result = await agent.run(AgentRequest(message, root.name, args.conversation, prompts, metadata, mandate, continuous))
            run_directory = agent.recorder.current
            return result
    try:
        human_name(args.run_name)
        if args.python_enabled:
            from .integrations.python_tools import python_configuration
            python_configuration()
        continuous = ContinuousConfig(
            max_context_bytes=args.context_bytes if args.context_bytes is not None else 524288,
            consolidation_threshold_bytes=args.consolidation_bytes if args.consolidation_bytes is not None else 262144,
            max_llm_calls=args.max_calls, max_tool_calls=args.max_tools,
            timeout_seconds=args.continuous_timeout_seconds) if args.continuous else None
        limits_data = json.loads(args.limits.read_text(encoding="utf-8")) if args.limits else {"timeout_seconds": args.timeout_seconds}
        limits = AgentLimits(**limits_data.get("limits", limits_data))
        root = args.experiment.absolute()
        mandate = None
        if args.mandate is not None:
            Workspace._check_links(args.mandate)
            for protected in (root / "estado", root / "ejecuciones"):
                disjoint(args.mandate, protected)
            mandate = args.mandate.read_text(encoding="utf-8")
            validate_mandate(mandate)
        # Adoption and validation belong under the same cooperative experiment lock.
        prompts = prepare_experiment(root, new=args.new, instructions=tuple(args.instructions),
                                     deliberative=mandate is not None, state_tools=args.state_tools)
        with experiment_lock(root):
            if args.adopt_state_tools_v5:
                prompts = prepare_experiment(root, new=False, deliberative=mandate is not None, adopt_state_tools_v5=True)
            if mandate is not None:
                deliberative_context(Workspace(root / "estado", create=False), mandate)
            result = asyncio.run(execute(root, prompts, limits))
    except (ValueError, OSError) as exc:
        parser.exit(2, f"research-agent: {exc}\n")
    print(result.answer or f"{result.status}: {result.stop_reason}")
    if args.continuous:
        print(f"continuous={result.status}: {result.stop_reason}")
    print(f"execution={run_directory}")
    print(f"run_id={result.run_id}")
    print("state=" + json.dumps(asdict(result.state), ensure_ascii=False))
    return 0 if result.status == "completed" or (args.continuous and result.stop_reason in {"call_limit", "tool_limit", "time_limit"}) else 1
