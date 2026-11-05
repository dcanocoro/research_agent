"""Context renewal contracts with local clients, no providers or databases."""
import asyncio
import json
from dataclasses import replace

import pytest
from runtime_contracts.errors import ProviderUnavailable
from infra.llm_errors import LLMTruncated
from runtime_contracts.llm import ConversationContext, ConversationMessage

from research_agent.composition.policies import compose_policy
from research_agent.extensions.context_note.note import NOTE_REQUEST
from research_agent.extensions.context_note.note import NOTE_MAX_BYTES
from research_agent.extensions.context_note.note import renewal_reason
from research_agent.core.execution import Action
from research_agent.core.execution import ModelCall
from support.continuous import make, text, call, events, execute
from research_agent.contracts import ContinuousConfig


@pytest.mark.parametrize("size,changed,expected", [
    (99, False, None), (100, False, "size"), (100, True, "size"),
    (59, True, None), (60, True, "commitment_changed"), (60, False, None),
])
def test_trigger_boundaries(size, changed, expected):
    assert renewal_reason(size, 100, changed) == expected


def test_cli_rejects_note_without_continuous_before_clients(monkeypatch):
    import research_agent.cli.main as cli
    monkeypatch.setattr(cli, "build_agent", lambda **kw: pytest.fail("client created"))
    with pytest.raises(SystemExit) as exc:
        cli.main(["--context-note", "--new"])
    assert exc.value.code == 2


@pytest.mark.parametrize("turn,status,included", [
    (text("Trabajo en curso\nContinuar por source.md"), "valid", True),
    (text("Hallazgo pendiente con procedencia. " * 300), "valid", True),
    (text(""), "invalid", False),
    (text("á" * (NOTE_MAX_BYTES // 2 + 1)), "invalid", False),
    (call("read_file", path="source.md"), "invalid", False),
    (ProviderUnavailable("offline"), "failed", False),
    (TimeoutError(), "failed", False),
    (LLMTruncated("max_output_tokens", provider="openai"), "failed", False),
])
def test_note_is_isolated_and_rebuild_reads_current_state(tmp_path, turn, status, included):
    async def scenario():
        a, req = make(tmp_path, [turn], config=ContinuousConfig(max_llm_calls=12, context_note=True))
        p = compose_policy(a, req)
        await p.prepare()
        try:
            a.workspace.write_file("indice.md", "NEW INDEX")
            a.workspace.write_file("agenda.md", "NEW AGENDA")
            before = a.recorder.snapshot(a.workspace)
            exchange = [ConversationMessage("assistant", "recent result")]
            p.exchanges = [exchange]
            a.history.extend(exchange)
            p.renewal_cause = "size"
            await p.renew_with_note()
            assert a.recorder.snapshot(a.workspace) == before
            assert "NEW INDEX" in str(a.history) and "NEW AGENDA" in str(a.history)
            assert exchange == p.exchanges[-1]
            notes = [i for i in a.history if isinstance(i, ConversationContext) and "continuity_note" in i.payload]
            assert bool(notes) is included
            assert NOTE_REQUEST not in str(a.history)
            assert p.calls == 1 and p.calls_by_phase["context_note"] == 1
            assert p.state.researcher_calls == 0
            request = a.client.requests[0]
            assert not request["allow_tools"] and request["tools"] == [] and request["max_tokens"] == 5000
            record = json.loads((a.recorder.current / "continuidad/nota-0001.json").read_bytes())
            assert record["status"] == status
            assert events(a, "lab.context.renewed")[-1]["note_included"] is included
        finally:
            await p.finalize(None)
    asyncio.run(scenario())


@pytest.mark.parametrize("error", [asyncio.CancelledError(), RuntimeError("terminal")])
def test_terminal_note_failures_do_not_renew(tmp_path, error):
    async def scenario():
        a, req = make(tmp_path, [error], config=ContinuousConfig(max_llm_calls=12, context_note=True))
        p = compose_policy(a, req)
        await p.prepare()
        try:
            with pytest.raises(type(error)):
                await p.renew_with_note()
            assert p.calls == 1 and not events(a, "lab.context.renewed")
        finally:
            await p.finalize(error)
    asyncio.run(scenario())


@pytest.mark.parametrize("resource", ["calls", "time", "space", "B"])
def test_note_preserves_resource_reserves(tmp_path, resource):
    async def scenario():
        a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=12, context_note=True))
        p = compose_policy(a, req)
        await p.prepare()
        try:
            if resource == "calls":
                p.resources.llm_calls = 7
            elif resource == "B":
                # a_remaining is the same protected-budget boundary used by ordinary A calls.
                p.a_remaining = lambda: 5
            elif resource == "time":
                from time import monotonic
                p.deadline = monotonic() + 1
            else:
                a.history.append(ConversationMessage("assistant", "x" * p.config.max_context_bytes))
            await p.renew_with_note()
            assert not a.client.requests
            assert p.calls_by_phase["context_note"] == 0
            assert events(a, "lab.context.note.skipped")
        finally:
            await p.finalize(None)
    asyncio.run(scenario())


def test_successive_notes_replace_without_accumulating(tmp_path):
    async def scenario():
        a, req = make(tmp_path, [text("FIRST NOTE"), text("SECOND NOTE"), text("")],
                      config=ContinuousConfig(max_llm_calls=20, context_note=True))
        p = compose_policy(a, req)
        await p.prepare()
        try:
            await p.renew_with_note()
            await p.renew_with_note()
            assert "FIRST NOTE" not in str(a.history) and "SECOND NOTE" in str(a.history)
            await p.renew_with_note()
            assert "SECOND NOTE" not in str(a.history)
            transcript = p.transcript.read_text(encoding="utf-8")
            assert "FIRST NOTE" in transcript and "SECOND NOTE" in transcript
        finally:
            await p.finalize(None)
    asyncio.run(scenario())


def test_commitment_event_is_consumed_once_below_threshold(tmp_path):
    async def scenario():
        a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=12, context_note=True))
        p = compose_policy(a, req)
        await p.prepare()
        try:
            p.commitment_changed = True
            step = await p.next_step()
            assert isinstance(step, ModelCall)
            assert p.commitment_changed is False and p.renewal_cause is None
        finally:
            await p.finalize(None)
    asyncio.run(scenario())


def test_opportunistic_trigger_produces_one_auxiliary_action(tmp_path):
    async def scenario():
        a, req = make(tmp_path, [text("NOTE")],
                      config=ContinuousConfig(max_llm_calls=12, context_note=True))
        p = compose_policy(a, req)
        await p.prepare()
        try:
            size = p.measure()["budgeted_bytes"]
            p.config = replace(p.config, consolidation_threshold_bytes=size * 3 // 2)
            p.commitment_changed = True
            step = await p.next_step()
            assert isinstance(step, Action)
            await step.apply()
            assert events(a, "lab.context.renewed")[-1]["reason"] == "commitment_changed"
            assert not p.commitment_changed
            assert isinstance(await p.next_step(), ModelCall)
        finally:
            await p.finalize(None)
    asyncio.run(scenario())


def test_note_that_overfills_seed_falls_back_atomically(tmp_path):
    async def scenario():
        a, req = make(tmp_path, [text("N" * 8000)],
                      config=ContinuousConfig(max_llm_calls=12, context_note=True))
        p = compose_policy(a, req)
        await p.prepare()
        try:
            p.config = replace(p.config, consolidation_threshold_bytes=p.measure()["budgeted_bytes"] + 100)
            await p.renew_with_note()
            assert events(a, "lab.context.note.skipped")[-1]["reason"] == "reconstruction_space"
            assert not events(a, "lab.context.renewed")[-1]["note_included"]
            assert "N" * 8000 not in str(a.history)
        finally:
            await p.finalize(None)
    asyncio.run(scenario())


def test_progress_signals_successors_even_when_alternative_ids_repeat(tmp_path, monkeypatch):
    from research_agent.regimes.continuous.policy import ContinuousPolicy
    import research_agent.extensions.progress.evaluator as evaluator
    from support.progress import Client, objective

    class ContinuingClient(Client):
        async def respond(self, **kwargs):
            if kwargs["system"] == evaluator.SYSTEM:
                self.final = "continue" if self.evaluations < 2 else "sufficient"
            return await super().respond(**kwargs)

    seen = []
    original = ContinuousPolicy.next_step

    async def observe(p):
        seen.append(p.commitment_changed)
        return await original(p)

    monkeypatch.setattr(ContinuousPolicy, "next_step", observe)
    a, req = make(tmp_path, [], config=ContinuousConfig(max_llm_calls=16, context_note=True))
    a.workspace.write_file("result.md", "Fixture support")
    a.client = ContinuingClient(research=lambda n: text("avance"))
    result = execute(a, replace(req, objective=objective(), progress_step_calls=1))
    assert result.stop_reason == "objective_sufficient"
    assert seen == [False, True]
    assert result.llm_calls_by_phase["context_note"] == 0
    assert not events(a, "lab.context.renewed")


def test_progress_note_is_not_counted_as_commitment_work(tmp_path):
    import research_agent.extensions.progress.evaluator as evaluator
    from support.progress import Client, objective

    class NoteClient(Client):
        async def respond(self, **kwargs):
            if kwargs["system"] == evaluator.SYSTEM:
                self.final = "continue" if self.evaluations < 2 else "sufficient"
            return await super().respond(**kwargs)

    a, req = make(tmp_path, [], config=ContinuousConfig(
        max_llm_calls=20, context_note=True, consolidation_threshold_bytes=80000))
    # First result reaches the opportunistic threshold but remains below the high threshold.
    a.workspace.write_file("result.md", "Fixture support")
    a.tools.register("large", "Read fixture", {}, lambda: {"text": "x" * 30000}, execution="inline")
    a.client = NoteClient(research=lambda n: call("large") if n == 1 else text("avance"))
    result = execute(a, replace(req, objective=objective(), progress_step_calls=1))
    assert result.stop_reason == "objective_sufficient"
    assert result.llm_calls_by_phase["context_note"] == 1
    assert result.llm_calls_by_phase["researcher"] == a.client.research_calls == 2
    assert result.llm_calls == sum(result.llm_calls_by_phase.values())
    assert events(a, "lab.context.renewed")[0]["reason"] == "commitment_changed"
