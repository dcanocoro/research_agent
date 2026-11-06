"""Launch paired open Progress runs with a synthetic portfolio and live FinData."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys

from research_agent.experiments.store import prepare_experiment
from research_agent.extensions.progress.objective import Objective

OBJECTIVE = {
    "id": "investigacion-cartera",
    "mode": "open",
    "description": "Construir y mantener progresivamente expedientes de empresas con datos reales de FinData para mejorar la comprensión de los riesgos y alternativas relevantes para la cartera del usuario.",
    "criteria": {
        "expedientes": "Cada avance material queda guardado en el expediente de la empresa, con evidencia fechada, cálculos verificables y un juicio vigente.",
        "cartera": "Relacionar hallazgos con posiciones, horizonte y restricciones del perfil cuando afecten a su interpretación.",
        "prioridad": "Elegir una incertidumbre material que pueda cambiar el juicio y que pueda investigarse con los datos disponibles.",
    },
}
MANDATE = """Construye y mantén progresivamente expedientes de empresas que ayuden a
tomar mejores decisiones para este usuario. Parte de su cartera. Decide qué empresas
investigar, qué preguntas son materiales y qué contrastes aportan información.
Guarda cada avance en el expediente de la empresa con evidencia, fechas, moneda,
unidades, cálculos, juicio vigente y qué evidencia podría cambiarlo. Relaciona
expedientes si comparten riesgos o sirven de contraste. Después de cada avance
selecciona otra pregunta útil. Registra qué queda abierto al cierre.

Usa exclusivamente datos de FinData y herramientas locales de cálculo y estado.
No consultes web ni sustituyas datos ausentes por supuestos sin etiquetar.
Registra la fecha de cada observación y no uses datos posteriores al 2026-11-05.
Si falta valoración comparable, condiciona el juicio y evita proponer operaciones.

Perfil sintético. Horizonte de cinco años, riesgo moderado. Pesos del ejercicio:
MSFT 12%, AMZN 10%, GOOGL 8%, resto diversificado fuera de estas posiciones 70%.
Máximo por empresa 15%. El resto de posiciones no se conoce. El usuario quiere
entender dependencias comunes y riesgos que podrían justificar revisar los pesos.
"""
MESSAGE = "Empieza la investigación abierta de la cartera y acumula expedientes de empresas con FinData."
BLOCKS = (("r1-progress", "r1-nota"), ("r2-nota", "r2-progress"))


def run(root, name):
    command = [
        sys.executable, "-X", "utf8", "-m", "research_agent", MESSAGE,
        "--continue", "--output", str(root / name), "--run-name", "investigacion",
        "--mandate", str(root / "mandato.md"), "--objective", str(root / "objetivo.json"),
        "--continuous", "--general-review", "off", "--max-calls", "120",
        "--renewal-bytes", "400000",
    ]
    if name.endswith("-nota"):
        command.append("--context-note")
    print(f"START {name}", flush=True)
    with (root / f"{name}.log").open("xb") as log:
        code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
    print(f"EXIT {name} {code}", flush=True)
    return code


def main(root, prepare_only):
    root.mkdir(parents=True)
    (root / "mandato.md").write_text(MANDATE, encoding="utf-8")
    objective = root / "objetivo.json"
    objective.write_text(json.dumps(OBJECTIVE, ensure_ascii=False, indent=2), encoding="utf-8")
    Objective.load(objective)
    for block in BLOCKS:
        for name in block:
            prepare_experiment(root / name, new=True, deliberative=True, knowledge_agent="off")
    if prepare_only:
        return 0
    os.environ["LLM_TIMEOUT_SECONDS"] = "180"
    os.environ["LLM_CALL_BUDGET_SECONDS"] = "180"
    with ThreadPoolExecutor(max_workers=2) as pool:
        for block in BLOCKS:
            codes = list(pool.map(lambda name: run(root, name), block))
            if any(codes):
                print(f"PAUSED {block}: {codes}", flush=True)
                return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    sys.exit(main(args.output.resolve(), args.prepare_only))
