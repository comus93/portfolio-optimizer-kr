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
    """Optimization canonical result kept for API compatibility.

    Product-neutral persisted runs are written by ``write_analysis_run`` from a
    plain canonical mapping so Backtest does not have to impersonate an
    Optimization result.
    """

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
        _write_json(self.to_dict(), path)


def _json_default(value: Any) -> Any:
    if isinstance(value, pd.Timestamp):
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
    if isinstance(value, pd.Timestamp):
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


def _write_json(value: Any, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            _normalise(value),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )


def write_validation_run(
    result: CanonicalResult,
    output_dir: str | Path,
    tables: dict[str, pd.DataFrame],
) -> None:
    """Persist a reviewable canonical result and one UTF-8 CSV per table."""
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    result.write_json(directory / "result.json")
    for name, table in sorted(tables.items()):
        table.to_csv(
            directory / f"{name}.csv", index=False, encoding="utf-8"
        )


def write_analysis_run(result: dict[str, Any], output_dir: str | Path) -> None:
    """Write product-neutral canonical JSON plus raw/review artifact layers."""
    tables = result.get("_tables", {})
    clean = {key: value for key, value in result.items() if key != "_tables"}
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    _write_json(clean, directory / "result.json")

    raw_dir, review_dir = directory / "raw", directory / "review"
    raw_dir.mkdir(exist_ok=True)
    review_dir.mkdir(exist_ok=True)
    for name, table in sorted(tables.items()):
        if table.empty:
            continue
        table.to_csv(
            raw_dir / f"{name}.csv", index=False, encoding="utf-8"
        )
        # Compatibility path for earlier callers; raw/ remains authoritative.
        table.to_csv(
            directory / f"{name}.csv", index=False, encoding="utf-8"
        )
        _review_table(table).to_csv(
            review_dir / f"{name}.csv", index=False, encoding="utf-8"
        )

    _write_review_summaries(result, tables, review_dir)
    configuration = result.get("configuration", {})
    product_mode = str(configuration.get("product_mode") or "optimization")
    title = "Backtest run" if product_mode == "backtest" else "Optimization run"
    (directory / "README.md").write_text(
        f"# {title}\n\n"
        f"Run ID: `{configuration.get('run_id', directory.name)}`. "
        "`result.json` is canonical full precision; `raw/` preserves decimal "
        "tables; `review/` contains human/LLM-readable presentation units.\n",
        encoding="utf-8",
    )


def _review_table(table: pd.DataFrame) -> pd.DataFrame:
    out = table.copy()
    for column in list(out.columns):
        lower = str(column).lower()
        if lower.endswith("_pct"):
            continue
        if any(
            token in lower
            for token in (
                "expected_return",
                "volatility",
                "weight_",
                "drawdown",
                "cagr",
                "tracking_error",
                "contribution",
            )
        ):
            numeric = pd.to_numeric(out[column], errors="coerce")
            if numeric.notna().any():
                out[f"{column}_pct"] = numeric * 100.0
                out = out.drop(columns=[column])
    return out


def _portfolio_order(
    result: dict[str, Any], performance: pd.DataFrame
) -> list[str]:
    configuration = result.get("configuration", {})
    product_mode = str(configuration.get("product_mode") or "optimization")
    if product_mode == "backtest":
        definitions = result.get("portfolio_definitions", {})
        names = list(definitions) if isinstance(definitions, dict) else []
    else:
        names = ["provided", "optimized"]
    if not performance.empty and "portfolio" in performance:
        existing = [str(value) for value in performance["portfolio"]]
        names = [name for name in names if name in existing]
        names.extend(name for name in existing if name not in names and name != "benchmark")
        if "benchmark" in existing:
            names.append("benchmark")
    return names


def _performance_summary_review(
    result: dict[str, Any], performance: pd.DataFrame
) -> pd.DataFrame:
    labels = [
        ("Start Balance", "start_balance", "balance"),
        ("End Balance", "end_balance", "balance"),
        ("CAGR", "cagr", "pct"),
        ("Annualized Return", "annualized_return", "pct"),
        ("Expected Return", "expected_return", "pct"),
        ("Standard Deviation", "annualized_volatility", "pct"),
        ("Best Year", "best_year", "pct"),
        ("Worst Year", "worst_year", "pct"),
        ("Maximum Drawdown", "max_drawdown", "pct"),
        ("Sharpe Ratio (ex-post)", "sharpe_ex_post", "ratio"),
        ("Sortino Ratio", "sortino", "ratio"),
    ]
    indexed = (
        performance.set_index("portfolio")
        if not performance.empty and "portfolio" in performance
        else pd.DataFrame()
    )
    rows: list[dict[str, Any]] = []
    order = _portfolio_order(result, performance)
    for label, key, unit in labels:
        if indexed.empty or key not in indexed.columns:
            if key == "expected_return":
                continue
        row: dict[str, Any] = {"metric": label, "unit": unit}
        for name in order:
            value = (
                indexed.loc[name, key]
                if name in indexed.index and key in indexed.columns
                else None
            )
            row[name] = value * 100.0 if unit == "pct" and value is not None else value
        rows.append(row)
    return pd.DataFrame(rows)


def _asset_performance_review(table: pd.DataFrame) -> pd.DataFrame:
    if table.empty:
        return table.copy()
    out = table.copy()
    percentage_columns = [
        "cagr",
        "annualized_return",
        "annualized_volatility",
        "best_year",
        "worst_year",
        "max_drawdown",
        "3m",
        "ytd",
        "1y",
        "3y",
        "5y",
        "10y",
    ]
    rename = {
        column: f"{column}_pct"
        for column in percentage_columns
        if column in out.columns
    }
    out = out.rename(columns=rename)
    for column in rename.values():
        out[column] = pd.to_numeric(out[column], errors="coerce") * 100.0
    return out


def _metrics_review(table: pd.DataFrame) -> pd.DataFrame:
    if table.empty:
        return table.copy()
    percentage_metrics = {
        "alpha",
        "modigliani_modigliani",
        "historical_var_95",
    }
    if {"portfolio", "metric", "value"}.issubset(table.columns):
        pivot = table.pivot_table(
            index="metric",
            columns="portfolio",
            values="value",
            aggfunc="first",
        ).reset_index()
        pivot.insert(
            1,
            "unit",
            pivot["metric"].map(
                lambda metric: "percent"
                if metric in percentage_metrics
                else "ratio"
            ),
        )
        percentage_rows = pivot["metric"].isin(percentage_metrics)
        value_columns = [
            column
            for column in pivot.columns
            if column not in {"metric", "unit"}
        ]
        pivot.loc[percentage_rows, value_columns] *= 100.0
        return pivot

    out = table.copy()
    if "metric" not in out:
        return out
    out.insert(
        1,
        "unit",
        out["metric"].map(
            lambda metric: "percent" if metric in percentage_metrics else "ratio"
        ),
    )
    percentage_rows = out["metric"].isin(percentage_metrics)
    value_columns = [
        column for column in out.columns if column not in {"metric", "unit"}
    ]
    out.loc[percentage_rows, value_columns] *= 100.0
    return out


def _write_review_summaries(
    result: dict[str, Any],
    tables: dict[str, pd.DataFrame],
    directory: Path,
) -> None:
    cfg = result.get("configuration", {})
    product_mode = str(cfg.get("product_mode") or "optimization")
    assets = pd.DataFrame(cfg.get("assets", []))

    if product_mode != "backtest" and not assets.empty:
        weights = result.get("optimization_result", {}).get("weights", {})
        out = pd.DataFrame(
            {
                "ticker": assets["symbol"],
                "name": assets.get("name"),
                "min_weight_pct": assets.get("min_weight", 0) * 100.0,
                "max_weight_pct": assets.get("max_weight", 1) * 100.0,
            }
        )
        out["provided_weight_pct"] = (
            out["ticker"].map(cfg.get("provided_weights") or {}) * 100.0
        )
        out["optimized_weight_pct"] = out["ticker"].map(weights) * 100.0
        out.to_csv(directory / "optimization_results.csv", index=False)

    performance = tables.get("portfolio_performance", pd.DataFrame())
    _performance_summary_review(result, performance).to_csv(
        directory / "performance_summary.csv", index=False
    )

    trailing = (
        pd.DataFrame(
            result.get("portfolio_performance", {}).get("trailing_returns", {})
        )
        .T.rename_axis("portfolio")
        .reset_index()
    )
    trailing_mapping = {
        "3m": "return_3m_pct",
        "ytd": "ytd_pct",
        "1y": "return_1y_pct",
        "3y": "annualized_3y_pct",
        "5y": "annualized_5y_pct",
        "10y": "annualized_10y_pct",
        "full_period": "full_period_cagr_pct",
        "3y_annualized_volatility": "volatility_3y_pct",
        "5y_annualized_volatility": "volatility_5y_pct",
    }
    trailing = trailing.rename(columns=trailing_mapping)
    for column in trailing_mapping.values():
        if column in trailing:
            trailing[column] = pd.to_numeric(
                trailing[column], errors="coerce"
            ) * 100.0
    trailing.to_csv(directory / "trailing_returns.csv", index=False)

    annual = tables.get("annual_returns", pd.DataFrame()).copy()
    if not annual.empty:
        rename = {
            column: f"{column}_return_pct"
            for column in annual.columns
            if column != "year"
        }
        annual = annual.rename(columns=rename)
        for column in rename.values():
            annual[column] = pd.to_numeric(
                annual[column], errors="coerce"
            ) * 100.0
        annual.to_csv(directory / "annual_returns.csv", index=False)

    calendar = tables.get("monthly_returns", pd.DataFrame()).copy()
    if not calendar.empty:
        month_keys = {
            "jan",
            "feb",
            "mar",
            "apr",
            "may",
            "jun",
            "jul",
            "aug",
            "sep",
            "oct",
            "nov",
            "dec",
            "ytd",
        }
        rename = {
            column: (
                "YTD_pct"
                if str(column).lower() == "ytd"
                else f"{str(column).title()}_pct"
            )
            for column in calendar.columns
            if str(column).lower() in month_keys
        }
        calendar = calendar.rename(columns=rename)
        for column in rename.values():
            calendar[column] = pd.to_numeric(
                calendar[column], errors="coerce"
            ) * 100.0
        calendar.to_csv(
            directory / "monthly_returns_calendar.csv", index=False
        )

    portfolio_names = [
        name for name in _portfolio_order(result, performance) if name != "benchmark"
    ]
    for source, target, prefix, unit in (
        ("risk_decomposition", "risk_decomposition", "risk_contribution", "pct"),
        (
            "return_decomposition",
            "return_decomposition",
            "contribution",
            "monetary_initial_value_1",
        ),
    ):
        frame = tables.get(source, pd.DataFrame()).rename(
            columns={"asset": "ticker"}
        )
        if frame.empty:
            continue
        frame["ticker"] = (
            frame["ticker"].astype(str).str.removeprefix("contribution_")
        )
        columns: dict[str, Any] = {"ticker": frame["ticker"]}
        for name in portfolio_names:
            if name not in frame:
                continue
            output_name = (
                f"{name}_{prefix}_pct" if unit == "pct" else f"{name}_{prefix}"
            )
            columns[output_name] = frame[name] * (100.0 if unit == "pct" else 1.0)
        out = pd.DataFrame(columns)
        if unit != "pct":
            out["unit"] = unit
        out.to_csv(directory / f"{target}.csv", index=False)

    benchmark = tables.get("benchmark_analytics", pd.DataFrame()).copy()
    if not benchmark.empty and "portfolio" in benchmark:
        benchmark = benchmark[benchmark["portfolio"].ne("coverage")].copy()
        columns = [
            column
            for column in (
                "portfolio",
                "active_return",
                "tracking_error",
                "information_ratio",
            )
            if column in benchmark
        ]
        out = benchmark[columns].rename(
            columns={
                "active_return": "active_return_pct",
                "tracking_error": "tracking_error_pct",
            }
        )
        for column in ("active_return_pct", "tracking_error_pct"):
            if column in out:
                out[column] = pd.to_numeric(
                    out[column], errors="coerce"
                ) * 100.0
        overlap = result.get("data_coverage", {}).get("benchmark_overlap") or {}
        if overlap:
            out["overlap_start"] = overlap.get("start")
            out["overlap_end"] = overlap.get("end")
            out["observations"] = overlap.get("observations")
        out.to_csv(directory / "benchmark_summary.csv", index=False)

    active_mapping = {
        "portfolio_return": "portfolio_return_pct",
        "benchmark_return": "benchmark_return_pct",
        "active_return": "active_return_pct",
        "cumulative_active_return": "cumulative_active_return_pct",
        "annual_active_return": "annual_active_return_pct",
        "rolling_active_return": "rolling_active_return_pct",
        "rolling_tracking_error": "rolling_tracking_error_pct",
    }
    active = tables.get("active_returns", pd.DataFrame()).copy()
    if not active.empty:
        rename = {
            key: value for key, value in active_mapping.items() if key in active
        }
        active = active.rename(columns=rename)
        for column in rename.values():
            active[column] = pd.to_numeric(
                active[column], errors="coerce"
            ) * 100.0
        active.to_csv(directory / "active_returns.csv", index=False)

    monthly_series = tables.get("monthly_return_series", pd.DataFrame()).copy()
    if not monthly_series.empty:
        rename = {
            column: f"{column}_return_pct"
            for column in monthly_series.columns
            if column != "date"
        }
        monthly_series = monthly_series.rename(columns=rename)
        for column in rename.values():
            monthly_series[column] = pd.to_numeric(
                monthly_series[column], errors="coerce"
            ) * 100.0
        monthly_series.to_csv(
            directory / "monthly_return_series.csv", index=False
        )

    annual_assets = tables.get("annual_asset_returns", pd.DataFrame()).copy()
    if not annual_assets.empty:
        annual_assets = annual_assets.rename(columns={"return": "return_pct"})
        annual_assets["return_pct"] = pd.to_numeric(
            annual_assets["return_pct"], errors="coerce"
        ) * 100.0
        annual_assets.to_csv(
            directory / "annual_asset_returns.csv", index=False
        )

    contribution = tables.get("active_return_contribution", pd.DataFrame()).copy()
    if not contribution.empty:
        contribution = contribution.rename(
            columns={
                "cumulative_active_contribution": "cumulative_active_contribution_pct"
            }
        )
        if "cumulative_active_contribution_pct" in contribution:
            contribution["cumulative_active_contribution_pct"] = pd.to_numeric(
                contribution["cumulative_active_contribution_pct"],
                errors="coerce",
            ) * 100.0
        contribution.to_csv(
            directory / "active_return_contribution.csv", index=False
        )

    up_down = tables.get("up_down_market_performance", pd.DataFrame()).copy()
    if not up_down.empty:
        decimal_columns = {
            "portfolio_return": "portfolio_return_pct",
            "benchmark_return": "benchmark_return_pct",
            "active_return": "active_return_pct",
            "above_active_return": "above_active_return_pct",
            "below_active_return": "below_active_return_pct",
        }
        for source, target in decimal_columns.items():
            if source not in up_down:
                continue
            if target in up_down:
                up_down = up_down.drop(columns=[source])
            else:
                up_down = up_down.rename(columns={source: target})
                up_down[target] = pd.to_numeric(
                    up_down[target], errors="coerce"
                ) * 100.0
        up_down.to_csv(
            directory / "up_down_market_performance.csv", index=False
        )

    observations = tables.get("up_down_market_scatter", pd.DataFrame()).copy()
    if not observations.empty:
        observations.to_csv(
            directory / "up_down_market_scatter.csv", index=False
        )

    stress = tables.get("stress_periods", pd.DataFrame()).copy()
    if not stress.empty:
        for column in list(stress.columns):
            if not str(column).endswith("_return"):
                continue
            target = f"{column}_pct"
            stress = stress.rename(columns={column: target})
            stress[target] = pd.to_numeric(
                stress[target], errors="coerce"
            ) * 100.0
        stress.to_csv(directory / "stress_periods.csv", index=False)

    metrics = tables.get("portfolio_metrics", pd.DataFrame()).copy()
    if not metrics.empty:
        _metrics_review(metrics).to_csv(
            directory / "portfolio_metrics.csv", index=False
        )

    asset_performance = tables.get(
        "portfolio_asset_performance", pd.DataFrame()
    ).copy()
    if not asset_performance.empty:
        _asset_performance_review(asset_performance).to_csv(
            directory / "portfolio_asset_performance.csv", index=False
        )
