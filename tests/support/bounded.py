import asyncio
import json
import subprocess
import sys
from pathlib import Path
import pytest
from runtime_contracts.llm import AssistantResponse, ResponseTurn, ResponseFunctionCall, ProviderContinuation, ToolResult
from research_agent.agent import AgentA
from research_agent.contracts import AgentRequest
from research_agent.contracts import AgentLimits
from research_agent.observability.recording import RunRecorder
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace
from research_agent.capabilities.state.files import register_files
from support import ScriptedClient, save_arguments

def response(text="done", call=None, provider=None):
    continuation = ProviderContinuation(provider, "test", {"opaque": [1, 2]}) if provider else None
    item = ResponseFunctionCall("call", call[0], call[1], continuation) if call else AssistantResponse(text, continuation)
    return ResponseTurn([item], text if not call else "", item if call else None)


def agent(tmp_path, turns, limits=None):
    recorder = RunRecorder(tmp_path / "runs")
    registry = ToolRegistry(recorder)
    space = Workspace(tmp_path / "workspace")
    register_files(registry, space)
    return AgentA(ScriptedClient(turns), registry, space, recorder, limits or AgentLimits())


def request(message="Investigate", conversation="test"):
    return AgentRequest(message, "space", conversation)

