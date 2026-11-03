"""Shared accounting for local sessions and their aggregate parent budget."""

from dataclasses import dataclass, field
from time import monotonic
from collections.abc import Callable


@dataclass
class CallBudget:
    max_llm_calls: int | None
    max_tool_calls: int | None
    deadline: float | None
    llm_calls: int = 0
    tool_calls: int = 0
    clock: Callable[[], float] = field(default=monotonic, repr=False)

    def charge_model(self) -> None:
        if self.max_llm_calls is not None and self.llm_calls >= self.max_llm_calls:
            raise RuntimeError("LLM budget exhausted")
        self.llm_calls += 1

    def charge_tool(self) -> None:
        if self.max_tool_calls is not None and self.tool_calls >= self.max_tool_calls:
            raise RuntimeError("Tool budget exhausted")
        self.tool_calls += 1

    def operation_timeout(self, requested: float) -> float:
        remaining = self.deadline - self.clock() if self.deadline is not None else requested
        return max(0, min(requested, remaining))
