"""Provider truncations never dispatch tools; recovery uses normal policy budgets."""
from dataclasses import replace

import pytest
from infra.llm_errors import LLMTruncated
from support.continuous import make, execute, text
from support.bounded import response
from support import save_arguments
from research_agent.contracts import ContinuousConfig


@pytest.mark.parametrize("continuous", [False, True])
def test_truncation_recovers_without_duplicate_writes(tmp_path, continuous):
    a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=8, general_review=False))
    if not continuous:
        req = replace(req, continuous=None)
    class Client:
        calls = 0
        async def respond(self, **kwargs):
            self.calls += 1
            if self.calls == 1:
                raise LLMTruncated("max_output_tokens", provider="openai")
            if self.calls == 2:
                assert "Runtime recovery" in kwargs["system"]
                return response(call=("record_research_advance", save_arguments(path="result.md", content="Saved once")))
            return text("Done")
    a.client = Client()
    result = execute(a, req)
    assert a.workspace.read_file("result.md")["text"] == "Saved once"
    assert result.tool_calls == 1
    assert result.llm_calls >= 3
    events = [e for e in a.recorder.events if e["event"] == "lab.model.truncated"]
    assert len(events) == 1 and events[0]["recovery_scheduled"]


def test_repeated_truncation_stops_without_tools(tmp_path):
    a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=8, general_review=False))
    class Client:
        async def respond(self, **kwargs):
            raise LLMTruncated("max_output_tokens", provider="openai")
    a.client = Client()
    result = execute(a, req)
    assert result.status == "failed" and result.error == "LLMTruncated"
    assert result.llm_calls == 2 and result.tool_calls == 0
    assert [e["recovery_scheduled"] for e in a.recorder.events if e["event"] == "lab.model.truncated"] == [True, False]


def test_truncation_cannot_expand_call_budget(tmp_path):
    a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=1, general_review=False))
    class Client:
        async def respond(self, **kwargs):
            raise LLMTruncated("max_output_tokens", provider="openai")
    a.client = Client()
    result = execute(a, req)
    assert result.llm_calls == 1 and result.tool_calls == 0
    assert result.stop_reason == "call_limit"
