"""Rebuild local execution observations from native captures; no provider calls."""
from pathlib import Path
from collections import Counter
from datetime import datetime
import gzip
import hashlib
import json

BASE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def summarize(condition):
    root = BASE / f"artifacts/intencion-amplia-{condition}-v1"
    progress = read(root / "progress.json")
    sessions = []
    for attempt in progress["attempts"]:
        if attempt["status"] != "completed":
            continue
        run = root / "agente/ejecuciones" / attempt["run"]
        result = read(run / "resultado.json")
        manifest = read(run / "manifiesto.json")
        events = [json.loads(line) for line in (run / "eventos.jsonl").read_text(encoding="utf-8").splitlines()]
        tools = [e for e in events if e["event"] == "lab.tool.started"]
        capture = read(root / "intentos" / attempt["id"] / "capture.json")
        usage = Counter()
        payloads = 0
        for path in (run / "trazas").glob("modelo-*.json.gz"):
            with gzip.open(path, "rt", encoding="utf-8") as stream:
                payload = json.load(stream)
            raw = payload.get("provider_output", {}).get("usage") or {}
            payloads += 1
            for field in ("input_tokens", "output_tokens"):
                usage[field] += raw.get(field) or 0
            usage["cached_input_tokens"] += (raw.get("input_tokens_details") or {}).get("cached_tokens") or 0
            usage["reasoning_output_tokens"] += (raw.get("output_tokens_details") or {}).get("reasoning_tokens") or 0
        sessions.append({
            "date": attempt["activation"]["date"], "kind": attempt["activation"]["kind"],
            "run": str(run.relative_to(BASE)), "status": result["status"],
            "stop_reason": result["stop_reason"], "llm_calls": result["llm_calls"], "tool_calls": result["tool_calls"],
            "seconds": (datetime.fromisoformat(events[-1]["occurred_at"]) - datetime.fromisoformat(events[0]["occurred_at"])).total_seconds(),
            "capture_complete": capture["capture_complete"], "capture_errors": capture["capture_errors"],
            "tool_counts": dict(Counter(e["tool_name"] for e in tools)),
            "financial_symbols": sorted({e["arguments"]["symbol"] for e in tools if e["tool_name"] in {"read_company", "read_financials"}}),
            "tool_failures": [{k:e.get(k) for k in ("tool_name", "error_type", "message")} for e in events if e["event"] == "lab.tool.failed"],
            "files_written": result["state"]["files_written"], "usage": dict(usage), "provider_payloads": payloads,
            "persistent_context": manifest.get("persistent_context"),
        })
    counts = Counter()
    usage = Counter()
    for session in sessions:
        counts.update(session["tool_counts"])
        usage.update(session["usage"])
    return {"condition":condition, "root":str(root.relative_to(BASE)), "finished":progress["finished"],
            "activations_completed":progress["next"], "attempts":len(progress["attempts"]),
            "scenario_sha256":hashlib.sha256((root/"definiciones/scenario.json").read_bytes()).hexdigest(),
            "data_sha256":hashlib.sha256((root/"simulador/data.json").read_bytes()).hexdigest(),
            "runtime_sha256":hashlib.sha256((root/"runtime.json").read_bytes()).hexdigest(),
            "sessions":sessions, "llm_calls":sum(s["llm_calls"] for s in sessions),
            "tool_calls":sum(s["tool_calls"] for s in sessions), "usage":dict(usage),
            "tool_counts":dict(counts), "financial_symbols":sorted({symbol for s in sessions for symbol in s["financial_symbols"]})}


report = {"schema_version":"intention-observations-v1", "semantic_review":"partial; see findings", "conditions":[summarize(c) for c in ("baseline", "deliberative")]}
(OUT / "observaciones.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
print(json.dumps([{k:v for k,v in c.items() if k not in {"sessions","root","tool_counts"}} for c in report["conditions"]], ensure_ascii=False, indent=2))
