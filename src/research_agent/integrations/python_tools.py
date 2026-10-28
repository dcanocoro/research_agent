"""Optional programmable operators, using bounded, disposable local processes."""
from __future__ import annotations

import asyncio
import csv
import hashlib
import io
import json
import os
import site
import sys
import tempfile
from importlib import metadata
from importlib.resources import files
from pathlib import Path
from time import monotonic
from typing import Any

from ..python_worker import reject_constant, validate_code
from ..tools import ToolRegistry
from ..workspace import Workspace

OPERATORS = ("calculate", "transform", "evaluate", "model")
POLICY: dict[str, Any] = {"version": "python-operators-v1", "isolation": "local-process-not-sandbox",
          "code_bytes": 32768, "input_bytes": 1048576, "output_bytes": 1048576,
          "stderr_bytes": 16384, "timeout_seconds": 30, "memory_limit": None}
DEPENDENCIES = ("numpy", "pandas", "scipy", "numpy-financial")


def python_configuration() -> dict[str, Any]:
    versions = {}
    for name in DEPENDENCIES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            raise ValueError('Python operators require optional dependencies. Run: python -m pip install -c constraints.txt -e ".[python]"') from None
    return {"enabled": True, "policy": dict(POLICY), "python": sys.version, "libraries": versions}


def encode(value: Any) -> bytes:
    try:
        return json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError) as exc:
        raise ValueError(f"serialization: {exc}") from None


async def run_worker(request: dict[str, Any], *, timeout: float = 30) -> dict[str, Any]:
    """Bound pipes while draining; always reap the child, including cancellation."""
    worker = Path(__file__).resolve().parents[1] / "python_worker.py"
    environment = {key: os.environ[key] for key in ("SystemRoot", "WINDIR", "TEMP", "TMP") if key in os.environ}
    environment.update({name: "1" for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")})
    process = None
    jobs: list[asyncio.Task[Any]] = []
    with tempfile.TemporaryDirectory(prefix="research-python-") as directory:
        # Windows venv python.exe is a launcher with another process behind it.
        # Launch the actual interpreter so kill/wait apply to the worker itself;
        # supply the current environment's library paths without processing .pth.
        executable = getattr(sys, "_base_executable", sys.executable)
        launch = asyncio.create_task(asyncio.create_subprocess_exec(
            executable, "-I", "-S", str(worker), json.dumps(site.getsitepackages()), cwd=directory, env=environment,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE))
        try:
            async with asyncio.timeout(timeout):
                process = await asyncio.shield(launch)
                assert process.stdin and process.stdout and process.stderr

                async def feed() -> None:
                    assert process is not None and process.stdin is not None
                    try:
                        process.stdin.write(encode(request))
                        await process.stdin.drain()
                    except (BrokenPipeError, ConnectionResetError):
                        pass
                    finally:
                        process.stdin.close()

                async def read(stream: asyncio.StreamReader, limit: int) -> bytes:
                    data = bytearray()
                    while chunk := await stream.read(8192):
                        data.extend(chunk)
                        if len(data) > limit:
                            raise ValueError("limit: worker output exceeded byte limit")
                    return bytes(data)

                jobs = [asyncio.create_task(feed()),
                        asyncio.create_task(read(process.stdout, POLICY["output_bytes"])),
                        asyncio.create_task(read(process.stderr, POLICY["stderr_bytes"]))]
                _, stdout, _ = await asyncio.gather(*jobs)
                await process.wait()
                if process.returncode:
                    raise ValueError(f"execution: worker exited with code {process.returncode}")
                try:
                    response = json.loads(stdout, parse_constant=reject_constant)
                    if not isinstance(response, dict) or not isinstance(response.get("ok"), bool):
                        raise ValueError("invalid envelope")
                    return response
                except (ValueError, UnicodeError):
                    raise ValueError("serialization: invalid worker response") from None
        except TimeoutError:
            raise ValueError("limit: Python invocation exceeded time limit") from None
        finally:
            # shield covers cancellation during process creation as well.
            if process is None:
                process = await launch
            if process.returncode is None:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass
            for job in jobs:
                if not job.done():
                    job.cancel()
            if jobs:
                await asyncio.gather(*jobs, return_exceptions=True)
            # A full pipe can delay process.wait even after kill. Drain discarded
            # bytes after stopping bounded readers, before waiting for transport.
            async def discard(stream: asyncio.StreamReader | None) -> None:
                if stream is not None:
                    while await stream.read(8192):
                        pass
            await asyncio.gather(discard(process.stdout), discard(process.stderr))
            await process.wait()


def register_python(registry: ToolRegistry, workspace: Workspace, configuration: dict[str, Any]) -> None:
    def describe_python_operator(operator: str) -> dict[str, str]:
        return {"operator": operator, "contract": files("research_agent").joinpath(
            f"python_contracts/{operator}.md").read_text(encoding="utf-8")}

    async def run_python(operator: str, code: str, inputs_json: str, input_refs_json: str,
                         parameters_json: str, source_refs: list[str]) -> dict[str, Any]:
        started = monotonic()
        execution_ref = None
        try:
            if len(code.encode("utf-8")) > POLICY["code_bytes"]:
                raise ValueError("limit: code exceeds 32 KiB")
            if sum(len(v.encode("utf-8")) for v in (inputs_json, input_refs_json, parameters_json)) > POLICY["input_bytes"]:
                raise ValueError("limit: JSON arguments exceed 1 MiB")

            def object_json(value: str, name: str) -> dict[str, Any]:
                try:
                    parsed = json.loads(value, parse_constant=reject_constant)
                except ValueError as exc:
                    raise ValueError(f"contract: {name} must encode a JSON object: {exc}") from None
                if not isinstance(parsed, dict):
                    raise ValueError(f"contract: {name} must encode a JSON object")
                return parsed

            inputs = object_json(inputs_json, "inputs_json")
            parameters = object_json(parameters_json, "parameters_json")
            input_refs = object_json(input_refs_json, "input_refs_json")
            if any(not isinstance(ref, str) or not ref for ref in input_refs.values()):
                raise ValueError("contract: input_refs_json values must be nonempty workspace paths")
            resolved = dict(inputs)
            hashes = {}
            remaining = POLICY["input_bytes"] - len(encode({"inputs": inputs, "parameters": parameters, "source_refs": source_refs}))
            for name, reference in input_refs.items():
                if name in resolved:
                    raise ValueError(f"contract: duplicate input name {name}")
                path = workspace.path(reference)
                if path.suffix.lower() not in {".json", ".csv"}:
                    raise ValueError("contract: input_refs supports workspace JSON or CSV only")
                with path.open("rb") as stream:
                    raw = stream.read(max(0, remaining) + 1)
                remaining -= len(raw)
                if remaining < 0:
                    raise ValueError("limit: input exceeds 1 MiB")
                hashes[name] = hashlib.sha256(raw).hexdigest()
                text = raw.decode("utf-8-sig")
                resolved[name] = json.loads(text, parse_constant=reject_constant) if path.suffix.lower() == ".json" else list(csv.DictReader(io.StringIO(text)))
            request = {"operator": operator, "code": code, "inputs": resolved, "parameters": parameters,
                       "source_refs": source_refs, "input_refs": input_refs, "input_sha256": hashes,
                       "configuration": configuration, "max_output_bytes": POLICY["output_bytes"]}
            if len(encode({"inputs": resolved, "parameters": parameters, "source_refs": source_refs})) > POLICY["input_bytes"]:
                raise ValueError("limit: resolved input exceeds 1 MiB")
            execution_ref = registry.recorder.artifact(request)
            registry.recorder.event("lab.python.prepared", operator=operator, execution_ref=execution_ref)
            validate_code(code)
            required = "criteria" if operator == "evaluate" else "assumptions" if operator == "model" else None
            if required and (not isinstance(parameters.get(required), dict) or not parameters[required]):
                raise ValueError(f"contract: {operator} requires a nonempty parameters.{required} object")
            remaining_time = POLICY["timeout_seconds"] - (monotonic() - started)
            if remaining_time <= 0:
                raise ValueError("limit: Python invocation exceeded time limit")
            response = await run_worker(request, timeout=remaining_time)
            if not response["ok"]:
                raise ValueError(str(response.get("message", "execution failed")))
            result = response.get("result")
            if not isinstance(result, dict):
                raise ValueError("serialization: result must be an object")
            encode(result)
            duration = round(monotonic() - started, 6)
            registry.recorder.event("lab.python.completed", operator=operator, execution_ref=execution_ref, duration_seconds=duration)
            return {"operator": operator, "result": result, "parameters": parameters, "source_refs": source_refs,
                    "input_refs": input_refs, "execution_ref": execution_ref, "configuration": configuration,
                    "code_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(), "duration_seconds": duration}
        except asyncio.CancelledError:
            registry.recorder.event("lab.python.failed", execution_ref=execution_ref, error_type="cancelled",
                                    duration_seconds=round(monotonic() - started, 6))
            raise
        except (ValueError, OSError, UnicodeError) as exc:
            registry.recorder.event("lab.python.failed", execution_ref=execution_ref, error_type=type(exc).__name__,
                                    message=str(exc)[:400], duration_seconds=round(monotonic() - started, 6))
            raise ValueError(str(exc)[:400]) from None

    operator_schema = {"type": "string", "enum": list(OPERATORS)}
    registry.register("describe_python_operator", "Read Python operator contract and example: calculate (metrics), transform (tables), evaluate (rules), model (estimates). Optional before execution.",
                      {"operator": operator_schema}, describe_python_operator, execution="inline")
    registry.register("run_python", "Execute one local Python run(inputs, parameters) returning a JSON object. Operators: calculate, transform, evaluate, model. NumPy/pandas/SciPy/numpy-financial; no file/network/process APIs. The three *_json strings encode objects (use '{}' when unused); the function receives decoded dictionaries. Use describe_python_operator for examples.",
                      {"operator": operator_schema, "code": {"type": "string", "minLength": 1, "maxLength": 32768},
                       "inputs_json": {"type": "string", "description": "JSON object of inline input data", "maxLength": 1048576},
                       "input_refs_json": {"type": "string", "description": "JSON object mapping additional input names to workspace JSON/CSV paths", "maxLength": 1048576},
                       "parameters_json": {"type": "string", "description": "JSON object of parameters; evaluate requires criteria, model requires assumptions", "maxLength": 1048576},
                       "source_refs": {"type": "array", "items": {"type": "string"}}},
                      run_python, execution="async", material=True)
