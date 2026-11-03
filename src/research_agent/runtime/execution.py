"""One interaction engine for bounded, renewable and delegated sessions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any, Protocol
from collections.abc import Callable, Awaitable

from runtime_contracts.llm import ResponseTurn, ToolResult
from runtime_contracts.execution import bind_run_context
from observability_context import bind_interaction_context
from .contracts import AgentResult
from .limits import CallBudget


@dataclass
class ModelCall:
    system: str
    items: list[Any]
    tools: list[Any]
    timeout: float
    allow_tools: bool = True
    options: dict[str, Any] = field(default_factory=dict)
    budget: CallBudget | None = None


@dataclass
class ToolCall:
    call: Any
    timeout: float
    allowed: frozenset[str] | None = None
    budget: CallBudget | None = None


@dataclass
class Renewal:
    apply: Callable[[], None]


@dataclass
class Action:
    """An isolated policy operation, such as a review, under the same engine."""

    apply: Callable[[], Awaitable[None]]


class Policy(Protocol):
    agent: Any
    context: Any
    interaction: Any

    async def prepare(self) -> None: ...
    async def next_step(self) -> ModelCall | ToolCall | Renewal | Action | None: ...
    async def receive(self, value: ResponseTurn | ToolResult | BaseException) -> None: ...
    async def finalize(self, error: BaseException | None) -> AgentResult: ...


async def interact(client: Any, step: ModelCall) -> ResponseTurn:
    """All managed model calls, including isolated reviews, use this transport."""
    timeout = step.budget.operation_timeout(step.timeout) if step.budget else step.timeout
    async with asyncio.timeout(timeout):
        return await client.respond(
            system=step.system,
            input_items=step.items,
            tools=step.tools,
            allow_tools=step.allow_tools,
            timeout=timeout,
            **step.options,
        )


async def execute(policy: Policy) -> AgentResult:
    """Own the only ReAct loop and always finalize under the session bindings."""
    error: BaseException | None = None
    with bind_run_context(policy.context), bind_interaction_context(policy.interaction):
        try:
            await policy.prepare()
            while (step := await policy.next_step()) is not None:
                if isinstance(step, Action):
                    await step.apply()
                    continue
                if isinstance(step, Renewal):
                    step.apply()
                    continue
                try:
                    if isinstance(step, ModelCall):
                        value = await interact(policy.agent.client, step)
                    else:
                        timeout = step.budget.operation_timeout(step.timeout) if step.budget else step.timeout
                        async with asyncio.timeout(timeout):
                            value = await policy.agent.tools.execute(step.call, allowed_names=step.allowed)
                except BaseException as exc:
                    await policy.receive(exc)
                else:
                    await policy.receive(value)
        except BaseException as exc:
            error = exc
        result = await policy.finalize(error)
        if error is not None and not isinstance(error, Exception):
            raise error
        return result
