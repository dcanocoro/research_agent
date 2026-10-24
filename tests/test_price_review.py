"""Adjusted units are derived from real sources, not retroactive share-count changes."""
from datetime import date, datetime, timezone
from decimal import Decimal
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("review_historical_prices", Path(__file__).parents[1] / "scripts/review_historical_prices.py")
assert spec is not None and spec.loader is not None
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


def payload():
    return {"chart": {"error": None, "result": [{"meta": {
        "symbol": "AAA", "currency": "USD", "exchangeTimezoneName": "America/New_York", "dataGranularity": "1d"},
        "timestamp": [int(datetime(2022, 12, 30, 15, tzinfo=timezone.utc).timestamp()),
                      int(datetime(2023, 1, 3, 15, tzinfo=timezone.utc).timestamp())],
        "indicators": {"quote": [{"close": [50, 50]}], "adjclose": [{"adjclose": [40, 40]}]},
        "events": {"splits": {"split": {"date": int(datetime(2023, 1, 3, 15, tzinfo=timezone.utc).timestamp()),
                                         "numerator": 2, "denominator": 1}}}}]}}


def test_normalization_cancels_common_future_factor_and_does_not_double_split():
    value = payload()
    prices, summary = review.normalize("AAA", value, date(2023, 1, 1), date(2023, 1, 31), "sha256:source")
    assert [Decimal(p["close"]) for p in prices] == [100, 100]
    assert summary["events"][0]["kind"] == "splits"
    value["chart"]["result"][0]["indicators"]["adjclose"][0]["adjclose"] = [20, 20]
    changed, _ = review.normalize("AAA", value, date(2023, 1, 1), date(2023, 1, 31), "sha256:source")
    assert changed == prices


@pytest.mark.parametrize("field,value", [("currency", "GBP"), ("symbol", "OTHER"), ("dataGranularity", "1h")])
def test_provider_identity_currency_and_granularity_are_checked(field, value):
    body = payload()
    body["chart"]["result"][0]["meta"][field] = value
    with pytest.raises(ValueError):
        review.normalize("AAA", body, date(2023, 1, 1), date(2023, 1, 31), "sha256:source")


def test_missing_adjusted_close_is_not_filled_with_raw_close():
    body = payload()
    body["chart"]["result"][0]["indicators"]["adjclose"][0]["adjclose"][1] = None
    with pytest.raises(ValueError):
        review.normalize("AAA", body, date(2023, 1, 1), date(2023, 1, 31), "sha256:source")


@pytest.mark.parametrize("days,record,ex_date", [
    (["2023-03-29", "2023-03-30", "2023-03-31"], "2023-03-31", "2023-03-30"),
    (["2024-06-27", "2024-06-28"], "2024-06-28", "2024-06-28")])
def test_issuer_adjustment_uses_regular_way_ex_date_and_neutralizes_dividend(days, record, ex_date):
    rows = [{"symbol": "AAA", "date": day, "close": "100" if day < ex_date else "99"} for day in days]
    actions = {"currency": "USD", "splits": [], "dividends": [{"record_date": record, "amount": "1"}],
               "ex_date_policy_source": "rule-source", "ex_date_policy": "derived", "reason": "provider unavailable"}
    prices, summary = review.normalize_issuer("AAA", rows, actions, date.fromisoformat(days[0]),
                                             date.fromisoformat(days[-1]), "sha256:source")
    assert all(Decimal(p["close"]) == 100 for p in prices)
    assert summary["events"][0]["date"] == ex_date
    assert summary["events"][0]["date_basis"] == "derived_regular_way_from_record"
