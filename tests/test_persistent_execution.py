"""Behavioral tests of bounded persistence closing, without remote services."""
import asyncio
import json
from pathlib import Path
from uuid import uuid4

import pytest

from research_agent.agent import AgentA
from research_agent.cases import CaseStore
from research_agent.contracts import AgentLimits, AgentRequest
from research_agent.integrations.case_tools import register_cases
from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from runtime_contracts.llm import AssistantResponse, ConversationContext, ResponseFunctionCall, ResponseTurn


def call(name, **arguments):
    item = ResponseFunctionCall(str(uuid4()), name, arguments)
    return ResponseTurn([item], "", item)


def text(value="Delivered"):
    return ResponseTurn([AssistantResponse(value)], value, None)


def budget(request):
    return next(i.payload["execution_budget"] for i in reversed(request["input_items"])
                if isinstance(i, ConversationContext) and "execution_budget" in i.payload)


def fixture(root, behavior, limits=None):
    recorder = RunRecorder(root / "runs")
    workspace = Workspace(root / "workspace")
    store = CaseStore(root / "cases", workspace.root, recorder)
    registry = ToolRegistry(recorder)
    register_files(registry, workspace)
    register_cases(registry, store)
    registry.register("search_web", "Test research source", {}, lambda: {"source": "fixed"})

    class Client:
        requests = None

        def __init__(self):
            self.requests = []

        async def respond(self, **kwargs):
            self.requests.append(kwargs)
            return behavior(agent, store, kwargs, len(self.requests))

    agent = AgentA(Client(), registry, workspace, recorder,
                   limits or AgentLimits(max_llm_calls=6, max_tool_calls=10))
    return agent, store


def save_call(store, previous=None, expected=None):
    reference = store.recorder.artifact({"revenue": 100, "period": "FY2026", "currency": "USD"})
    case = previous["case"] if previous else None
    return call("save_case", case_id=case["case_id"] if case else None, asset="NVDA", question="Investiga NVIDIA",
                content="# Provisional\nDemand is uncertain; investigate customer concentration.", references=[reference],
                expected_revision=expected if expected else case["current_revision"] if case else None,
                change="Preserve current foundations and pending work")


def run(agent):
    return asyncio.run(agent.run(AgentRequest("Investiga NVIDIA", "workspace", "chat")))


def test_call_reserve_publishes_before_answer_and_budget_is_recorded(tmp_path):
    def behavior(agent, store, req, number):
        phase = budget(req)["phase"]
        if phase == "research":
            return call("search_web")
        if phase == "consolidation":
            return save_call(store)
        assert req["tools"] == [] and req["allow_tools"] is False
        return text()

    agent, store = fixture(tmp_path, behavior)
    result = run(agent)
    assert result.status == "completed" and result.persistence.status == "confirmed"
    assert result.persistence.response_delivered is True
    assert result.llm_calls == 5 and result.tool_calls == 4
    phases = [budget(r)["phase"] for r in agent.client.requests]
    assert phases == ["research"] * 3 + ["consolidation", "response"]
    assert [budget(r)["llm_calls_available"] for r in agent.client.requests] == [6, 5, 4, 3, 2]
    transcript = json.loads((agent.recorder.current / "transcript.json").read_bytes())
    assert sum("execution_budget" in i.get("payload", {}) for i in transcript) == 5
    assert store.publications(result.run_id) == list(result.persistence.revisions)
    assert json.loads((agent.recorder.current / "result.json").read_bytes())["persistence"]["status"] == "confirmed"


def test_consolidation_dispatch_rejects_hidden_research_and_preserves_retry(tmp_path):
    research_executions = []

    def behavior(agent, store, req, number):
        phase = budget(req)["phase"]
        names = {s.name for s in req["tools"]}
        if phase == "research":
            return call("search_web")
        if phase == "consolidation":
            assert "search_web" not in names and "save_case" in names
            return call("search_web") if number == 4 else save_call(store)
        return text()

    agent, store = fixture(tmp_path, behavior)
    spec, _ = agent.tools._tools["search_web"]
    agent.tools._tools["search_web"] = (spec, lambda: research_executions.append(1))
    result = run(agent)
    assert len(research_executions) == 3  # Disallowed fourth call never executes.
    assert result.llm_calls == 6 and result.persistence.status == "confirmed"
    assert any(e["event"] == "lab.tool.failed" and e["tool_name"] == "search_web" for e in agent.recorder.events)


def test_early_answer_is_a_draft_until_consolidation_saves(tmp_path):
    def behavior(agent, store, req, number):
        return text("Provisional draft") if number == 1 else save_call(store) if number == 2 else text("Final after saving")

    agent, _ = fixture(tmp_path, behavior)
    result = run(agent)
    assert result.answer == "Final after saving" and result.persistence.status == "confirmed"
    drafts = [r for r in result.artifact_refs if r.startswith("drafts/")]
    assert len(drafts) == 1
    assert json.loads((agent.recorder.current / drafts[0]).read_bytes())["text"] == "Provisional draft"
    assert [budget(r)["phase"] for r in agent.client.requests] == ["research", "consolidation", "response"]


def test_early_answer_after_publication_can_finish_without_extra_calls(tmp_path):
    agent, _ = fixture(tmp_path, lambda a, s, r, n: save_call(s) if n == 1 else text())
    result = run(agent)
    assert result.llm_calls == 2 and result.stop_reason == "answered"
    assert result.persistence.status == "confirmed"


def test_model_claim_without_publication_is_unconfirmed_and_bounded(tmp_path):
    agent, _ = fixture(tmp_path, lambda *args: text("I saved everything"))
    result = run(agent)
    assert result.answer == "I saved everything"
    assert result.persistence.status == "unconfirmed"
    assert result.persistence.revisions == ()
    assert result.llm_calls == 4  # Draft, two consolidation opportunities, final answer.


def test_consolidation_can_correct_a_revision_conflict(tmp_path):
    previous = None

    def behavior(agent, store, req, number):
        nonlocal previous
        if number == 1:
            return save_call(store)
        previous = store.read_case(store.list_cases("NVDA")["cases"][0]["case_id"])
        if number == 2:
            return call("search_web")
        if number == 3:
            return save_call(store, previous, str(uuid4()))
        if number == 4:
            return save_call(store, previous)
        return text()

    agent, store = fixture(tmp_path, behavior, AgentLimits(max_llm_calls=5))
    result = run(agent)
    assert result.persistence.status == "confirmed" and len(result.persistence.revisions) == 2
    assert len(store.list_case_revisions(previous["case"]["case_id"])["revisions"]) == 2
    assert result.llm_calls == 5


def test_time_reserve_allows_writes_inside_last_45_seconds(tmp_path, monkeypatch):
    clock = [0.0]
    monkeypatch.setattr("research_agent.agent.monotonic", lambda: clock[0])

    def behavior(agent, store, req, number):
        if number == 1:
            return call("search_web")
        if number == 2:
            assert budget(req)["phase"] == "consolidation"
            assert req["timeout"] == pytest.approx(14)  # 44 seconds left; preserve 30 for response.
            return save_call(store)
        assert budget(req)["phase"] == "response"
        return text()

    agent, _ = fixture(tmp_path, behavior)
    spec, _ = agent.tools._tools["search_web"]

    def research():
        clock[0] = 256.0
        return {"source": "fixed"}

    agent.tools._tools["search_web"] = (spec, research)
    result = run(agent)
    assert result.persistence.status == "confirmed"
    assert result.llm_calls == 3


def test_tool_budget_reserves_two_persistence_opportunities(tmp_path):
    agent, _ = fixture(tmp_path, lambda a, s, r, n: call("search_web") if n == 1 else
                       save_call(s) if budget(r)["phase"] == "consolidation" else text(),
                       AgentLimits(max_tool_calls=3))
    result = run(agent)
    assert [budget(r)["phase"] for r in agent.client.requests] == ["research", "consolidation", "response"]
    assert result.persistence.status == "confirmed" and result.tool_calls == 2


def test_early_consolidation_uses_available_time_while_reserving_response(tmp_path, monkeypatch):
    monkeypatch.setattr("research_agent.agent.monotonic", lambda: 0.0)

    def behavior(agent, store, req, number):
        if number == 1:
            return text("Draft")
        if number == 2:
            assert budget(req)["phase"] == "consolidation"
            assert req["timeout"] == pytest.approx(270)  # Not a fixed 15-second cap.
            return save_call(store)
        return text()

    agent, _ = fixture(tmp_path, behavior)
    result = run(agent)
    assert result.persistence.status == "confirmed" and result.llm_calls == 3


def test_context_reserve_enters_consolidation_without_silent_trimming(tmp_path):
    agent, _ = fixture(tmp_path, lambda a, s, r, n: save_call(s) if budget(r)["phase"] == "consolidation" else text())
    from runtime_contracts.llm import ConversationMessage
    agent.history.append(ConversationMessage("user", "X" * 232000))
    result = run(agent)
    assert budget(agent.client.requests[0])["phase"] == "consolidation"
    assert result.persistence.status == "confirmed"
    assert "X" * 232000 in (agent.recorder.current / "transcript.json").read_text()


def test_phase_timeout_retains_opportunity_to_save(tmp_path):
    def behavior(agent, store, req, number):
        if number == 1:
            raise TimeoutError()
        return save_call(store) if number == 2 else text()

    agent, _ = fixture(tmp_path, behavior)
    result = run(agent)
    assert result.persistence.status == "confirmed" and result.answer == "Delivered"
    assert any(e["event"] == "lab.phase.timeout" for e in agent.recorder.events)


def test_truncated_delivery_preserves_verified_revision(tmp_path):
    from infra.llm_errors import LLMTruncated

    def behavior(agent, store, req, number):
        if number == 1:
            return save_call(store)
        raise LLMTruncated("response_truncated", provider="openai")

    agent, store = fixture(tmp_path, behavior)
    result = run(agent)
    assert result.status == "failed" and result.error == "LLMTruncated"
    assert result.persistence.status == "confirmed" and result.persistence.response_delivered is False
    assert store.read_case(result.persistence.revisions[0]["case_id"])["content"].startswith("# Provisional")


def test_verification_failure_is_not_reported_as_no_writes(tmp_path):
    def behavior(agent, store, req, number):
        if number == 1:
            return save_call(store)
        for path in store.root.glob("*/revisions/*.md"):
            path.write_text("Tampered", encoding="utf-8")
        return text()

    agent, _ = fixture(tmp_path, behavior)
    result = run(agent)
    assert result.persistence.status == "verification_failed"
    assert result.persistence.error == "ValueError"


@pytest.mark.parametrize("limits", [AgentLimits(max_llm_calls=3), AgentLimits(max_tool_calls=1)])
def test_persistent_mode_rejects_budgets_without_a_closing_reserve(tmp_path, limits):
    with pytest.raises(ValueError, match="at least four"):
        fixture(tmp_path, lambda *args: text(), limits)
