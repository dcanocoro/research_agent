"""Fixed objectives and deterministic coverage; independent of model and finance."""
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


def parse_evaluation(text: str, objective: Objective) -> dict[str, Any]:
    value = json.loads(text, object_pairs_hook=unique_object)
    if (not isinstance(value, dict) or "criteria" not in value or set(value) - {"criteria", "decision_review"}
            or not isinstance(value["criteria"], list)):
        raise ValueError("Expected evaluation criteria list.")
    expected = {c.id for c in objective.criteria}
    seen: set[str] = set()
    for item in value["criteria"]:
        if not isinstance(item, dict) or set(item) != {"criterion_id", "status", "justification", "references", "pending"}:
            raise ValueError("Invalid criterion evaluation fields.")
        key = item["criterion_id"]
        if not isinstance(key, str) or key not in expected or key in seen:
            raise ValueError("Unknown or duplicate evaluation criterion.")
        seen.add(key)
        if item["status"] not in ("cubierto", "no_cubierto", "no_evaluable"):
            raise ValueError("Invalid coverage status.")
        if not isinstance(item["justification"], str) or not item["justification"].strip():
            raise ValueError("Criterion justification required.")
        refs = item["references"]
        if not isinstance(refs, list) or any(not isinstance(r, str) or not r.strip() for r in refs):
            raise ValueError("Invalid criterion references.")
        if item["status"] == "cubierto":
            if not refs or item["pending"] is not None:
                raise ValueError("Covered criteria need references and null pending.")
        elif not isinstance(item["pending"], str) or not item["pending"].strip():
            raise ValueError("Uncovered/unevaluable criteria need pending explanation.")
    if seen != expected:
        raise ValueError("Missing evaluation criteria.")
    if "decision_review" in value:
        review = value["decision_review"]
        if (not isinstance(review, dict) or set(review) != {"decision_useful", "blockers", "resolved_blockers", "adaptation_assessment"}
                or not isinstance(review["decision_useful"], bool) or not isinstance(review["blockers"], list)
                or not isinstance(review["resolved_blockers"], list)
                or any(not isinstance(s, str) or not s.strip() for s in review["resolved_blockers"])
                or not isinstance(review["adaptation_assessment"], str) or not review["adaptation_assessment"].strip()):
            raise ValueError("Invalid decision review.")
        ids = set()
        for blocker in review["blockers"]:
            if (not isinstance(blocker, dict) or set(blocker) != {"id", "criterion_id", "kind", "missing", "decision_impact", "references"}
                    or any(not isinstance(blocker[k], str) or not blocker[k].strip() for k in ("id", "criterion_id", "kind", "missing", "decision_impact"))
                    or blocker["id"] in ids or blocker["criterion_id"] not in expected
                    or blocker["kind"] not in {"evidencia", "calculo", "interpretacion", "coherencia", "preferencia_usuario"}
                    or not isinstance(blocker["references"], list)
                    or any(not isinstance(s, str) or not s.strip() for s in blocker["references"])):
                raise ValueError("Invalid decision blocker.")
            ids.add(blocker["id"])
        if review["decision_useful"] and review["blockers"]:
            raise ValueError("A decision-useful assessment cannot retain material decision blockers.")
    return dict(value)


def metrics(report: dict[str, Any], previous: dict[str, Any] | None = None) -> dict[str, Any]:
    items = report["criteria"]
    covered = sum(c["status"] == "cubierto" for c in items)
    complete = all(c["status"] != "no_evaluable" for c in items)
    distance = 1 - covered / len(items) if complete else None
    prior = metrics(previous)["distance"] if previous is not None else None
    return {"covered": covered, "total": len(items), "distance": distance,
            "delta_distance": prior - distance if prior is not None and distance is not None else None}


@dataclass
class EvaluationState:
    last_valid: dict[str, Any] | None = None
    last_valid_reference: str | None = None
    last_feedback: dict[str, Any] | None = None
    last_valid_feedback: dict[str, Any] | None = None
    last_review_feedback: dict[str, Any] | None = None
    stagnant: int = 0
    closure_active: bool = False

    def accept(self, report: dict[str, Any], reference: str) -> dict[str, Any]:
        result = metrics(report, self.last_valid)
        old = {c["criterion_id"]: c for c in (self.last_valid or {}).get("criteria", [])}
        reopened = [c["criterion_id"] for c in report["criteria"]
                    if c["status"] == "no_cubierto" and old.get(c["criterion_id"], {}).get("status") == "cubierto"]
        interventions = []
        if reopened:
            self.closure_active = False
            interventions.append("Revisa los criterios reabiertos y los motivos indicados.")
        if result["distance"] is None:
            self.stagnant = 0
        else:
            self.stagnant = self.stagnant + 1 if result["delta_distance"] is not None and result["delta_distance"] <= 0 else 1
            if self.stagnant >= 3 and result["distance"] > 0:
                interventions.append("Tres evaluaciones válidas consecutivas sin reducción: identifica el impedimento material, qué método anterior no lo resolvió, qué harás distinto y qué resultado observable permitirá revisar el juicio. La próxima revisión comprobará esa adaptación; no es una orden de abandonar.")
            if result["distance"] == 0 and not self.closure_active:
                interventions.append("Todos los criterios están cubiertos: prepara una síntesis de cierre con fundamentos y límites. El continuo no termina automáticamente.")
            self.closure_active = result["distance"] == 0
            self.last_valid, self.last_valid_reference = report, reference
        return {"metrics": result, "reopened": reopened, "interventions": interventions}

    def failed(self) -> None:
        self.stagnant = 0
