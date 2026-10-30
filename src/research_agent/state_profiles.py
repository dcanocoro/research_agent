"""Explicit experiment capability selection, outside agent-editable state."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any

from .workspace import Workspace

CONFIG = "herramientas.json"
GUIDE = "herramientas-estado-v5.md"


def state_profile(root: Path) -> str:
    path = root / CONFIG
    Workspace._check_links(path)
    if not path.exists():
        return "legacy"
    value = json.loads(path.read_bytes())
    if not isinstance(value, dict) or value.get("schema_version") != "state-tools-profile-v1" or value.get("profile") not in {"legacy", "v5"}:
        raise ValueError("Invalid experiment state tools profile.")
    if value["profile"] == "v5":
        guide = root / "instrucciones" / GUIDE
        Workspace._check_links(guide)
        if not guide.is_file():
            raise ValueError("V5 requires its frozen instruction guide.")
    return str(value["profile"])


def set_state_profile(root: Path, profile: str, *, adoption: bool = False) -> None:
    if profile not in {"legacy", "v5"}:
        raise ValueError("Unknown state tools profile.")
    config = root / CONFIG
    Workspace._check_links(config)
    history: list[Any] = []
    if config.exists():
        previous = json.loads(config.read_bytes())
        history = previous.get("transitions", [])
        if previous.get("profile") == profile:
            state_profile(root)
            return
    if profile == "v5":
        guide = root / "instrucciones" / GUIDE
        Workspace._check_links(guide)
        content = files("research_agent").joinpath("prompts/state_tools_v5.md").read_bytes()
        if guide.exists() and guide.read_bytes() != content:
            raise ValueError("Adoption would replace an existing guide; resolve it explicitly.")
        if not guide.exists():
            with guide.open("xb") as stream:
                stream.write(content)
    history = [*history, {"profile": profile, "adoption": adoption,
                         "occurred_at": datetime.now(timezone.utc).isoformat()}]
    value = {"schema_version": "state-tools-profile-v1", "profile": profile, "transitions": history}
    with tempfile.NamedTemporaryFile(dir=root, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8"))
        stream.flush()
        os.fsync(stream.fileno())
    try:
        temporary.replace(config)
    finally:
        temporary.unlink(missing_ok=True)
