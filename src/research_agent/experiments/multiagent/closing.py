"""Existing prepared B closing policy, reusing the bounded session infrastructure."""

from __future__ import annotations
from time import monotonic
from typing import Any
from ...runtime.contracts import AgentLimits
from runtime_contracts.llm import ConversationMessage, ResponseTurn
from ...runtime.bounded import BoundedPolicy


class IntegrationPolicy(BoundedPolicy):
    component = "agent_b"

    def __init__(self, agent, request):
        super().__init__(agent, request)
        self.can_consolidate = False
        self.integration_response_seconds = min(15, self.agent.limits.finalization_seconds / 4)

    def select_phase(self) -> None:
        if self.phase == "research" and (
            self.calls >= self.agent.limits.max_llm_calls - 4
            or self.tool_calls >= self.agent.limits.max_tool_calls - 4
            or self.remaining <= self.agent.limits.finalization_seconds
            or (self.size >= self.agent.limits.max_context_bytes - 32768)
        ):
            self.phase = "integration_closing"
            self.agent.history.append(
                ConversationMessage(
                    "user",
                    "Runtime integration closing: stop expanding the task. Verify applied changes, publish one coherent batch if justified, then call finish_integration. Declare pending with explicit unresolved work when evidence is insufficient. A text response does not close the integration. Prioritize closure now; the final opportunity only accepts finish_integration.",
                )
            )
        final_declaration = (
            self.calls >= self.agent.limits.max_llm_calls - 1
            or self.tool_calls >= self.agent.limits.max_tool_calls - 1
            or self.remaining <= self.integration_response_seconds
        )
        self.closing = False
        self.allowed = frozenset({"finish_integration"}) if final_declaration else None
        self.call_deadline = (
            self.deadline - self.agent.limits.finalization_seconds
            if self.phase == "research"
            else self.deadline if final_declaration else self.deadline - self.integration_response_seconds
        )

    def phase_opportunities(self) -> int:
        return self.agent.limits.max_llm_calls - self.calls - (4 if self.phase == "research" else 0)

    def tool_seconds(self) -> float:
        return self.call_deadline - monotonic()

    def model_timeout(self) -> None:
        if self.call_deadline >= self.deadline:
            raise TimeoutError()
        self.phase = "integration_closing"
        self.agent.history.append(
            ConversationMessage(
                "user",
                "Ordinary integration time ended. Close now with finish_integration, preserving explicit pending work.",
            )
        )

    def text_response(self, turn: ResponseTurn) -> None:
        self.phase = "integration_closing"
        self.agent.history.append(
            ConversationMessage(
                "user",
                "Integration is still open. Use finish_integration to declare the verified result "
                "or explicit pending work; a text response is insufficient.",
            )
        )

    def tool_received(self) -> None:
        if self.agent.stop_requested:
            self.status, self.reason, self.done = "completed", "answered", True


def closing_metadata(limits: AgentLimits) -> dict[str, Any]:
    return {
        "integration_closing_calls": 4,
        "final_tool": "finish_integration",
        "reserved_seconds": limits.finalization_seconds,
        "final_declaration_seconds": min(15, limits.finalization_seconds / 4),
        "closing_tool_reserve": 4,
    }
