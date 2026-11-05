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

from research_agent.storage.workspace import Workspace


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


def instruction_bundle(directory: Path, *, deliberative: bool) -> dict[str, str]:
    """Read a complete replacement bundle before creating an experiment or clients."""
    Workspace._check_links(directory)
    if not directory.is_dir():
        raise ValueError("Instructions directory must be a directory.")
    expected = {"agente.md", "investigacion-financiera.md"}
    if deliberative:
        expected.add("deliberacion.md")
    entries = list(directory.iterdir())
    if {p.name for p in entries} != expected:
        raise ValueError(f"Instructions directory requires exactly: {', '.join(sorted(expected))}.")
    result = {}
    for path in entries:
        Workspace._check_links(path)
        if not path.is_file():
            raise ValueError("Instruction bundle entries must be regular Markdown files.")
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError("Instruction bundle files must be nonempty.")
        result[path.name] = content
    return result


def prepare_experiment(root: Path, *, new: bool, instructions: tuple[Path, ...] = (),
                       deliberative: bool = False, instructions_dir: Path | None = None,
                       knowledge_agent: str | None = None) -> tuple[Path, ...]:
    from research_agent.experiments.configuration import freeze_state_configuration
    from research_agent.experiments.configuration import validate_state_configuration
    from research_agent.composition.configuration import knowledge_mode as mode_for
    from research_agent.composition.configuration import freeze_knowledge as freeze
    from research_agent.composition.configuration import freeze_runtime_configuration
    if knowledge_agent not in (None, "off", "prepared"):
        raise ValueError("Invalid knowledge agent mode")
    root = root.absolute()
    Workspace._check_links(root)
    if not new:
        mode_for(root, knowledge_agent)
    if not new:
        validate_state_configuration(root)
    # The experiment can live under artifacts/, but never include the source package.
    package = Path(str(files("research_agent")))
    disjoint(root, package)
    bundle = None
    if instructions_dir is not None:
        if not new or instructions:
            raise ValueError("instructions_dir requires a new experiment without additive instructions.")
        disjoint(root, instructions_dir)
        bundle = instruction_bundle(instructions_dir, deliberative=deliberative)
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
        prompts = files("research_agent").joinpath("")
        if bundle is None:
            bundle = {"agente.md": prompts.joinpath("instructions/agent.md").read_text(encoding="utf-8"),
                      "investigacion-financiera.md": prompts.joinpath("instructions/financial_research.md").read_text(encoding="utf-8")}
            if deliberative:
                bundle["deliberacion.md"] = prompts.joinpath("extensions/deliberation/instructions.md").read_text(encoding="utf-8")
        for name, content in bundle.items():
            (root / "instrucciones" / name).write_bytes(content.encode("utf-8"))
        if deliberative:
            from research_agent.extensions.deliberation.agenda import AGENDA_TEMPLATE
            (root / "estado/agenda.md").write_bytes(AGENDA_TEMPLATE.encode("utf-8"))
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
    if new:
        freeze_state_configuration(root)
        freeze_runtime_configuration(root)
        if knowledge_agent is not None:
            freeze(root, knowledge_agent)
    paths = (root / "instrucciones/agente.md", *sorted(p for p in (root / "instrucciones").glob("*.md") if p.name not in {"agente.md", "agente-conocimiento.md", "delegacion-conocimiento.md"}))
    if not paths[0].is_file():
        raise ValueError("Experiment requires instrucciones/agente.md.")
    for path in paths:
        Workspace._check_links(path)
        path.read_text(encoding="utf-8")
    if deliberative:
        if not (root / "instrucciones/deliberacion.md").is_file():
            raise ValueError("Deliberative experiment requires instrucciones/deliberacion.md.")
        from research_agent.extensions.deliberation.context import deliberative_context
        deliberative_context(Workspace(root / "estado", create=False), "validation")
    elif (root / "instrucciones/deliberacion.md").exists():
        raise ValueError("Deliberative experiment requires --mandate on every activation.")
    return paths
