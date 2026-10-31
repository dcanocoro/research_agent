"""Shared process execution and capture inspection for all campaign modes."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
from time import monotonic
from typing import Any, Callable
from .evidence import inspect_run
from .report import persist

def launch(command: list[str], stdout: Path, stderr: Path) -> int:
    """No shell, no output parsing. Let Ctrl+C reach the child before forcing exit."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    with stdout.open("wb") as out, stderr.open("wb") as err:
        child = subprocess.Popen(command, stdout=out, stderr=err, env=env)
        try:
            return child.wait()
        except KeyboardInterrupt:
            try:
                child.wait(timeout=5)
            except (subprocess.TimeoutExpired, KeyboardInterrupt):
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait()
            raise



def execute(root: Path, experiment: Path, record: dict[str, Any], session: dict[str, Any],
            command: list[str], *, launcher: Callable[[list[str], Path, Path], int] = launch) -> None:
    """Persist intent before launch; retain partial capture on all exit paths."""
    logs = experiment / "ejecuciones"
    before = {p.name for p in logs.iterdir() if p.is_dir() and (p / "manifiesto.json").is_file()}
    session.update(status="running", command=command, runs_before=sorted(before))
    for key in ("stdout", "stderr"):
        session[key] = (logs / f"{session['id']}.{key}.txt").relative_to(root).as_posix()
    record["status"] = "running"
    persist(root, record)
    start = monotonic()
    try:
        session["returncode"] = launcher(command, root / session["stdout"], root / session["stderr"])
    except KeyboardInterrupt:
        session.update(status="interrupted", error="KeyboardInterrupt")
    except Exception as exc:
        session.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    finally:
        session["elapsed_seconds"] = round(monotonic() - start, 3)
        runs = [p for p in logs.iterdir()
                if p.is_dir() and (p / "manifiesto.json").is_file() and p.name not in before]
        if len(runs) == 1:
            details = inspect_run(root, runs[0], record["runtime"], (record.get("objective") or {}).get("sha256"))
            session.update(details)
        else:
            session.update(capture_complete=False, capture_errors=[{"error": "Expected exactly one native run", "found": len(runs)}])
        if session["status"] == "running":
            session["status"] = "completed" if session.get("returncode") == 0 and session.get("agent_status") == "completed" and session["capture_complete"] else "failed"
        for key in ("stdout", "stderr"):
            path = root / session[key]
            if path.exists() and (not path.stat().st_size or key == "stdout" and session["status"] == "completed"):
                path.unlink()
                session.pop(key)
        record["status"] = session["status"]
        record["stop_reason"] = session.get("error") or session.get("stop_reason")
        persist(root, record)
