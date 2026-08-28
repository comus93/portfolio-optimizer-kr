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
    _write_review_summaries(result, tables, review_dir)
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


def _write_review_summaries(result: dict[str, Any], tables: dict[str, pd.DataFrame], directory: Path) -> None:
    cfg, weights = result["configuration"], result["optimization_result"].get("weights", {})
    assets = pd.DataFrame(cfg.get("assets", []))
    if not assets.empty:
        out = pd.DataFrame({"ticker": assets["symbol"], "name": assets.get("name"), "min_weight_pct": assets.get("min_weight", 0) * 100, "max_weight_pct": assets.get("max_weight", 1) * 100})
        out["provided_weight_pct"] = out["ticker"].map(cfg.get("provided_weights") or {}) * 100
        out["optimized_weight_pct"] = out["ticker"].map(weights) * 100
        out.to_csv(directory / "optimization_results.csv", index=False)
    perf = tables.get("portfolio_performance", pd.DataFrame())
    labels = [("Start Balance", "start_balance", "balance"), ("End Balance", "end_balance", "balance"), ("CAGR", "cagr", "pct"), ("Annualized Return", "annualized_return", "pct"), ("Expected Return", "expected_return", "pct"), ("Standard Deviation", "annualized_volatility", "pct"), ("Best Year", "best_year", "pct"), ("Worst Year", "worst_year", "pct"), ("Maximum Drawdown", "max_drawdown", "pct"), ("Sharpe Ratio (ex-post)", "sharpe_ex_post", "ratio"), ("Sortino Ratio", "sortino", "ratio")]
    indexed = perf.set_index("portfolio") if not perf.empty and "portfolio" in perf else pd.DataFrame()
    rows=[]
    for label,key,unit in labels:
        row={"metric":label,"unit":unit}
        for name in ("provided","optimized","benchmark"):
            value=indexed.loc[name,key] if name in indexed.index and key in indexed else None
            row[name]=value*100 if unit=="pct" and value is not None else value
        rows.append(row)
    pd.DataFrame(rows).to_csv(directory / "performance_summary.csv", index=False)
    trailing = pd.DataFrame(result.get("portfolio_performance", {}).get("trailing_returns", {})).T.rename_axis("portfolio").reset_index()
    mapping={"3m":"return_3m_pct","ytd":"ytd_pct","1y":"return_1y_pct","3y":"annualized_3y_pct","5y":"annualized_5y_pct","10y":"annualized_10y_pct","full_period":"full_period_cagr_pct","3y_annualized_volatility":"volatility_3y_pct","5y_annualized_volatility":"volatility_5y_pct"}
    trailing=trailing.rename(columns=mapping)
    for col in mapping.values():
        if col in trailing: trailing[col]=trailing[col]*100
    trailing.to_csv(directory / "trailing_returns.csv", index=False)
    annual=tables.get("annual_returns",pd.DataFrame()).rename(columns={c:f"{c}_return_pct" for c in ("optimized","provided","benchmark") if c in tables.get("annual_returns",pd.DataFrame())})
    for col in annual.columns:
        if col.endswith("_return_pct"): annual[col]*=100
    annual.to_csv(directory / "annual_returns.csv",index=False)
    cal=tables.get("monthly_returns",pd.DataFrame()).rename(columns={c:("YTD_pct" if c.lower()=="ytd" else f"{c.title()}_pct") for c in tables.get("monthly_returns",pd.DataFrame()).columns if c.lower() in {"jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec","ytd"}})
    for col in cal.columns:
        if col.endswith("_pct"): cal[col]*=100
    cal.to_csv(directory / "monthly_returns_calendar.csv",index=False)
    for source,target,prefix,unit in (("risk_decomposition","risk_decomposition","risk_contribution","pct"),("return_decomposition","return_decomposition","contribution","monetary_initial_value_1")):
        frame=tables.get(source,pd.DataFrame()).rename(columns={"asset":"ticker"})
        if not frame.empty:
            cols={"ticker":frame["ticker"]}
            for name in ("provided","optimized"):
                if name in frame: cols[f"{name}_{prefix}_pct" if unit=="pct" else f"{name}_{prefix}"]=frame[name]*(100 if unit=="pct" else 1)
            out=pd.DataFrame(cols)
            if unit!="pct": out["unit"]=unit
            out.to_csv(directory/f"{target}.csv",index=False)
    bench=tables.get("benchmark_analytics",pd.DataFrame())
    if not bench.empty:
        cols=[c for c in ["portfolio","active_return","tracking_error","information_ratio"] if c in bench]
        out=bench[cols].rename(columns={"active_return":"active_return_pct","tracking_error":"tracking_error_pct"})
        for c in ("active_return_pct","tracking_error_pct"):
            if c in out: out[c]*=100
        out.to_csv(directory/"benchmark_summary.csv",index=False)
