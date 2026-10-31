"""Launch the three fixed prompts in isolated native Agent A processes."""
from __future__ import annotations

import argparse
from contextlib import ExitStack
import json
import os
from pathlib import Path
import signal
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFINITION = ROOT / "campaigns" / "casos-fijos"
CASES = ("analista", "microsoft", "sector-ia")
OPTIONS = (
    "--new", "--continuous", "--max-calls", "100", "--max-tools", "200",
    "--timeout-seconds", "300", "--python", "--state-tools", "v5",
    "--context-bytes", "524288", "--consolidation-bytes", "262144",
)


def closure(experiment: Path) -> str:
    """Describe native closure without equating process success with task success."""
    results = list((experiment / "ejecuciones").glob("*/resultado.json"))
    if len(results) != 1:
        return "sin resultado nativo único; consultar logs y capturas"
    try:
        result = json.loads(results[0].read_text(encoding="utf-8"))
        reason = result["stop_reason"]
        status = result["status"]
    except (OSError, ValueError, KeyError, TypeError):
        return "resultado nativo ilegible; consultar logs y capturas"
    if reason == "call_limit":
        return "presupuesto de llamadas agotado (call_limit); no acredita cumplimiento"
    return f"estado={status}, cierre={reason}; no acredita cumplimiento"


def stop(children: list[tuple[str, subprocess.Popen]]) -> None:
    """Stop all live children before waiting, then force and reap if necessary."""
    previous = signal.signal(signal.SIGINT, signal.SIG_IGN)
    try:
        for _, child in children:
            if child.poll() is None:
                try:
                    child.terminate()
                except ProcessLookupError:
                    pass
        for _, child in children:
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
    finally:
        signal.signal(signal.SIGINT, previous)


def run(output: Path) -> int:
    output = output.absolute()
    # Read every input before creating a destination or starting any process.
    inputs = {f"{case}.md": (DEFINITION / f"{case}.md").read_bytes() for case in CASES}
    inputs["mandato.md"] = (DEFINITION / "mandato.md").read_bytes()
    for name, content in inputs.items():
        if not content.decode("utf-8").strip():
            raise ValueError(f"Entrada vacía: {name}")
    output.mkdir(parents=True, exist_ok=False)
    frozen = output / "entradas"
    frozen.mkdir()
    for name, content in inputs.items():
        (frozen / name).write_bytes(content)
    logs = output / "logs"
    logs.mkdir()
    children: list[tuple[str, subprocess.Popen]] = []
    failed = False
    with ExitStack() as streams:
        try:
            # All launches precede the first wait: each child owns a fresh workspace.
            for case in CASES:
                out = streams.enter_context((logs / f"{case}.stdout.txt").open("wb"))
                err = streams.enter_context((logs / f"{case}.stderr.txt").open("wb"))
                command = [
                    sys.executable, "-m", "research_agent", inputs[f"{case}.md"].decode("utf-8"),
                    "--experiment", str(output / case), "--run-name", case,
                    "--mandate", str(frozen / "mandato.md"), *OPTIONS,
                ]
                try:
                    child = subprocess.Popen(
                        command, cwd=ROOT, stdout=out, stderr=err,
                        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                    )
                except OSError as exc:
                    err.write(f"{type(exc).__name__}: {exc}\n".encode("utf-8"))
                    failed = True
                    print(f"{case}: fallo de lanzamiento; logs en {logs}", flush=True)
                    continue
                children.append((case, child))
                print(f"{case}: iniciado; resultados en {output / case}", flush=True)
            for case, child in children:
                code = child.wait()
                failed = failed or code != 0
                print(f"{case}: código={code}; {closure(output / case)}; resultados en {output / case}", flush=True)
        except KeyboardInterrupt:
            print(f"Cancelación: deteniendo procesos; capturas y logs en {output}", flush=True)
            return 130
        finally:
            stop(children)
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Directorio nuevo para las tres ejecuciones")
    args = parser.parse_args(argv)
    try:
        return run(args.output)
    except (OSError, ValueError) as exc:
        print(f"casos-fijos: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
