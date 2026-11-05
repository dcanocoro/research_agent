"""Fixed-case launcher checks; never construct providers or financial clients."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def launcher():
    spec = importlib.util.spec_from_file_location("fixed_cases", ROOT / "scripts/run_fixed_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def native_result(experiment, *, reason="call_limit", status="interrupted"):
    run = experiment / "ejecuciones" / "fake-run"
    run.mkdir(parents=True)
    (run / "resultado.json").write_text(json.dumps({"status": status, "stop_reason": reason}), encoding="utf-8")


def test_three_real_local_processes_overlap_and_have_isolated_inputs(launcher, tmp_path, monkeypatch, capsys):
    """Replace only the child command with an offline worker and a three-way barrier."""
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "180")
    monkeypatch.setenv("LLM_CALL_BUDGET_SECONDS", "180")
    actual_popen = subprocess.Popen
    calls = []
    worker = """
import json, sys, time
from pathlib import Path
root = Path(sys.argv[1])
root.mkdir()
(root / 'estado').mkdir()
(root / 'estado' / 'own.txt').write_text(root.name)
(root / 'started').touch()
deadline = time.monotonic() + 10
while len(list(root.parent.glob('*/started'))) != 3:
    if time.monotonic() > deadline:
        raise SystemExit(7)
    time.sleep(0.02)
run = root / 'ejecuciones' / 'local'
run.mkdir(parents=True)
(run / 'resultado.json').write_text(json.dumps({'status': 'interrupted', 'stop_reason': 'call_limit'}))
print('worker output')
"""

    def popen(command, **kwargs):
        calls.append(command)
        experiment = command[command.index("--experiment") + 1]
        assert kwargs["cwd"] == ROOT
        assert kwargs["env"]["LLM_TIMEOUT_SECONDS"] == "180"
        assert kwargs["env"]["LLM_CALL_BUDGET_SECONDS"] == "180"
        return actual_popen([sys.executable, "-c", worker, experiment], **kwargs)

    monkeypatch.setattr(launcher.subprocess, "Popen", popen)
    output = tmp_path / "batch"
    assert launcher.run(output) == 0
    assert len(calls) == 3
    for case, command in zip(launcher.CASES, calls):
        assert command[:3] == [sys.executable, "-m", "research_agent"]
        assert command[3] == (launcher.DEFINITION / f"{case}.md").read_text(encoding="utf-8")
        assert command[4:] == [
            "--experiment", str(output / case), "--run-name", case,
            "--mandate", str(output / "entradas/mandato.md"), *launcher.OPTIONS,
        ]
        assert (output / "entradas" / f"{case}.md").read_bytes() == (launcher.DEFINITION / f"{case}.md").read_bytes()
        assert (output / case / "estado/own.txt").read_text() == case
        assert "worker output" in (output / "logs" / f"{case}.stdout.txt").read_text()
    assert (output / "entradas/mandato.md").read_bytes() == (launcher.DEFINITION / "mandato.md").read_bytes()
    console = capsys.readouterr().out
    assert "worker output" not in console
    assert console.count("presupuesto de llamadas agotado") == 3
    assert "no acredita cumplimiento" in console


def test_budget_and_shared_runtime_options(launcher):
    options = launcher.OPTIONS
    for flag, value in (("--max-calls", "100"), ("--max-tools", "200"), ("--timeout-seconds", "300"),
                        ("--context-bytes", "524288"), ("--renewal-bytes", "262144")):
        assert options[options.index(flag) + 1] == value
    assert {"--new", "--continuous", "--python"} <= set(options)
    assert "--objective" not in options and "--continuous-timeout-seconds" not in options


def test_existing_destination_rejected_without_launch(launcher, tmp_path, monkeypatch):
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *a, **k: pytest.fail("must not launch"))
    marker = tmp_path / "keep.txt"
    marker.write_text("unchanged")
    assert launcher.main(["--output", str(tmp_path)]) == 2
    assert marker.read_text() == "unchanged"


def test_invalid_input_does_not_create_destination(launcher, tmp_path, monkeypatch):
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    for name in (*launcher.CASES, "mandato"):
        (inputs / f"{name}.md").write_text(" " if name == "sector-ia" else "prompt")
    monkeypatch.setattr(launcher, "DEFINITION", inputs)
    monkeypatch.setattr(launcher.subprocess, "Popen", lambda *a, **k: pytest.fail("must not launch"))
    output = tmp_path / "out"
    assert launcher.main(["--output", str(output)]) == 2
    assert not output.exists()


@pytest.mark.parametrize("launch_failure", [False, True])
def test_failure_preserves_other_runs_and_does_not_retry(launcher, tmp_path, monkeypatch, launch_failure):
    started = []
    waited = []

    class Child:
        def __init__(self, case):
            self.case = case

        def wait(self, timeout=None):
            # All three have been attempted before any result is awaited.
            assert started == list(launcher.CASES)
            waited.append(self.case)
            return 1 if self.case == "microsoft" else 0

        def poll(self):
            return 0

    output = tmp_path / "batch"

    def popen(command, **kwargs):
        case = command[command.index("--run-name") + 1]
        started.append(case)
        if launch_failure and case == "microsoft":
            raise OSError("simulated launch failure")
        native_result(output / case)
        return Child(case)

    monkeypatch.setattr(launcher.subprocess, "Popen", popen)
    assert launcher.run(output) == 1
    assert set(waited) == ({"analista", "sector-ia"} if launch_failure else set(launcher.CASES))
    for case in ("analista", "sector-ia"):
        assert (output / case / "ejecuciones/fake-run/resultado.json").is_file()
    if launch_failure:
        assert "simulated launch failure" in (output / "logs/microsoft.stderr.txt").read_text()


def test_cancel_terminates_all_then_reaps_and_kills_stuck_child(launcher, tmp_path, monkeypatch):
    events = []
    children = []

    class Child:
        alive = True

        def __init__(self, index):
            self.index = index

        def poll(self):
            return None if self.alive else 0

        def terminate(self):
            events.append(("terminate", self.index))

        def kill(self):
            events.append(("kill", self.index))
            self.alive = False

        def wait(self, timeout=None):
            if timeout is None and not events:
                raise KeyboardInterrupt
            assert events[:3] == [("terminate", i) for i in range(3)]
            if self.index == 1 and self.alive:
                raise subprocess.TimeoutExpired("fake", timeout)
            self.alive = False
            events.append(("reaped", self.index))
            return 0

    def popen(*args, **kwargs):
        child = Child(len(children))
        children.append(child)
        return child

    monkeypatch.setattr(launcher.subprocess, "Popen", popen)
    assert launcher.run(tmp_path / "batch") == 130
    assert ("kill", 1) in events
    assert all(("reaped", i) in events for i in range(3))
    assert all(not c.alive for c in children)


def test_output_required(launcher):
    with pytest.raises(SystemExit) as exc:
        launcher.main([])
    assert exc.value.code == 2


@pytest.mark.parametrize("content", [None, "{broken", "[]", '{"status": "failed", "stop_reason": "operation_timeout"}'])
def test_closure_handles_partial_native_capture(launcher, tmp_path, content):
    if content is not None:
        run = tmp_path / "ejecuciones/run"
        run.mkdir(parents=True)
        (run / "resultado.json").write_text(content)
    message = launcher.closure(tmp_path)
    if content and "operation_timeout" in content:
        assert "cumplimiento" in message
    else:
        assert "consultar" in message
