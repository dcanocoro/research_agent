"""Architecture and compatibility checks with no provider or database access."""

import ast
import asyncio
import hashlib
import json
from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import pytest

import research_agent.core as runtime
from research_agent.experiments.store import prepare_experiment
from research_agent.core import execution
from support.continuous import make, text, execute


def test_basic_managed_run_does_not_load_experimental_implementations(tmp_path):
    script = r"""
import asyncio, importlib.abc, sys
from pathlib import Path
class BlockExperiments(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(('research_agent.extensions.progress', 'research_agent.extensions.knowledge_agent', 'research_agent.extensions.context_note', 'research_agent.regimes.continuous', 'research_agent.capabilities.python', 'research_agent.capabilities.simulation')):
            raise AssertionError('Unexpected optional implementation: ' + fullname)
sys.meta_path.insert(0, BlockExperiments())
from research_agent.agent import AgentA
from research_agent.contracts import AgentRequest
from research_agent.experiments.store import prepare_experiment
from research_agent.capabilities.state.files import register_files
from research_agent.observability.recording import RunRecorder
from research_agent.core.tools import ToolRegistry
from research_agent.storage.workspace import Workspace
from runtime_contracts.llm import AssistantResponse, ResponseTurn
class Client:
    async def respond(self, **kwargs):
        return ResponseTurn([AssistantResponse('respuesta')], 'respuesta', None)
root = Path(sys.argv[1])
prompts = prepare_experiment(root, new=True)
recorder = RunRecorder(root / 'ejecuciones', experiment=root)
space = Workspace(root / 'estado')
registry = ToolRegistry(recorder)
register_files(registry, space)
agent = AgentA(Client(), registry, space, recorder)
result = asyncio.run(agent.run(AgentRequest('Consulta breve', 'state', 'conversation', prompts)))
assert result.status == 'completed' and result.answer == 'respuesta'
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path / "basic")], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_all_three_routes_enter_the_same_engine(tmp_path, monkeypatch):
    from support.knowledge import service, writer, finish, payload

    seen = []
    original = execution.execute

    async def tracked(policy):
        seen.append(type(policy).__name__)
        return await original(policy)

    monkeypatch.setattr(execution, "execute", tracked)
    bounded, request = make(tmp_path / "bounded", [text("respuesta")])
    assert execute(bounded, replace(request, continuous=None, mandate=None)).answer == "respuesta"
    continuous, request = make(
        tmp_path / "continuous", [text("avance")], config=replace(request.continuous, max_llm_calls=1)
    )
    assert execute(continuous, request).stop_reason == "call_limit"
    parent, child_request, _ = service(tmp_path / "child", [writer(), finish()])
    asyncio.run(parent.knowledge.register(**payload()))
    assert parent.knowledge.store.get("advance1")["status"] == "integrated"
    assert seen == ["BoundedPolicy", "ContinuousPolicy", "IntegrationPolicy"]

    def no_recovery(*args, **kwargs):
        raise AssertionError("Invalid B configuration reached transaction recovery")

    monkeypatch.setattr("research_agent.storage.transactions.recover", no_recovery)
    with pytest.raises(ValueError, match="100 total"):
        execute(parent, replace(child_request, continuous=None))


def test_only_shared_engine_calls_models_and_dispatches_tools():
    package = Path(runtime.__file__).parents[1]
    model_owners, tool_owners = [], []
    for path in package.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == "respond":
                    model_owners.append(path.relative_to(package).as_posix())
                if (
                    node.func.attr == "execute"
                    and isinstance(node.func.value, ast.Attribute)
                    and node.func.value.attr == "tools"
                ):
                    tool_owners.append(path.relative_to(package).as_posix())
    assert model_owners == ["core/execution.py"]
    assert tool_owners == ["core/execution.py"]
    for name in (
        "regimes/bounded/policy.py",
        "regimes/continuous/policy.py",
        "extensions/knowledge_agent/policy.py",
    ):
        tree = ast.parse((package / name).read_text(encoding="utf-8"))
        assert not any(isinstance(node, (ast.While, ast.AsyncFor)) for node in ast.walk(tree)), name


def test_frozen_e2_record_retains_pre_refactor_bytes(tmp_path):
    root = tmp_path / "experiment"
    prepare_experiment(root, new=True)
    # Captured from the original runtime identity at 73794df, not recomputed from
    # the new resource. A move or reformat must not invalidate an existing run.
    assert (
        hashlib.sha256((root / "runtime.json").read_bytes()).hexdigest()
        == "741e00e75db8a52c3160b416e44f6fd3c491d17e18f7961e20bbaaf4ad6716a8"
    )


def test_cancellation_finishes_model_event_before_session_cleanup(tmp_path):
    class CancelClient:
        async def respond(self, **kwargs):
            raise asyncio.CancelledError()

    agent, request = make(tmp_path, [])
    agent.client = CancelClient()
    try:
        execute(agent, request)
    except asyncio.CancelledError:
        pass
    else:
        raise AssertionError("Cancellation must propagate")
    names = [event["event"] for event in agent.recorder.events]
    assert (
        names.index("lab.model.started")
        < names.index("lab.model.finished")
        < names.index("lab.continuous.paused")
    )
    record = json.loads((agent.recorder.current / "resultado.json").read_bytes())
    assert record["status"] == "cancelled" and record["llm_calls"] == 1


def test_effective_composition_is_recorded_without_changing_legacy_fields(tmp_path):
    agent, request = make(tmp_path, [text()])
    request = replace(request, continuous=replace(request.continuous, max_llm_calls=1))
    execute(agent, request)
    manifest = json.loads((agent.recorder.current / "manifiesto.json").read_bytes())
    assert manifest["extensions"] == {
        "regime": "continuous-e2",
        "progress": "general-review",
        "multiagent": "off",
    }
    assert manifest["runtime_control"]["policy"]["version"] == "interventions-e2-v1"
    assert manifest["review_policy"]["evaluation_backstop"] == 20


def test_dependency_boundaries_and_removed_implementations():
    package = Path(runtime.__file__).parents[1]
    forbidden_core = ("research_agent.regimes", "research_agent.extensions", "research_campaigns", "findata", "infra", "finmate", "engine", "api")
    legacy = {"research_agent.continuous", "research_agent.knowledge", "research_agent.objectives", "research_agent.objective_review", "research_agent.external_review", "research_agent.runtime_control", "research_agent.runtime", "research_agent.integrations", "research_agent.bootstrap", "research_agent.experiment_store", "research_agent.state_configuration", "research_agent.continuity", "research_agent.context_management"}
    for path in package.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = ([node.module or ""] if isinstance(node, ast.ImportFrom) else
                     [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
            for name in names:
                assert not any(name == old or name.startswith(old + ".") for old in legacy), (path, name)
                assert not name.startswith(("research_campaigns", "experience_audit")), (path, name)
                if path.is_relative_to(package / "core"):
                    assert not name.startswith(forbidden_core), (path, name)
                if path.is_relative_to(package / "regimes/continuous"):
                    assert not name.startswith("research_agent.extensions.progress"), (path, name)
        assert not any(isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in
                       {"EvaluationState", "parse_evaluation", "evaluate_objective", "progress_components"} for node in ast.walk(tree)), path
    for name in ["continuous.py", "knowledge.py", "objectives.py", "objective_review.py", "external_review.py", "runtime_control.py"]:
        assert not (package / name).exists()


def test_continuous_without_progress_does_not_import_progress_or_note(tmp_path):
    script = """
import asyncio, importlib.abc, sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'tests'))
class BlockOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(('research_agent.extensions.progress', 'research_agent.extensions.context_note')):
            raise AssertionError(fullname)
sys.meta_path.insert(0, BlockOptional())
from support.continuous import make, text, execute
from research_agent.contracts import ContinuousConfig
a, req = make(Path(sys.argv[1]), [text()], config=ContinuousConfig(max_llm_calls=1, general_review=False))
result = execute(a, req)
assert result.llm_calls == 1 and result.answer
"""
    result = subprocess.run([sys.executable, "-c", script, str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
