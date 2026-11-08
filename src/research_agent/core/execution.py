"""One interaction engine for bounded, renewable and delegated sessions."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field, replace
from typing import Any, Protocol
from collections.abc import Callable, Awaitable

from runtime_contracts.llm import ResponseTurn, ToolResult
from runtime_contracts.execution import bind_run_context
from observability_context import bind_interaction_context
from research_agent.core.contracts import AgentResult
from research_agent.core.limits import CallBudget


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
    recovery_pending = False
    recoveries = 0
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
                        if recovery_pending:
                            step = replace(step, system=step.system + "\nRuntime recovery: the previous model response was truncated and discarded; "
                                           "no tool from that response was executed. Generate a fresh, smaller response. "
                                           "For writes, preserve one small coherent advance per call; do not repeat long hashes or text. "
                                           "For structured reports, use concise reasons and references from the current input only.")
                        value = await interact(policy.agent.client, step)
                    else:
                        timeout = step.budget.operation_timeout(step.timeout) if step.budget else step.timeout
                        async with asyncio.timeout(timeout):
                            value = await policy.agent.tools.execute(step.call, allowed_names=step.allowed)
                except BaseException as exc:
                    # A provider exception has not yielded a ResponseTurn: no tool can
                    # have been dispatched by this engine. Never retry a ToolCall.
                    if isinstance(step, ModelCall) and isinstance(exc, getattr(policy.agent, "truncated_response_errors", ())):
                        retry = not recovery_pending and recoveries < 3
                        policy.agent.recorder.event("lab.model.truncated", error_type=type(exc).__name__,
                                                    recovery_scheduled=retry, recoveries_used=recoveries)
                        if retry:
                            recoveries += 1
                            recovery_pending = True
                            # Ask the policy for a fresh call: it charges resources and
                            # checks deadlines/context/reserves just like any other call.
                            continue
                    await policy.receive(exc)
                else:
                    if isinstance(step, ModelCall):
                        recovery_pending = False
                    await policy.receive(value)
        except BaseException as exc:
            error = exc
        result = await policy.finalize(error)
        if error is not None and not isinstance(error, Exception):
            raise error
        return result
