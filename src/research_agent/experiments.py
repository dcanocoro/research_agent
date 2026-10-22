"""Explicit experiment lifecycle. Git is observed, never mutated."""
from __future__ import annotations

from contextlib import contextmanager
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterator
import os
import re
import subprocess
import unicodedata

from .workspace import Workspace


def human_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")[:80]
    if not value or not re.search(r"[a-z]", value) or value.split("-")[0] in {
        "con", "prn", "aux", "nul", *(f"com{i}" for i in range(10)), *(f"lpt{i}" for i in range(10))
    }:
        raise ValueError("Use a descriptive run name containing letters.")
    return value


def disjoint(left: Path, right: Path) -> None:
    a, b = left.resolve(), right.resolve()
    if a == b or a in b.parents or b in a.parents:
        raise ValueError("State, instructions, recordings and code must be disjoint.")


def git_state(root: Path | None) -> dict[str, Any]:
    if root is None or not (root / ".git").exists():
        return {"status": "absent"}
    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                              capture_output=True, text=True, timeout=10)
    try:
        top = git("rev-parse", "--show-toplevel")
        if top.returncode or Path(top.stdout.strip()).resolve() != root.resolve():
            return {"status": "error", "error_type": "InvalidExperimentRepository"}
        head = git("rev-parse", "--verify", "HEAD")
        changes = git("status", "--porcelain", "--untracked-files=all")
        if changes.returncode:
            return {"status": "error", "error_type": "GitStatusFailed"}
        return {"status": "present", "commit": head.stdout.strip() if head.returncode == 0 else None,
                "dirty": bool(changes.stdout), "changes": changes.stdout.splitlines()}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "error", "error_type": type(exc).__name__}


@contextmanager
def experiment_lock(root: Path) -> Iterator[None]:
    path = root / ".run.lock"
    Workspace._check_links(path)
    with path.open("a+b") as stream:
        stream.seek(0, 2)
        if not stream.tell():
            stream.write(b"0")
            stream.flush()
        try:
            if os.name == "nt":
                import msvcrt
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import importlib
                locking = importlib.import_module("fcntl")
                locking.flock(stream.fileno(), locking.LOCK_EX | locking.LOCK_NB)
        except OSError:
            raise ValueError("Another run is using this experiment.") from None
        try:
            yield
        finally:
            if os.name == "nt":
                import msvcrt
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                locking.flock(stream.fileno(), locking.LOCK_UN)


def prepare_experiment(root: Path, *, new: bool, instructions: tuple[Path, ...] = (),
                       knowledge_mode: str | None = None, tool_profile: str | None = None) -> tuple[Path, ...]:
    root = root.absolute()
    Workspace._check_links(root)
    # The experiment can live under artifacts/, but never include the source package.
    package = Path(str(files("research_agent")))
    disjoint(root, package)
    import json
    config_path = root / "experimento.json"
    Workspace._check_links(config_path)
    if not new and not config_path.exists() and (root / "conocimiento").exists():
        raise ValueError("Argumentative experiment configuration is missing")
    stored = json.loads(config_path.read_text(encoding="utf-8")) if not new and config_path.exists() else {
        "knowledge_mode": "markdown", "tool_profile": "live"}
    chosen = {"knowledge_mode": knowledge_mode or stored["knowledge_mode"], "tool_profile": tool_profile or stored["tool_profile"]}
    if chosen["knowledge_mode"] not in {"markdown", "argumentative"} or chosen["tool_profile"] not in {"live", "closed-corpus"}:
        raise ValueError("Invalid experiment mode or tool profile")
    if not new and chosen != stored:
        raise ValueError("Continuation cannot change experiment mode or tool profile")
    extras = []
    for path in instructions:
        Workspace._check_links(path)
        disjoint(root, path)
        if path.suffix.lower() != ".md":
            raise ValueError("Instructions must be Markdown.")
        extras.append(path.read_text(encoding="utf-8"))
    if new:
        root.mkdir(parents=True, exist_ok=False)
        for name in ("instrucciones", "estado", "ejecuciones"):
            (root / name).mkdir()
        config_path.write_text(json.dumps(chosen), encoding="utf-8")
        prompts = files("research_agent").joinpath("prompts")
        (root / "instrucciones/agente.md").write_text(prompts.joinpath("agent_a.md").read_text(encoding="utf-8"), encoding="utf-8")
        (root / "instrucciones/investigacion-financiera.md").write_text(
            prompts.joinpath("financial_research.md").read_text(encoding="utf-8"), encoding="utf-8")
        for i, content in enumerate(extras, 1):
            (root / f"instrucciones/adicional-{i:02d}.md").write_text(content, encoding="utf-8")
        if chosen["knowledge_mode"] == "argumentative":
            (root / "conocimiento").mkdir()
            (root / "instrucciones/expediente.md").write_text(prompts.joinpath("argumentative.md").read_text(encoding="utf-8"), encoding="utf-8")
        (root / ".gitignore").write_text("ejecuciones/\n.run.lock\n.env\n.env.*\n", encoding="utf-8")
    elif instructions:
        raise ValueError("--instructions is only accepted with --new; edit experiment instructions explicitly.")
    for name in ("instrucciones", "estado", "ejecuciones"):
        path = root / name
        Workspace._check_links(path)
        if not path.is_dir():
            raise ValueError("Invalid experiment: expected instrucciones/, estado/ and ejecuciones/.")
    paths = (root / "instrucciones/agente.md", *sorted(p for p in (root / "instrucciones").glob("*.md") if p.name != "agente.md"))
    if not paths[0].is_file():
        raise ValueError("Experiment requires instrucciones/agente.md.")
    for path in paths:
        Workspace._check_links(path)
        path.read_text(encoding="utf-8")
    return paths
