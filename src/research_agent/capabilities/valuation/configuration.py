from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
from dcf_lab import FinancialSnapshot, __version__
from dcf_lab.reporting import fingerprint
from research_agent.storage.workspace import Workspace


class ValuationConfiguration(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, allow_inf_nan=False)
    schema_version: Literal["1"] = "1"
    package_version: Literal["0.2.0"] = "0.2.0"
    source: Literal["snapshot", "findata"]
    model: str = Field(min_length=1)
    timeout_seconds: float = Field(default=120, gt=0, le=300)
    snapshot: FinancialSnapshot | None = None
    equity_risk_premium: float | None = Field(default=None, ge=0, le=1)
    erp_as_of: date | None = None
    erp_source: str | None = None

    @model_validator(mode="after")
    def validate_source(self) -> ValuationConfiguration:
        if __version__ != self.package_version:
            raise ValueError("Installed DCF Lab version differs from frozen configuration")
        if not self.model.strip():
            raise ValueError("Explicit valuation model required")
        if (self.source == "snapshot") != (self.snapshot is not None):
            raise ValueError("Snapshot source requires exactly one explicit snapshot")
        if self.source == "findata" and any(v is None for v in (
                self.equity_risk_premium, self.erp_as_of, self.erp_source)):
            raise ValueError("FinData source requires explicit ERP, date and reference")
        return self


def configuration(root: Path | None, requested: dict | None = None) -> ValuationConfiguration | None:
    saved = None
    if root is not None:
        path = root / "dcf-lab.json"
        Workspace._check_links(path)
        if path.exists():
            saved = ValuationConfiguration.model_validate_json(path.read_bytes())
        if requested is not None:
            proposed = ValuationConfiguration.model_validate(requested)
            if saved != proposed:
                raise ValueError("DCF configuration is frozen; create a new experiment")
        for manifest in sorted((root / "ejecuciones").glob("*/manifiesto.json"),
                               key=lambda p: p.stat().st_mtime_ns, reverse=True):
            Workspace._check_links(manifest)
            metadata = json.loads(manifest.read_bytes()).get("configuration", {}).get("valuation", {})
            expected = fingerprint(saved.model_dump(mode="json")) if saved else None
            if metadata.get("configuration_sha256") != expected:
                raise ValueError("DCF configuration differs from the previous recorded run")
            break
    return saved if root is not None else (ValuationConfiguration.model_validate(requested) if requested else None)


def freeze_configuration(root: Path, supplied: Path | None) -> None:
    if supplied is None:
        return
    Workspace._check_links(supplied)
    config = ValuationConfiguration.model_validate(json.loads(supplied.read_bytes()))
    path = root / "dcf-lab.json"
    Workspace._check_links(path)
    with path.open("xb") as stream:
        stream.write(config.model_dump_json(indent=2).encode("utf-8"))
