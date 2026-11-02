"""Technical E2 reconstruction using complete exchanges, with no LLM calls."""
from __future__ import annotations

from typing import Any, Callable
from .context_budget import ContextConfigurationError


def reconstruct(seed: list[Any], exchanges: list[list[Any]], measure: Callable[[list[Any]], dict[str, int]],
                threshold: int, maximum: int, headroom: int = 16384) -> tuple[list[Any], list[list[Any]]]:
    if measure(seed)["budgeted_bytes"] >= threshold:
        raise ContextConfigurationError("protected_context_too_large")
    target = max(measure(seed)["budgeted_bytes"] + 1, threshold - headroom)
    retained: list[list[Any]] = []
    for exchange in reversed(exchanges):
        candidate = [*seed, *(item for group in [exchange, *retained] for item in group)]
        if measure(candidate)["budgeted_bytes"] >= target:
            break
        retained.insert(0, exchange)
    # The most recent action/result is indispensable. Do not slice provider continuations.
    if exchanges and not retained:
        candidate = [*seed, *exchanges[-1]]
        if measure(candidate)["budgeted_bytes"] > maximum:
            raise ContextConfigurationError("context_exchange_too_large")
        retained = [exchanges[-1]]
    return [*seed, *(item for group in retained for item in group)], retained
