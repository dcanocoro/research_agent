from __future__ import annotations
from pathlib import Path
import json
from importlib.resources import files
from research_agent.storage.workspace import Workspace


def knowledge_mode(root: Path | None, requested: str | None = None) -> str:
    """Inspect the frozen selector before importing a concrete implementation."""
    if requested not in (None, "off", "prepared"):
        raise ValueError("Invalid knowledge-agent mode")
    saved = {"version": "durable-b-v1", "mode": "off"}
    if root is not None:
        path = root / "agente-conocimiento.json"
        Workspace._check_links(path)
        if path.exists():
            saved = json.loads(path.read_bytes())
    if saved not in [{"version": "durable-b-v1", "mode": m} for m in ("off", "prepared")]:
        raise ValueError("Incompatible knowledge-agent configuration")
    if root is not None and requested is not None and requested != saved["mode"]:
        raise ValueError("Knowledge mode is frozen; create a new experiment")
    mode = requested or saved["mode"]
    if mode == "prepared":
        from research_agent.extensions.knowledge_agent.delegation import mode_for

        return mode_for(root, requested)
    return mode


def freeze_knowledge(root: Path, mode: str) -> None:
    if mode == "off":
        from research_agent.storage.transactions import atomic_bytes
        from research_agent.observability.recording import encoded

        atomic_bytes(root / "agente-conocimiento.json", encoded({"version": "durable-b-v1", "mode": mode}))
    else:
        from research_agent.extensions.knowledge_agent.delegation import freeze

        freeze(root, mode)


def freeze_runtime_configuration(root: Path) -> None:
    """Preserve the historical frozen record without loading the E2 controller."""
    from research_agent.observability.recording import encoded

    definition = json.loads(
        files("research_agent").joinpath("regimes/continuous/identity.json").read_bytes()
    )
    path = root / "runtime.json"
    Workspace._check_links(path)
    with path.open("xb") as stream:
        stream.write(encoded(definition))
