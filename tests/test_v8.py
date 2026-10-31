"""V8 deterministic and integration checks with local clients, never providers."""
import asyncio
from dataclasses import replace
import json

import pytest

from research_agent.contracts import AgentRequest, ContinuousConfig
from research_agent.experiments import prepare_experiment
from research_agent.external_review import knowledge
from research_agent.objectives import Objective, Criterion, EvaluationState, encode, metrics, parse_evaluation
from research_agent.objective_review import packet, feedback, content_hash, previous_state
from research_agent.workspace import Workspace
from test_continuous import make, execute, text, call, events
from test_continuous_pilot import prepared_inputs


def objective(**changes):
    return Objective.from_dict({"id": "business", "description": "Explicar negocio TEST",
        "criteria": {"products": "Explicar productos", "revenue": "Explicar ingresos"}, **changes})


def report(*statuses):
    return {"criteria": [{"criterion_id": key, "status": status, "justification": "Fundamento contrastable",
                          "references": ["modelo.md#M1"], "pending": None if status == "cubierto" else "Falta explicar el criterio"}
                         for key, status in zip(("products", "revenue"), statuses or ("cubierto", "no_cubierto"))]}


class Client:
    def __init__(self, reports=None):
        self.requests = []
        self.evaluations = []
        self.reports = iter(reports if reports is not None else [report()] * 10)

    async def respond(self, **kwargs):
        self.requests.append(kwargs)
        if "objective_evaluation_packet" in getattr(kwargs["input_items"][0], "payload", {}):
            self.evaluations.append(kwargs)
            response = next(self.reports)
            if isinstance(response, BaseException):
                raise response
            return text(json.dumps(response)) if isinstance(response, dict) else response
        return text("Avance ordinario")


def setup(tmp_path, *, calls=21, reports=None, config=None):
    agent, request = make(tmp_path, [], config=config or ContinuousConfig(max_llm_calls=calls))
    agent.client = Client(reports)
    return agent, replace(request, objective=objective())


def saved(agent):
    return [json.loads(p.read_bytes()) for p in sorted((agent.recorder.current / "evaluacion-objetivo").glob("evaluation-*.json"))
            if not p.name.endswith("-input.json")]


@pytest.mark.parametrize("value", [None, {}, {"id": "a", "description": "b", "criteria": {}},
    {"id": " ", "description": "b", "criteria": {"c": "d"}},
    {"id": "a", "description": "b", "criteria": {"c": ""}},
    {"id": "a", "description": "b", "criteria": {"c": "d"}, "extra": True}])
def test_objective_rejects_invalid_definitions(value):
    with pytest.raises(ValueError):
        Objective.from_dict(value)


def test_objective_is_immutable_identified_and_canonical(tmp_path):
    value = objective()
    assert value.sha256 == objective(criteria={"revenue": "Explicar ingresos", "products": "Explicar productos"}).sha256
    with pytest.raises(ValueError):
        Objective("x", "d", (Criterion("a", "d"), Criterion("a", "e")))
    with pytest.raises(ValueError):
        objective(description="a" * 17000)
    path = tmp_path / "objective.json"
    path.write_text('{"id":"x","description":"d","criteria":{"a":"b","a":"c"}}')
    with pytest.raises(ValueError, match="Duplicate"):
        Objective.load(path)
    with pytest.raises(ValueError, match="continuous"):
        AgentRequest("m", "w", "c", objective=value)


@pytest.mark.parametrize("fault", ["missing", "duplicate", "unknown", "status", "justification", "references", "pending", "extra"])
def test_evaluation_requires_exact_criteria_and_substantive_fields(fault):
    value = report("cubierto", "no_cubierto")
    if fault == "missing":
        value["criteria"].pop()
    elif fault == "duplicate":
        value["criteria"].append(value["criteria"][0])
    elif fault == "unknown":
        value["criteria"][0]["criterion_id"] = "unknown"
    elif fault == "references":
        value["criteria"][0]["references"] = []
    elif fault == "pending":
        value["criteria"][1]["pending"] = None
    elif fault == "extra":
        value["extra"] = "x"
    else:
        value["criteria"][0][fault] = ""
    with pytest.raises(ValueError):
        parse_evaluation(json.dumps(value), objective())


def test_distance_reopening_stagnation_and_incomplete_reset():
    state = EvaluationState()
    first = state.accept(report(), "one")
    assert first["metrics"] == {"covered": 1, "total": 2, "distance": .5, "delta_distance": None}
    assert not state.accept(report(), "two")["interventions"]
    assert "Tres evaluaciones" in state.accept(report(), "three")["interventions"][0]
    partial = state.accept(report("cubierto", "no_evaluable"), "partial")
    assert partial["metrics"]["distance"] is None and state.last_valid_reference == "three" and state.stagnant == 0
    closed = state.accept(report("cubierto", "cubierto"), "closed")
    assert closed["metrics"]["delta_distance"] == .5
    assert any("síntesis" in i for i in closed["interventions"])
    assert not state.accept(report("cubierto", "cubierto"), "still-closed")["interventions"]
    reopened = state.accept(report(), "reopened")
    assert reopened["metrics"]["delta_distance"] == -.5 and reopened["reopened"] == ["revenue"]
    assert any("síntesis" in i for i in state.accept(report("cubierto", "cubierto"), "closed-again")["interventions"])
    state.failed()
    assert state.stagnant == 0


def test_packet_reserves_sources_declares_omissions_and_hashes_source_versions(tmp_path):
    space = Workspace(tmp_path / "state")
    source = space.root / "materiales/source.json"
    source.parent.mkdir(exist_ok=True)
    source.write_text(json.dumps({"evidence": "fuente" * 2000}), encoding="utf-8")
    for n in range(40):
        space.write_file(f"modelo-{n:02}.md", "productos ingresos " * 600 + " materiales/source.json")
    current = knowledge(space)
    current["capture_errors"] = {"errors": [{"path": "long" * 1000, "error_type": "fixture"}] * 100}
    payload = packet(space, objective(), current, None, {}, [{"event": "lab.tool.started", "detail": "x" * 1000}] * 100)
    assert len(encode(payload)) <= 65536
    assert payload["evidence"] and payload["evidence"][0]["sha256"]
    assert payload["evidence"][0]["partial"] and payload["omitted"]["documents"] > 0
    assert payload["omitted"]["actions"] > 0
    assert payload["omitted"]["capture_errors"] == 100
    before = content_hash(space, objective(), current)
    source.write_text("changed source", encoding="utf-8")
    assert content_hash(space, objective(), current) != before


def test_feedback_is_bounded_and_preserves_full_report():
    value = report()
    for item in value["criteria"]:
        item.update(justification="é" * 12000, references=["r" * 10000])
    original = json.dumps(value)
    result = feedback(value, {"metrics": metrics(value), "reopened": [], "interventions": []}, "ref")
    assert len(encode(result)) <= 8192 and result["partial"]
    assert json.dumps(value) == original


def test_periodic_priority_isolation_accounting_and_final_reuse(tmp_path):
    agent, request = setup(tmp_path)
    result = execute(agent, request)
    assert result.stop_reason == "call_limit"
    assert result.llm_calls_by_phase == {"research": 21, "consolidation": 0, "review": 2,
                                         "external_review": 0, "objective_evaluation": 1}
    assert result.llm_calls == sum(result.llm_calls_by_phase.values())
    phases = [e["phase"] for e in events(agent, "lab.model.started")]
    assert phases[phases.index("objective_evaluation") - 1] == "review"
    evaluation = agent.client.evaluations[0]
    assert not evaluation["allow_tools"] and evaluation["tools"] == []
    assert len(evaluation["input_items"]) == 1 and "objective_evaluation_packet" in evaluation["input_items"][0].payload
    manifest = json.loads((agent.recorder.current / "manifiesto.json").read_bytes())
    assert manifest["objective"]["sha256"] == request.objective.sha256
    assert manifest["external_review_policy"] is None
    assert json.loads((agent.recorder.current / "evaluacion-objetivo/final.json").read_bytes())["reused"]
    assert saved(agent)[0]["previous_valid_reference"] is None


@pytest.mark.parametrize("bad", [text("not JSON"), call("write_file", path="forbidden.md", content="x"), TimeoutError("fixture")])
def test_failed_evaluations_are_recorded_without_retry_or_stopping_research(tmp_path, bad):
    agent, request = setup(tmp_path, reports=[bad, report()])
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and result.llm_calls_by_phase["research"] == 21
    assert [v["status"] for v in saved(agent)] == ["failed", "complete"]
    assert not (agent.workspace.root / "forbidden.md").exists()
    assert len(events(agent, "lab.objective.failed")) == 1
    assert saved(agent)[-1]["metrics"]["delta_distance"] is None


def test_partial_is_diagnostic_without_distance(tmp_path):
    agent, request = setup(tmp_path, calls=2, reports=[report("cubierto", "no_evaluable")])
    result = execute(agent, request)
    assert result.llm_calls_by_phase["objective_evaluation"] == 1
    value = saved(agent)[0]
    assert value["status"] == "partial" and value["metrics"]["distance"] is None
    summary = json.loads((agent.recorder.current / "evaluacion-objetivo/summary.json").read_bytes())
    assert summary["last_valid_reference"] is None


def test_cancellation_captures_attempt_and_does_not_add_final_evaluation(tmp_path):
    agent, request = setup(tmp_path, reports=[asyncio.CancelledError()])
    with pytest.raises(asyncio.CancelledError):
        execute(agent, request)
    assert len(saved(agent)) == 1 and saved(agent)[0]["status"] == "cancelled"
    assert not (agent.recorder.current / "evaluacion-objetivo/final.json").exists()


def test_time_and_operational_stops_do_not_evaluate(tmp_path):
    agent, request = setup(tmp_path)
    async def fail(**kwargs):
        raise RuntimeError("research failed")
    agent.client.respond = fail
    result = execute(agent, request)
    assert result.stop_reason == "operational_failure" and not saved(agent)
    other, req = setup(tmp_path / "expired", config=ContinuousConfig(max_llm_calls=2, timeout_seconds=.00001))
    result = execute(other, req)
    assert result.stop_reason == "time_limit" and not saved(other)


def test_feedback_correction_renewal_and_final_reassessment(tmp_path):
    agent, request = setup(tmp_path, config=ContinuousConfig(max_llm_calls=26, max_context_bytes=524288,
                                                            consolidation_threshold_bytes=100000))
    class Workflow(Client):
        def __init__(self):
            super().__init__([report(), report("cubierto", "cubierto")])
            self.research = 0
            self.recovered = False

        async def respond(self, **kwargs):
            items = kwargs["input_items"]
            if "objective_evaluation_packet" in getattr(items[0], "payload", {}):
                return await super().respond(**kwargs)
            if not kwargs["allow_tools"]:
                return text("Continuar")
            if not any(t.name == "calculate" for t in kwargs["tools"]):
                return text("Conocimiento conservado")
            self.research += 1
            contexts = [getattr(x, "payload", {}) for x in items]
            if self.research == 20:
                return call("write_file", path="modelo.md", content="Explica productos. Pendientes ingresos.")
            if self.research == 21:
                assert any(c.get("objective_feedback", {}).get("metrics", {}).get("distance") == .5 for c in contexts)
                return call("write_file", path="modelo.md", content="Explica productos e ingresos. #M1")
            if self.research == 22:
                return text("investigación " * 9000)
            if self.research >= 23:
                assert any("fixed_objective" in c for c in contexts)
                assert any("objective_feedback" in c for c in contexts)
                self.recovered = True
            return text("Avance")
    agent.client = Workflow()
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and agent.client.recovered
    assert events(agent, "lab.context.renewed")
    assert [s["metrics"]["distance"] for s in saved(agent)] == [.5, 0]
    assert saved(agent)[1]["previous_valid_reference"] == saved(agent)[0]["reference"]


def test_managed_continuation_only_recovers_same_workspace_and_objective(tmp_path):
    root = tmp_path / "experiment"
    prompts = prepare_experiment(root, new=True, deliberative=True)
    agent, request = setup(root, calls=1)
    agent.recorder.experiment = root
    request = replace(request, instructions=prompts)
    execute(agent, request)
    # A damaged later capture must not hide the earlier complete evaluation in this run.
    (agent.recorder.current / "evaluacion-objetivo/evaluation-9999.json").write_text("{", encoding="utf-8")
    next_agent, next_request = setup(root, calls=1)
    next_agent.recorder.experiment = root
    execute(next_agent, replace(next_request, instructions=prompts))
    first_contexts = [getattr(x, "payload", {}) for x in next_agent.client.requests[0]["input_items"]]
    assert any(c.get("objective_feedback", {}).get("historical") for c in first_contexts)
    assert events(next_agent, "lab.objective.history_unavailable")
    assert saved(next_agent)[0]["metrics"]["delta_distance"] == 0
    assert previous_state(next_agent.recorder, objective(description="Otro objetivo")).last_valid is None
    next_agent.recorder.workspace_fingerprint = "another workspace"
    assert previous_state(next_agent.recorder, objective()).last_valid is None


def test_cli_validates_objective_before_clients_or_experiment_creation(tmp_path, monkeypatch):
    import research_agent.cli as cli
    monkeypatch.setattr(cli, "build_agent", lambda *a, **k: pytest.fail("Client constructed"))
    path = tmp_path / "objective.json"
    path.write_text('{"bad": true}')
    base = ["m", "--experiment", str(tmp_path / "experiment"), "--new", "--run-name", "test", "--objective", str(path)]
    with pytest.raises(SystemExit) as error:
        cli.main(base)
    assert error.value.code == 2
    with pytest.raises(SystemExit) as error:
        cli.main([*base, "--continuous", "--mandate", str(tmp_path / "mandate.md")])
    assert error.value.code == 2 and not (tmp_path / "experiment").exists()


def test_campaign_freezes_objective_and_rejects_drift(prepared_inputs):
    from research_campaigns import continuous as pilot
    root, definition, source, _ = prepared_inputs
    (definition / "objective.json").write_bytes(encode(objective().definition()))
    pilot.prepare(root, definition, source)
    pilot.check(root)
    record = json.loads((root / "campaign.json").read_bytes())
    assert record["objective"]["sha256"] == objective().sha256
    command = record["command"]
    assert command[command.index("--objective") + 1] == str(root / "definicion/objective.json")
    assert "definicion/objective.json" in record["files"]
    (root / "definicion/objective.json").write_bytes(encode(objective(description="Changed").definition()))
    with pytest.raises(ValueError, match="changed"):
        pilot.check(root)


def test_native_reader_and_report_show_partial_failures_and_objective_phase(tmp_path):
    import importlib
    from research_campaigns.evidence import inspect_run
    agent, request = setup(tmp_path, calls=42, reports=[report(), text("invalid"), report("cubierto", "no_evaluable")])
    result = execute(agent, request)
    info = inspect_run(tmp_path, agent.recorder.current, objective_sha256=objective().sha256)
    summary = info["objective_summary"]
    assert summary["last_valid_metrics"]["distance"] == .5
    assert summary["failures"] == 1 and summary["partial"] == 1 and summary["latest_status"] == "partial"
    wrong = inspect_run(tmp_path, agent.recorder.current, objective_sha256="changed")
    assert any("objective differs" in i["error"] for i in wrong["capture_errors"])
    record = {"id": "v8", "mode": "continuous", "status": "interrupted", "runtime": {},
              "objective": {"sha256": objective().sha256},
              "sessions": [{"id": "one", "status": "interrupted", "run_directory": info["run_directory"]}]}
    importlib.import_module("research_campaigns.report").report(tmp_path, record)
    view = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert "Cobertura V8" in view and "fallidas: 1" in view and "parciales: 1" in view
    assert f"Llamadas: {result.llm_calls_by_phase['objective_evaluation']}" in view


def test_tool_limit_evaluates_final_without_extra_research(tmp_path):
    agent, request = setup(tmp_path, config=ContinuousConfig(max_llm_calls=21, max_tool_calls=1))
    original = agent.client.respond
    async def respond(**kwargs):
        if kwargs["allow_tools"]:
            return call("write_file", path="modelo.md", content="Resultado #M1")
        return await original(**kwargs)
    agent.client.respond = respond
    result = execute(agent, request)
    assert result.stop_reason == "tool_limit" and result.tool_calls == 1
    assert result.llm_calls_by_phase["research"] == 1 and len(saved(agent)) == 1
    assert saved(agent)[0]["kind"] == "final"


def test_oversized_packet_is_captured_as_skipped_and_not_a_distance(tmp_path):
    agent, request = setup(tmp_path, config=ContinuousConfig(max_llm_calls=1, max_context_bytes=50000,
                                                            consolidation_threshold_bytes=48000))
    for n in range(10):
        (agent.workspace.root / f"materiales/source-{n}.json").write_text("fuente " * 1000, encoding="utf-8")
    references = " ".join(f"materiales/source-{n}.json" for n in range(10))
    for n in range(40):
        agent.workspace.write_file(f"modelo-{n}.md", "productos " * 500 + references)
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and result.llm_calls_by_phase["objective_evaluation"] == 0
    assert saved(agent)[0]["status"] == "skipped"
    assert "metrics" not in saved(agent)[0]


def test_zero_distance_requests_closure_once_without_stopping_continuous(tmp_path):
    agent, request = setup(tmp_path, calls=42, reports=[report("cubierto", "cubierto")] * 3)
    result = execute(agent, request)
    assert result.stop_reason == "call_limit" and result.llm_calls_by_phase["research"] == 42
    reports = saved(agent)
    assert len(reports) == 2  # The unchanged final result reuses the second periodic evaluation.
    assert sum(any("síntesis" in i for i in r["interventions"]) for r in reports) == 1


def test_consolidation_defers_due_evaluation_without_backlog(tmp_path):
    agent, request = setup(tmp_path, config=ContinuousConfig(max_llm_calls=25, max_context_bytes=524288,
                                                            consolidation_threshold_bytes=100000))
    original = agent.client.respond
    count = 0
    async def respond(**kwargs):
        nonlocal count
        if kwargs["allow_tools"] and any(t.name == "calculate" for t in kwargs["tools"]):
            count += 1
            if count == 20:
                return text("material " * 18000)
        return await original(**kwargs)
    agent.client.respond = respond
    result = execute(agent, request)
    assert result.stop_reason == "call_limit"
    phases = [e["phase"] for e in events(agent, "lab.model.started")]
    evaluation_index = phases.index("objective_evaluation")
    assert "consolidation" in phases[20:evaluation_index]
    assert phases[evaluation_index - 1] == "review"
    assert result.llm_calls_by_phase["objective_evaluation"] == 1
