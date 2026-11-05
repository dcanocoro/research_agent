"""Fixed objective values and input formats for commitment-based progress."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any


def encode(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(encode(value)).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


@dataclass(frozen=True)
class Criterion:
    id: str
    description: str


@dataclass(frozen=True)
class Objective:
    id: str
    description: str
    criteria: tuple[Criterion, ...]
    assessment_path: str | None = None

    def __post_init__(self) -> None:
        if (not isinstance(self.id, str) or not self.id.strip()
                or not isinstance(self.description, str) or not self.description.strip()
                or not isinstance(self.criteria, tuple) or not self.criteria
                or any(not isinstance(c, Criterion) or not isinstance(c.id, str) or not c.id.strip()
                       or not isinstance(c.description, str) or not c.description.strip() for c in self.criteria)):
            raise ValueError("Objective requires an id, description and nonempty identified criteria.")
        if len({c.id for c in self.criteria}) != len(self.criteria):
            raise ValueError("Duplicate objective criterion.")
        if self.assessment_path is not None:
            path = self.assessment_path
            if (not isinstance(path, str) or not path or "\\" in path or ":" in path
                    or path.startswith("/") or any(p in {"", ".", ".."} for p in path.split("/"))
                    or path.split("/")[0].casefold() == "materiales" or not path.endswith(".md")):
                raise ValueError("assessment_path requires a relative editable Markdown path.")
        if len(encode(self.definition())) > 16384:
            raise ValueError("Objective exceeds 16 KiB.")

    def definition(self) -> dict[str, Any]:
        value: dict[str, Any] = {"id": self.id, "description": self.description,
                "criteria": {c.id: c.description for c in self.criteria}}
        if self.assessment_path is not None:
            value["assessment_path"] = self.assessment_path
        return value

    @property
    def sha256(self) -> str:
        return digest(self.definition())

    @classmethod
    def from_dict(cls, value: Any) -> Objective:
        if isinstance(value, dict) and "goal" in value:
            if set(value) != {"id", "goal", "criteria"} or not isinstance(value["criteria"], list):
                raise ValueError("Expected id, goal and a criteria list.")
            value = {"id": value["id"], "description": value["goal"],
                     "criteria": {f"criterion-{i}": text for i, text in enumerate(value["criteria"], 1)}}
        if (not isinstance(value, dict) or not {"id", "description", "criteria"} <= set(value)
                or set(value) - {"id", "description", "criteria", "assessment_path"}
                or not isinstance(value["criteria"], dict)):
            raise ValueError("Expected objective JSON: id, description, criteria (id: description).")
        return cls(value["id"], value["description"],
                   tuple(Criterion(k, v) for k, v in value["criteria"].items()), value.get("assessment_path"))

    @classmethod
    def load(cls, path: Path) -> Objective:
        raw = path.read_bytes()
        if len(raw) > 16384:
            raise ValueError("Objective file exceeds 16 KiB.")
        return cls.from_dict(json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object))


GENERATION_SYSTEM = """Define the requested outcome as JSON only: {"id": "short-id",
"goal": "desired result", "criteria": ["verifiable sufficiency criterion", ...]}.
Use the user's language. Respect the request and mandate, including exclusions.
Criteria describe outcomes, never research phases or an obligatory order.
Do not expand authority, invent user preferences, or demand investment certainty.
The definition will remain fixed across research segments and continuations."""

__all__ = ["Objective", "Criterion", "digest", "unique_object", "GENERATION_SYSTEM"]
