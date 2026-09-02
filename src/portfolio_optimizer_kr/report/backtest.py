from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .result import _normalise, _review_table


def _write_backtest_review_summaries(
    result: dict[str, Any], tables: dict[str, pd.DataFrame], directory: Path
) -> None:
    definitions = result.get("portfolio_definitions", {})
    configuration = result.get("configuration", {})
    assets = {
        row.get("symbol"): row
        for row in configuration.get("assets", [])
        if isinstance(row, dict) and row.get("symbol")
    }

    allocation_rows: list[dict[str, Any]] = []
    for portfolio_name, definition in definitions.items():
        weights = definition.get("target_weights", {}) if isinstance(definition, dict) else {}
        for ticker, weight in weights.items():
            asset = assets.get(ticker, {})
            allocation_rows.append(
                {
                    "portfolio": portfolio_name,
                    "ticker": ticker,
                    "name": asset.get("name"),
                    "target_weight_pct": float(weight) * 100.0,
                }
            )
    pd.DataFrame(
        allocation_rows,
        columns=["portfolio", "ticker", "name", "target_weight_pct"],
    ).to_csv(directory / "target_allocations.csv", index=False, encoding="utf-8")

    performance = tables.get("portfolio_performance", pd.DataFrame())
    if not performance.empty and "portfolio" in performance:
        indexed = performance.set_index("portfolio")
        metrics = [
            ("Start Balance", "start_balance", "balance"),
            ("End Balance", "end_balance", "balance"),
            ("CAGR", "cagr", "pct"),
            ("Annualized Return", "annualized_return", "pct"),
            ("Standard Deviation", "annualized_volatility", "pct"),
            ("Best Year", "best_year", "pct"),
            ("Worst Year", "worst_year", "pct"),
            ("Maximum Drawdown", "max_drawdown", "pct"),
            ("Sharpe Ratio (ex-post)", "sharpe_ex_post", "ratio"),
            ("Sortino Ratio", "sortino", "ratio"),
        ]
        rows: list[dict[str, Any]] = []
        for label, key, unit in metrics:
            row: dict[str, Any] = {"metric": label, "unit": unit}
            for name in indexed.index:
                value = indexed.loc[name, key] if key in indexed.columns else None
                row[str(name)] = (
                    float(value) * 100.0
                    if unit == "pct" and value is not None and pd.notna(value)
                    else value
                )
            rows.append(row)
        pd.DataFrame(rows).to_csv(
            directory / "performance_summary.csv", index=False, encoding="utf-8"
        )

    trailing = result.get("portfolio_performance", {}).get("trailing_returns", {})
    trailing_rows: list[dict[str, Any]] = []
    for name, values in trailing.items():
        row: dict[str, Any] = {"portfolio": name}
        for key, value in values.items():
            if value is None:
                row[key] = None
            else:
                row[f"{key}_pct"] = float(value) * 100.0
        trailing_rows.append(row)
    pd.DataFrame(trailing_rows).to_csv(
        directory / "trailing_returns.csv", index=False, encoding="utf-8"
    )

    annual = tables.get("annual_returns", pd.DataFrame()).copy()
    if not annual.empty:
        for column in list(annual.columns):
            if column == "year":
                continue
            annual[f"{column}_return_pct"] = annual.pop(column) * 100.0
        annual.to_csv(directory / "annual_returns.csv", index=False, encoding="utf-8")

    calendar = tables.get("monthly_returns", pd.DataFrame()).copy()
    if not calendar.empty:
        for column in list(calendar.columns):
            if column in {"portfolio", "year"}:
                continue
            calendar[f"{column}_pct"] = calendar.pop(column) * 100.0
        calendar.to_csv(
            directory / "monthly_returns_calendar.csv", index=False, encoding="utf-8"
        )

    benchmark = result.get("benchmark_analytics", {})
    benchmark_rows: list[dict[str, Any]] = []
    for name, values in benchmark.items():
        if name in {"coverage", "active_returns"} or not isinstance(values, dict):
            continue
        benchmark_rows.append(
            {
                "portfolio": name,
                "active_return_pct": (
                    None
                    if values.get("active_return") is None
                    else float(values["active_return"]) * 100.0
                ),
                "tracking_error_pct": (
                    None
                    if values.get("tracking_error") is None
                    else float(values["tracking_error"]) * 100.0
                ),
                "information_ratio": values.get("information_ratio"),
            }
        )
    pd.DataFrame(benchmark_rows).to_csv(
        directory / "benchmark_summary.csv", index=False, encoding="utf-8"
    )


def write_backtest_analysis_run(result: dict[str, Any], output_dir: str | Path) -> None:
    tables = result.get("_tables", {})
    clean = {key: value for key, value in result.items() if key != "_tables"}
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "result.json").write_text(
        json.dumps(
            _normalise(clean),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )

    raw_dir = directory / "raw"
    review_dir = directory / "review"
    raw_dir.mkdir(exist_ok=True)
    review_dir.mkdir(exist_ok=True)
    for name, table in sorted(tables.items()):
        if not isinstance(table, pd.DataFrame) or table.empty:
            continue
        table.to_csv(raw_dir / f"{name}.csv", index=False, encoding="utf-8")
        _review_table(table).to_csv(
            review_dir / f"{name}.csv", index=False, encoding="utf-8"
        )

    _write_backtest_review_summaries(result, tables, review_dir)
    configuration = result.get("configuration", {})
    (directory / "README.md").write_text(
        f"# Backtest run\n\nRun ID: `{configuration.get('run_id', directory.name)}`. "
        "`result.json` is canonical full precision; `raw/` preserves machine-oriented tables; "
        "`review/` contains human/LLM-oriented summaries.\n",
        encoding="utf-8",
    )
