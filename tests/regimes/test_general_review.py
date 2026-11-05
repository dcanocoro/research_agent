"""Review selection changes model work, not persistence or total budgets."""
import asyncio
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import pytest
from runtime_contracts.llm import ConversationContext
from research_agent.cli.main import main
from research_agent.contracts import ContinuousConfig
from research_agent.composition.policies import compose_policy
from research_agent.regimes.continuous.control import RuntimeState
from support.continuous import make, text, call, execute, events
from support import save_arguments

@pytest.mark.parametrize("enabled,review_count", [(True, 2), (False, 0)])
def test_review_selection_and_final_response_share_total_budget(tmp_path, enabled, review_count):
    a, req = make(tmp_path, [text("Saved findings and gaps")] * 30,
        config=ContinuousConfig(max_llm_calls=25, general_review=enabled))
    result = execute(a, req)
    assert result.stop_reason == "call_limit" and result.llm_calls == 25
    assert result.llm_calls_by_phase["evaluator"] == review_count
    assert len(a.client.review_requests) == review_count
    assert result.answer == "Saved findings and gaps"
    manifest = json.loads((a.recorder.current / "manifiesto.json").read_bytes())
    assert manifest["general_review"] == {"requested": enabled, "effective": enabled}
    assert bool(manifest["external_review_policy"]) is enabled
    assert bool(list((a.recorder.current / "revision-externa").glob("*.json"))) is enabled
    assert (a.recorder.current / "continuidad/indice.json").exists()
    if not enabled:
        assert result.llm_calls_by_phase["closing"] == 1
        assert not a.client.requests[-1]["allow_tools"] and a.client.requests[-1]["tools"] == []
        assert not any(e.get("kind") == "evaluate" for e in a.recorder.events)


def test_disabled_review_keeps_writes_and_tool_limit_closing(tmp_path):
    a, req = make(tmp_path, [call("record_research_advance", **save_arguments(path="result.md", content="Persisted")), text("Final gaps")],
        config=ContinuousConfig(max_llm_calls=5, max_tool_calls=1, general_review=False))
    result = execute(a, req)
    assert result.stop_reason == "tool_limit" and result.answer == "Final gaps"
    assert result.llm_calls == 2 and result.tool_calls == 1
    assert a.workspace.read_file("result.md")["text"] == "Persisted"
    assert not a.client.review_requests


def test_disabled_review_does_not_inject_previous_feedback(tmp_path):
    async def scenario():
        a, req = make(tmp_path, [text()], config=ContinuousConfig(max_llm_calls=1, general_review=False))
        root = a.recorder.root / "previous/runtime/estado.json"
        state = RuntimeState(feedback={"status": "complete", "findings": ["OLD_REVIEW_MARKER"]})
        state.save(root, a.workspace, req.mandate)
        p = compose_policy(a, req)
        await p.prepare()
        try:
            assert "OLD_REVIEW_MARKER" not in str(a.history)
            assert p.state.feedback is None
        finally:
            await p.finalize(None)
    asyncio.run(scenario())


@pytest.mark.parametrize("tail", [["--general-review", "off"], ["--general-review", "on"],
    ["--continuous", "--progress", "--general-review", "on"]])
def test_invalid_cli_selection_never_builds_clients(tmp_path, monkeypatch, tail):
    import research_agent.cli.main as cli
    monkeypatch.setattr(cli, "build_agent", lambda *a, **kw: pytest.fail("client constructed"))
    with pytest.raises(SystemExit) as exc:
        main(["Question", "--run-name", "initial", "--output", str(tmp_path / "out"), "--new", *tail])
    assert exc.value.code == 2 and not (tmp_path / "out").exists()


def test_old_config_defaults_and_type_validation():
    assert ContinuousConfig(**{"max_llm_calls": 3}).general_review is True
    with pytest.raises(ValueError, match="boolean"):
        ContinuousConfig(general_review="off")
