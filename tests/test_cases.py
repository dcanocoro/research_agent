import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest

from research_agent.agent import AgentA
from research_agent.cases import CaseStore
from research_agent.cli import main
from research_agent.contracts import AgentRequest
from research_agent.integrations.case_tools import register_cases
from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from runtime_contracts.llm import AssistantResponse, ResponseFunctionCall, ResponseTurn


def store_at(root):
    workspace = Workspace(root / "workspace")
    recorder = RunRecorder(root / "runs")
    recorder.start(str(uuid4()), {"workspace_fingerprint": hashlib.sha256(str(workspace.root.resolve()).encode()).hexdigest()})
    return CaseStore(root / "cases", workspace.root, recorder)


def save(store, previous=None, content="# Evaluation\nDemand remains uncertain."):
    reference = store.recorder.artifact({"period": "2026-Q2", "currency": "USD", "revenue": 100})
    case = previous["case"] if previous else None
    return store.save_case(case["case_id"] if case else None, "NVDA", "Investiga NVIDIA", content,
                           [reference], case["current_revision"] if case else None, "New material")


def test_create_update_history_and_new_process_recovery(tmp_path):
    store = store_at(tmp_path)
    first = save(store)
    before = {p.name: p.read_bytes() for p in (store.root / first["case"]["case_id"] / "revisions").iterdir()}
    second = save(store, first, "# Evaluation\nA correction limits the inference.")
    assert len(store.list_cases("nvda")["cases"]) == 1
    assert len(store.list_case_revisions(first["case"]["case_id"])["revisions"]) == 2
    assert "Demand remains" in store.read_case(first["case"]["case_id"], first["case"]["current_revision"])["content"]
    assert all((store.root / first["case"]["case_id"] / "revisions" / name).read_bytes() == data
               for name, data in before.items())
    code = '''
import sys,json
from pathlib import Path
from research_agent.cases import CaseStore
from research_agent.recording import RunRecorder
root=Path(sys.argv[1])
store=CaseStore(root/'cases',root/'workspace',RunRecorder(root/'runs'))
case=store.list_cases('NVDA')['cases'][0]
assert 'correction' in store.read_case(case['case_id'])['content']
assert len(store.list_case_revisions(case['case_id'])['revisions'])==2
'''
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert second["revision"]["parent_revision"] == first["case"]["current_revision"]


def test_conflicts_immutable_question_and_multiple_cases(tmp_path):
    store = store_at(tmp_path)
    first = save(store)
    second = save(store, first)
    with pytest.raises(ValueError, match="Revision conflict.*read_case"):
        save(store, first)
    with pytest.raises(ValueError, match="immutable"):
        store.save_case(second["case"]["case_id"], "NVDA", "Different question", "Content", [],
                        second["case"]["current_revision"], "Change")
    save(store)
    assert len(store.list_cases("NVDA")["cases"]) == 2


def test_reference_integrity_and_workspace_isolation(tmp_path):
    store = store_at(tmp_path)
    args = (None, "NVDA", "Question", "Content")
    with pytest.raises(ValueError, match="Invalid artifact"):
        store.save_case(*args, ["https://example.com"], None, "Initial")
    with pytest.raises(FileNotFoundError):
        store.save_case(*args, ["artifacts/" + "a" * 64 + ".json"], None, "Initial")
    reference = store.recorder.artifact({"source": "original"})
    (store.recorder.current / reference).write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        store.save_case(*args, [reference], None, "Initial")
    with pytest.raises(ValueError, match="bound to another"):
        CaseStore(store.root, tmp_path / "other-workspace", store.recorder)
    with pytest.raises(ValueError, match="bound to another"):
        CaseStore(store.root, store.workspace, RunRecorder(tmp_path / "other-runs"))
    store.recorder.start(str(uuid4()), {"workspace_fingerprint": "other"})
    with pytest.raises(ValueError, match="another workspace"):
        store.save_case(*args, [], None, "Initial")


def test_paths_notes_and_instruction_isolation(tmp_path):
    store = store_at(tmp_path)
    with pytest.raises(ValueError):
        store.read_case("../runs")
    with pytest.raises(ValueError, match="disjoint"):
        CaseStore(store.workspace / "cases", store.workspace, store.recorder)
    with pytest.raises(ValueError, match="disjoint"):
        CaseStore(store.recorder.root / "cases", store.workspace, store.recorder)
    workspace = Workspace(store.workspace)
    with pytest.raises(ValueError):
        workspace.write_markdown("../cases/file.md", "Bypass")
    registry = ToolRegistry(store.recorder)
    register_cases(registry, store)
    private_prompt = store.root / "instructions.md"
    private_prompt.write_text("test", encoding="utf-8")
    agent = AgentA(None, registry, workspace, store.recorder)
    with pytest.raises(ValueError, match="disjoint"):
        asyncio.run(agent.run(AgentRequest("test", "workspace", "chat", (private_prompt,))))


def test_crash_before_head_publication_keeps_old_head_and_diagnoses_orphans(tmp_path, monkeypatch):
    store = store_at(tmp_path)
    first = save(store)
    original = store._atomic

    def interrupted(path, value):
        if path.name == "case.json":
            raise OSError("simulated crash")
        original(path, value)

    monkeypatch.setattr(store, "_atomic", interrupted)
    with pytest.raises(OSError):
        save(store, first, "Unpublished revision")
    reopened = CaseStore(store.root, store.workspace, store.recorder)
    assert reopened.read_case(first["case"]["case_id"])["revision"]["revision_id"] == first["case"]["current_revision"]
    snapshot = reopened.snapshot()
    assert len(snapshot["unpublished_files"]) == 2
    assert len(reopened.publications(store.recorder.current.name)) == 1
    assert reopened.publications(str(uuid4())) == []
    orphan = Path(snapshot["unpublished_files"][0]).stem
    with pytest.raises(ValueError, match="not in published"):
        reopened.read_case(first["case"]["case_id"], orphan)
    save(reopened, first, "Recovered publication")
    assert len(reopened.list_case_revisions(first["case"]["case_id"])["revisions"]) == 2
    assert len(reopened.snapshot()["unpublished_files"]) == 2


def test_incomplete_revision_and_new_case_are_not_published(tmp_path, monkeypatch):
    store = store_at(tmp_path)
    original = store._exclusive

    def interrupted(path, data):
        if path.suffix == ".json":
            raise OSError("simulated interruption after Markdown")
        original(path, data)

    monkeypatch.setattr(store, "_exclusive", interrupted)
    with pytest.raises(OSError):
        save(store)
    assert store.list_cases("NVDA")["cases"] == []
    assert len(store.snapshot()["unpublished_files"]) == 1


def test_os_lock_and_stale_revision_prevent_lost_updates(tmp_path):
    store = store_at(tmp_path)
    other = CaseStore(store.root, store.workspace, store.recorder)
    first = save(store)
    with store._lock():
        with ThreadPoolExecutor() as pool:
            future = pool.submit(save, other, first)
            with pytest.raises(ValueError, match="busy"):
                future.result()
    second = save(other, first)
    with pytest.raises(ValueError, match="Revision conflict"):
        save(store, first)
    assert store.read_case(first["case"]["case_id"])["revision"]["revision_id"] == second["case"]["current_revision"]


def test_case_tools_state_partial_failure_and_fresh_instance(tmp_path):
    store = store_at(tmp_path)
    reference = store.recorder.artifact({"original": "source"})
    initial_run = store.recorder.current.name
    workspace = Workspace(store.workspace)
    registry = ToolRegistry(store.recorder)
    register_files(registry, workspace)
    register_cases(registry, store)

    class Scripted:
        count = 0

        async def respond(self, **kwargs):
            self.count += 1
            if self.count == 1:
                call = ResponseFunctionCall("save", "save_case", dict(case_id=None, asset="NVDA", question="Investiga NVIDIA",
                    content="# Evaluation\nUncertain", references=[reference], expected_revision=None, change="Initial"))
                return ResponseTurn([call], "", call)
            raise ConnectionError("provider failed after save")

    prompt = Path(__file__).parents[1] / "src/research_agent/prompts/case_research.md"
    agent = AgentA(Scripted(), registry, workspace, store.recorder, instructions=(prompt,))
    result = asyncio.run(agent.run(AgentRequest("Investiga NVIDIA", "workspace", "chat")))
    assert result.status == "failed" and result.error == "ConnectionError"
    record = store.recorder.current
    assert json.loads((record / "state_before.json").read_bytes())["cases"]["heads"] == {}
    assert len(json.loads((record / "state_after.json").read_bytes())["cases"]["heads"]) == 1
    assert (record / "result.json").exists() and (record / "transcript.json").exists()
    assert "case_research.md" in (record / "manifest.json").read_text()
    # A fresh recorder and instance must read the source from the original run.
    reopened = CaseStore(store.root, store.workspace, RunRecorder(store.recorder.root))

    class Fresh:
        calls = 0

        async def respond(self, **kwargs):
            # Only fresh memory/user input and runtime budget; no prior conversation replay.
            self.calls += 1
            if self.calls == 1:
                assert len(kwargs["input_items"]) == 3
            assert initial_run != reopened.recorder.current.name
            case = reopened.list_cases("NVDA")["cases"][0]
            assert reopened.read_case(case["case_id"])["revision"]["references"] == [reference]
            assert "original" in reopened.recorder.read_artifact(reference)["text"]
            return ResponseTurn([AssistantResponse("Recovered")], "Recovered", None)

    fresh_registry = ToolRegistry(reopened.recorder)
    register_cases(fresh_registry, reopened)
    fresh = AgentA(Fresh(), fresh_registry, workspace, reopened.recorder, instructions=(prompt,))
    recovered = asyncio.run(fresh.run(AgentRequest("Continue", "workspace", "new-chat")))
    assert recovered.answer == "Recovered"
    assert recovered.persistence.status == "unconfirmed"  # Prior run writes do not count as new publication.


@pytest.mark.parametrize("extra", [["--knowledge-mode", "cases"], ["--case-store", "cases"],
    ["--knowledge-mode", "cases", "--case-store", "workspace/cases"]])
def test_cli_rejects_ambiguous_configuration(extra):
    with pytest.raises(SystemExit) as exc:
        main(["hello", "--workspace", "workspace", "--runs", "runs", *extra])
    assert exc.value.code == 2


def test_case_content_tampering_is_detected(tmp_path):
    store = store_at(tmp_path)
    first = save(store)
    revision = store.root / first["case"]["case_id"] / "revisions" / (first["case"]["current_revision"] + ".md")
    revision.write_text("Rewritten", encoding="utf-8")
    with pytest.raises(ValueError, match="hash mismatch"):
        store.read_case(first["case"]["case_id"])


def test_large_case_uses_existing_artifact_pagination(tmp_path):
    store = store_at(tmp_path)
    first = save(store, content="á" * 20000)
    registry = ToolRegistry(store.recorder)
    register_cases(registry, store)
    call = ResponseFunctionCall("read", "read_case", {"case_id": first["case"]["case_id"], "revision": None})
    asyncio.run(registry.execute(call))
    tool_file = sorted(store.recorder.current.glob("tools/*.json"))[-1]
    payload = json.loads(tool_file.read_bytes())["result"]
    assert payload["value"]["limited"] is True
    page = store.recorder.read_artifact(payload["artifact_ref"])
    assert page["next_offset"] is not None
    assert "á" in page["text"]


def test_lock_excludes_another_process_and_releases_after_exit(tmp_path):
    store = store_at(tmp_path)
    code = '''
import sys
from pathlib import Path
from research_agent.cases import CaseStore
from research_agent.recording import RunRecorder
root=Path(sys.argv[1])
try:
    CaseStore(root/'cases',root/'workspace',RunRecorder(root/'runs'))
except ValueError as exc:
    assert 'busy' in str(exc)
    sys.exit(7)
'''
    with store._lock():
        result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True, text=True)
        assert result.returncode == 7, result.stderr
    assert CaseStore(store.root, store.workspace, store.recorder).snapshot()["heads"] == {}


def test_answer_without_save_does_not_create_case(tmp_path):
    store = store_at(tmp_path)
    registry = ToolRegistry(store.recorder)
    register_cases(registry, store)

    class AnswerOnly:
        async def respond(self, **kwargs):
            return ResponseTurn([AssistantResponse("Limited answer")], "Limited answer", None)

    agent = AgentA(AnswerOnly(), registry, Workspace(store.workspace), store.recorder)
    result = asyncio.run(agent.run(AgentRequest("Question", "workspace", "chat")))
    assert result.answer == "Limited answer" and store.snapshot()["heads"] == {}
    assert (store.recorder.current / "answer.md").read_text() == "Limited answer"
