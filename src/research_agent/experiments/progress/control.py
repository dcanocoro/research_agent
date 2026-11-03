"""Existing E2 evaluation and reconciliation decisions."""

from __future__ import annotations
from typing import Any
from ...workspace import Workspace


def evaluation_policy(
    state: Any,
    workspace: Workspace,
    assessment_path: str | None,
    *,
    configuration: dict[str, Any],
    intervention: Any,
):

    if assessment_path:
        try:
            sha = workspace.read_version(assessment_path)[1]
        except FileNotFoundError:
            sha = None
        if sha != state.assessment_sha:
            state.assessment_sha = sha
            state.evaluation_requested = True
    elapsed = state.researcher_calls - state.last_evaluation_call
    if elapsed >= configuration["evaluation_backstop"] or (
        state.evaluation_requested and elapsed >= configuration["evaluation_spacing"]
    ):
        return [intervention("evaluate", "event" if state.evaluation_requested else "backstop")]
    return []


def reconciliation_policy(
    state: Any,
    workspace: Workspace,
    assessment_path: str | None,
    *,
    configuration: dict[str, Any],
    intervention: Any,
):

    state.refresh(workspace)
    proposals = []
    pending = state.view()
    if pending["pending_count"]:
        proposals.append(intervention("notice", "pending_integration", pending))
    for path, version in state.evaluated_versions.items():
        try:
            current = workspace.read_version(path)[1]
        except (OSError, ValueError):
            current = "missing"
        if current != version:
            proposals.append(
                intervention(
                    "notice",
                    "review_outdated",
                    {
                        "path": path,
                        "reviewed_sha256": version,
                        "current_sha256": current,
                        "note": "La revisión corresponde a una versión anterior; valora su impacto.",
                    },
                )
            )
    if state.feedback:
        proposals.append(intervention("notice", "evaluation_feedback", state.feedback))
    return proposals
