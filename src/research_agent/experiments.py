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
import hashlib

from .workspace import Workspace


def validate_mandate(mandate: str) -> None:
    if not mandate.strip() or len(mandate.encode("utf-8")) > 16384:
        raise ValueError("Mandate must be nonempty UTF-8 text of at most 16 KiB.")


def deliberative_context(workspace: Workspace, mandate: str) -> dict[str, Any]:
    validate_mandate(mandate)
    agenda = workspace.read_file("agenda.md", max_bytes=8192)
    if agenda["next_offset"] is not None:
        raise ValueError("agenda.md exceeds 8 KiB; compact it explicitly before continuing.")
    return {name: {"text": content, "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest()}
            for name, content in (("mandate", mandate), ("agenda", agenda["text"]))}


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
                       deliberative: bool = False) -> tuple[Path, ...]:
    root = root.absolute()
    Workspace._check_links(root)
    # The experiment can live under artifacts/, but never include the source package.
    package = Path(str(files("research_agent")))
    disjoint(root, package)
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
        prompts = files("research_agent").joinpath("prompts")
        (root / "instrucciones/agente.md").write_text(prompts.joinpath("agent_a.md").read_text(encoding="utf-8"), encoding="utf-8")
        (root / "instrucciones/investigacion-financiera.md").write_text(
            prompts.joinpath("financial_research.md").read_text(encoding="utf-8"), encoding="utf-8")
        if deliberative:
            (root / "instrucciones/deliberacion.md").write_text(
                prompts.joinpath("deliberation.md").read_text(encoding="utf-8"), encoding="utf-8")
            (root / "estado/agenda.md").write_text("", encoding="utf-8")
        for i, content in enumerate(extras, 1):
            (root / f"instrucciones/adicional-{i:02d}.md").write_text(content, encoding="utf-8")
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
    if deliberative:
        if not (root / "instrucciones/deliberacion.md").is_file():
            raise ValueError("Deliberative experiment requires instrucciones/deliberacion.md.")
        deliberative_context(Workspace(root / "estado", create=False), "validation")
    elif (root / "instrucciones/deliberacion.md").exists():
        raise ValueError("Deliberative experiment requires --mandate on every activation.")
    return paths
