import asyncio
import hashlib
import json
from dataclasses import replace
from datetime import date, datetime, timezone

import pytest

pytest.importorskip("dcf_lab")
from dcf_lab import FinancialSnapshot, load_evaluation
from dcf_lab.adapters.llm import LLMReply
from dcf_lab.schemas import AnnualPeriod, Macro, Price, Profile
from research_agent.capabilities.valuation.tools import ValuationTools, summarize
from research_agent.capabilities.valuation.configuration import ValuationConfiguration, configuration, freeze_configuration
from research_agent.core.contracts import AgentLimits
from research_agent.core.tool_runtime import current_tool_runtime
from support.bounded import agent, request, response
from support.continuous import make, call, text, execute


@pytest.fixture
def snapshot():
    # Synthetic operating company, deliberately not real investment data.
    return FinancialSnapshot(captured_at=datetime(2026, 11, 3, tzinfo=timezone.utc),
        profile=Profile(symbol="AAA", sector="TECHNOLOGY", industry="SOFTWARE", currency="USD",
                        market_capitalization=10000, shares_outstanding=100, beta=1.1),
        annual=[AnnualPeriod(fiscal_period=date(year, 12, 31), currency="USD", values={
            "total_revenue": revenue, "operating_cashflow": 120, "capital_expenditures": -30,
            "interest_expense": 10, "income_before_tax": 100, "income_tax_expense": 20,
            "total_debt": 200, "cash_and_short_term_investments": 50, "net_income": 80})
            for year, revenue in [(2025, 1000), (2024, 900), (2023, 800)]],
        price=Price(value=100, as_of=date(2026, 10, 9), currency="USD"),
        macro=Macro(risk_free_rate=.04, risk_free_as_of=date(2026, 10, 8), equity_risk_premium=.05,
                    erp_as_of=date(2026, 6, 1), erp_source="fixture:erp"))


class Source:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def load(self, symbol):
        return self.snapshot


class Model:
    identity = {"provider": "fixture", "model": "deterministic"}

    def __init__(self, fail=None):
        self.phases = []
        self.fail = fail
        self.inputs = []

    async def acomplete(self, phase, instructions, payload, schema):
        self.phases.append(phase)
        self.inputs.append(payload)
        if self.fail == phase:
            raise RuntimeError("secret-provider-message")
        if self.fail == "cancel" and phase == "synthesis":
            raise asyncio.CancelledError()
        if self.fail == "timeout" and phase == "synthesis":
            await asyncio.sleep(1)
        if phase == "assumptions":
            output = {"initial_revenue_growth": .1, "target_fcff_margin": .12,
                "growth_justification": "Historia ilustrativa", "margin_justification": "Mejora ilustrativa",
                "uncertainty": "Reinversión", "evidence_refs": ["profile"]}
        else:
            output = {"verdict": "indeterminate", "confidence": "low", "reasoning": "Supuestos exploratorios",
                "risks": ["Margen"], "limitations": ["Sin comparables"], "review_conditions": ["Cambios de negocio"],
                "evidence_refs": ["dcf"], "research_implications": [{"kind": "uncertainty",
                    "observation": "Persistencia del margen", "question": "¿Es sostenible?", "review_trigger": None,
                    "evidence_refs": ["assumptions"]}]}
        return LLMReply(output, {"usage": {"input_tokens": 12, "output_tokens": 20}})


def args(**changes):
    return {"company_id": "AAA", "knowledge_paths": [], "previous_evaluation_ref": None, **changes}


def attach(a, snapshot, model=None, timeout=120):
    tools = ValuationTools(a.tools, a.workspace, Source(snapshot), model or Model(), timeout)
    tools.register()
    return tools


def bundles(a):
    return list(a.workspace.root.glob("materiales/dcf-*.json"))


def test_managed_bounded_tool_counts_and_recovery(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args())), response("valoración archivada")])
    model = Model()
    attach(a, snapshot, model)
    result = asyncio.run(a.run(request()))
    assert result.status == "completed" and result.llm_calls == 4 and result.tool_calls == 1
    assert result.llm_calls_by_phase["valuation_assumptions"] == 1
    assert result.llm_calls_by_phase["valuation_diagnosis"] == 1
    assert current_tool_runtime.get() is None
    e = load_evaluation(bundles(a)[0])
    assert e.status == "completed" and e.synthesis.research_implications
    assert (a.recorder.current / "valoraciones" / f"{e.run_id}.json").exists()
    assert tools_result(a)["value"]["bundle_ref"] in result.state.materials
    recovered = a.workspace.read_file(tools_result(a)["value"]["bundle_ref"], max_bytes=128)
    assert recovered["next_offset"]


def tools_result(a):
    from runtime_contracts.llm import ToolResult
    return next(item.payload for item in a.history if isinstance(item, ToolResult) and item.name == "evaluate_company")


def test_insufficient_budget_makes_no_specialist_call(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args())), response("insuficiente")], AgentLimits(max_llm_calls=5))
    model = Model()
    attach(a, snapshot, model)
    result = asyncio.run(a.run(request()))
    assert not model.phases and result.llm_calls == 2
    e = load_evaluation(bundles(a)[0])
    assert e.status == "failed" and e.phases["calculation"].status == "not_started"


@pytest.mark.parametrize("failure", ["synthesis", "timeout"])
def test_partial_result_with_failed_or_timed_out_diagnosis(tmp_path, snapshot, failure):
    a = agent(tmp_path, [response(call=("evaluate_company", args())), response("resultado parcial")])
    attach(a, snapshot, Model(failure), timeout=.05)
    result = asyncio.run(a.run(request()))
    e = load_evaluation(bundles(a)[0])
    assert result.llm_calls == 4 and e.status == "partial" and e.calculations
    assert e.llm_calls[-1]["status"] == "failed"
    assert "secret-provider-message" not in (a.recorder.current / "resultado.json").read_text()


def test_cancel_preserves_bundle_and_propagates(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args()))])
    attach(a, snapshot, Model("cancel"))
    with pytest.raises(asyncio.CancelledError):
        asyncio.run(a.run(request()))
    e = load_evaluation(bundles(a)[0])
    assert e.calculations and e.status == "cancelled"
    assert json.loads((a.recorder.current / "resultado.json").read_text())["status"] == "cancelled"


def test_outer_tool_deadline_keeps_timeout_semantics(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args())), response("cierre tras timeout")],
              AgentLimits(timeout_seconds=.8, finalization_seconds=.1))
    attach(a, snapshot, Model("timeout"), timeout=2)
    result = asyncio.run(a.run(request()))
    assert result.status != "cancelled"
    assert tools_result(a)["error_type"] == "timeout"
    e = load_evaluation(bundles(a)[0])
    assert e.calculations and e.status == "cancelled"


def test_continuous_budget_counts_both_calls(tmp_path, snapshot):
    a, req = make(tmp_path, [call("evaluate_company", **args()), text("cierre")])
    req = replace(req, continuous=replace(req.continuous, max_llm_calls=4, general_review=False))
    attach(a, snapshot)
    result = execute(a, req)
    assert result.llm_calls == 4 and result.tool_calls == 1
    assert result.llm_calls_by_phase["valuation_assumptions"] == 1
    assert result.llm_calls_by_phase["valuation_diagnosis"] == 1
    assert load_evaluation(bundles(a)[0]).status == "completed"


def test_react_ceiling_preserves_specialist_calls_and_stops_research(tmp_path, snapshot):
    a, req = make(tmp_path, [call("evaluate_company", **args()),
                            call("evaluate_company", **args()), text("cierre")])
    req = replace(req, continuous=replace(req.continuous, max_llm_calls=None,
                                         max_react_calls=3, general_review=False))
    model = Model()
    attach(a, snapshot, model)
    result = execute(a, req)
    assert result.stop_reason == "call_limit"
    assert result.llm_calls == 7 and result.tool_calls == 2
    assert result.llm_calls_by_phase["researcher"] == 2
    assert result.llm_calls_by_phase["closing"] == 1
    assert model.phases == ["assumptions", "synthesis"] * 2
    last = next(e for e in reversed(a.recorder.events) if e["event"] == "lab.continuous.paused")
    assert last["react_calls_used"] == last["react_calls_limit"] == 3
    assert last["total_llm_calls_limit"] is None


def test_react_ceiling_does_not_override_total_ceiling(tmp_path, snapshot):
    a, req = make(tmp_path, [call("evaluate_company", **args()), text("cierre")])
    req = replace(req, continuous=replace(req.continuous, max_llm_calls=4,
                                         max_react_calls=300, general_review=False))
    attach(a, snapshot)
    result = execute(a, req)
    assert result.llm_calls == 4 and result.tool_calls == 1
    assert result.llm_calls_by_phase["closing"] == 1


def test_last_react_call_can_finish_specialist_work(tmp_path, snapshot):
    a, req = make(tmp_path, [call("evaluate_company", **args())])
    req = replace(req, continuous=replace(req.continuous, max_llm_calls=None,
                                         max_react_calls=1, general_review=True))
    attach(a, snapshot)
    result = execute(a, req)
    assert result.stop_reason == "call_limit" and result.llm_calls == 3
    assert result.llm_calls_by_phase["researcher"] == 1
    assert load_evaluation(bundles(a)[0]).status == "completed"


@pytest.mark.parametrize("value", [0, -1, True, 1.5])
def test_react_ceiling_requires_positive_integer(value):
    from research_agent.contracts import ContinuousConfig
    with pytest.raises(ValueError):
        ContinuousConfig(max_react_calls=value)


def test_explicit_context_previous_evaluation_and_audit(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args(knowledge_paths=["business.md"]))), response("primera")])
    a.workspace.write_file("business.md", "Negocio recurrente; evidencia sintética.")
    model = Model()
    tools = attach(a, snapshot, model)
    asyncio.run(a.run(request()))
    first = bundles(a)[0]
    ref = first.relative_to(a.workspace.root).as_posix()
    e = load_evaluation(first)
    assert e.context[0].version == hashlib.sha256(a.workspace.path("business.md").read_bytes()).hexdigest()
    assert tools.previous(ref).run_id == e.run_id
    a.client.turns = iter([response(call=("evaluate_company", args(previous_evaluation_ref=ref))), response("segunda")])
    asyncio.run(a.run(request("revisar")))
    assert model.inputs[-1]["previous_evaluation"]["evaluation_id"] == e.run_id
    # A validly resealed edit of the material still cannot impersonate the audit copy.
    from dcf_lab.service import seal
    edited = seal(e.model_copy(update={"issues": ["edited"]}))
    first.write_text(edited.model_dump_json(), encoding="utf-8")
    with pytest.raises(ValueError, match="audit"):
        tools.previous(ref)


@pytest.mark.parametrize("paths", [["../escape.md"], ["missing.md"], ["business.md", "business.md"]])
def test_invalid_context_paths_never_call_model(tmp_path, snapshot, paths):
    a = agent(tmp_path, [response(call=("evaluate_company", args(knowledge_paths=paths))), response("fallo")])
    model = Model()
    attach(a, snapshot, model)
    result = asyncio.run(a.run(request()))
    assert not model.phases and result.llm_calls == 2 and not bundles(a)


def test_configuration_freezes_and_rejects_version_drift(tmp_path, snapshot):
    supplied = tmp_path / "input.json"
    supplied.write_text(json.dumps({"source": "snapshot", "model": "explicit-model",
                                    "snapshot": snapshot.model_dump(mode="json")}), encoding="utf-8")
    root = tmp_path / "experiment"
    root.mkdir()
    freeze_configuration(root, supplied)
    saved = configuration(root)
    assert saved.snapshot == snapshot
    with pytest.raises(ValueError, match="frozen"):
        configuration(root, {**saved.model_dump(), "model": "changed"})
    with pytest.raises(ValueError):
        ValuationConfiguration(source="findata", model="explicit-model")
    from dcf_lab.reporting import fingerprint
    manifest = root / "ejecuciones" / "prior" / "manifiesto.json"
    manifest.parent.mkdir(parents=True)
    manifest.write_text(json.dumps({"configuration": {"valuation": {"enabled": True,
        "configuration_sha256": fingerprint(saved.model_dump(mode="json"))}}}), encoding="utf-8")
    assert configuration(root) == saved
    frozen = root / "dcf-lab.json"
    raw = frozen.read_bytes()
    frozen.write_text(saved.model_copy(update={"model": "changed"}).model_dump_json(), encoding="utf-8")
    with pytest.raises(ValueError, match="previous recorded"):
        configuration(root)
    frozen.write_bytes(raw)
    frozen.unlink()
    with pytest.raises(ValueError, match="previous recorded"):
        configuration(root)


def test_simulation_rejected_before_clients(tmp_path):
    from research_agent.composition.build import build_agent

    async def attempt():
        async with build_agent(tmp_path / "state", tmp_path / "runs", simulation=tmp_path / "simulation",
                               valuation={"source": "snapshot"}):
            pytest.fail("Historical simulation must not reach client construction")

    with pytest.raises(ValueError, match="historical simulation"):
        asyncio.run(attempt())


def test_composition_registers_optional_tool_without_external_calls(tmp_path, snapshot, monkeypatch):
    from research_agent.composition.build import build_agent
    from support import ScriptedClient
    monkeypatch.setenv("DCF_LAB_OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("infra.llm_factory.LLMFactory.conversation", lambda *a, **kw: ScriptedClient([]))

    async def inspect():
        config = {"source": "snapshot", "model": "explicit-model", "snapshot": snapshot.model_dump(mode="json")}
        async with build_agent(tmp_path / "state", tmp_path / "runs", valuation=config) as a:
            assert "evaluate_company" in {spec.name for spec in a.tools.specs()}
            assert a.configuration["valuation"]["enabled"]
            assert "dcf_lab" in a.configuration["code_sha256"]

    asyncio.run(inspect())


def test_failed_assumptions_charge_attempt_and_skip_diagnosis(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args())), response("fallo registrado")])
    model = Model("assumptions")
    attach(a, snapshot, model)
    result = asyncio.run(a.run(request()))
    assert result.llm_calls == 3 and model.phases == ["assumptions"]
    e = load_evaluation(bundles(a)[0])
    assert e.status == "failed" and e.calculations is None
    assert e.llm_calls[0]["status"] == "failed"


def test_ineligible_financials_make_no_model_call(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args())), response("datos insuficientes")])
    model = Model()
    attach(a, snapshot.model_copy(update={"annual": []}), model)
    result = asyncio.run(a.run(request()))
    assert result.llm_calls == 2 and not model.phases
    assert load_evaluation(bundles(a)[0]).status == "insufficient_data"


def test_summary_is_bounded_without_mutating_bundle(tmp_path, snapshot):
    a = agent(tmp_path, [response(call=("evaluate_company", args())), response("fin")])
    attach(a, snapshot)
    asyncio.run(a.run(request()))
    e = load_evaluation(bundles(a)[0])
    e = e.model_copy(update={"issues": ["x" * 9000]})
    before = e.model_dump_json()
    assert len(json.dumps(summarize(e)).encode()) <= 8192
    assert e.model_dump_json() == before
