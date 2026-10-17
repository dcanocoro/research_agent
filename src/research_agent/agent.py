from __future__ import annotations
from typing import Any, Literal
"""Conventional bounded agent loop, preserving provider replay verbatim."""
import asyncio
import hashlib
from pathlib import Path
from dataclasses import asdict
from importlib.resources import files
from time import monotonic
from uuid import uuid4
from runtime_contracts.execution import RunContext, bind_run_context
from runtime_contracts.llm import ConversationClient, ConversationItem, ConversationMessage, ConversationContext
from observability_context import bind_interaction_context, interaction_context_for
from .contracts import AgentLimits, AgentRequest, AgentResult
from .recording import RunRecorder, encoded
from .tools import ToolRegistry
from .workspace import Workspace


class AgentA:
    def __init__(self, client: ConversationClient, tools: ToolRegistry, workspace: Workspace,
                 recorder: RunRecorder, limits: AgentLimits = AgentLimits(), configuration: dict[str, Any] | None = None,
                 instructions: tuple[Path, ...] = ()) -> None:
        self.client, self.tools, self.workspace, self.recorder = client, tools, workspace, recorder
        self.limits, self.configuration = limits, configuration or {}
        self.history: list[ConversationItem] = []
        self._conversation_id: str | None = None
        self.instructions = instructions

    async def run(self, request: AgentRequest) -> AgentResult:
        if self._conversation_id not in (None, request.conversation_id):
            raise ValueError("An AgentA instance belongs to one conversation.")
        self._conversation_id = request.conversation_id
        instructions = (*self.instructions, *request.instructions)
        protected = [Path(str(files("research_agent"))), *instructions]
        for path in protected:
            if self.workspace.root.resolve() == path.resolve() or self.workspace.root.resolve() in path.resolve().parents:
                raise ValueError("Workspace must not contain instructions or package code.")
            for root in self.tools.protected_roots:
                a, b = root.resolve(), path.resolve()
                if a == b or a in b.parents or b in a.parents:
                    raise ValueError("State stores must be disjoint from instructions and package code.")
        run_id, interaction_id = str(uuid4()), str(uuid4())
        deadline = monotonic() + self.limits.timeout_seconds
        base = files("research_agent").joinpath("prompts/agent_a.md").read_text(encoding="utf-8")
        prompts = {"agent_a.md": base, **{str(p): p.read_text(encoding="utf-8") for p in instructions}}
        system = "\n\n".join(prompts.values())
        self.recorder.start(run_id, {"run_id": run_id, "interaction_id": interaction_id,
            "conversation_id": request.conversation_id, "workspace_id": request.workspace_id,
            "workspace_fingerprint": hashlib.sha256(str(self.workspace.root.resolve()).encode()).hexdigest(),
            "limits": asdict(self.limits), "configuration": self.configuration, "metadata": request.metadata,
            "prompts": {k: {"sha256": hashlib.sha256(v.encode()).hexdigest(), "text": v} for k, v in prompts.items()},
            "tools": self.tools.specs()})
        calls = tool_calls = 0
        answer = error = None
        status: Literal["completed", "interrupted", "failed", "cancelled"] = "interrupted"
        reason = "budget"
        context = RunContext(run_id, turn_id=interaction_id, regime="lab", component="agent_a", deadline=deadline)
        interaction = interaction_context_for(interaction_id=interaction_id, conversation_id=request.conversation_id)
        with bind_run_context(context), bind_interaction_context(interaction):
            self.recorder.event("lab.run.started", **request.metadata)
            try:
                self.recorder.save("workspace_before.json", self.workspace.snapshot())
                if self.tools.state_readers:
                    self.recorder.save("state_before.json", self.tools.snapshot_state())
                index = self.workspace.path("memory/index.md")
                memory = self.workspace.read_file("memory/index.md", max_bytes=8192) if index.exists() else {"text": ""}
                self.history.append(ConversationContext({"memory_index": memory}))
                self.history.append(ConversationMessage("user", request.message))
                while calls < self.limits.max_llm_calls:
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        reason = "timeout"
                        break
                    size = len(encoded({"system": system, "input": self.history, "tools": self.tools.specs()}))
                    closing = (remaining <= self.limits.finalization_seconds
                               or calls >= self.limits.max_llm_calls - 1
                               or tool_calls >= self.limits.max_tool_calls
                               or size >= self.limits.max_context_bytes - 4096)
                    if closing:
                        reason = "context_limit" if size >= self.limits.max_context_bytes - 4096 else "budget"
                        self.history.append(ConversationMessage("user", "Execution resources are ending. Deliver the best supported answer from available evidence, state limitations and unfinished work. Do not call tools."))
                    if len(encoded({"system": system, "input": self.history, "tools": [] if closing else self.tools.specs()})) > self.limits.max_context_bytes:
                        reason = "context_limit"
                        break
                    calls += 1
                    async with asyncio.timeout(max(0.001, deadline - monotonic())):
                        turn = await self.client.respond(system=system, input_items=list(self.history),
                            tools=[] if closing else self.tools.specs(), allow_tools=not closing,
                            timeout=max(0.001, deadline - monotonic()))
                    self.history.extend(turn.output_items)
                    if turn.function_call is None:
                        if turn.text.strip():
                            answer, status = turn.text, "completed"
                            if not closing:
                                reason = "answered"
                        else:
                            reason = "empty_response"
                        break
                    if closing:
                        reason = "tools_disabled"
                        break
                    tool_calls += 1
                    tool_time = deadline - monotonic() - self.limits.finalization_seconds
                    try:
                        async with asyncio.timeout(max(0.001, tool_time)):
                            result = await self.tools.execute(turn.function_call)
                    except TimeoutError:
                        from runtime_contracts.llm import ToolResult
                        result = ToolResult(turn.function_call.call_id, turn.function_call.name,
                                            {"ok": False, "error_type": "timeout"})
                    self.history.append(result)
            except asyncio.CancelledError:
                status, reason = "cancelled", "cancelled"
                raise
            except TimeoutError:
                reason = "timeout"
            except Exception as exc:
                status, reason, error = "failed", "operational_failure", type(exc).__name__
            finally:
                self.recorder.save("transcript.json", self.history)
                self.recorder.save("workspace_after.json", self.workspace.snapshot())
                if self.tools.state_readers:
                    self.recorder.save("state_after.json", self.tools.snapshot_state())
                outcome = AgentResult(run_id, status, answer, reason,
                    ("manifest.json", "transcript.json", "workspace_before.json", "workspace_after.json", "events.jsonl",
                     *(("state_before.json", "state_after.json") if self.tools.state_readers else ())),
                    calls, tool_calls, error)
                self.recorder.save("result.json", outcome)
                if answer is not None and self.recorder.current is not None:
                    (self.recorder.current / "answer.md").write_text(answer, encoding="utf-8")
                terminal = "completed" if status == "completed" else "failed" if status == "failed" else "interrupted"
                self.recorder.event(f"lab.run.{terminal}", status=status, stop_reason=reason, llm_calls=calls, tool_calls=tool_calls)
        return outcome
