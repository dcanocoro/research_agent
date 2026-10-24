"""Historical tool composition; no campaign imports and no unrestricted data reads."""
from datetime import date
from typing import Any

from ..tools import ToolRegistry
from .state import Simulator


def register_simulation(registry: ToolRegistry, simulator: Simulator, search: Any) -> None:
    from findata.read.historical import available_facts
    string = {"type": "string", "minLength": 1, "maxLength": 200}

    def search_companies(query: str, page: int = 1) -> dict[str, Any]:
        matches = [item for symbol, item in sorted(simulator.universe.items())
                   if query.casefold() in (symbol + " " + item["name"]).casefold()]
        offset = (page - 1) * 25
        return {"as_of": simulator.state["date"], "companies": matches[offset:offset + 25],
                "total": len(matches), "page": page, "page_size": 25}

    def read_financials(symbol: str) -> dict[str, Any]:
        symbol = simulator.symbol(symbol)
        facts = available_facts([r for r in simulator.data["facts"] if r["symbol"] == symbol],
                                simulator.today, simulator.config["annual_lag_days"])
        return {"symbol": symbol, "as_of": simulator.state["date"], "observations": facts,
                "last_close": simulator.last_price(symbol),
                "price_convention": simulator.data.get("price_convention"),
                "availability_policy": {"annual_lag_days": simulator.config["annual_lag_days"],
                                        "unknown_nonannual": "excluded"},
                "limitations": simulator.data.get("limitations", [])}

    def read_company(symbol: str) -> dict[str, Any]:
        symbol = simulator.symbol(symbol)
        return {"identity": simulator.universe[symbol], **read_financials(symbol)}

    def read_metric_trend(symbol: str, metric: str, years: int) -> dict[str, Any]:
        simulator.symbol(symbol)
        return {"available": False, "reason": "Current derived tables are disabled in historical mode. Use dated observations and calculate."}

    async def search_web(query: str) -> Any:
        results = await search.search_documents(query, end_date=simulator.today, filter_by_published_date=True)
        return {"as_of": simulator.state["date"], "end_date": simulator.state["date"],
                "filter_by_published_date": True, "results": results,
                "limitation": "Search dates and historical page contents are imperfect; model training may include future events."}

    registry.register("search_companies", "Search frozen universe; empty query lists all companies, 25 per page.",
                      {"query": {"type": "string", "maxLength": 200}, "page": {"type": "integer", "minimum": 1}},
                      search_companies, execution="inline", material=True)
    registry.register("read_company", "Read declared identity and available historical observations; no current snapshot.",
                      {"symbol": string}, read_company, execution="inline", material=True)
    registry.register("read_financials", "Read facts available as of simulated date; estimated dates are explicitly labelled.",
                      {"symbol": string}, read_financials, execution="inline", material=True)
    registry.register("read_metric_trend", "Historical derived trends are unavailable; use observations and calculate.",
                      {"symbol": string, "metric": string, "years": {"type": "integer", "enum": [3, 5]}},
                      read_metric_trend, execution="inline")
    registry.register("search_web", "Search web up to simulated date; snippets only.",
                      {"query": {"type": "string", "minLength": 1, "maxLength": 4000}},
                      search_web, execution="async", material=True)
    for name, description, properties, function in (
        ("portfolio_get", "Read simulated portfolio and reserved resources.", {}, simulator.get),
        ("portfolio_buy", "Reserve USD for purchase at next available close strictly after today.",
         {"symbol": string, "amount": string}, simulator.buy),
        ("portfolio_sell", "Reserve shares for sale at next available close strictly after today.",
         {"symbol": string, "quantity": string}, simulator.sell),
        ("portfolio_close", "Sell all available shares; pending sales remain reserved.", {"symbol": string}, simulator.close),
        ("portfolio_history", "Read pending, executed and cancelled orders.", {}, simulator.history),
        ("notify_user", "Record an explicit user communication locally. No external message is sent.",
         {"message": {"type": "string", "minLength": 1, "maxLength": 16000}}, simulator.notify),
    ):
        registry.register(name, description, properties, function, execution="inline", material=True)


def activation_message(simulator: Simulator, message: str, kind: str) -> str:
    return (f"Fecha simulada: {simulator.today}. Activación: {kind}.\n"
            "Actúa únicamente con la información disponible en esta fecha. La cartera es ficticia; "
            "puedes operarla dentro del universo y los límites de sus herramientas. Las órdenes se ejecutan "
            "al siguiente cierre disponible, no al solicitarlas. Consulta cartera e investigaciones cuando resulte útil. "
            "La disponibilidad estimada de fundamentales es una convención experimental aplicada por las herramientas.\n"
            + ("Los precios de cartera son participaciones normalizadas de una serie histórica real ajustada: "
               "no son cotizaciones ni cantidades de acciones negociadas. Dividendos y splits están incorporados "
               "en la serie; no se abonan ni se aplican otra vez.\n" if simulator.data.get("price_convention") else "")
            + ("No hay un nuevo mensaje humano. Decide si procede investigar, revisar, operar o no actuar. "
               "Tu cierre es un registro interno; usa notify_user solo si hay algo que comunicar.\n" if kind == "temporal" else "")
            + message)
