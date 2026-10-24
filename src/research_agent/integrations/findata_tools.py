from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, Iterator
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..tools import ToolRegistry


class FindataTools:
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self.session_factory = session_factory

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self.session_factory() as session:
            if session.get_bind().dialect.name != "postgresql":
                raise ValueError("Findata reads require PostgreSQL.")
            session.execute(text("SET TRANSACTION READ ONLY"))
            session.execute(text("SET LOCAL statement_timeout = '15000'"))
            try:
                yield session
            finally:
                session.rollback()

    def search_companies(self, query: str, page: int = 1) -> Any:
        from findata.read import universe
        with self.session() as session:
            return universe.list(session, search=query, page=page)

    def read_company(self, symbol: str) -> Any:
        from findata.read.company import snapshot
        with self.session() as session:
            return snapshot(session, [symbol])

    def read_financials(self, symbol: str) -> Any:
        from findata.read.case_financials import observations
        with self.session() as session:
            return observations(session, symbol)

    def read_metric_trend(self, symbol: str, metric: str, years: int) -> Any:
        from findata.read.metrics import trend
        with self.session() as session:
            return trend(session, symbol, metric, years)

    def register(self, registry: ToolRegistry) -> None:
        from findata.read.metrics import METRIC_DEFINITIONS
        string = {"type": "string", "minLength": 1, "maxLength": 200}
        registry.register("search_companies", "Search the stored financial universe.",
                          {"query": string, "page": {"type": "integer", "minimum": 1}}, self.search_companies, material=True)
        registry.register("read_company", "Read company snapshot with coverage metadata.", {"symbol": string}, self.read_company, material=True)
        registry.register("read_financials", "Read annual/quarterly financial observations with individual provenance.", {"symbol": string}, self.read_financials, material=True)
        registry.register("read_metric_trend", "Read supported deterministic metric history.",
                          {"symbol": string, "metric": {"type": "string", "enum": list(METRIC_DEFINITIONS)},
                           "years": {"type": "integer", "enum": [3, 5]}}, self.read_metric_trend, material=True)
