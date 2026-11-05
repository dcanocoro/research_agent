"""Public request adapter; runtime values remain experiment-independent."""

from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from pathlib import Path
from research_agent.core.contracts import AgentLimits
from research_agent.core.contracts import ContinuousConfig
from research_agent.core.contracts import StateSummary
from research_agent.core.contracts import AgentResult
from research_agent.core.contracts import serializable

if TYPE_CHECKING:
    from research_agent.extensions.progress.objective import Objective


@dataclass(frozen=True)
class AgentRequest:
    message: str
    workspace_id: str
    conversation_id: str
    instructions: tuple[Path, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    mandate: str | None = None
    continuous: ContinuousConfig | None = None
    objective: Objective | None = None
    progress: bool = False
    progress_step_calls: int = 15

    def __post_init__(self) -> None:
        if type(self.progress_step_calls) is not int or self.progress_step_calls < 1:
            raise ValueError("progress_step_calls must be a positive integer.")
        if self.objective is None:
            return
        from research_agent.extensions.progress.objective import Objective

        if not isinstance(self.objective, Objective):
            raise ValueError("An objective requires an Objective value.")
        object.__setattr__(self, "progress", True)
