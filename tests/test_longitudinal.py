"""Temporal gates, accounting and crash recovery without financial database writes."""
import asyncio
from copy import deepcopy
from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from findata.read.historical import available_facts
from research_agent.contracts import AgentLimits
from research_agent.simulation.state import Simulator, read, save
from research_benchmarks.longitudinal import activations, load_scenario, preflight, run_campaign
from support import fake_cli


def config(count=50):
    return {"schema_version": "longitudinal-v1", "id": "test", "start": "2023-01-01", "end": "2024-12-31",
            "universe": [{"symbol": f"S{i:02d}", "name": f"Company {i}"} for i in range(count)],
            "initial_cash": "100000", "max_positions": min(10, count), "annual_lag_days": 120,
            "messages": {"2023-01-01": "Investiga libremente y conserva lo útil.", "2023-03-01": "Revisa lo conservado."},
            "limits": asdict(AgentLimits()),
            "price_review": {"status": "approved", "basis": "synthetic", "evidence": "Deterministic test fixture"}}


def fact(symbol="S00", period="2021-12-31", kind="annual", published=None):
    return {"symbol": symbol, "metric": "total_revenue", "value": "100", "unit": "currency", "currency": "USD",
            "period": period, "period_type": kind, "published_at": published, "source_ref": "fixture:revenue",
            "provenance": {"provider": "fixture", "payload_hash": "fixed"}}


def dataset(cfg):
    prices = []
    day = date.fromisoformat(cfg["start"]) - timedelta(days=7)
    end = date.fromisoformat(cfg["end"])
    while day <= end:
        if day.weekday() < 5:
            prices.extend({"symbol": c["symbol"], "date": str(day), "close": "10", "provider": "fixture"}
                          for c in cfg["universe"])
        day += timedelta(days=1)
    return {"schema_version": "historical-input-v1", "price_basis": "synthetic", "prices": prices,
            "facts": [fact(c["symbol"]) for c in cfg["universe"]],
            "limitations": ["Synthetic fixture; no historical financial result"]}


def scenario(tmp_path, cfg):
    path = tmp_path / "scenario.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


def sim(tmp_path, count=50):
    cfg = config(count)
    return Simulator.create(tmp_path / "sim", cfg, dataset(cfg))


def test_available_day119_day120_leap_and_no_fabrication():
    row = fact(period="2023-12-31")
    assert available_facts([row], date(2024, 4, 28)) == []
    result = available_facts([row], date(2024, 4, 29))[0]
    assert result["available_on"] == "2024-04-29"
    assert result["availability_basis"] == "estimated"
    assert result["availability_lag_days"] == 120
    assert result["published_at"] is None
    assert "available_on" not in row


def test_real_date_overrides_estimate_and_unknown_quarter_is_excluded():
    row = fact(published="2022-06-01T12:00:00+00:00")
    assert available_facts([row], date(2022, 5, 31)) == []
    result = available_facts([row], date(2022, 6, 1))[0]
    assert result["availability_basis"] == "reported"
    assert result["availability_lag_days"] is None
    assert not available_facts([fact(kind="quarterly")], date(2024, 1, 1))


def test_filter_precedes_period_limit():
    rows = [fact(period=f"{year}-12-31") for year in range(2000, 2026)]
    result = available_facts(rows, date(2010, 5, 1), limit=2)
    assert {r["period"] for r in result} == {"2009-12-31", "2008-12-31"}


def test_tenth_pending_position_and_eleventh_rejected(tmp_path):
    simulator = sim(tmp_path)
    for i in range(10):
        order = simulator.buy(f"S{i:02d}", "100")
        assert "price" not in order and "executed_on" not in order
    with pytest.raises(ValueError, match="Maximum"):
        simulator.buy("S10", "100")
    simulator.buy("S00", "100")
    assert simulator.get()["available_cash"] == "98900"
    simulator.advance(date(2023, 1, 2))
    simulator.close("S00")
    with pytest.raises(ValueError, match="Maximum"):
        simulator.buy("S10", "100")
    simulator.advance(date(2023, 1, 3))
    simulator.buy("S10", "100")
    assert len(simulator.get()["positions"]) == 9


@pytest.mark.parametrize("value", ["0", "-1", "NaN", "Infinity", "abc", "100001"])
def test_invalid_and_unfunded_orders(tmp_path, value):
    simulator = sim(tmp_path, 2)
    with pytest.raises(ValueError):
        simulator.buy("S00", value)
    assert simulator.pending() == []


def test_weekend_fill_reservation_reopen_and_finish(tmp_path):
    simulator = sim(tmp_path, 2)
    simulator.advance(date(2023, 1, 6))
    simulator.buy("S00", "100000")
    with pytest.raises(ValueError, match="cash"):
        simulator.buy("S01", "1")
    simulator.advance(date(2023, 1, 8))
    assert simulator.get()["positions"] == []
    simulator.advance(date(2023, 1, 9))
    assert simulator.history()["orders"][0]["executed_on"] == "2023-01-09"
    assert Decimal(simulator.get()["equity"]) == 100000
    simulator.close("S00")
    with pytest.raises(ValueError):
        simulator.sell("S00", "1")
    simulator.advance(date(2023, 1, 10))
    assert simulator.get()["positions"] == []
    simulator.advance(date(2024, 12, 31))
    simulator.buy("S01", "10")
    simulator.advance(date(2024, 12, 31), finish=True)
    assert simulator.history()["orders"][-1]["status"] == "cancelled"
    with pytest.raises(ValueError, match="finished"):
        simulator.buy("S01", "1")
    assert Simulator(simulator.root).state == simulator.state


def test_unknown_symbol_clock_backwards_and_decimal_close(tmp_path):
    simulator = sim(tmp_path, 2)
    for p in simulator.prices["S00"]:
        p["close"] = "3"
    with pytest.raises(ValueError, match="universe"):
        simulator.buy("NVDA", "10")
    simulator.buy("S00", "10")
    simulator.advance(date(2023, 1, 2))
    simulator.close("S00")
    simulator.advance(date(2023, 1, 3))
    assert not simulator.get()["positions"]
    with pytest.raises(ValueError, match="Clock"):
        simulator.advance(date(2023, 1, 1))


def test_full_schedule_and_offline_validation(tmp_path):
    cfg = config()
    path = scenario(tmp_path, cfg)
    assert len(activations(load_scenario(path))) == 24
    code = """
import sys
class Block:
    def find_spec(self, fullname, *args):
        if fullname.split('.')[0] in {'infra', 'findata', 'engine', 'finmate', 'api'}:
            raise AssertionError(fullname)
sys.meta_path.insert(0, Block())
from research_benchmarks.runner import main
raise SystemExit(main(['longitudinal', 'validate', sys.argv[1]]))
"""
    result = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_preflight_flags_prices_without_blocking_estimated_facts():
    cfg = config(2)
    source = dataset(cfg)
    assert preflight(cfg, source)["ready"]
    cfg["price_review"]["status"] = "pending"
    report = preflight(cfg, source)
    assert not report["ready"]
    assert all(c["available_initial_facts"] == 1 for c in report["coverage"])
    source["prices"].append(deepcopy(source["prices"][0]))
    assert any("duplicate" in p for p in preflight(cfg, source)["problems"])


@pytest.mark.parametrize("failure", ["during", "after_native", "capture", "none"])
def test_resume_preserves_attempts_memory_and_economic_effects(tmp_path, failure):
    cfg = config(2)
    cfg["end"] = "2023-03-31"
    path = scenario(tmp_path, cfg)
    campaign = tmp_path / "campaign"
    calls = []
    failed = False

    def worker(command, out, err):
        nonlocal failed
        root = Path(command[command.index("--experiment") + 1])
        simulator = Simulator(Path(command[command.index("--simulation") + 1]))
        index = len(calls)
        calls.append(simulator.state["date"])
        if simulator.state["date"] == cfg["start"]:
            assert not simulator.pending()
            assert not (root / "estado/research.md").exists()
            simulator.buy("S00", "100")
            (root / "estado/research.md").write_text("remembered", encoding="utf-8")
        else:
            assert (root / "estado/research.md").read_text() == "remembered"
            assert len(simulator.state["orders"]) == 1
        if not failed and failure == "during":
            failed = True
            raise KeyboardInterrupt
        code = fake_cli(command, out, err)
        if not failed and failure == "after_native":
            failed = True
            raise KeyboardInterrupt
        if not failed and failure == "capture":
            failed = True
            run = root / "ejecuciones" / command[command.index("--run-name") + 1]
            (run / "trazas/modelo-0001.json.gz").write_bytes(b"broken")
        return code

    code = run_campaign(campaign, scenario=path, data=dataset(cfg), launcher=worker, identity=lambda: {"fixed": 1})
    if failure != "none":
        assert code == 1
        assert run_campaign(campaign, launcher=worker, identity=lambda: {"fixed": 1}) == 0
    else:
        assert code == 0
    final = Simulator(campaign / "simulador")
    assert len(final.state["orders"]) == 1
    assert len(final.state["positions"]) == 1
    assert read(campaign / "progress.json")["finished"]
    count = len(calls)
    assert run_campaign(campaign, launcher=worker, identity=lambda: {"fixed": 1}) == 0
    assert len(calls) == count
    if failure in {"during", "capture"}:
        assert list((campaign / "intentos").glob("*/failed-state-*"))
        assert len(read(campaign / "progress.json")["attempts"]) == 4
    if failure == "after_native":
        assert calls == ["2023-01-01", "2023-02-01", "2023-03-01"]
    with pytest.raises(ValueError, match="configuration"):
        run_campaign(campaign, identity=lambda: {"fixed": 2})


def test_tools_temporal_gate_universe_and_no_extract(tmp_path):
    from research_agent.integrations.file_tools import register_files
    from research_agent.recording import RunRecorder
    from research_agent.simulation.tools import register_simulation
    from research_agent.tools import ToolRegistry
    from research_agent.workspace import Workspace
    simulator = sim(tmp_path)
    recorder = RunRecorder(tmp_path / "runs")
    registry = ToolRegistry(recorder)
    register_files(registry, Workspace(tmp_path / "memory"))
    seen = []
    class Search:
        async def search_documents(self, query, **kwargs):
            seen.append(kwargs)
            return []
    register_simulation(registry, simulator, Search())
    assert "read_document" not in registry._tools
    assert len(registry._tools["search_companies"].function("", 2)["companies"]) == 25
    result = registry._tools["read_company"].function("S00")
    assert "pe_ratio" not in json.dumps(result)
    assert result["observations"][0]["availability_basis"] == "estimated"
    with pytest.raises(ValueError):
        registry._tools["read_financials"].function("NVDA")
    asyncio.run(registry._tools["search_web"].function("query"))
    assert seen == [{"end_date": date(2023, 1, 1), "filter_by_published_date": True}]
    assert simulator.state["notifications"] == []


def test_two_years_fifty_companies_no_activity_is_valid(tmp_path):
    cfg = config()
    calls = []
    def worker(command, out, err):
        simulator = Simulator(Path(command[command.index("--simulation") + 1]))
        calls.append(simulator.state["date"])
        return fake_cli(command, out, err)
    campaign = tmp_path / "full"
    assert run_campaign(campaign, scenario=scenario(tmp_path, cfg), data=dataset(cfg),
                        launcher=worker, identity=lambda: {}) == 0
    assert len(calls) == 24 and len(set(calls)) == 24
    assert read(campaign / "communications.json") == []
    assert read(campaign / "history-final.json")["orders"] == []
    assert read(campaign / "portfolio-final.json")["cash"] == "100000"


def test_resume_rejects_changed_inputs_and_instructions(tmp_path):
    cfg = config(1)
    cfg["end"] = "2023-01-31"
    cfg["messages"].pop("2023-03-01")
    campaign = tmp_path / "frozen"
    run_campaign(campaign, scenario=scenario(tmp_path, cfg), data=dataset(cfg), launcher=fake_cli, identity=lambda: {})
    instructions = campaign / "agente/instrucciones/agente.md"
    original = instructions.read_bytes()
    instructions.write_text("changed", encoding="utf-8")
    with pytest.raises(ValueError, match="Instructions changed"):
        run_campaign(campaign, identity=lambda: {})
    instructions.write_bytes(original)
    source = read(campaign / "simulador/data.json")
    source["prices"][0]["close"] = "11"
    save(campaign / "simulador/data.json", source)
    with pytest.raises(ValueError, match="Frozen"):
        run_campaign(campaign, identity=lambda: {})


def test_missing_file_is_tool_failure_not_capture_loss(tmp_path, monkeypatch):
    from research_agent.integrations.file_tools import register_files
    from research_agent.recording import RunRecorder
    from research_agent.tools import ToolRegistry
    from research_agent.workspace import Workspace
    from runtime_contracts.llm import ResponseFunctionCall
    recorder = RunRecorder(tmp_path / "runs")
    recorder.start("test", {})
    registry = ToolRegistry(recorder)
    register_files(registry, Workspace(tmp_path / "memory"))
    result = asyncio.run(registry.execute(ResponseFunctionCall("missing", "read_file", {
        "path": "absent.md", "offset": 0, "max_bytes": 100})))
    assert not result.payload["ok"]
    assert not recorder.capture_errors
    def fail_capture(value):
        raise OSError("disk failure")
    monkeypatch.setattr(recorder, "artifact", fail_capture)
    result = asyncio.run(registry.execute(ResponseFunctionCall("capture", "list_files", {"path": "."})))
    assert not result.payload["ok"]
    assert recorder.capture_errors == [{"operation": "tool_capture", "error_type": "OSError"}]


def test_longitudinal_real_cli_subprocesses_with_controlled_provider(tmp_path):
    from research_benchmarks.runner import launch
    cfg = config(2)
    cfg["end"] = "2023-03-31"
    worker = tmp_path / "worker.py"
    worker.write_text('''
from contextlib import asynccontextmanager
import os
from pathlib import Path
from research_agent import cli
from research_agent.agent import AgentA
from research_agent.recording import RunRecorder
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from research_agent.integrations.file_tools import register_files
from research_agent.simulation.state import Simulator
from research_agent.simulation.tools import register_simulation
from runtime_contracts.llm import AssistantResponse, ResponseFunctionCall, ResponseTurn
from runtime_contracts.execution import current_run_context
from infra.adapters.llm_trace import LLMCallTrace
@asynccontextmanager
async def builder(workspace, runs, limits, **kwargs):
    simulator = Simulator(kwargs.pop('simulation'))
    recorder = RunRecorder(runs, **kwargs)
    space = Workspace(workspace)
    tools = ToolRegistry(recorder)
    register_files(tools, space)
    class Search:
        async def search_documents(self, *args, **kwargs):
            return []
    register_simulation(tools, simulator, Search())
    class Client:
        n = 0
        async def respond(self, **request):
            self.n += 1
            if self.n == 1:
                if str(simulator.today) == '2023-01-01':
                    item = ResponseFunctionCall('buy', 'portfolio_buy', {'symbol':'S00','amount':'100'})
                else:
                    assert (space.root/'memory.md').exists()
                    item = ResponseFunctionCall('read', 'read_file', {'path':'memory.md','offset':0,'max_bytes':100})
            elif self.n == 2:
                old = (space.root/'memory.md').read_text() if (space.root/'memory.md').exists() else ''
                item = ResponseFunctionCall('write', 'write_file', {'path':'memory.md','content':old+str(os.getpid())+'\\n'})
            else:
                item = AssistantResponse('done')
            turn = ResponseTurn([item], 'done' if self.n == 3 else '', item if self.n < 3 else None)
            LLMCallTrace(operation='conversation', model='controlled', provider_request={'input':[]}).emit(
                context=current_run_context(), response={'output':[]}, result=turn, operational_output=None,
                status='success', error_type=None, duration_ms=1)
            return turn
    yield AgentA(Client(), tools, space, recorder, limits)
cli.build_agent = builder
raise SystemExit(cli.main())
''', encoding="utf-8")
    def launcher(command, out, err):
        return launch([sys.executable, str(worker), *command[3:]], out, err)
    campaign = tmp_path / "cli-campaign"
    assert run_campaign(campaign, scenario=scenario(tmp_path, cfg), data=dataset(cfg),
                        launcher=launcher, identity=lambda: {}) == 0
    pids = (campaign / "agente/estado/memory.md").read_text().splitlines()
    assert len(pids) == 3 and len(set(pids)) == 3
    assert len(Simulator(campaign / "simulador").state["orders"]) == 1


def test_resume_after_interrupted_checkpoint_preparation(tmp_path, monkeypatch):
    import research_benchmarks.longitudinal as module
    cfg = config(1)
    cfg["end"] = "2023-01-31"
    cfg["messages"].pop("2023-03-01")
    original = module.shutil.copytree
    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt
    monkeypatch.setattr(module.shutil, "copytree", interrupted)
    campaign = tmp_path / "interrupted-checkpoint"
    with pytest.raises(KeyboardInterrupt):
        run_campaign(campaign, scenario=scenario(tmp_path, cfg), data=dataset(cfg), identity=lambda: {})
    monkeypatch.setattr(module.shutil, "copytree", original)
    assert run_campaign(campaign, launcher=fake_cli, identity=lambda: {}) == 0
    assert len(list((campaign / "intentos").iterdir())) == 2


@pytest.mark.parametrize("child_model, expected_code", [("frozen", 0), ("changed", 1)])
def test_child_profile_is_verified_before_committing_activation(tmp_path, child_model, expected_code):
    import hashlib
    cfg = config(1)
    cfg["end"] = "2023-01-31"
    cfg["messages"].pop("2023-03-01")
    packages = ("research_agent", "infra", "findata", "runtime_contracts")
    frozen = {"profile": {"model": "frozen"}, "source": {p: {} for p in packages}}
    def worker(command, out, err):
        code = fake_cli(command, out, err)
        experiment = Path(command[command.index("--experiment") + 1])
        name = command[command.index("--run-name") + 1]
        path = experiment / "ejecuciones" / name / "manifiesto.json"
        manifest = read(path)
        manifest["configuration"] = {"model": child_model, "code_sha256": {
            p: hashlib.sha256(repr([]).encode()).hexdigest() for p in packages}}
        save(path, manifest)
        return code
    campaign = tmp_path / "profile-check"
    assert run_campaign(campaign, scenario=scenario(tmp_path, cfg), data=dataset(cfg), launcher=worker,
                        identity=lambda: frozen) == expected_code
    progress = read(campaign / "progress.json")
    assert progress["next"] == (1 if expected_code == 0 else 0)
