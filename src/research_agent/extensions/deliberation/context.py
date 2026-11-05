from typing import Any
import hashlib
from research_agent.storage.workspace import Workspace

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
