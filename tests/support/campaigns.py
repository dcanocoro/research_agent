import asyncio
import hashlib
from copy import deepcopy
from dataclasses import asdict
from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys
import pytest
import yaml
from findata.read.historical import available_facts
from research_agent.contracts import AgentLimits
from research_agent.capabilities.simulation.state import Simulator
from research_agent.capabilities.simulation.state import read
from research_agent.capabilities.simulation.state import save
from research_campaigns.execution.longitudinal import activations
from research_campaigns.execution.longitudinal import load_scenario
from research_campaigns.execution.longitudinal import preflight
from research_campaigns.execution.longitudinal import run_campaign
from support import fake_cli, instruction_control

def config(count=50):
    return {"schema_version": "longitudinal-v1", "id": "test", "start": "2023-01-01", "end": "2024-12-31",
            "universe": [{"symbol": f"S{i:02d}", "name": f"Company {i}"} for i in range(count)],
            "initial_cash": "100000", "max_positions": min(10, count), "annual_lag_days": 120,
            "messages": {"2023-01-01": "Investiga libremente y conserva lo útil.", "2023-03-01": "Revisa lo conservado."},
            "limits": asdict(AgentLimits()),
            "price_review": {"status": "approved", "basis": "synthetic", "evidence": "Deterministic test fixture"}}



def fact(symbol="S00", period="2021-12-31", kind="annual", published=None):
    return {"symbol": symbol, "metric": "total_revenue", "value": "100", "unit": "currency", "currency": "USD",
            "period": period, "period_type": kind, "published_at": published, "source_ref": "fixture:revenue",
            "provenance": {"provider": "fixture", "payload_hash": "fixed"}}


def dataset(cfg):
    prices = []
    day = date.fromisoformat(cfg["start"]) - timedelta(days=7)
    end = date.fromisoformat(cfg["end"])
    while day <= end:
        if day.weekday() < 5:
            prices.extend({"symbol": c["symbol"], "date": str(day), "close": "10", "provider": "fixture"}
                          for c in cfg["universe"])
        day += timedelta(days=1)
    return {"schema_version": "historical-input-v1", "price_basis": "synthetic", "prices": prices,
            "facts": [fact(c["symbol"]) for c in cfg["universe"]],
            "limitations": ["Synthetic fixture; no historical financial result"]}


def scenario(tmp_path, cfg):
    (tmp_path / "definition").mkdir(exist_ok=True)
    path = tmp_path / "definition/scenario.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


def sim(tmp_path, count=50):
    cfg = config(count)
    return Simulator.create(tmp_path / "sim", cfg, dataset(cfg))
