"""Public agent facade. Composition selects policies; runtime owns execution."""

from __future__ import annotations
from typing import Any
from pathlib import Path
from runtime_contracts.llm import ConversationClient, ConversationItem
from research_agent.core.contracts import AgentLimits
from research_agent.core.contracts import AgentResult
from research_agent.contracts import AgentRequest
from research_agent.observability.recording import RunRecorder
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace


class AgentA:
    def __init__(
        self,
        client: ConversationClient,
        tools: ToolRegistry,
        workspace: Workspace,
        recorder: RunRecorder,
        limits: AgentLimits = AgentLimits(),
        configuration: dict[str, Any] | None = None,
        instructions: tuple[Path, ...] = (),
        *,
        role: str = "A",
    ) -> None:
        self.client, self.tools, self.workspace, self.recorder = (client, tools, workspace, recorder)
        self.limits, self.configuration = (limits, configuration or {})
        self.history: list[ConversationItem] = []
        self._conversation_id: str | None = None
        self.instructions = instructions
        self.role = role
        self.knowledge: Any = None
        self.journal_root = recorder.root
        self.deadline_override: float | None = None
        self.on_model_call: Any = None
        self.on_tool_call: Any = None
        self.run_id: str | None = None
        self.stop_requested = False

    async def run(self, request: AgentRequest) -> AgentResult:
        from research_agent.composition.policies import compose_policy
        from research_agent.composition.policies import validate_execution
        from research_agent.core.execution import execute
        from research_agent.storage.transactions import recover

        validate_execution(self, request)
        if self.recorder.experiment is not None:
            from research_agent.experiments.configuration import validate_state_configuration

            validate_state_configuration(self.recorder.experiment)
        recover(self.workspace, self.journal_root)
        return await execute(compose_policy(self, request))

    def _prepare(
        self,
        request: AgentRequest,
        run_id: str,
        interaction_id: str,
        persistent: dict[str, Any] | None = None,
    ) -> str:
        from research_agent.composition.instructions import prepare_run

        return prepare_run(self, request, run_id, interaction_id, persistent)

    def _finish(self, result: AgentResult, captured: list[dict[str, Any]]) -> AgentResult:
        from research_agent.core.lifecycle import finish_run

        return finish_run(self, result, captured)
