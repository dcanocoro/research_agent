from dataclasses import dataclass
from typing import Literal
import math


@dataclass(frozen=True)
class CommunicationConfig:
    mode: Literal["off", "hook", "communicator"] = "off"
    max_calls: int = 20
    timeout_seconds: float = 30

    def __post_init__(self) -> None:
        if self.mode not in {"off", "hook", "communicator"}:
            raise ValueError("Unknown communication mode")
        if type(self.max_calls) is not int or self.max_calls < 1:
            raise ValueError("communication max_calls must be positive")
        if (isinstance(self.timeout_seconds, bool) or not isinstance(self.timeout_seconds, (int, float))
                or not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0):
            raise ValueError("communication timeout_seconds must be finite and positive")
        if self.mode != "communicator" and (self.max_calls != 20 or self.timeout_seconds != 30):
            raise ValueError("Communication budgets require communicator mode")
