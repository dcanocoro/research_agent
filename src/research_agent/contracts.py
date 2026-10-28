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
class ContinuousConfig:
    max_context_bytes: int = 512 * 1024
    consolidation_threshold_bytes: int = 256 * 1024
    max_llm_calls: int | None = None  # Research + consolidation; periodic reviews are additional.
    max_tool_calls: int | None = None
    timeout_seconds: float | None = None

    def __post_init__(self) -> None:
        if not 0 < self.consolidation_threshold_bytes < self.max_context_bytes:
            raise ValueError("Continuous context threshold must be below the byte limit.")
        if any(v is not None and v < 1 for v in (self.max_llm_calls, self.max_tool_calls)):
            raise ValueError("Continuous call limits must be positive.")
        if self.timeout_seconds is not None and (not isfinite(self.timeout_seconds) or self.timeout_seconds <= 0):
            raise ValueError("Continuous timeout must be finite and positive.")


@dataclass(frozen=True)
class AgentRequest:
    message: str
    workspace_id: str
    conversation_id: str
    instructions: tuple[Path, ...] = ()
    metadata: dict[str, str] = field(default_factory=dict)
    mandate: str | None = None
    continuous: ContinuousConfig | None = None


@dataclass(frozen=True)
class StateSummary:
    files_written: tuple[str, ...] = ()
    materials: tuple[str, ...] = ()
    capture_errors: tuple[dict[str, str], ...] = ()


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
    state: StateSummary = field(default_factory=StateSummary)
    llm_calls_by_phase: dict[str, int] = field(default_factory=dict)


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
