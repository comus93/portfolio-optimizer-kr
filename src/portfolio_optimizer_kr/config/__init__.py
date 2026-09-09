from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from .names import hydrate_asset_names
from .yaml import (
    ConfigValidationError,
    RunConfig,
    request_from_config as _request_from_config,
    write_user_config,
)

PINNED_US_3M_TBILL_ANNUAL_RATE_PCT = 3.8394827586206895


def _materialize_default_risk_free(config: Mapping[str, Any]) -> Mapping[str, Any]:
    """Materialize the project research RF default when the user omitted RF.

    The value is the effective U.S. 3-Month T-Bill annual rate previously
    resolved by runs/20260908-0002/result.json. Persisting it as fixed avoids
    re-fetching FRED/FDR TB3MS on every default research run.
    """
    risk_free = config.get("risk_free")
    if risk_free not in (None, {}):
        return config
    effective = dict(config)
    effective["risk_free"] = {
        "mode": "fixed",
        "annual_rate_pct": PINNED_US_3M_TBILL_ANNUAL_RATE_PCT,
    }
    return effective


def request_from_config(config: Mapping[str, Any]) -> RunConfig:
    return _request_from_config(_materialize_default_risk_free(config))


def load_run_config(path: str | Path) -> RunConfig:
    source = Path(path)
    loaded = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise ConfigValidationError("YAML root must be a mapping")
    return request_from_config(loaded)


__all__ = [
    "ConfigValidationError",
    "PINNED_US_3M_TBILL_ANNUAL_RATE_PCT",
    "RunConfig",
    "hydrate_asset_names",
    "load_run_config",
    "request_from_config",
    "write_user_config",
]
