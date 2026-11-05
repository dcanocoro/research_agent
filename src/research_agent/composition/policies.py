from typing import Any
from research_agent.agent import AgentA
from research_agent.contracts import AgentRequest
from research_agent.core.execution import Policy

def validate_execution(agent: AgentA, request: AgentRequest) -> None:
    """Reject unsupported combinations before recovery or run preparation."""
    if request.progress and (agent.knowledge is not None or agent.role != "A"):
        raise ValueError("Progress cannot be combined with the knowledge agent yet.")
    if agent.knowledge is not None:
        agent.knowledge.validate_request(request)


def compose_policy(agent: AgentA, request: AgentRequest) -> Policy:
    """The only selector of concrete execution policies; no implicit variants."""
    validate_execution(agent, request)
    if request.progress:
        from research_agent.extensions.progress.policy import ProgressPolicy
        return ProgressPolicy(agent, request)
    if agent.role == "B":
        from research_agent.extensions.knowledge_agent.policy import IntegrationPolicy
        return IntegrationPolicy(agent, request)
    if request.continuous is not None:
        from research_agent.regimes.continuous.policy import ContinuousPolicy
        return ContinuousPolicy(agent, request)
    from research_agent.regimes.bounded.policy import BoundedPolicy
    return BoundedPolicy(agent, request)
