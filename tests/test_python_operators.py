"""Local numerical references, capture, process lifecycle and POC restrictions."""
import asyncio
import json
import re
import sys
from importlib import metadata
from importlib.resources import files
from pathlib import Path

import pytest
from runtime_contracts.llm import ResponseFunctionCall, ToolResult

from research_agent.integrations import python_tools as python
from research_agent.python_worker import validate_code
from research_agent.contracts import AgentLimits
from research_agent.recording import encoded
from test_agent import agent, request, response


@pytest.fixture
def configuration():
    try:
        return python.python_configuration()
    except ValueError:
        pytest.skip("Install .[python] to run scientific worker tests")


@pytest.fixture
def registered(tmp_path, configuration):
    a = agent(tmp_path, [])
    python.register_python(a.tools, a.workspace, configuration)
    a.recorder.start("python-test", {})
    return a


def call(a, code, operator="calculate", **kwargs):
    args = {"operator": operator, "code": code, "inputs": {}, "input_refs": {},
            "parameters": {}, "source_refs": [], **kwargs}
    result = asyncio.run(a.tools.execute(ResponseFunctionCall("python-call", "run_python", wire(args))))
    return json.loads(encoded(result.payload))


def wire(arguments):
    return {key + "_json" if key in {"inputs", "input_refs", "parameters"} else key:
            json.dumps(value, ensure_ascii=False) if key in {"inputs", "input_refs", "parameters"} else value
            for key, value in arguments.items()}


def example(operator):
    text = files("research_agent").joinpath(f"python_contracts/{operator}.md").read_text(encoding="utf-8")
    code = re.search(r"```python\n(.*?)```", text, re.S).group(1)
    objects = re.findall(r"```json\n(.*?)```", text, re.S)
    invocation = json.loads(objects[2])
    assert invocation == wire({"operator": operator, "code": code, "inputs": json.loads(objects[0]),
                               "input_refs": {}, "parameters": json.loads(objects[1]), "source_refs": []})
    return code, json.loads(objects[0]), json.loads(objects[1])


@pytest.mark.parametrize("operator", python.OPERATORS)
def test_documented_examples_against_independent_references(registered, operator):
    code, inputs, parameters = example(operator)
    corpus = json.loads((Path(__file__).parents[1] / "docs/experiments/python-operators-v1/fixtures.json").read_text(encoding="utf-8"))
    fixture = next(item for item in corpus["cases"] if item["operator"] == operator)
    assert fixture["inputs"] == inputs and fixture["parameters"] == parameters
    payload = call(registered, code, operator, inputs=inputs, parameters=parameters, source_refs=["synthetic-v1"])
    assert payload["ok"], payload
    value = payload["value"]
    result = value["result"]
    if operator == "calculate":
        assert result["operating_margin"] == pytest.approx([0.2, 0.25])
    elif operator == "transform":
        assert result["rows"] == [{"period": "2023", "revenue": 100, "fcf": None},
                                  {"period": "2024", "revenue": None, "fcf": 15}]
    elif operator == "evaluate":
        assert result["rows"] == [{"symbol": "A", "passes": True}, {"symbol": "B", "passes": None}]
    else:
        # Closed-form growing annuity plus terminal value, independent of worker's loop.
        for row in result["scenarios"]:
            d = row["discount"]
            annuity = 10.5 / (d - 0.05) * (1 - (1.05 / (1 + d)) ** 5)
            terminal = 10 * 1.05 ** 5 * 1.02 / (d - 0.02) / (1 + d) ** 5
            assert row["enterprise_value"] == pytest.approx(annuity + terminal)
        values = [r["enterprise_value"] for r in result["scenarios"]]
        assert values == sorted(values, reverse=True)
    assert value["source_refs"] == ["synthetic-v1"]
    captured = registered.recorder.read_artifact(value["execution_ref"])
    record = json.loads(captured["text"])
    assert record["code"] == code and record["inputs"] == inputs
    material = json.loads(registered.workspace.path(payload["material_ref"]).read_text(encoding="utf-8"))
    assert material["result"] == result


def test_all_libraries_available(registered):
    payload = call(registered, """import numpy_financial as npf
from scipy import stats
import statistics
import math
def run(inputs, parameters):
    return {"npv": float(npf.npv(0.1, [-100, 60, 60])),
            "cdf": float(stats.norm.cdf(0)), "mean": statistics.mean([1, 3]), "sqrt": math.sqrt(4)}
""")
    assert payload["ok"], payload
    assert payload["value"]["result"] == pytest.approx({"npv": 4.132231404958674, "cdf": 0.5, "mean": 2, "sqrt": 2})


def test_reference_resolution_and_frozen_inputs(registered):
    registered.workspace.write_file("data/observations.json", '{"value": 7, "currency": "USD"}')
    registered.workspace.write_file("data/rows.csv", "period,value\n2023,5\n2024,6\n")
    payload = call(registered, """def run(inputs, parameters):
    return {"total": inputs["observed"]["value"] + sum(int(row["value"]) for row in inputs["rows"])}
""", input_refs={"observed": "data/observations.json", "rows": "data/rows.csv"})
    assert payload["ok"], payload
    assert payload["value"]["result"]["total"] == 18
    registered.workspace.write_file("data/observations.json", '{"value": 0}')
    frozen = json.loads(registered.recorder.read_artifact(payload["value"]["execution_ref"])["text"])
    assert frozen["inputs"]["observed"] == {"value": 7, "currency": "USD"}
    assert frozen["inputs"]["rows"][0]["value"] == "5"
    material = payload["material_ref"]
    chained = call(registered, 'def run(inputs, parameters):\n    return {"total": inputs["prior"]["result"]["total"] * 2}', input_refs={"prior": material})
    assert chained["value"]["result"]["total"] == 36


@pytest.mark.parametrize("code,category", [
    ("def run(:", "syntax"),
    ("def other(inputs, parameters):\n    return {}", "contract"),
    ("def run(data):\n    return {}", "contract"),
    ("value = 3\ndef run(inputs, parameters):\n    return {}", "contract"),
    ("import os\ndef run(inputs, parameters):\n    return {}", "restricted"),
    ("def run(inputs, parameters):\n    return open('x')", "restricted"),
    ("import pandas as pd\ndef run(inputs, parameters):\n    return pd.read_csv('https://example.test')", "restricted"),
    ("def run(inputs, parameters):\n    return inputs.__class__", "restricted"),
    ("def run(inputs, parameters):\n    return eval('2')", "restricted"),
    ("import numpy as np\ndef run(inputs, parameters):\n    return np.load('x')", "restricted"),
])
def test_static_failures_are_actionable_and_captured(registered, code, category):
    payload = call(registered, code)
    assert not payload["ok"] and category in payload["message"]
    prepared = [e for e in registered.recorder.events if e["event"] == "lab.python.prepared"]
    assert prepared
    frozen = json.loads(registered.recorder.read_artifact(prepared[-1]["execution_ref"])["text"])
    assert frozen["code"] == code


@pytest.mark.parametrize("code,message", [
    ('def run(inputs, parameters):\n    return {"x": 1 / 0}', "ZeroDivisionError at line 2"),
    ('def run(inputs, parameters):\n    return {"x": float("nan")}', "JSON"),
    ('def run(inputs, parameters):\n    return {"x": {1, 2}}', "serializable"),
    ('import numpy as np\ndef run(inputs, parameters):\n    return {"x": np.array([1])}', "serializable"),
    ('def run(inputs, parameters):\n    return [1, 2]', "JSON object"),
    ('def run(inputs, parameters):\n    return {"x": "a" * 1100000}', "limit"),
])
def test_worker_errors(registered, code, message):
    payload = call(registered, code)
    assert not payload["ok"] and message in payload["message"], payload


@pytest.mark.parametrize("operator,parameters", [("model", {}), ("evaluate", {}), ("model", {"assumptions": []})])
def test_specific_contract_requirements(registered, operator, parameters):
    payload = call(registered, "def run(inputs, parameters):\n    return {}", operator, parameters=parameters)
    assert not payload["ok"] and "contract" in payload["message"]


def test_input_limits_and_paths(registered):
    code = "def run(inputs, parameters):\n    return {}"
    for kwargs in ({"inputs": {"x": "a" * 1048576}},
                   {"inputs": {"x": 1}, "input_refs": {"x": "absent.json"}},
                   {"input_refs": {"x": "../outside.json"}},
                   {"input_refs": {"x": "notes.md"}}):
        assert not call(registered, code, **kwargs)["ok"]
    assert not call(registered, code + "\n#" + "á" * 20000)["ok"]


def test_large_result_uses_existing_pagination(registered):
    payload = call(registered, 'def run(inputs, parameters):\n    return {"rows": list(range(10000))}')
    assert payload["ok"] and payload["value"]["limited"]
    first = registered.recorder.read_artifact(payload["material_ref"])
    assert first["next_offset"] == 32768
    second = registered.recorder.read_artifact(payload["material_ref"], first["next_offset"])
    value = json.loads(first["text"] + second["text"])
    assert len(value["result"]["rows"]) == 10000


@pytest.mark.parametrize("cancel", [False, True])
def test_timeout_and_cancellation_reap_real_process(monkeypatch, cancel):
    original = asyncio.create_subprocess_exec
    children = []

    async def track(*args, **kwargs):
        # Exercise lifecycle even when the scientific extra is not installed.
        child = await original(args[0], "-I", "-S", "-c", "while True:\n    pass", **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(asyncio, "create_subprocess_exec", track)

    async def exercise():
        request_value = {"code": "def run(inputs, parameters):\n    while True:\n        pass",
                         "inputs": {}, "parameters": {}, "max_output_bytes": 1048576}
        task = asyncio.create_task(python.run_worker(request_value, timeout=0.2 if not cancel else 30))
        if cancel:
            while not children:
                await asyncio.sleep(0.01)
            task.cancel()
        with pytest.raises(asyncio.CancelledError if cancel else ValueError):
            await task
        assert children and all(child.returncode is not None for child in children)

    asyncio.run(exercise())


@pytest.mark.parametrize("stream", ["stdout", "stderr"])
def test_pipe_overflow_and_minimal_environment(monkeypatch, stream):
    original = asyncio.create_subprocess_exec
    children = []
    monkeypatch.setenv("RESEARCH_TEST_SECRET", "never-inherit")

    async def replace_command(*args, **kwargs):
        assert "RESEARCH_TEST_SECRET" not in kwargs["env"]
        assert kwargs["env"]["OMP_NUM_THREADS"] == "1"
        assert "-I" in args
        script = f"import sys; sys.{stream}.write('x' * 1200000); sys.{stream}.flush()"
        child = await original(getattr(sys, "_base_executable", sys.executable), "-I", "-c", script, **kwargs)
        children.append(child)
        return child

    monkeypatch.setattr(asyncio, "create_subprocess_exec", replace_command)
    with pytest.raises(ValueError, match="limit"):
        asyncio.run(python.run_worker({}))
    assert children[0].returncode is not None


def test_optional_dependencies_fail_before_clients_or_experiment(monkeypatch, tmp_path):
    from research_agent.cli import main

    def missing(name):
        raise metadata.PackageNotFoundError(name)

    monkeypatch.setattr(metadata, "version", missing)
    with pytest.raises(ValueError, match="pip install"):
        python.python_configuration()
    target = tmp_path / "not-created"
    with pytest.raises(SystemExit) as exc:
        main(["test", "--experiment", str(target), "--new", "--run-name", "test", "--python"])
    assert exc.value.code == 2 and not target.exists()


def test_agent_discovers_corrects_and_interprets(tmp_path, configuration):
    arguments = {"operator": "calculate", "code": "def run(inputs, parameters):\n    return {\"x\": 1 / 0}",
                 "inputs": {}, "input_refs": {}, "parameters": {}, "source_refs": ["synthetic"]}
    fixed = {**arguments, "code": 'def run(inputs, parameters):\n    return {"x": 1 / 2}'}
    a = agent(tmp_path, [response(call=("describe_python_operator", {"operator": "calculate"})),
                         response(call=("run_python", wire(arguments))), response(call=("run_python", wire(fixed))),
                         response("La fracción calculada es 0,5.")], AgentLimits(max_llm_calls=8))
    assert "run_python" not in {s.name for s in a.tools.specs()}
    python.register_python(a.tools, a.workspace, configuration)
    assert not {"run_python", "describe_python_operator"} & a.tools.consolidation_tools
    result = asyncio.run(a.run(request()))
    assert result.status == "completed" and result.tool_calls == 3
    delivered = [item for item in a.history if isinstance(item, ToolResult) and item.name == "run_python"]
    assert not delivered[0].payload["ok"] and delivered[1].payload["value"]["result"] == {"x": 0.5}


def test_restrictions_without_scientific_dependencies():
    validate_code("def run(inputs, parameters):\n    return {\"value\": sum(inputs[\"x\"])}")
    with pytest.raises(ValueError, match="restricted"):
        validate_code("import subprocess\ndef run(inputs, parameters):\n    return {}")


def test_strict_provider_schema_and_json_validation(registered):
    spec = next(s for s in registered.tools.specs() if s.name == "run_python")

    def check(value):
        if isinstance(value, dict):
            if value.get("type") == "object":
                assert value.get("additionalProperties") is False
                assert set(value.get("required", [])) == set(value["properties"])
            for child in value.values():
                check(child)
        elif isinstance(value, (tuple, list)):
            for child in value:
                check(child)

    check(spec.parameters)
    for malformed in ("{", "[]", '{"x": NaN}'):
        args = wire({"operator": "calculate", "code": "def run(inputs, parameters):\n    return {}",
                     "inputs": {}, "input_refs": {}, "parameters": {}, "source_refs": []})
        args["inputs_json"] = malformed
        result = asyncio.run(registered.tools.execute(ResponseFunctionCall("bad-json", "run_python", args)))
        assert not result.payload["ok"] and "inputs_json" in result.payload["message"]


@pytest.mark.parametrize("simulation", [False, True])
def test_cli_composition_captures_environment_and_preserves_copies(tmp_path, monkeypatch, configuration, simulation):
    from dataclasses import dataclass
    from types import SimpleNamespace
    from research_agent.cli import main
    import infra.llm_factory as llm
    import infra.adapters.tavily_web_search as web
    import infra.adapters.tavily_documents as documents
    import sqlalchemy
    from support import ScriptedClient

    @dataclass
    class Profile:
        name: str = "test"
        provider: str = "test"
        model: str = "scripted"
        max_output_tokens: int = 128

    class Factory:
        def __init__(self, settings):
            pass

        def conversation(self, profile):
            return ScriptedClient([response(call=("run_python", wire({
                "operator": "calculate", "code": 'def run(inputs, parameters):\n    return {"x": 2}',
                "inputs": {}, "input_refs": {}, "parameters": {}, "source_refs": []}))), response("Computed")])

        async def aclose(self):
            pass

    monkeypatch.setattr(llm, "LLMFactory", Factory)
    monkeypatch.setattr(llm, "configured_profile", lambda *a: Profile())
    monkeypatch.setattr(web, "TavilyWebSearchTool", lambda **kw: SimpleNamespace())
    monkeypatch.setattr(documents, "TavilyDocumentReader", lambda **kw: SimpleNamespace())
    real_engine = sqlalchemy.create_engine
    monkeypatch.setattr(sqlalchemy, "create_engine", lambda *a, **kw: real_engine("sqlite://"))
    root = tmp_path / "experiment"
    options = []
    if simulation:
        from test_longitudinal import sim
        simulator = sim(tmp_path, count=1)
        options = ["--simulation", str(simulator.root)]
    assert main(["Compute", "--experiment", str(root), "--new", "--run-name", "initial", "--python", *options]) == 0
    run = next((root / "ejecuciones").iterdir())
    manifest = json.loads((run / "manifiesto.json").read_text(encoding="utf-8"))
    assert manifest["configuration"]["python_operators"] == configuration
    assert {"run_python", "describe_python_operator"} <= {t["name"] for t in manifest["tools"]}
    assert json.loads((run / "resultado.json").read_text(encoding="utf-8"))["state"]["materials"]
    # Continuing does not update instructions and absence of --python disables it.
    (root / "instrucciones/agente.md").write_text("Custom frozen instructions", encoding="utf-8")
    assert main(["Continue", "--experiment", str(root), "--continue", "--run-name", "resume", *options]) == 0
    second = next(r for r in (root / "ejecuciones").iterdir() if r != run)
    metadata_value = json.loads((second / "manifiesto.json").read_text(encoding="utf-8"))
    assert metadata_value["configuration"]["python_operators"] == {"enabled": False}
    assert "run_python" not in {t["name"] for t in metadata_value["tools"]}
    assert (root / "instrucciones/agente.md").read_text(encoding="utf-8") == "Custom frozen instructions"


def test_python_in_continuous_mode(tmp_path, configuration):
    from dataclasses import replace
    from test_continuous import make
    from research_agent.contracts import ContinuousConfig
    a, req = make(tmp_path, [response(call=("run_python", wire({
        "operator": "calculate", "code": 'def run(inputs, parameters):\n    return {"x": 4}',
        "inputs": {}, "input_refs": {}, "parameters": {}, "source_refs": []}))), response("Observed 4")],
        config=ContinuousConfig(max_llm_calls=2))
    python.register_python(a.tools, a.workspace, configuration)
    a.configuration["python_operators"] = configuration
    result = asyncio.run(a.run(replace(req)))
    assert result.stop_reason == "call_limit" and result.tool_calls == 1
    assert "Observed 4" == result.answer
    assert result.state.materials and not result.state.capture_errors
