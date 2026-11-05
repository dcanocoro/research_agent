import asyncio
import hashlib
import json
from dataclasses import replace
import pytest
from research_agent.contracts import ContinuousConfig
from research_agent.extensions.knowledge_agent.delegation import attach
from research_agent.extensions.knowledge_agent.delegation import mode_for
from research_agent.extensions.knowledge_agent.delegation import TaskStore
from research_agent.experiments.store import prepare_experiment
from research_agent.regimes.continuous.control import RuntimeState
from research_agent.observability.recording import encoded
from support import ScriptedClient, save_arguments
from support.continuous import make, call, text, execute

def payload(task_id="advance1", **changes):
    return {"task_id": task_id, "finding": "La hipótesis requiere revisión", "interpretation": "Fundamento provisional",
            "unresolved": [], "evidence_refs": [], "affected_documents": [{"path": "nota.md", "section_id": None}],
            "scope": ["nota.md"], **changes}


def finish(status="integrated", path="nota.md", content="Avance", **changes):
    return call("finish_integration", **{"status": status, "reason": "Integración comprobada",
                "documents": [{"path": path, "sha256": hashlib.sha256(content.encode()).hexdigest()}],
                "evidence_refs": [], "unresolved": [], "pending_reason": "none", **changes})


def writer(path="nota.md", content="Avance"):
    return call("record_research_advance", **save_arguments(path=path, content=content))


def service(tmp_path, child_turns=(), mode="prepared"):
    agent, request = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=100, max_tool_calls=200))
    clients = []

    def factory():
        client = ScriptedClient(child_turns)
        clients.append(client)
        return client

    attach(agent, factory, mode)
    agent._prepare(request, "activation1", "interaction")
    state = RuntimeState()
    agent.knowledge.begin(request, state)
    agent.knowledge.available = lambda: {"calls": 100, "tools": 200, "seconds": None}
    return agent, request, clients

