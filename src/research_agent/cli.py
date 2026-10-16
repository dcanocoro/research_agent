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
    args = parser.parse_args(argv)

    async def execute() -> AgentResult:
        async with build_agent(args.workspace, args.runs, AgentLimits(timeout_seconds=args.timeout_seconds)) as agent:
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
