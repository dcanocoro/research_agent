from support import save_turn, save_arguments, save_current
import asyncio
import json
from dataclasses import replace
import pytest
from support import review_turn
from runtime_contracts.llm import (AssistantResponse, ConversationContext, ConversationMessage,
    ProviderContinuation, ResponseFunctionCall, ResponseTurn, ToolResult)
from research_agent.agent import AgentA
from research_agent.core.context_budget import ByteCounter
from research_agent.contracts import AgentLimits
from research_agent.contracts import AgentRequest
from research_agent.contracts import ContinuousConfig
from research_agent.capabilities.state.files import register_files
from research_agent.observability.recording import RunRecorder
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace
from support import ScriptedClient

def text(value="avance"):
    return ResponseTurn([AssistantResponse(value)], value, None)


def call(name, **arguments):
    item = ResponseFunctionCall("call", name, arguments)
    return ResponseTurn([item], "", item)


def make(tmp_path, turns, *, config=None, profile=None):
    space = Workspace(tmp_path / "estado")
    space.write_file("agenda.md", "Investigar la pregunta pendiente.")
    recorder = RunRecorder(tmp_path / "ejecuciones")
    registry = ToolRegistry(recorder)
    register_files(registry, space)
    agent = AgentA(ScriptedClient(turns), registry, space, recorder, AgentLimits(),
                   configuration=profile or {"provider": "openai", "model": "gpt-4o", "max_output_tokens": 128})
    request = AgentRequest("Comparar alternativas conservando los fundamentos.", "state", "conversation",
                           mandate="Gestiona una cartera ficticia sin apalancamiento.",
                           continuous=config or ContinuousConfig(max_llm_calls=3))
    return agent, request


def execute(agent, request):
    return asyncio.run(agent.run(request))


def events(agent, name):
    return [e for e in agent.recorder.events if e["event"] == name]

