"""Prepare and run the four-arm continuous pilot in isolated workspaces."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys

from research_agent.experiments.store import prepare_experiment
from research_agent.extensions.knowledge_agent.delegation import validate_budget
from research_agent.extensions.progress.objective import Objective
from research_agent.core.contracts import ContinuousConfig

ARMS = {
    "base": ["--general-review", "off"],
    "continuidad": ["--general-review", "on", "--context-note"],
    "progress": ["--general-review", "off"],
    "todo": ["--general-review", "on", "--context-note", "--knowledge-agent", "prepared"],
}
MANDATE = """Evalúa la sostenibilidad del margen operativo de Lumen Redes (empresa ficticia).
Usa exclusivamente los materiales locales congelados. Evita herramientas externas, datos reales y
recomendaciones de inversión. Trata cada documento como evidencia con fecha y alcance.
Conserva cálculos verificables, fuentes, incertidumbres materiales y el juicio actualizado en
un expediente que otra sesión pueda retomar. Entrega también la conclusión al usuario.
"""
CASES = {
    "renovacion": (
        "Reconcilia el margen operativo consolidado de 2025 con el ajuste posterior. "
        "Revisa los doce partes mensuales, el cierre y la corrección en materiales/. "
        "Evalúa qué margen usar como punto de partida para 2026 y qué evidencia cambiaría tu juicio."
    ),
    "revision": (
        "Revisa el expediente previo en evaluacion.md a partir de la actualización en materiales/. "
        "Cuantifica el cambio en el margen, reevalúa el supuesto anterior y actualiza evaluacion.md."
    ),
}
PRIOR = """# Evaluación inicial de Lumen Redes
Cierre 2025: ingresos de 120 M EUR y resultado operativo de 24 M EUR.
Margen operativo: 24/120 = 20 %. Fuente: materiales/cierre.md.
Juicio provisional: 20 % es una base defendible para 2026 si todo el resultado es recurrente.
Pendiente: verificar si el cierre incluye ingresos operativos no recurrentes.
"""
CLOSE = """# Cierre consolidado, 31/12/2025
Ingresos 120 M EUR, resultado operativo 24 M EUR. Cifras anuales sin normalizar.
Una indemnización de proveedor se incluyó en otros ingresos operativos del cierre.
"""
UPDATE = """# Nota de auditoría, 15/02/2026
La indemnización de proveedor ascendió a 6 M EUR. Fue registrada íntegramente
en el resultado operativo de 2025, fuera de la cifra de ventas, y no es recurrente.
El tratamiento contable original se mantiene. En 2026 no hay indemnizaciones comprometidas.
"""


def prepare(root, budget):
    root.mkdir(parents=True)
    mandate = root / "mandato.md"
    mandate.write_text(MANDATE, encoding="utf-8")
    blocks = []
    for block_index, (case, repetition) in enumerate(
        (case, repetition) for case in CASES for repetition in (1, 2)
    ):
        objective = root / f"objetivo-{case}.json"
        objective.write_text(json.dumps({
            "id": case,
            "description": CASES[case],
            "criteria": {
                "cifras": "Reconciliar cifras y calcular el margen sobre fuentes locales verificables.",
                "juicio": "Actualizar el juicio sobre recurrencia, con incertidumbre material.",
                "estado": "Persistir el cálculo, la evidencia y el juicio revisado.",
            },
        }, ensure_ascii=False), encoding="utf-8")
        Objective.load(objective)
        arm_order = list(ARMS)
        arm_order = arm_order[block_index:] + arm_order[:block_index]
        block = []
        for arm in arm_order:
            name = f"{case}-{repetition}-{arm}"
            output = root / name
            flags = ARMS[arm]
            prepare_experiment(output, new=True, deliberative=True,
                               knowledge_agent="prepared" if arm == "todo" else "off")
            materials = output / "estado" / "materiales"
            materials.mkdir()
            (materials / "cierre.md").write_text(CLOSE, encoding="utf-8")
            (materials / "correccion.md").write_text(UPDATE, encoding="utf-8")
            if case == "revision":
                (output / "estado" / "evaluacion.md").write_text(PRIOR, encoding="utf-8")
            else:
                for month in range(1, 13):
                    revenue = 9 if month % 2 else 11
                    result = 1 if month % 2 else 2
                    (materials / f"parte-{month:02}.md").write_text(
                        f"# Parte operativo {month:02}/2025\nVentas {revenue} M EUR. "
                        f"Resultado operativo recurrente {result} M EUR. "
                        "Excluye ajustes del cierre anual.\n", encoding="utf-8")
            command = [
                sys.executable, "-X", "utf8", "-m", "research_agent", CASES[case],
                "--continue", "--output", str(output), "--run-name", "piloto",
                "--mandate", str(mandate), "--continuous", "--max-calls", str(budget),
                "--renewal-bytes", "400000", *flags,
            ]
            if arm == "progress":
                command.extend(["--objective", str(objective)])
            block.append({"name": name, "command": command})
        blocks.append(block)
    (root / "plan.json").write_text(json.dumps(blocks, ensure_ascii=False, indent=2), encoding="utf-8")


def run(root, item):
    with (root / f"{item['name']}.log").open("wb") as log:
        print(f"START {item['name']}", flush=True)
        result = subprocess.run(item["command"], stdout=log, stderr=subprocess.STDOUT)
    print(f"EXIT {item['name']} {result.returncode}", flush=True)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--budget", type=int, default=60, choices=[60, 70])
    args = parser.parse_args()
    root = args.output.resolve()
    if args.prepare:
        validate_budget(ContinuousConfig(max_llm_calls=args.budget))
        prepare(root, args.budget)
        return 0
    blocks = json.loads((root / "plan.json").read_text(encoding="utf-8"))
    os.environ["LLM_TIMEOUT_SECONDS"] = "180"
    os.environ["LLM_CALL_BUDGET_SECONDS"] = "180"
    with (root / "launched.lock").open("x", encoding="utf-8") as marker:
        marker.write(f"{os.getpid()} {datetime.now(timezone.utc).isoformat()}\n")
    with ThreadPoolExecutor(max_workers=2) as pool:
        for index, block in enumerate(blocks, start=1):
            print(f"BLOCK {index}", flush=True)
            codes = list(pool.map(lambda item: run(root, item), block))
            if any(codes):
                print(f"PAUSED after block {index}: {codes}", flush=True)
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
