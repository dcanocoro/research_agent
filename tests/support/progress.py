import asyncio
import json
from dataclasses import replace
import pytest
from research_agent.contracts import AgentRequest
from research_agent.contracts import AgentLimits
from research_agent.contracts import ContinuousConfig
from research_agent.extensions.progress.objective import Objective
import research_agent.extensions.progress.evaluator as evaluator
from support.bounded import agent as bounded_agent, response
from support.continuous import make, execute, text
from support import save_arguments

def objective():
    return Objective.from_dict({"id": "test", "goal": "Explain the result", "criteria": ["Supported explanation"]})


def report(view, *, outcome="continue", kind="initial", reconsideration=""):
    refs = [{"path": d["path"], "sha256": d["sha256"]} for d in view["documents"] if d["path"] == "result.md"]
    ids = list(view["objective"]["criteria"])
    return {"criteria": [{"id": identifier, "status": "sufficient" if outcome == "sufficient" else "pending",
                           "reason": "Persisted explanation" if refs else "Explanation is missing", "references": refs} for identifier in ids],
            "gaps": [] if outcome == "sufficient" else [{"id": "gap", "criterion_id": ids[0], "missing": "Explain the result", "references": []}],
            "alternatives": [] if outcome != "continue" else [
                {"id": str(i), "gap_id": "gap", "action": "Write an explanation" if i == 1 else "Find supporting data",
                 "expected_result": "result.md with a grounded explanation", "verification": "Inspect the saved argument",
                 "impact": "high", "effort": "low"} for i in (1, 2)],
            "selected": "1" if outcome == "continue" else None,
            "reason": "Resolve the material gap" if outcome == "continue" else "All requested results are supported" if outcome == "sufficient" else "No feasible advance",
            "outcome": outcome, "change": {"kind": kind, "reason": "New supported explanation" if kind == "progress" else "No verified result delta", "references": refs},
            "reconsideration": reconsideration}


class Client:
    def __init__(self, *, final="sufficient", fail=None, research=None):
        self.requests = []
        self.evaluations = 0
        self.generations = 0
        self.research_calls = 0
        self.final, self.fail, self.research = final, fail, research

    async def respond(self, **kwargs):
        self.requests.append(kwargs)
        system = kwargs["system"]
        if system.startswith("Define the requested outcome"):
            self.generations += 1
            return text(json.dumps({"id": "test", "goal": "Explain the result", "criteria": ["Supported explanation"]}))
        if system == evaluator.SYSTEM:
            self.evaluations += 1
            if self.fail:
                if isinstance(self.fail, BaseException):
                    raise self.fail
                return text(self.fail)
            view = kwargs["input_items"][0].payload
            if self.evaluations == 1 and view["previous"] is None:
                return text(json.dumps(report(view)))
            changed = any(d["path"] == "result.md" and view["before_versions"].get(d["path"]) != d["sha256"] for d in view["documents"])
            return text(json.dumps(report(view, outcome=self.final, kind="progress" if self.final == "sufficient" and changed else "stagnant",
                                          reconsideration="Use a different source and a narrower question")))
        if not kwargs["allow_tools"]:
            return text("Resultado verificado; pendientes explícitos.")
        self.research_calls += 1
        if self.research:
            return self.research(self.research_calls)
        return response(call=("record_research_advance", save_arguments(path="result.md", content="A supported explanation.")))

