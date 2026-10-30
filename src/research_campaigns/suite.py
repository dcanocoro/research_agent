"""Sequential document publication with isolated, file-persistent cases."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import sys
from typing import Any, Callable

from research_agent.contracts import AgentLimits
from research_agent.experiments import prepare_experiment, git_state
from research_agent.workspace import Workspace
from .catalog import Suite, load_suite
from .report import persist
from .runner import launch, execute
from .storage import create, digest, freeze_files, dependencies


def run_suite(suite: Suite, output: Path, selected: str | None = None, *,
              state_tools: str = "v5",
              launcher: Callable[[list[str], Path, Path], int] = launch) -> tuple[Path, int]:
    if selected is not None and selected not in {c.id for c in suite.cases}:
        raise ValueError(f"Unknown case: {selected}")
    root = output.absolute()
    record = create(root, suite.root, "suite", suite.id, suite.files())
    suite = load_suite(root / "definicion")
    import research_agent
    source = Path(str(research_agent.__file__)).parent
    record.update(limits=asdict(AgentLimits()), runtime={"dependencies": dependencies(), "python": sys.version,
        "git": git_state(Path(__file__).resolve().parents[2]),
        "source": {name: {p.relative_to(folder).as_posix(): digest(p) for p in sorted(folder.rglob("*")) if p.suffix in {".py", ".md"}}
                   for name, folder in (("research_agent", source), ("research_campaigns", Path(__file__).parent))}})
    persist(root, record)
    interrupted = False
    for case in suite.cases:
        if selected is not None and case.id != selected:
            continue
        experiment = root / "casos" / case.id
        prepare_experiment(experiment, new=True, state_tools=state_tools)
        Workspace(experiment / "estado").write_file("indice.md", case.context + "\n\nEntradas disponibles:\n" +
            "".join(f"- {p.target}\n" for p in case.sessions[0].publish))
        record.setdefault("instructions_sha256", {})[case.id] = freeze_files(experiment / "instrucciones")
        blocked = interrupted
        published: dict[str, str] = {}
        for definition in case.sessions:
            session: dict[str, Any] = {"id": f"{case.id}-{definition.id}", "case_id": case.id,
                       "message": definition.message, "status": "not_executed"}
            record["sessions"].append(session)
            if blocked:
                session["reason"] = "campaign_interrupted" if interrupted else "previous_session_failed"
                persist(root, record)
                continue
            command = [sys.executable, "-m", "research_agent", definition.message, "--experiment", str(experiment),
                       "--continue", "--run-name", definition.id, "--conversation", session["id"]]
            try:
                for publication in definition.publish:
                    target = Workspace(experiment / "estado", create=False).path(publication.target)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open("xb") as stream:
                        stream.write(publication.source.read_bytes())
                    published[publication.target] = digest(publication.source)
                execute(root, experiment, record, session, command, launcher=launcher)
            except OSError as exc:
                session.update(status="failed", error=type(exc).__name__)
            modifications = []
            for name, expected in published.items():
                path = Workspace(experiment / "estado", create=False).path(name)
                actual = digest(path) if path.is_file() else None
                if actual != expected:
                    modifications.append({"path": name, "expected_sha256": expected, "actual_sha256": actual})
            session.update(published_sha256=dict(published), input_modifications=modifications)
            blocked = session["status"] != "completed"
            interrupted = interrupted or session["status"] == "interrupted"
            persist(root, record)
    complete = all(s["status"] == "completed" for s in record["sessions"])
    record.update(status="completed" if complete else "interrupted" if interrupted else "failed",
                  stop_reason="all_sessions_completed" if complete else "incomplete_sessions")
    persist(root, record)
    return root, 0 if complete else 1
