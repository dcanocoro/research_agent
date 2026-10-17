import argparse
import asyncio
from importlib.resources import files, as_file
from pathlib import Path
from .bootstrap import build_agent
from .contracts import AgentRequest, AgentLimits, AgentResult
from .tracing import capture_traces


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="research-agent", description="Agent A: Markdown memory and shared financial tools.")
    parser.add_argument("message")
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--conversation", default="cli")
    parser.add_argument("--instructions", type=Path, action="append", default=[])
    parser.add_argument("--timeout-seconds", type=float, default=300)
    parser.add_argument("--knowledge-mode", choices=("vanilla", "cases"), default="vanilla")
    parser.add_argument("--case-store", type=Path)
    args = parser.parse_args(argv)
    if (args.knowledge_mode == "cases") != (args.case_store is not None):
        parser.error("--knowledge-mode cases requires --case-store; vanilla must not specify --case-store.")
    if args.case_store is not None:
        from .cases import disjoint
        try:
            for path in (args.workspace, args.runs, Path(__file__).parent, *args.instructions):
                disjoint(args.case_store, path)
        except ValueError as exc:
            parser.error(str(exc))

    async def execute() -> AgentResult:
        async with build_agent(args.workspace, args.runs, AgentLimits(timeout_seconds=args.timeout_seconds),
                               case_store=args.case_store) as agent:
            with as_file(files("research_agent").joinpath("prompts/financial_research.md")) as prompt:
                with capture_traces(args.runs / "capture"):
                    return await agent.run(AgentRequest(args.message, args.workspace.name,
                        args.conversation, (prompt, *args.instructions)))
    try:
        result = asyncio.run(execute())
    except (ValueError, OSError) as exc:
        parser.exit(2, f"research-agent: {exc}\n")
    print(result.answer or f"{result.status}: {result.stop_reason}")
    print(f"run_id={result.run_id}")
    return 0 if result.status == "completed" else 1
