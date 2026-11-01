"""Frozen identity of the single state-tool interface, never a selectable profile."""
from importlib.resources import files
import json
from pathlib import Path

from .workspace import Workspace

CONTRACT = "state-tools-e1"
CONFIG = "herramientas.json"
GUIDE = "herramientas-estado.md"
CONFIGURATION = {"schema_version": "state-tools-contract-v1", "contract": CONTRACT}


def validate_state_configuration(root: Path) -> None:
    path = root / CONFIG
    Workspace._check_links(path)
    if not path.is_file() or json.loads(path.read_bytes()) != CONFIGURATION:
        raise ValueError("Incompatible state tools contract: use the previous code for this experiment or an explicitly authorized migration; historical instructions and captures were not changed.")
    guide = root / "instrucciones" / GUIDE
    Workspace._check_links(guide)
    if not guide.is_file():
        raise ValueError("Experiment requires its frozen state-tool guide.")


def freeze_state_configuration(root: Path) -> None:
    guide = root / "instrucciones" / GUIDE
    Workspace._check_links(guide)
    with guide.open("xb") as stream:
        stream.write(files("research_agent").joinpath("prompts/state_tools.md").read_bytes())
    path = root / CONFIG
    Workspace._check_links(path)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(CONFIGURATION, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
