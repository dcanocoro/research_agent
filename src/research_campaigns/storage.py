"""One atomic campaign record; native agent recordings remain the evidence owner."""
from __future__ import annotations

from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any
import hashlib
import shutil

from research_agent.experiments import disjoint, prepare_experiment
from research_agent.simulation.state import read, save
from research_agent.workspace import Workspace


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze_files(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): digest(p) for p in sorted(root.rglob("*")) if p.is_file()}


def dependencies() -> dict[str, Any]:
    result = {}
    for name in ("research-agent", "findata", "PyYAML"):
        dist = metadata.distribution(name)
        record = dist.read_text("RECORD")
        result[name] = {"version": dist.version,
                        "record_sha256": hashlib.sha256(record.encode()).hexdigest() if record else None}
    return result


def create(root: Path, definition: Path, mode: str, identifier: str, files: list[Path], *,
           deliberative: bool = False, instructions_dir: Path | None = None,
           state_tools: str = "v5") -> dict[str, Any]:
    import research_agent
    Workspace._check_links(root)
    for source in (definition, Path(__file__).parent, Path(str(research_agent.__file__)).parent):
        disjoint(root, source)
    if mode == "suite":
        root.mkdir(parents=True, exist_ok=False)
    else:
        prepare_experiment(root, new=True, deliberative=deliberative, instructions_dir=instructions_dir, state_tools=state_tools)
    for source in files:
        Workspace._check_links(source)
        target = root / "definicion" / source.relative_to(definition)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    record: dict[str, Any] = {"schema_version": "campaign-v1", "mode": mode, "id": identifier,
                              "started_at": datetime.now(timezone.utc).isoformat(),
                              "status": "prepared", "sessions": [], "runtime": {},
                              "definition_sha256": freeze_files(root / "definicion")}
    save(root / "campaign.json", record)
    return record


def load(root: Path) -> dict[str, Any]:
    value = read(root / "campaign.json")
    if value.get("schema_version") != "campaign-v1" or value.get("mode") not in {"suite", "historical", "continuous"}:
        raise ValueError("Expected a new campaign-v1 campaign; historical formats are unsupported.")
    return value
