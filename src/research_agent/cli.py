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
from .objectives import Objective


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
    parser.add_argument("--mandate", type=Path, help="Trusted persistent user mandate outside state and recordings; enables deliberative condition")
    parser.add_argument("--knowledge-agent", choices=["off", "prepared"], default=None)
    parser.add_argument("--timeout-seconds", type=float, default=300)
    parser.add_argument("--simulation", type=Path, help="Private simulator directory supplied by the longitudinal controller")
    parser.add_argument("--python", dest="python_enabled", action="store_true", help="Enable optional local Python operators (POC, not a security sandbox)")
    parser.add_argument("--activation-kind", choices=["usuario", "temporal"], default="usuario")
    parser.add_argument("--limits", type=Path, help="Frozen AgentLimits JSON or campaign record containing limits")
    parser.add_argument("--continuous", action="store_true", help="Keep A running with bounded renewable context; requires --mandate")
    parser.add_argument("--objective", type=Path, help="Fixed objective JSON outside state/recordings; requires --continuous")
    parser.add_argument("--context-bytes", type=int, default=None, help="Continuous local byte budget including reserves (default 524288)")
    parser.add_argument("--renewal-bytes", type=int, default=None, help="Continuous context renewal threshold (default 262144)")
    parser.add_argument("--consolidation-bytes", type=int, default=None, help="Deprecated alias for --renewal-bytes")
    parser.add_argument("--max-calls", type=int, default=None, help="Optional TOTAL managed LLM calls in continuous mode, including evaluations/checkpoints")
    parser.add_argument("--max-tools", type=int, default=None, help="Optional total tool calls in continuous mode")
    parser.add_argument("--max-total-calls", type=int, default=None, help="Compatibility ceiling; E2 already counts all managed calls in --max-calls")
    parser.add_argument("--continuous-timeout-seconds", type=float, default=None, help="Optional global continuous duration")
    args = parser.parse_args(raw)
    if args.max_total_calls is not None:
        if args.max_total_calls < 1:
            parser.error("--max-total-calls must be positive")
        args.max_calls = min(args.max_calls, args.max_total_calls) if args.max_calls is not None else args.max_total_calls
    continuous_options = (args.renewal_bytes, args.context_bytes, args.consolidation_bytes, args.max_calls, args.max_tools, args.continuous_timeout_seconds)
    if args.continuous and (args.mandate is None or args.limits is not None):
        parser.error("--continuous requires --mandate and cannot use bounded --limits; use --max-calls/--max-tools instead.")
    if not args.continuous and any(value is not None for value in continuous_options):
        parser.error("Continuous budget options require --continuous.")
    if args.objective is not None and not args.continuous:
        parser.error("--objective requires --continuous.")
    if args.renewal_bytes is not None and args.consolidation_bytes is not None and args.renewal_bytes != args.consolidation_bytes:
        parser.error("--renewal-bytes and --consolidation-bytes contradict each other.")
    if args.consolidation_bytes is not None:
        print("--consolidation-bytes is deprecated; use --renewal-bytes", file=sys.stderr)
    run_directory: Path | None = None

    async def execute(root: Path, prompts: tuple[Path, ...], limits: AgentLimits) -> AgentResult:
        nonlocal run_directory
        options = {"simulation": args.simulation} if args.simulation is not None else {}
        if args.python_enabled:
            options["python_enabled"] = True
        from .knowledge import mode_for
        knowledge_mode = mode_for(root, args.knowledge_agent)
        if knowledge_mode != "off":
            options["knowledge_agent"] = knowledge_mode
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
            result = await agent.run(AgentRequest(message, root.name, args.conversation, prompts, metadata, mandate, continuous, objective))
            run_directory = agent.recorder.current
            return result
    try:
        human_name(args.run_name)
        if args.python_enabled:
            from .integrations.python_tools import python_configuration
            python_configuration()
        continuous = ContinuousConfig(
            max_context_bytes=args.context_bytes if args.context_bytes is not None else 524288,
            consolidation_threshold_bytes=(args.renewal_bytes if args.renewal_bytes is not None else
                                           args.consolidation_bytes if args.consolidation_bytes is not None else 262144),
            max_llm_calls=args.max_calls, max_tool_calls=args.max_tools,
            timeout_seconds=args.continuous_timeout_seconds) if args.continuous else None
        limits_data = json.loads(args.limits.read_text(encoding="utf-8")) if args.limits else {"timeout_seconds": args.timeout_seconds}
        limits = AgentLimits(**limits_data.get("limits", limits_data))
        root = args.experiment.absolute()
        objective = None
        if args.objective is not None:
            Workspace._check_links(args.objective)
            for protected in (root / "estado", root / "ejecuciones"):
                disjoint(args.objective, protected)
            objective = Objective.load(args.objective)
        mandate = None
        if args.mandate is not None:
            Workspace._check_links(args.mandate)
            for protected in (root / "estado", root / "ejecuciones"):
                disjoint(args.mandate, protected)
            mandate = args.mandate.read_text(encoding="utf-8")
            validate_mandate(mandate)
        # Adoption and validation belong under the same cooperative experiment lock.
        prompts = prepare_experiment(root, new=args.new, instructions=tuple(args.instructions),
                                     deliberative=mandate is not None, knowledge_agent=args.knowledge_agent)
        from .knowledge import mode_for
        if mode_for(root, args.knowledge_agent) != "off" and (continuous is None or continuous.max_llm_calls != 100):
            raise ValueError("Durable B requires --continuous --max-calls 100")
        with experiment_lock(root):
            if continuous is not None:
                from .runtime_control import validate_runtime
                validate_runtime(root)
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
