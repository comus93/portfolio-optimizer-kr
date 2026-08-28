from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class CanonicalResult:
    configuration: dict[str, Any]
    data_coverage: dict[str, Any]
    asset_statistics: dict[str, Any]
    optimization_result: dict[str, Any]
    efficient_frontier: list[dict[str, Any]] = field(default_factory=list)
    portfolio_performance: dict[str, Any] = field(default_factory=dict)
    benchmark_analytics: dict[str, Any] = field(default_factory=dict)
    correlations: dict[str, Any] = field(default_factory=dict)
    return_decomposition: dict[str, Any] = field(default_factory=dict)
    risk_decomposition: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write_json(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(_normalise(self.to_dict()), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _json_default(value: Any) -> Any:
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="records")
    if isinstance(value, pd.Series):
        return value.to_dict()
    raise TypeError(f"not JSON serializable: {type(value)!r}")


def _normalise(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if value is pd.NaT:
        return None
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (pd.Timestamp,)):
        return value.isoformat()
    if isinstance(value, np.generic):
        return _normalise(value.item())
    if isinstance(value, np.ndarray):
        return [_normalise(item) for item in value.tolist()]
    if isinstance(value, pd.DataFrame):
        return _normalise(value.to_dict(orient="records"))
    if isinstance(value, pd.Series):
        return _normalise(value.to_dict())
    if isinstance(value, dict):
        return {str(key): _normalise(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_normalise(item) for item in value]
    return _json_default(value)


def write_validation_run(
    result: CanonicalResult, output_dir: str | Path, tables: dict[str, pd.DataFrame]
) -> None:
    """Persist a reviewable canonical result and one UTF-8 CSV per table."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    result.write_json(directory / "result.json")
    for name, table in sorted(tables.items()):
        table.to_csv(directory / f"{name}.csv", index=False, encoding="utf-8")


def write_analysis_run(result: dict[str, Any], output_dir: str | Path) -> None:
    """Write canonical JSON plus lossless raw and human review CSV layers."""
    tables = result.get("_tables", {})
    clean = {key: value for key, value in result.items() if key != "_tables"}
    canonical = CanonicalResult(**clean)
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    canonical.write_json(directory / "result.json")
    raw_dir, review_dir = directory / "raw", directory / "review"
    raw_dir.mkdir(exist_ok=True); review_dir.mkdir(exist_ok=True)
    for name, table in sorted(tables.items()):
        if table.empty:
            continue
        table.to_csv(raw_dir / f"{name}.csv", index=False, encoding="utf-8")
        # Temporary compatibility path for earlier callers; raw/ is authoritative.
        table.to_csv(directory / f"{name}.csv", index=False, encoding="utf-8")
        _review_table(table).to_csv(review_dir / f"{name}.csv", index=False, encoding="utf-8")
    configuration = result.get("configuration", {})
    (directory / "README.md").write_text(
        f"# Optimization run\n\nRun ID: `{configuration.get('run_id', directory.name)}`. "
        "`result.json` is canonical full precision; `raw/` preserves decimal tables; "
        "`review/` presents percentage-point columns suffixed `_pct` while ratios remain unitless.\n",
        encoding="utf-8",
    )


def _review_table(table: pd.DataFrame) -> pd.DataFrame:
    out = table.copy()
    for column in list(out.columns):
        lower = str(column).lower()
        if any(token in lower for token in ("expected_return", "volatility", "weight_", "drawdown", "cagr", "tracking_error", "contribution")):
            out[f"{column}_pct"] = out.pop(column) * 100.0
    return out
