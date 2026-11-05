from typing import Any
from research_agent.contracts import AgentRequest

def effective_extensions(agent: Any, request: AgentRequest) -> dict[str, str]:
    return {
        "regime": (
            "knowledge-integration"
            if agent.role == "B"
            else "continuous-e2" if request.continuous else "bounded"
        ),
        "progress": (
            "commitments-v1" if request.progress else "general-review" if request.continuous and request.continuous.general_review else "off"
        ),
        "multiagent": "prepared" if agent.role == "B" or agent.knowledge is not None else "off",
    }


def objective_policy(request: AgentRequest) -> dict[str, Any] | None:
    if not request.progress:
        return None
    return {"version": "commitments-v1", "step_calls": request.progress_step_calls,
            "evaluations_in_total_budget": True, "numeric_completion": False}


def closing_metadata(agent: Any, request: AgentRequest) -> dict[str, Any] | None:
    if agent.role == "B":
        from research_agent.extensions.knowledge_agent.policy import closing_metadata as integration_metadata

        return integration_metadata(agent.limits)
    return (
        {
            "consolidation_calls": 2,
            "response_calls": 1,
            "consolidation_seconds_at_time_threshold": agent.limits.finalization_seconds / 3,
            "response_seconds": agent.limits.finalization_seconds * 2 / 3,
            "context_reserve_bytes": min(32768, agent.limits.max_context_bytes // 4),
            "consolidation_tools": sorted(agent.tools.consolidation_tools or ()),
        }
        if agent.role == "A"
        and request.continuous is None
        and (agent.limits.max_llm_calls >= 4)
        and (agent.limits.max_tool_calls >= 2)
        else None
    )
