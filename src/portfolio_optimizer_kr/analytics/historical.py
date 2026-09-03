from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import pandas as pd

from .metrics import (
    active_analytics,
    active_return_metrics,
    annual_returns,
    drawdown_series,
    performance_summary,
    portfolio_metrics,
    rolling_return_summary,
    rolling_returns,
    trailing_returns,
)


def _returns(path: Any) -> pd.Series:
    return path.returns


def _has_weights(path: Any) -> bool:
    return isinstance(getattr(path, "weights", None), pd.DataFrame)


def portfolio_paths(paths: Mapping[str, Any]) -> list[tuple[str, Any]]:
    """Return product-neutral investable portfolio paths, excluding benchmarks."""
    return [
        (name, path)
        for name, path in paths.items()
        if name != "benchmark" and _has_weights(path)
    ]


def performance_table(
    paths: Mapping[str, Any],
    annual_rf: float,
    *,
    initial_balance: float = 1.0,
    expected_returns: Mapping[str, float] | None = None,
) -> tuple[dict[str, dict[str, float]], pd.DataFrame]:
    summary: dict[str, dict[str, float]] = {}
    rows: list[dict[str, object]] = []
    expected_returns = expected_returns or {}
    for name, path in paths.items():
        metrics = performance_summary(_returns(path), annual_rf)
        metrics["start_balance"] = float(initial_balance)
        metrics["end_balance"] = float(
            initial_balance * (1.0 + _returns(path)).prod()
        )
        if name in expected_returns:
            metrics["expected_return"] = float(expected_returns[name])
        summary[name] = metrics
        rows.append({"portfolio": name, **metrics})
    return summary, pd.DataFrame(rows)


def wealth_with_initial(
    returns: pd.Series,
    initial_balance: float = 1.0,
    *,
    include_initial_anchor: bool = False,
) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float, name="balance")
    compounded = (1.0 + returns).cumprod().mul(float(initial_balance))
    if not include_initial_anchor:
        return compounded.rename("balance")
    first = pd.Timestamp(returns.index[0])
    start_marker = first.to_period("M").start_time.normalize()
    initial = pd.Series(
        [float(initial_balance)],
        index=pd.DatetimeIndex([start_marker]),
        name="balance",
    )
    if start_marker in compounded.index:
        compounded = compounded.drop(index=start_marker)
    return pd.concat([initial, compounded]).sort_index().rename("balance")


def growth_table(
    paths: Mapping[str, Any],
    *,
    initial_balance: float = 1.0,
    include_initial_anchor: bool = False,
) -> pd.DataFrame:
    values = {
        f"{name}_balance": wealth_with_initial(
            _returns(path),
            initial_balance,
            include_initial_anchor=include_initial_anchor,
        )
        for name, path in paths.items()
    }
    return pd.DataFrame(values).rename_axis("date").reset_index()


def drawdown_series_table(paths: Mapping[str, Any]) -> pd.DataFrame:
    values = {
        f"{name}_drawdown": drawdown_series(_returns(path))
        for name, path in paths.items()
    }
    return pd.DataFrame(values).rename_axis("date").reset_index()


def annual_asset_returns_table(asset_returns: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for ticker in asset_returns:
        for year, value in annual_returns(asset_returns[ticker]).items():
            rows.append(
                {"year": int(year), "ticker": str(ticker), "return": value}
            )
    return pd.DataFrame(rows, columns=["year", "ticker", "return"])


def correlations_table(
    asset_returns: pd.DataFrame,
    paths: Mapping[str, Any],
    benchmark: pd.Series | None = None,
) -> pd.DataFrame:
    inputs: list[pd.DataFrame | pd.Series] = [asset_returns]
    inputs.extend(_returns(path).rename(name) for name, path in paths.items())
    if benchmark is not None and "benchmark" not in paths:
        inputs.append(benchmark.rename("benchmark"))
    return pd.concat(inputs, axis=1, join="inner").corr()


def asset_performance_table(
    asset_returns: pd.DataFrame,
    annual_rf: float,
    *,
    asset_names: Mapping[str, str] | None = None,
) -> pd.DataFrame:
    """Canonical realized asset-level historical performance table.

    Values stay in decimal units. Review/presentation layers own percentage-point
    conversion and human labels. The extended trailing fields preserve the
    established Optimization result contract while Backtest may display only the
    subset applicable to its report.
    """
    asset_names = asset_names or {}
    rows: list[dict[str, object]] = []
    for ticker in asset_returns.columns:
        returns = asset_returns[ticker].dropna()
        summary = performance_summary(returns, annual_rf)
        trailing = trailing_returns(returns)
        rows.append(
            {
                "ticker": str(ticker),
                "name": asset_names.get(str(ticker), ""),
                "start_balance": summary.get("start_balance"),
                "end_balance": summary.get("end_balance"),
                "cagr": summary.get("cagr"),
                "annualized_return": summary.get("annualized_return"),
                "annualized_volatility": summary.get("annualized_volatility"),
                "best_year": summary.get("best_year"),
                "worst_year": summary.get("worst_year"),
                "max_drawdown": summary.get("max_drawdown"),
                "sharpe_ratio": summary.get("sharpe_ex_post"),
                "sortino_ratio": summary.get("sortino"),
                "3m": trailing.get("3m"),
                "ytd": trailing.get("ytd"),
                "1y": trailing.get("1y"),
                "3y": trailing.get("3y"),
                "5y": trailing.get("5y"),
                "10y": trailing.get("10y"),
                "full_period": trailing.get("full_period"),
                "3y_annualized_volatility": trailing.get(
                    "3y_annualized_volatility"
                ),
                "5y_annualized_volatility": trailing.get(
                    "5y_annualized_volatility"
                ),
            }
        )
    return pd.DataFrame(rows)


def asset_performance_mapping(
    table: pd.DataFrame,
) -> dict[str, dict[str, object]]:
    if table.empty:
        return {}
    out: dict[str, dict[str, object]] = {}
    for source in table.to_dict(orient="records"):
        row = dict(source)
        ticker = str(row.pop("ticker"))
        row.pop("name", None)
        out[ticker] = {
            "start_balance": row.get("start_balance"),
            "end_balance": row.get("end_balance"),
            "cagr": row.get("cagr"),
            "annualized_return": row.get("annualized_return"),
            "annualized_volatility": row.get("annualized_volatility"),
            "best_year": row.get("best_year"),
            "worst_year": row.get("worst_year"),
            "max_drawdown": row.get("max_drawdown"),
            "sharpe_ex_post": row.get("sharpe_ratio"),
            "sortino": row.get("sortino_ratio"),
            "trailing_returns": {
                "3m": row.get("3m"),
                "ytd": row.get("ytd"),
                "1y": row.get("1y"),
                "3y": row.get("3y"),
                "5y": row.get("5y"),
                "10y": row.get("10y"),
                "full_period": row.get("full_period"),
                "3y_annualized_volatility": row.get(
                    "3y_annualized_volatility"
                ),
                "5y_annualized_volatility": row.get(
                    "5y_annualized_volatility"
                ),
            },
        }
    return out


def active_tables(
    paths: Mapping[str, Any], benchmark: pd.Series | None
) -> tuple[dict[str, dict[str, float]], dict[str, pd.DataFrame]]:
    summary: dict[str, dict[str, float]] = {}
    tables: dict[str, pd.DataFrame] = {}
    if benchmark is None:
        return summary, tables
    for name, path in portfolio_paths(paths):
        summary[name] = active_return_metrics(_returns(path), benchmark)
        tables[name] = active_analytics(_returns(path), benchmark)
    return summary, tables


def active_contribution_table(
    asset_returns: pd.DataFrame,
    paths: Mapping[str, Any],
    benchmark: pd.Series | None,
) -> pd.DataFrame:
    columns = [
        "date",
        "portfolio",
        "ticker",
        "cumulative_active_contribution",
    ]
    if benchmark is None:
        return pd.DataFrame(columns=columns)
    joined = pd.concat(
        [asset_returns, benchmark.rename("benchmark")],
        axis=1,
        join="inner",
    ).dropna()
    rows: list[dict[str, object]] = []
    for name, path in portfolio_paths(paths):
        weights = path.weights.loc[joined.index, asset_returns.columns]
        contribution = weights.mul(
            joined[asset_returns.columns].sub(joined["benchmark"], axis=0)
        ).cumsum()
        for ticker in contribution:
            rows.extend(
                {
                    "date": timestamp,
                    "portfolio": name,
                    "ticker": str(ticker),
                    "cumulative_active_contribution": value,
                }
                for timestamp, value in contribution[ticker].items()
            )
    return pd.DataFrame(rows, columns=columns)


def up_down_market_table(
    paths: Mapping[str, Any], benchmark: pd.Series | None
) -> pd.DataFrame:
    columns = [
        "portfolio",
        "market_type",
        "portfolio_return",
        "benchmark_return",
        "active_return",
        "occurrences",
        "above_benchmark_count",
        "below_benchmark_count",
        "total_count",
        "pct_above_benchmark",
        "above_active_return",
        "below_active_return",
        "above_active_return_pct",
        "below_active_return_pct",
        "overall_active_return_pct",
    ]
    if benchmark is None:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, object]] = []
    for name, path in portfolio_paths(paths):
        joined = pd.concat(
            [_returns(path).rename("portfolio"), benchmark.rename("benchmark")],
            axis=1,
            join="inner",
        ).dropna()
        for market_type, selector in (
            ("up", joined["benchmark"] > 0),
            ("down", joined["benchmark"] < 0),
        ):
            selected = joined.loc[selector]
            if selected.empty:
                continue
            active = selected["portfolio"] - selected["benchmark"]
            above = active > 0
            below = active < 0
            overall = float(active.mean())
            above_mean = float(active.loc[above].mean()) if above.any() else None
            below_mean = float(active.loc[below].mean()) if below.any() else None
            rows.append(
                {
                    "portfolio": name,
                    "market_type": market_type,
                    "portfolio_return": float(selected["portfolio"].mean()),
                    "benchmark_return": float(selected["benchmark"].mean()),
                    "active_return": overall,
                    "occurrences": int(len(selected)),
                    "above_benchmark_count": int(above.sum()),
                    "below_benchmark_count": int(below.sum()),
                    "total_count": int(len(selected)),
                    "pct_above_benchmark": float(above.mean() * 100.0),
                    "above_active_return": above_mean,
                    "below_active_return": below_mean,
                    "above_active_return_pct": (
                        None if above_mean is None else above_mean * 100.0
                    ),
                    "below_active_return_pct": (
                        None if below_mean is None else below_mean * 100.0
                    ),
                    "overall_active_return_pct": overall * 100.0,
                }
            )
    return pd.DataFrame(rows, columns=columns)


def up_down_market_observations(
    paths: Mapping[str, Any], benchmark: pd.Series | None
) -> pd.DataFrame:
    columns = [
        "date",
        "portfolio",
        "market_type",
        "benchmark_return",
        "portfolio_return",
        "active_return",
        "benchmark_return_pct",
        "portfolio_return_pct",
        "active_return_pct",
    ]
    if benchmark is None:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, object]] = []
    for name, path in portfolio_paths(paths):
        joined = pd.concat(
            [_returns(path).rename("portfolio"), benchmark.rename("benchmark")],
            axis=1,
            join="inner",
        ).dropna()
        for timestamp, row in joined.iterrows():
            benchmark_return = float(row["benchmark"])
            portfolio_return = float(row["portfolio"])
            active_return = portfolio_return - benchmark_return
            rows.append(
                {
                    "date": timestamp,
                    "portfolio": name,
                    "market_type": (
                        "up"
                        if benchmark_return > 0
                        else "down"
                        if benchmark_return < 0
                        else "flat"
                    ),
                    "benchmark_return": benchmark_return,
                    "portfolio_return": portfolio_return,
                    "active_return": active_return,
                    "benchmark_return_pct": benchmark_return * 100.0,
                    "portfolio_return_pct": portfolio_return * 100.0,
                    "active_return_pct": active_return * 100.0,
                }
            )
    return pd.DataFrame(rows, columns=columns)


def portfolio_metrics_table(
    paths: Mapping[str, Any],
    benchmark: pd.Series | None,
    annual_rf: float,
) -> pd.DataFrame:
    """Shared comparison matrix using the established Optimizer table contract."""
    if benchmark is None:
        return pd.DataFrame(columns=["metric", *[name for name in paths if name != "benchmark"]])

    by_portfolio: dict[str, dict[str, float]] = {}
    for name, path in paths.items():
        if name == "benchmark":
            continue
        by_portfolio[name] = portfolio_metrics(
            _returns(path), benchmark, annual_rf
        )

    # The benchmark itself is a useful comparison reference even when it is not
    # represented as a path object in a caller.
    by_portfolio["benchmark"] = portfolio_metrics(
        benchmark, benchmark, annual_rf
    )
    metric_names = sorted(
        {
            metric
            for values in by_portfolio.values()
            for metric in values
        }
    )
    return pd.DataFrame(
        [
            {
                "metric": metric,
                **{
                    name: values.get(metric)
                    for name, values in by_portfolio.items()
                },
            }
            for metric in metric_names
        ]
    )


def rolling_summary_table(
    paths: Mapping[str, Any],
    years: tuple[int, ...] = (1, 3, 5, 7),
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "roll_period_years": period,
                **{
                    f"{name}_{metric}": value
                    for name, path in paths.items()
                    for metric, value in rolling_return_summary(
                        _returns(path), period
                    ).items()
                },
            }
            for period in years
        ]
    )


def rolling_review_table(
    paths: Mapping[str, Any], years: int
) -> pd.DataFrame:
    series = [
        rolling_returns(_returns(path), years * 12).rename(
            f"{name}_annualized_return_pct"
        )
        * 100.0
        for name, path in paths.items()
    ]
    return (
        pd.concat(series, axis=1)
        .dropna(how="all")
        .reset_index(names="date")
    )
