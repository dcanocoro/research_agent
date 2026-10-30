"""Manual pilot preparation is reproducible, isolated and entirely offline."""
from pathlib import Path
import shutil
import socket
from contextlib import asynccontextmanager
import json

import pytest

from research_agent.integrations.file_tools import register_files
from research_agent.recording import RunRecorder
from research_agent.simulation.state import Simulator, read, save
from research_agent.simulation.tools import register_simulation
from research_agent.tools import ToolRegistry
from research_agent.workspace import Workspace
from research_campaigns import continuous as pilot
from research_agent.agent import AgentA
from runtime_contracts.llm import AssistantResponse, ConversationContext, ResponseFunctionCall, ResponseTurn


@pytest.fixture(params=["compact", "current"])
def prepared_inputs(tmp_path, monkeypatch, request):
    original_connect = socket.socket.connect

    def forbidden(sock, address):
        # Windows asyncio creates a loopback socket pair for its own event loop.
        if isinstance(address, tuple) and address[0] in {"127.0.0.1", "::1"}:
            return original_connect(sock, address)
        raise AssertionError("Network is forbidden during pilot preparation")

    monkeypatch.setattr(socket.socket, "connect", forbidden)
    definition = tmp_path / "definition"
    # The retired v1 definition is absent from the current checkout. Exercise two
    # synthetic budgets over the maintained definition without restoring a campaign.
    shutil.copytree(Path(__file__).parents[1] / "campaigns/contexto-continuo-v3", definition)
    config = read(definition / "scenario.json")
    if request.param == "compact":
        config["continuous"]["consolidation_threshold_bytes"] = 220000
    config["universe"] = [{"symbol": "TEST", "name": "Synthetic fixture"}]
    config["price_review"] = {"status": "approved", "basis": "synthetic"}
    source = tmp_path / "data.json"
    save(source, {"schema_version": "historical-input-v1", "price_basis": "synthetic",
                  "prices": [{"symbol": "TEST", "date": "2022-12-30", "close": "10"}],
                  "facts": [{"symbol": "TEST", "metric": "total_revenue", "value": "100", "unit": "currency",
                             "currency": "USD", "period": "2021-12-31", "period_type": "annual",
                             "published_at": None, "source_ref": "fixture", "provenance": {"provider": "fixture"}}]})
    config["dataset_sha256"] = pilot.digest(source)
    save(definition / "scenario.json", config)
    identity = {"profile": config["expected_profile"], "source": {"fixture": "fixed"}}
    monkeypatch.setattr(pilot, "runtime_identity", lambda: identity)
    return tmp_path / "pilot", definition, source, identity


def test_prepare_freezes_new_state_and_builds_luna_command_without_network(prepared_inputs):
    root, definition, source, _ = prepared_inputs
    before = source.read_bytes()
    pilot.prepare(root, definition, source)
    pilot.check(root)
    sim = Simulator(root / "simulador")
    assert sim.state == {"date": "2023-01-01", "cash": "100000", "positions": {}, "orders": [], "notifications": []}
    assert source.read_bytes() == before == (root / "simulador/data.json").read_bytes()
    assert list((root / "ejecuciones").iterdir()) == []
    from research_agent.continuity import AGENDA_TEMPLATE
    assert Workspace(root / "estado").snapshot() == {"agenda.md": AGENDA_TEMPLATE}
    command = read(root / "campaign.json")["command"]
    assert "--continuous" in command and "--context-bytes" in command and "--limits" not in command
    assert command[command.index("--max-calls") + 1] == "60"
    report = read(root / "campaign.json")["preflight"]
    assert report["ready"] and not report["provider_checked"] and not report["campaign_executed"]
    threshold = read(root / "definicion/scenario.json")["continuous"]["consolidation_threshold_bytes"]
    assert command[command.index("--consolidation-bytes") + 1] == str(threshold)
    assert report["initial_budget"]["budgeted_bytes"] + report["startup_margin_bytes"] < threshold
    assert read(root / "campaign.json")["runtime"]["profile"]["model"] == "gpt-6-luna"


@pytest.mark.parametrize("changed", ["definicion/mandato.md", "simulador/state.json", "definicion/peticion.md", "ejecuciones/attempt.txt"])
def test_check_rejects_changed_or_used_pilot(prepared_inputs, changed):
    root, definition, source, _ = prepared_inputs
    pilot.prepare(root, definition, source)
    with (root / changed).open("a", encoding="utf-8") as stream:
        stream.write("changed")
    with pytest.raises(ValueError, match="changed|already run"):
        pilot.check(root)


def test_check_rejects_runtime_drift_and_prepare_refuses_overwrite(prepared_inputs):
    root, definition, source, identity = prepared_inputs
    pilot.prepare(root, definition, source)
    identity["source"]["fixture"] = "changed"
    with pytest.raises(ValueError, match="Runtime changed"):
        pilot.check(root)
    with pytest.raises(FileExistsError):
        pilot.prepare(root, definition, source)


def test_prepare_rejects_wrong_data_or_profile_before_creating_destination(prepared_inputs):
    root, definition, source, identity = prepared_inputs
    with source.open("a") as stream:
        stream.write(" ")
    with pytest.raises(ValueError, match="hash mismatch"):
        pilot.prepare(root, definition, source)
    assert not root.exists()

    config = read(definition / "scenario.json")
    config["dataset_sha256"] = pilot.digest(source)
    save(definition / "scenario.json", config)
    identity["profile"] = {**identity["profile"], "model": "different"}
    with pytest.raises(ValueError, match="model/profile"):
        pilot.prepare(root, definition, source)
    assert not root.exists()


def test_run_integrates_preparation_launch_report_and_frozen_profile(prepared_inputs):
    from support import fake_cli
    root, definition, source, identity = prepared_inputs
    def worker(command, out, err):
        assert Path(command[command.index("--experiment") + 1]) == root
        assert (root / "README.md").is_file()
        result = fake_cli(command, out, err)
        manifest = root / "ejecuciones/piloto/manifiesto.json"
        value = read(manifest)
        value["configuration"] = identity["profile"]
        save(manifest, value)
        return result
    assert pilot.run_campaign(root, definition, source, launcher=worker) == 0
    record = read(root / "campaign.json")
    assert record["mode"] == "continuous" and record["status"] == "completed"
    assert "--continuous" in record["sessions"][0]["command"]
    assert not any((root / name).exists() for name in ("command.json", "preparacion.json", "preflight.json", "agente"))
    assert "Respuesta" in (root / "README.md").read_text(encoding="utf-8")


def test_fixed_corpus_pilot_offers_no_web_tool_but_legacy_default_keeps_it(prepared_inputs):
    root, definition, source, _ = prepared_inputs
    pilot.prepare(root, definition, source)
    simulator = Simulator(root / "simulador")
    for allow_web in (False, True):
        simulator.config["allow_web"] = allow_web
        registry = ToolRegistry(RunRecorder(root / "runs"))
        register_files(registry, Workspace(root / "estado"))
        register_simulation(registry, simulator, None)
        assert ("search_web" in {tool.name for tool in registry.specs()}) is allow_web
    del simulator.config["allow_web"]
    registry = ToolRegistry(RunRecorder(root / "runs"))
    register_simulation(registry, simulator, None)
    assert "search_web" in {tool.name for tool in registry.specs()}


def test_prepared_cli_crosses_three_windows_with_real_prompts_and_luna_reserve(prepared_inputs, monkeypatch):
    from research_agent.cli import main
    root, definition, source, identity = prepared_inputs
    pilot.prepare(root, definition, source)

    class Client:
        written: set[int] = set()

        async def respond(self, **kwargs):
            assert kwargs["max_tokens"] == 16000
            budget = next(x.payload["execution_budget"] for x in reversed(kwargs["input_items"])
                          if isinstance(x, ConversationContext) and "execution_budget" in x.payload)
            n = budget["context_number"]
            if not any(t.name == "calculate" for t in kwargs["tools"]):
                if n not in self.written:
                    self.written.add(n)
                    call = ResponseFunctionCall("call", "write_file", {"path": "agenda.md", "content": f"Pregunta pendiente {n + 1}"})
                    return ResponseTurn([call], "", call)
                return ResponseTurn([AssistantResponse("Conservado")], "Conservado", None)
            if n < 3:
                value = "observacion material " * 2000
                return ResponseTurn([AssistantResponse(value)], value, None)
            assert "Pregunta pendiente 3" in str(kwargs["input_items"])
            return ResponseTurn([AssistantResponse("Recuperado")], "Recuperado", None)

    @asynccontextmanager
    async def build(workspace, runs, limits, *, experiment, run_name, simulation, state_tools="legacy"):
        space = Workspace(workspace)
        recorder = RunRecorder(runs, experiment=experiment, run_name=run_name)
        registry = ToolRegistry(recorder)
        register_files(registry, space, state_tools=state_tools)
        simulator = Simulator(simulation)
        register_simulation(registry, simulator, None)
        yield AgentA(Client(), registry, space, recorder, limits,
                     configuration={**identity["profile"], "simulated_date": str(simulator.today)})

    monkeypatch.setattr("research_agent.cli.build_agent", build)
    command = read(root / "campaign.json")["command"][3:]
    # V3 needs two research responses per window before crossing its higher threshold.
    command[command.index("--max-calls") + 1] = "14"
    assert main(command) == 0
    run = next((root / "ejecuciones").iterdir())
    events = [json.loads(line) for line in (run / "eventos.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len([e for e in events if e["event"] == "lab.context.renewed"]) == 3
    assert all(e["budgeted_bytes"] <= 524288 for e in events if e["event"] == "lab.context.budget")
    result = read(run / "resultado.json")
    assert result["stop_reason"] == "call_limit" and result["answer"] == "Recuperado"
    assert not result["state"]["capture_errors"]
    assert Simulator(root / "simulador").state["date"] == "2023-01-01"
