"""Prepare frozen inputs and run two paired, two-phase repetitions."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from research_agent.experiments.store import prepare_experiment
from research_agent.extensions.progress.objective import Objective

BUDGET = 80
THRESHOLD = 400_000
MANDATE = """Construye y mantén una evaluación comparativa de las tres empresas.
Explica cómo ganan dinero, qué riesgos comparten y qué diferencias importan para
esta cartera. Cuando recibas información nueva, revisa los cálculos y juicios
afectados y deja constancia de qué cambió, por qué y qué incertidumbre queda abierta.
Usa exclusivamente materiales/ locales congelados. Separa hechos, supuestos,
cálculos y juicio; cita fuente, fecha, periodo, moneda y unidades. Guarda el
estado en el expediente y entrega una síntesis al usuario. Condiciona cualquier
implicación de cartera a las valoraciones y datos disponibles.
"""
TASKS = {
    "inicial": ("Construye la primera evaluación con la evidencia disponible.",
                {"activos": "Conservar los motores económicos y riesgos materiales de los tres activos con fuentes.",
                 "entorno": "Comparar exposición directa e indirecta al crédito y justificar sensibilidades.",
                 "usuario": "Relacionar exposiciones y diferencias con la cartera y los límites del perfil."}),
    "actualizacion": ("Incorpora los nuevos documentos al expediente existente y explica qué cambia.",
                      {"cambios": "Identificar la nueva evidencia material y recalcular magnitudes afectadas.",
                       "estado": "Actualizar expedientes y comparación común sin dejar vigentes premisas corregidas; conservar fundamentos válidos.",
                       "usuario": "Revisar implicaciones de cartera y explicar qué información podría cambiar el juicio."}),
}
INITIAL = {
    "sector.md": """# Observatorio sectorial, 31/12/2025
Infraestructura digital. Datos sintéticos de 2023, 2024 y 2025, respectivamente.
Demanda de capacidad (índice 2023=100): 100, 113, 128. Utilización media: 71%, 73%, 76%.
Coste de referencia del crédito variable: 3%, 4%, 4%. Los proyectos de clientes
dependen de refinanciación y presupuestos de capital. Escenario del observatorio:
analizar una subida de 200 puntos básicos sobre el principal expuesto durante un año.
No se dispone de cotizaciones ni múltiplos comparables.
""",
    "perfil.md": """# Perfil ficticio al 31/12/2025
Horizonte cinco años, riesgo moderado. Cartera: Nébula 12%, Prisma 10%, resto
diversificado ajeno al sector 78%. Límite por activo 15%, límite sectorial 25%.
Evalúa riesgos y prioridades de investigación bajo esas restricciones.
""",
    "nebula-estados.md": """# Nébula, cierre 31/12/2025
2023, 2024, 2025. Magnitudes en M EUR. Ingresos: 88, 99, 113.
Resultado operativo: 14, 17, 20. Flujo operativo: 16, 18, 21. Capex: 19, 22, 25.
Opera centros de datos propios, cobra por potencia reservada y servicios.
""",
    "nebula-deuda.md": """# Nébula, nota de financiación al 31/12/2025
Deuda 90 M EUR: 60 M EUR variable y 30 M EUR fija al 4,5%.
El cuadro preliminar indica que los 60 M EUR variables están expuestos.
Vencimientos principales en 2028; caja disponible 12 M EUR.
""",
    "nebula-clientes.md": """# Nébula, contratos vigentes al 31/12/2025
El 72% de ingresos de 2025 provino de capacidad reservada por contratos de 3 a 5 años.
Hay cláusulas de traslado parcial de electricidad. El cliente mayor aporta 18%.
""",
    "prisma-estados.md": """# Prisma, cierre 31/12/2025
2023, 2024, 2025, en M EUR. Ingresos: 75, 82, 90. Resultado operativo: 13, 14, 16.
Flujo operativo: 16, 17, 18. Capex: 11, 12, 13. Alquila fibra metropolitana.
""",
    "prisma-deuda.md": """# Prisma, nota de financiación al 31/12/2025
80 M EUR a tipo fijo del 4% hasta 2029. Sin tramo variable. Caja 9 M EUR.
La financiación futura dependerá de las condiciones al refinanciar.
""",
    "prisma-clientes.md": """# Prisma, contratos vigentes al 31/12/2025
El 81% de ingresos de 2025 estuvo cubierto por alquileres mayoristas plurianuales.
El cliente mayor aporta 14%. Las renovaciones de 2027 aún no están contratadas.
""",
    "vector-estados.md": """# Vector, cierre 31/12/2025
2023, 2024, 2025, en M EUR. Ingresos: 52, 65, 83. Resultado operativo: 6, 8, 12.
Flujo operativo: 5, 7, 9. Capex: 3, 4, 5. Integra instalaciones y cobra por hitos.
""",
    "vector-deuda.md": """# Vector, nota de financiación al 31/12/2025
Deuda fija 5 M EUR al 5%, caja 11 M EUR. Sin deuda variable.
No incluye deuda de clientes ni garantiza la financiación de sus proyectos.
""",
    "vector-clientes.md": """# Vector, cartera comercial al 31/12/2025
El 48% de ingresos de 2025 provino de proyectos cuyos clientes recurrieron a crédito.
La cartera inicial para 2026 tiene 36 M EUR de hitos previstos, con fechas sujetas
a aprobación final de los clientes. Los aplazamientos desplazan la facturación.
""",
}
UPDATE = {
    "2026-04-15-credito.md": """# Observatorio, actualización 15/04/2026
El coste de referencia del crédito variable sube del 4% al 6%. Para el puente
anualizado manténgase constante el principal y aplíquese el cambio solo a la parte
efectivamente expuesta. La deuda fija vigente de Prisma conserva sus condiciones.
""",
    "2026-04-15-nebula.md": """# Nébula, fe de erratas sobre el cierre de 2025
El cuadro preliminar omitía una cobertura vigente que fija el coste de 30 M EUR
del tramo variable hasta fin de 2027. El tramo variable nominal sigue siendo
60 M EUR, pero solo 30 M EUR quedan expuestos al cambio de referencia durante
el horizonte anualizado. El total de deuda y los vencimientos no cambian.
""",
    "2026-04-15-vector.md": """# Vector, actualización comercial 15/04/2026
Dos clientes aplazaron hasta 2027 hitos por 9 M EUR antes previstos para 2026
al no cerrar financiación. No se han cancelado los contratos. No hay datos
suficientes para estimar el efecto exacto sobre margen o flujo de caja.
""",
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def materialize(path, documents):
    path.mkdir(exist_ok=True)
    for name, content in documents.items():
        with (path / name).open("x", encoding="utf-8") as stream:
            stream.write(content)


def prepare(root):
    root.mkdir(parents=True)
    (root / "mandato.md").write_text(MANDATE, encoding="utf-8")
    materialize(root / "fuentes-iniciales", INITIAL)
    materialize(root / "fuentes-actualizacion", UPDATE)
    for phase, (message, criteria) in TASKS.items():
        objective = root / f"{phase}.json"
        dump(objective, {"id": phase, "description": message, "criteria": criteria})
        Objective.load(objective)
    for rep in (1, 2):
        for arm in ("progress", "nota"):
            output = root / f"r{rep}-{arm}"
            prepare_experiment(output, new=True, deliberative=True, knowledge_agent="off")
            shutil.copytree(root / "fuentes-iniciales", output / "estado/materiales")
    inputs = [root / "mandato.md", *(root.glob("*.json")),
              *(root.glob("fuentes-*/*.md"))]
    dump(root / "plan.json", {
        "budget_per_phase": BUDGET, "renewal_bytes": THRESHOLD,
        "blocks": [["r1-progress", "r1-nota"], ["r2-nota", "r2-progress"]],
        "sha256": {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in inputs},
    })


def run_phase(root, name, phase, plan):
    output = root / name
    command = [
        sys.executable, "-X", "utf8", "-m", "research_agent", Objective.load(root / f"{phase}.json").description,
        "--continue", "--output", str(output), "--run-name", phase,
        "--mandate", str(root / "mandato.md"), "--continuous", "--general-review", "off",
        "--objective", str(root / f"{phase}.json"), "--max-calls", str(plan["budget_per_phase"]),
        "--renewal-bytes", str(plan["renewal_bytes"]), "--progress-step-calls", "15",
    ]
    if name.endswith("-nota"):
        command.append("--context-note")
    print(f"START {name} {phase}", flush=True)
    with (root / f"{name}-{phase}.log").open("xb") as log:
        code = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT).returncode
    print(f"EXIT {name} {phase} {code}", flush=True)
    return code


def launch(root):
    plan = json.loads((root / "plan.json").read_bytes())
    for name, digest in plan["sha256"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"Frozen input changed: {name}")
    os.environ["LLM_TIMEOUT_SECONDS"] = "180"
    os.environ["LLM_CALL_BUDGET_SECONDS"] = "180"
    from dataclasses import asdict
    from findata.settings import settings
    from infra.llm_factory import configured_profile
    profile = configured_profile(settings, "planner")
    effective = asdict(profile)
    dump(root / "perfil-modelo.json", {key: effective[key] for key in
                                      ("provider", "model", "max_output_tokens") if key in effective})
    with (root / "launched.lock").open("x", encoding="utf-8") as marker:
        marker.write(str(os.getpid()))
    for block in plan["blocks"]:
        with ThreadPoolExecutor(max_workers=2) as pool:
            for phase in TASKS:
                results = list(pool.map(lambda name: run_phase(root, name, phase, plan), block))
                if any(results):
                    print(f"PAUSED {block} {phase}: {results}", flush=True)
                    return 1
                if phase == "inicial":
                    for name in block:
                        output = root / name
                        shutil.copytree(output / "estado", root / "instantaneas" / name)
                        for path in sorted((root / "fuentes-actualizacion").glob("*.md")):
                            target = output / "estado/materiales" / path.name
                            with target.open("xb") as stream:
                                stream.write(path.read_bytes())
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--prepare", action="store_true")
    args = parser.parse_args()
    root = args.output.resolve()
    if args.prepare:
        prepare(root)
    else:
        sys.exit(launch(root))
