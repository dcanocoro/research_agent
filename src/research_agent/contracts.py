"""Small runtime values, independent of the financial specialization."""
from dataclasses import dataclass, field
from pathlib import Path
from math import isfinite
from typing import Any, Literal


@dataclass(frozen=True)
class AgentLimits:
    max_llm_calls: int = 18
    max_tool_calls: int = 30
    timeout_seconds: float = 300
    finalization_seconds: float = 45
    max_context_bytes: int = 256 * 1024

    def __post_init__(self) -> None:
        if (self.max_llm_calls < 1 or self.max_tool_calls < 0 or self.max_context_bytes < 1024
                or not all(isfinite(v) and v > 0 for v in (self.timeout_seconds, self.finalization_seconds))
                or self.finalization_seconds >= self.timeout_seconds):
            raise ValueError("Invalid agent limits.")


@dataclass(frozen=True)
class AgentRequest:
    message: str
    workspace_id: str
    conversation_id: str
    instructions: tuple[Path, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PersistenceResult:
    status: Literal["confirmed", "unconfirmed", "verification_failed"]
    revisions: tuple[dict[str, str], ...]
    response_delivered: bool
    error: str | None = None


@dataclass(frozen=True)
class AgentResult:
    run_id: str
    status: Literal["completed", "interrupted", "failed", "cancelled"]
    answer: str | None
    stop_reason: str
    artifact_refs: tuple[str, ...]
    llm_calls: int
    tool_calls: int
    error: str | None = None
    persistence: PersistenceResult | None = None


def serializable(value: Any) -> Any:
    from dataclasses import asdict, is_dataclass
    from runtime_contracts.json import json_safe
    if is_dataclass(value) and not isinstance(value, type):
        return serializable(asdict(value))
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serializable(v) for v in value]
    return json_safe(value)
