"""Run-scoped resources for tools that make isolated, managed model calls."""
from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar
from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True)
class ToolRuntime:
    call_id: str
    deadline: float
    available: Callable[[], int | None]
    charge: Callable[[str], None]

    def require(self, calls: int = 1) -> None:
        remaining = self.available()
        if monotonic() >= self.deadline:
            raise TimeoutError("Tool deadline exhausted")
        if remaining is not None and remaining < calls:
            raise RuntimeError("Managed model budget exhausted")


current_tool_runtime: ContextVar[ToolRuntime | None] = ContextVar("tool_runtime", default=None)
