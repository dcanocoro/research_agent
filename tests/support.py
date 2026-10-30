"""Deterministic clients and native campaign fixtures shared by local tests."""
import gzip
import json
from pathlib import Path
import yaml
from research_campaigns.storage import save


class ScriptedClient:
    def __init__(self, turns):
        self.turns = iter(turns)
        self.requests = []
        self.review_requests = []

    async def respond(self, **kwargs):
        if any(getattr(item, "payload", {}).get("review_packet") for item in kwargs["input_items"]):
            self.review_requests.append(kwargs)
            return review_turn()
        self.requests.append(kwargs)
        turn = next(self.turns)
        if isinstance(turn, BaseException):
            raise turn
        return turn


def catalog(tmp_path, cases=2, sessions=2):
    root = tmp_path / "suite"
    root.mkdir()
    paths = []
    for n in range(cases):
        case = root / f"C{n}"
        case.mkdir()
        (case / "source.md").write_text("initial evidence", encoding="utf-8")
        (case / "future.md").write_text("future evidence", encoding="utf-8")
        (case / "rubric.md").write_text("EVALUATOR ONLY", encoding="utf-8")
        value = {"id": f"C{n}", "title": "Test", "context": "Company", "competencies": ["memory"],
                 "difficulty": "Requires recovery", "rubric": "rubric.md", "sessions": [
                     {"id": f"s{i}", "message": f"Question {i}",
                      "publish": {"entradas/initial.md": "source.md"} if i == 0 else
                                 {"entradas/future.md": "future.md"} if i == 1 else {}}
                     for i in range(sessions)]}
        (case / "case.yaml").write_text(yaml.safe_dump(value), encoding="utf-8")
        paths.append(f"C{n}/case.yaml")
    (root / "suite.yaml").write_text(yaml.safe_dump({"schema_version": "campaign-suite-v1", "id": "test", "cases": paths}), encoding="utf-8")
    return root


def fake_cli(command, out, err, *, status="completed", missing=None):
    """Small native-format fixture, not a replacement used by the product runner."""
    experiment = Path(command[command.index("--experiment") + 1])
    session = command[command.index("--run-name") + 1]
    run = experiment / "ejecuciones" / session
    run.mkdir()
    (run / "trazas").mkdir()
    out.write_text("arbitrary output; never parsed", encoding="utf-8")
    err.write_text("diagnostic", encoding="utf-8")
    run_id = f"run-{experiment.name}-{session}"
    save(run / "manifiesto.json", {"run_id": run_id})
    save(run / "resultado.json", {"run_id": run_id, "status": status, "stop_reason": "answered", "answer": "done",
                                 "llm_calls": 1, "tool_calls": 0, "state": {"capture_errors": []}})
    save(run / "estado-inicial.json", {})
    save(run / "estado-final.json", {})
    save(run / "conversacion.json", [])
    (run / "peticion.md").write_text(command[3], encoding="utf-8")
    (run / "respuesta.md").write_text("done", encoding="utf-8")
    native = [{"run_id": run_id, "event": "lab.run.started", "occurred_at": "2026-10-20T00:00:00+00:00"},
              {"run_id": run_id, "event": f"lab.run.{status}", "occurred_at": "2026-10-20T00:00:02+00:00"}]
    (run / "eventos.jsonl").write_text("\n".join(json.dumps(e) for e in native), encoding="utf-8")
    event = {"run_id": run_id, "event": "engine.llm_call", "llm_call_id": run_id + "-llm",
             "occurred_at": "2026-10-20T00:00:01+00:00", "archive_file": "modelo-0001.json.gz"}
    (run / "trazas/events.jsonl").write_text(json.dumps(event) + "\n", encoding="utf-8")
    with gzip.open(run / "trazas/modelo-0001.json.gz", "wt", encoding="utf-8") as stream:
        json.dump({"provider_input": {"input": ["question"]}, "provider_output": {"text": "done"}}, stream)
    if missing:
        (run / missing).unlink()
    return 0 if status == "completed" else 1


def review_turn():
    from runtime_contracts.llm import AssistantResponse, ResponseTurn
    value = json.dumps({"progress": "No evaluado por fixture", "blockers": [], "findings": [], "recommendations": []})
    return ResponseTurn([AssistantResponse(value)], value, None)
