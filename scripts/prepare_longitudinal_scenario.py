"""Freeze an alphabetical universe by data coverage, never by subsequent returns."""
import argparse
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy import create_engine, text
from findata.settings import settings
from research_agent.contracts import AgentLimits
import yaml


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    start, end = date(2023, 1, 1), date(2024, 12, 31)
    engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 10})
    try:
        with engine.connect() as connection:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            connection.execute(text("SET LOCAL statement_timeout = '30000'"))
            rows = connection.execute(text("""
                SELECT p.symbol, coalesce(cp.name,p.symbol) name
                FROM price_bars p LEFT JOIN company_profiles cp ON cp.symbol=p.symbol
                WHERE p.provider='alpha_vantage' AND cp.country='USA' AND p.trade_date BETWEEN :before AND :end
                  AND EXISTS (SELECT 1 FROM financial_facts f WHERE f.symbol=p.symbol
                    AND f.provider='alpha_vantage' AND f.period_type='annual' AND f.currency='USD'
                    AND f.fiscal_period <= :available_period AND f.value IS NOT NULL)
                GROUP BY p.symbol,cp.name
                HAVING min(p.trade_date) <= :start AND max(p.trade_date) >= :last_week
                ORDER BY p.symbol LIMIT 50
            """), {"start": start, "before": start - timedelta(days=7), "end": end,
                    "last_week": end - timedelta(days=7), "available_period": start - timedelta(days=120)}).mappings().all()
            connection.rollback()
    finally:
        engine.dispose()
    if len(rows) != 50:
        raise ValueError(f"Need 50 covered companies, found {len(rows)}")
    messages = [
        "Soy un inversor a largo plazo. Dispongo de 100.000 USD ficticios y acepto mantener efectivo. Investiga dentro del universo disponible y decide cómo empezar; conserva lo útil para futuras revisiones.",
        "Revisa cómo ha evolucionado tu evaluación desde el comienzo. Decide si conviene actuar o conservar la cartera.",
        "Me preocupa la concentración. Revisa los riesgos de las posiciones y las alternativas que consideres relevantes.",
        "Comprueba si las nuevas cifras alteran los fundamentos de tus decisiones. No es obligatorio cambiar de opinión ni operar.",
        "Llevamos aproximadamente un año. Recupera lo conservado y revisa qué se sostiene, qué ha cambiado y qué queda pendiente.",
        "Reconsidera las posiciones que hoy merezcan atención. Distingue cambios de negocio, precio y tus hipótesis.",
        "Revisa si mantener efectivo o reasignar capital tiene sentido con la información disponible.",
        "Nos acercamos al final del seguimiento. Revisa la cartera y deja claros fundamentos, incertidumbres y asuntos que convendría seguir.",
    ]
    dates = [date(2023 + n // 4, 1 + 3 * (n % 4), 1).isoformat() for n in range(8)]
    config = {"schema_version": "longitudinal-v1", "id": "colaboracion-historica-v1",
              "start": str(start), "end": str(end), "universe": [dict(row) for row in rows],
              "initial_cash": "100000", "max_positions": 10, "annual_lag_days": 120,
              "messages": dict(zip(dates, messages)), "limits": asdict(AgentLimits()),
              "price_review": {"status": "pending", "basis": "unadjusted",
                               "evidence": "Findata Alpha Vantage TIME_SERIES_DAILY. Corporate actions are not stored; adjustment review pending."}}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        yaml.safe_dump(config, stream, allow_unicode=True, sort_keys=False)
    print(f"Frozen 50 companies by coverage and alphabetical order: {args.output}")


if __name__ == "__main__":
    main()
