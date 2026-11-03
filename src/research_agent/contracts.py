"""Public request adapter; runtime values remain experiment-independent."""

from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass, field
from pathlib import Path
from .runtime.contracts import AgentLimits, ContinuousConfig, StateSummary, AgentResult, serializable

if TYPE_CHECKING:
    from .objectives import Objective


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

    def __post_init__(self) -> None:
        if self.objective is None:
            return
        from .objectives import Objective

        if not isinstance(self.objective, Objective) or self.continuous is None:
            raise ValueError("An objective requires continuous mode and an Objective value.")
