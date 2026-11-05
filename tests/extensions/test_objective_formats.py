import hashlib
import json
import pytest
from research_agent.extensions.progress.objective import Objective, Criterion
from research_agent.contracts import AgentRequest

@pytest.mark.parametrize("value", [
    {"id": "x", "goal": "Explain", "criteria": ["Grounded"]},
    {"id": "x", "description": "Explain", "criteria": {"c": "Grounded"}},
    {"id": "x", "description": "Explain", "criteria": {"c": "Grounded"}, "assessment_path": "empresas/MSFT/evaluacion.md"},
])
def test_objective_formats_preserve_definition_hash_and_select_progress(value):
    objective = Objective.from_dict(value)
    definition = objective.definition()
    expected = hashlib.sha256(json.dumps(definition, ensure_ascii=False, sort_keys=True, allow_nan=False).encode()).hexdigest()
    assert objective.sha256 == expected
    assert AgentRequest("Question", "w", "c", objective=objective).progress
    if "assessment_path" in value:
        assert definition["assessment_path"] == value["assessment_path"]

@pytest.mark.parametrize("path", ["../outside.md", "materiales/data.md", "C:/private.md", "empty.txt"])
def test_historical_assessment_path_still_validates(path):
    with pytest.raises(ValueError, match="assessment_path"):
        Objective.from_dict({"id": "x", "description": "Explain", "criteria": {"c": "Grounded"}, "assessment_path": path})


def objective(**changes):
    return Objective.from_dict({"id": "business", "description": "Explicar negocio TEST",
        "criteria": {"products": "Explicar productos", "revenue": "Explicar ingresos"}, **changes})


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
    assert AgentRequest("m", "w", "c", objective=value).progress


def test_cli_validates_objective_before_clients_or_experiment_creation(tmp_path, monkeypatch):
    import research_agent.cli.main as cli
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



def test_new_objective_hash_and_old_definition_roundtrip():
    old = objective()
    assert 'assessment_path' not in old.definition()
    value = objective(assessment_path='evaluacion.md')
    assert Objective.from_dict(value.definition()) == value and value.sha256 != old.sha256

