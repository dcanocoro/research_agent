"""Freeze 50 adjusted market series and event evidence; no financial database writes."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import yaml

from research_agent.simulation.state import positive, read, save
from research_campaigns.longitudinal import export_data, load_scenario, preflight


ENDPOINT = "https://query1.finance.yahoo.com/v8/finance/chart/"
METHODOLOGY = "https://in.help.yahoo.com/kb/adjusted-close-sln28256.html"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(symbol: str, payload: dict, start: date, end: date, reference: str) -> tuple[list[dict], dict]:
    """Provider close is split-adjusted; adjclose includes dividends. Never split it twice."""
    chart = payload["chart"]
    if chart.get("error") or not chart.get("result"):
        raise ValueError(f"Missing provider result for {symbol}")
    result = chart["result"][0]
    meta = result["meta"]
    if meta["symbol"] != symbol or meta["currency"] != "USD" or meta.get("dataGranularity") != "1d":
        raise ValueError(f"Unexpected symbol or currency for {symbol}")
    zone = ZoneInfo(meta["exchangeTimezoneName"])
    closes = result["indicators"]["quote"][0]["close"]
    adjusted = result["indicators"]["adjclose"][0]["adjclose"]
    timestamps = result["timestamp"]
    if len(timestamps) != len(closes) or len(timestamps) != len(adjusted):
        raise ValueError(f"Unequal series lengths for {symbol}")
    observations = []
    for stamp, close, adjclose in zip(timestamps, closes, adjusted):
        day = datetime.fromtimestamp(stamp, zone).date()
        if start - timedelta(days=10) <= day <= end:
            # A missing trading-session value is not silently forward-filled.
            observations.append({"date": str(day), "close": str(positive(close)),
                                 "adjusted_close": str(positive(adjclose))})
    anchors = [row for row in observations if row["date"] <= str(start)]
    if not anchors:
        raise ValueError(f"No anchor close at/before start for {symbol}")
    anchor = max(anchors, key=lambda row: row["date"])
    prices = []
    with localcontext() as context:
        context.prec = 34
        for row in observations:
            # Common subsequent adjustment factors cancel in this ratio. The
            # synthetic unit is not the historical traded share price or quantity.
            value = Decimal(100) * Decimal(row["adjusted_close"]) / Decimal(anchor["adjusted_close"])
            prices.append({"symbol": symbol, "date": row["date"], "close": str(value),
                           "unit": "USD_per_normalized_adjusted_unit", "provider": "yahoo_finance_chart",
                           "source_ref": reference, "anchor_date": anchor["date"]})
    events = []
    for kind, entries in result.get("events", {}).items():
        for entry in entries.values():
            day = datetime.fromtimestamp(entry["date"], zone).date()
            if start <= day <= end:
                events.append({"symbol": symbol, "kind": kind, "date": str(day), "value": entry})
    events.sort(key=lambda row: (row["date"], row["kind"]))
    changes = []
    for previous, current in zip(observations, observations[1:]):
        change = Decimal(current["adjusted_close"]) / Decimal(previous["adjusted_close"]) - 1
        if abs(change) >= Decimal("0.20"):
            changes.append({"date": current["date"], "adjusted_daily_return": str(change)})
    summary = {"symbol": symbol, "currency": meta["currency"], "sessions": len(prices),
               "first": prices[0]["date"], "last": prices[-1]["date"], "anchor": anchor,
               "events": events, "large_changes": changes, "source_ref": reference}
    return prices, summary


def normalize_issuer(symbol: str, original: list[dict], actions: dict, start: date, end: date,
                     reference: str) -> tuple[list[dict], dict]:
    """Same documented cash-dividend multiplier as Yahoo, with explicit issuer fallback."""
    if actions["currency"] != "USD" or actions["splits"]:
        raise ValueError("Issuer fallback supports reviewed USD cash dividends without splits only.")
    rows = sorted((p for p in original if p["symbol"] == symbol and
                   start - timedelta(days=10) <= date.fromisoformat(p["date"]) <= end), key=lambda p: p["date"])
    events = []
    for dividend in actions["dividends"]:
        record = dividend["record_date"]
        prior = [r for r in rows if r["date"] < record]
        if not prior:
            raise ValueError("Missing session before record date")
        ex_date = prior[-1]["date"] if record < "2024-05-29" else record
        events.append({"symbol": symbol, "kind": "dividends", "date": ex_date,
                       "date_basis": "derived_regular_way_from_record", "value": dividend,
                       "rule_source": actions["ex_date_policy_source"]})
    adjusted = []
    factor = Decimal(1)
    with localcontext() as context:
        context.prec = 34
        for row in reversed(rows):
            adjusted.append({"date": row["date"], "close": row["close"],
                             "adjusted_close": str(positive(row["close"]) * factor)})
            for event in (e for e in events if e["date"] == row["date"]):
                prior = [p for p in rows if p["date"] < row["date"]]
                previous_close = positive(prior[-1]["close"])
                multiplier = 1 - positive(event["value"]["amount"]) / previous_close
                if not 0 < multiplier <= 1:
                    raise ValueError("Invalid distribution multiplier")
                factor *= multiplier
        adjusted.reverse()
        anchor = max((r for r in adjusted if r["date"] <= str(start)), key=lambda p: p["date"])
        prices = [{"symbol": symbol, "date": r["date"],
                   "close": str(100 * Decimal(r["adjusted_close"]) / Decimal(anchor["adjusted_close"])),
                   "unit": "USD_per_normalized_adjusted_unit", "provider": "findata_plus_issuer_cash_adjustment",
                   "source_ref": reference, "anchor_date": anchor["date"]} for r in adjusted]
    summary = {"symbol": symbol, "currency": "USD", "sessions": len(prices), "first": prices[0]["date"],
               "last": prices[-1]["date"], "anchor": anchor, "events": events, "large_changes": [],
               "source_ref": reference, "exception": actions["reason"], "ex_date_policy": actions["ex_date_policy"]}
    return prices, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, default=Path("campaigns/colaboracion-historica-v1/scenario.yaml"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--facts", type=Path, help="Previously frozen real Findata export; otherwise export read-only")
    parser.add_argument("--cached-responses", type=Path, help="Replay already captured Yahoo JSON without network")
    parser.add_argument("--issuer-actions", type=Path, help="Explicit reviewed issuer dividend fallback for unavailable series")
    args = parser.parse_args()
    config = load_scenario(args.scenario)
    start, end = date.fromisoformat(config["start"]), date.fromisoformat(config["end"])
    args.output.mkdir(parents=True, exist_ok=False)
    raw = args.output / "responses"
    raw.mkdir()
    issuer_actions = read(args.issuer_actions) if args.issuer_actions else {}
    if args.issuer_actions:
        save(args.output / "issuer-actions.json", issuer_actions)
    params = {"period1": int(datetime.combine(start - timedelta(days=10), time(), timezone.utc).timestamp()),
              "period2": int(datetime.combine(end + timedelta(days=2), time(), timezone.utc).timestamp()),
              "interval": "1d", "events": "div,splits,capitalGains"}

    def fetch(company: dict) -> dict:
        symbol = company["symbol"]
        path = raw / f"{symbol}.json"
        cached = args.cached_responses / f"{symbol}.json" if args.cached_responses else None
        if cached is not None and cached.exists():
            payload = read(cached)
            save(path, payload)
        else:
            response = httpx.get(ENDPOINT + symbol, params=params, headers={"User-Agent": "Mozilla/5.0"}, timeout=40)
            response.raise_for_status()
            payload = response.json()
            save(path, payload)
        return {"symbol": symbol, "path": path.name, "sha256": sha(path),
                "url": ENDPOINT + symbol, "parameters": params,
                "cached_from": str(cached) if cached is not None and cached.exists() else None}

    manifest = {"retrieved_at": datetime.now(timezone.utc).isoformat(), "provider": "Yahoo Finance chart",
                "methodology_url": METHODOLOGY, "sources": [], "errors": []}
    # Small bounded concurrency, no service, ingestion or installed dependency changes.
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = [(c["symbol"], pool.submit(fetch, c)) for c in config["universe"] if c["symbol"] not in issuer_actions]
        for symbol, future in futures:
            try:
                manifest["sources"].append(future.result())
            except Exception as exc:
                manifest["errors"].append({"symbol": symbol, "error_type": type(exc).__name__})
            save(args.output / "sources.json", manifest)
    if manifest["errors"]:
        raise ValueError("Incomplete provider coverage; see sources.json. No universe reduction.")
    data = read(args.facts) if args.facts else export_data(config)
    save(args.output / "findata-original.json", data)
    prices, coverage = [], []
    for source in manifest["sources"]:
        rows, summary = normalize(source["symbol"], read(raw / source["path"]), start, end,
                                  f"sha256:{source['sha256']}")
        prices.extend(rows)
        coverage.append(summary)
    for symbol, actions in issuer_actions.items():
        rows, summary = normalize_issuer(symbol, data["prices"], actions, start, end,
                                        "sha256:" + sha(args.output / "issuer-actions.json"))
        prices.extend(rows)
        coverage.append(summary)
    if {c["symbol"] for c in coverage} != {c["symbol"] for c in config["universe"]}:
        raise ValueError("Adjusted coverage must match frozen universe exactly.")
    # Preserve raw Findata inputs above; only this new experimental dataset replaces prices.
    data.update(prices=prices, price_basis="adjusted", price_convention={
        "method": "100 * adjusted_close(t) / adjusted_close(last session <= scenario start); Yahoo or explicit issuer dividend fallback",
        "unit": "USD_per_normalized_adjusted_unit", "dividends": "embedded in provider adjustment; no extra cash credit",
        "splits": "embedded in provider adjustment; do not multiply holdings or orders",
        "methodology_url": METHODOLOGY, "sources_sha256": sha(args.output / "sources.json")})
    data["price_convention"]["issuer_fallback_symbols"] = list(issuer_actions)
    data["price_convention"]["findata_original_sha256"] = sha(args.output / "findata-original.json")
    if issuer_actions:
        data["price_convention"]["issuer_actions_sha256"] = sha(args.output / "issuer-actions.json")
    data["price_convention"]["normalization_anchor"] = "last trading session at or before " + str(start)
    data["limitations"] = [
        "Real observed prices, normalized adjusted units; not traded share prices or broker execution.",
        "Provider adjusted history is retrospective and can be revised; raw responses are frozen.",
        "Dividends/distributions follow provider adjustment; no separate cash or spin-off asset accounting.",
        "Event feed is not an exhaustive legal corporate-action registry; market/reference anomalies require review.",
        "Stored Findata fundamentals may have been restated; publication availability may be estimated."]
    save(args.output / "data.json", data)
    report = {"companies": coverage, "splits": [e for c in coverage for e in c["events"] if e["kind"] == "splits"],
              "event_counts": {kind: sum(e["kind"] == kind for c in coverage for e in c["events"])
                               for kind in {e["kind"] for c in coverage for e in c["events"]}},
              "large_changes": [{"symbol": c["symbol"], **change} for c in coverage for change in c["large_changes"]],
              "data_sha256": sha(args.output / "data.json"), "status": "awaiting_review"}
    save(args.output / "review.json", report)
    print(json.dumps({"companies": len(coverage), "prices": len(prices), "splits": report["splits"],
                      "event_counts": report["event_counts"], "large_changes": report["large_changes"]}, indent=2))


if __name__ == "__main__":
    main()
