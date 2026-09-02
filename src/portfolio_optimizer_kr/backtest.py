from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd

from portfolio_optimizer_kr.analytics import (
    active_analytics,
    active_return_metrics,
    annual_returns,
    drawdown_episodes,
    drawdown_series,
    monthly_returns_table,
    performance_summary,
    portfolio_metrics,
    return_decomposition,
    risk_contribution,
    rolling_return_summary,
    rolling_returns,
    trailing_returns,
)
from portfolio_optimizer_kr.models import BacktestRequest
from portfolio_optimizer_kr.pipeline import (
    _annual_rf,
    _asset_price_coverage,
    _benchmark_returns,
    prepare_monthly_returns,
)
from portfolio_optimizer_kr.portfolio import PortfolioPath, build_portfolio_path
from portfolio_optimizer_kr.stats import annualized_statistics


@dataclass(frozen=True)
class _BenchmarkPath:
    returns: pd.Series


def _performance_with_balance(
    returns: pd.Series, annual_rf: float, initial_balance: float
) -> dict[str, float]:
    metrics = performance_summary(returns, annual_rf)
    metrics["start_balance"] = float(initial_balance)
    metrics["end_balance"] = float(initial_balance * (1.0 + returns).prod())
    return metrics


def _performance_table(
    paths: Mapping[str, PortfolioPath | _BenchmarkPath],
    annual_rf: float,
    initial_balance: float,
) -> tuple[dict[str, dict[str, float]], pd.DataFrame]:
    summary: dict[str, dict[str, float]] = {}
    rows: list[dict[str, object]] = []
    for name, path in paths.items():
        metrics = _performance_with_balance(path.returns, annual_rf, initial_balance)
        summary[name] = metrics
        rows.append({"portfolio": name, **metrics})
    return summary, pd.DataFrame(rows)


def _wealth_with_initial(returns: pd.Series, initial_balance: float) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float, name="balance")
    first = pd.Timestamp(returns.index[0])
    start_marker = first.to_period("M").start_time.normalize()
    compounded = (1.0 + returns).cumprod().mul(float(initial_balance))
    initial = pd.Series(
        [float(initial_balance)],
        index=pd.DatetimeIndex([start_marker]),
        name="balance",
    )
    if start_marker in compounded.index:
        compounded = compounded.drop(index=start_marker)
    return pd.concat([initial, compounded]).sort_index()


def _growth_table(
    paths: Mapping[str, PortfolioPath | _BenchmarkPath], initial_balance: float
) -> pd.DataFrame:
    values = {
        f"{name}_balance": _wealth_with_initial(path.returns, initial_balance)
        for name, path in paths.items()
    }
    return pd.DataFrame(values).rename_axis("date").reset_index()


def _drawdown_series_table(paths: Mapping[str, PortfolioPath | _BenchmarkPath]) -> pd.DataFrame:
    values = {
        f"{name}_drawdown": drawdown_series(path.returns)
        for name, path in paths.items()
    }
    return pd.DataFrame(values).rename_axis("date").reset_index()


def _annual_asset_returns(asset_returns: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for ticker in asset_returns:
        for year, value in annual_returns(asset_returns[ticker]).items():
            rows.append({"year": int(year), "ticker": ticker, "return": value})
    return pd.DataFrame(rows, columns=["year", "ticker", "return"])


def _correlations(
    asset_returns: pd.DataFrame,
    paths: Mapping[str, PortfolioPath | _BenchmarkPath],
) -> pd.DataFrame:
    inputs = [asset_returns]
    inputs.extend(path.returns.rename(name) for name, path in paths.items())
    return pd.concat(inputs, axis=1, join="inner").corr()


def _active_contribution_table(
    asset_returns: pd.DataFrame,
    paths: Mapping[str, PortfolioPath | _BenchmarkPath],
    benchmark: pd.Series | None,
) -> pd.DataFrame:
    columns = ["date", "portfolio", "ticker", "cumulative_active_contribution"]
    if benchmark is None:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, object]] = []
    for name, path in paths.items():
        if name == "benchmark" or not isinstance(path, PortfolioPath):
            continue
        joined = pd.concat(
            [asset_returns, benchmark.rename("benchmark")], axis=1, join="inner"
        ).dropna()
        weights = path.weights.loc[joined.index, asset_returns.columns]
        contribution = weights.mul(
            joined[asset_returns.columns].sub(joined["benchmark"], axis=0)
        ).cumsum()
        for ticker in contribution:
            rows.extend(
                {
                    "date": timestamp,
                    "portfolio": name,
                    "ticker": ticker,
                    "cumulative_active_contribution": value,
                }
                for timestamp, value in contribution[ticker].items()
            )
    return pd.DataFrame(rows, columns=columns)


def _up_down_market_table(
    paths: Mapping[str, PortfolioPath | _BenchmarkPath], benchmark: pd.Series | None
) -> pd.DataFrame:
    columns = [
        "portfolio",
        "market_type",
        "portfolio_return",
        "benchmark_return",
        "active_return",
        "occurrences",
    ]
    if benchmark is None:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, object]] = []
    for name, path in paths.items():
        if name == "benchmark":
            continue
        joined = pd.concat(
            [path.returns.rename("portfolio"), benchmark.rename("benchmark")],
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
            rows.append(
                {
                    "portfolio": name,
                    "market_type": market_type,
                    "portfolio_return": float(selected["portfolio"].mean()),
                    "benchmark_return": float(selected["benchmark"].mean()),
                    "active_return": float(active.mean()),
                    "occurrences": int(len(selected)),
                }
            )
    return pd.DataFrame(rows, columns=columns)


def _portfolio_metrics_table(
    paths: Mapping[str, PortfolioPath | _BenchmarkPath],
    benchmark: pd.Series | None,
    annual_rf: float,
) -> pd.DataFrame:
    if benchmark is None:
        return pd.DataFrame(columns=["portfolio", "metric", "value"])
    rows: list[dict[str, object]] = []
    for name, path in paths.items():
        metrics = portfolio_metrics(path.returns, benchmark, annual_rf)
        for metric, value in metrics.items():
            rows.append({"portfolio": name, "metric": metric, "value": value})
    return pd.DataFrame(rows, columns=["portfolio", "metric", "value"])


def analyze_backtest_prices(
    request: BacktestRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
    annual_rf: float | None = None,
) -> dict:
    """Run the Backtest product path without invoking optimization/frontier logic."""
    monthly_returns = prepare_monthly_returns(request, prices, usdkrw)  # type: ignore[arg-type]
    rf = _annual_rf(request, annual_rf)  # type: ignore[arg-type]

    paths: dict[str, PortfolioPath | _BenchmarkPath] = {}
    for portfolio in request.portfolios:
        paths[portfolio.name] = build_portfolio_path(
            monthly_returns,
            portfolio.target_weights,
            request.rebalancing,
            calendar_aligned=request.calendar_aligned,
        )

    benchmark_returns = _benchmark_returns(request, prices, usdkrw)  # type: ignore[arg-type]
    if benchmark_returns is not None:
        benchmark_returns = benchmark_returns.loc[
            monthly_returns.index.min() : monthly_returns.index.max()
        ]
        paths["benchmark"] = _BenchmarkPath(benchmark_returns)

    performance, performance_table = _performance_table(
        paths, rf, request.initial_balance
    )

    benchmark_summary: dict[str, object] = {}
    active_tables: dict[str, pd.DataFrame] = {}
    if benchmark_returns is not None:
        for name, path in paths.items():
            if name == "benchmark":
                continue
            benchmark_summary[name] = active_return_metrics(
                path.returns, benchmark_returns
            )
            active_tables[name] = active_analytics(path.returns, benchmark_returns)
        overlap = pd.concat(
            [next(iter(paths.values())).returns, benchmark_returns],
            axis=1,
            join="inner",
        ).dropna()
        if not overlap.empty:
            benchmark_summary["coverage"] = {
                "start": str(overlap.index.min().date()),
                "end": str(overlap.index.max().date()),
                "observations": int(len(overlap)),
            }

    stats = annualized_statistics(monthly_returns)
    asset_performance = {
        symbol: {
            **performance_summary(monthly_returns[symbol], rf),
            "trailing_returns": trailing_returns(monthly_returns[symbol]),
        }
        for symbol in monthly_returns
    }

    annual_table = pd.DataFrame(
        {name: annual_returns(path.returns) for name, path in paths.items()}
    ).rename_axis("year").reset_index()
    monthly_series = pd.concat(
        [
            monthly_returns.add_prefix("asset_"),
            *[path.returns.rename(name) for name, path in paths.items()],
        ],
        axis=1,
    ).reset_index(names="date")
    monthly_calendar = pd.concat(
        [
            monthly_returns_table(path.returns).assign(portfolio=name)
            for name, path in paths.items()
        ],
        ignore_index=True,
    )

    drawdown_rows: list[pd.DataFrame] = []
    for name, path in paths.items():
        table = drawdown_episodes(path.returns).copy()
        table.insert(0, "portfolio", name)
        drawdown_rows.append(table)
    drawdowns = (
        pd.concat(drawdown_rows, ignore_index=True)
        if drawdown_rows
        else pd.DataFrame()
    )

    portfolio_paths: dict[str, object] = {}
    return_decomp: dict[str, dict[str, float]] = {}
    risk_decomp: dict[str, dict[str, float]] = {}
    for portfolio in request.portfolios:
        path = paths[portfolio.name]
        assert isinstance(path, PortfolioPath)
        wealth = _wealth_with_initial(path.returns, request.initial_balance)
        portfolio_paths[portfolio.name] = {
            "returns": {str(index.date()): float(value) for index, value in path.returns.items()},
            "weights": [
                {
                    "date": str(pd.Timestamp(index).date()),
                    **{symbol: float(value) for symbol, value in row.items()},
                }
                for index, row in path.weights.iterrows()
            ],
            "wealth": {
                str(index.date()): float(value)
                for index, value in wealth.items()
            },
        }
        return_decomp[portfolio.name] = return_decomposition(
            monthly_returns,
            path.weights,
            initial_value=request.initial_balance,
        ).iloc[-1].to_dict()
        risk_decomp[portfolio.name] = risk_contribution(
            pd.Series(portfolio.target_weights, index=monthly_returns.columns),
            stats.covariance,
        ).to_dict()

    correlation = _correlations(monthly_returns, paths)
    growth = _growth_table(paths, request.initial_balance)
    drawdown_series_output = _drawdown_series_table(paths)
    annual_assets = _annual_asset_returns(monthly_returns)
    active_contribution = _active_contribution_table(
        monthly_returns, paths, benchmark_returns
    )
    up_down_market = _up_down_market_table(paths, benchmark_returns)
    metrics_table = _portfolio_metrics_table(paths, benchmark_returns, rf)
    asset_price_coverage = _asset_price_coverage(request, prices)  # type: ignore[arg-type]

    portfolio_definitions = {
        portfolio.name: {
            "target_weights": dict(portfolio.target_weights),
        }
        for portfolio in request.portfolios
    }

    result: dict[str, object] = {
        "configuration": {
            "product_mode": "backtest",
            "run_id": request.run_id,
            "market_data_source": "FinanceDataReader",
            "return_semantics": "canonical_total_return",
            "time_period_mode": str(request.time_period_mode),
            "analysis_period": {
                "start": str(request.start) if request.start else None,
                "end": str(request.end) if request.end else None,
            },
            "assets": [
                {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "currency": asset.currency,
                }
                for asset in request.assets
            ],
            "benchmark": (
                {
                    "symbol": request.benchmark.symbol,
                    "name": request.benchmark.name,
                    "currency": request.benchmark.currency,
                }
                if request.benchmark
                else None
            ),
            "initial_balance": request.initial_balance,
            "rebalancing_period": str(request.rebalancing),
            "calendar_aligned": request.calendar_aligned,
            "risk_free": {
                "requested_mode": str(request.risk_free.mode),
                "effective_annual_rate": rf,
            },
        },
        "data_coverage": {
            "backtest_monthly_returns": {
                "start": str(monthly_returns.index.min().date()),
                "end": str(monthly_returns.index.max().date()),
                "observations": int(len(monthly_returns)),
            },
            "benchmark_overlap": benchmark_summary.get("coverage"),
            "asset_prices": asset_price_coverage,
        },
        "asset_statistics": {
            "correlation": stats.correlation.to_dict(),
            "asset_performance": asset_performance,
        },
        "portfolio_definitions": portfolio_definitions,
        "portfolio_paths": portfolio_paths,
        "portfolio_performance": {
            **performance,
            "summary": performance,
            "trailing_returns": {
                name: trailing_returns(path.returns) for name, path in paths.items()
            },
            "annual_returns": annual_table.to_dict(orient="records"),
            "monthly_returns": monthly_series.to_dict(orient="records"),
            "drawdowns": drawdowns.to_dict(orient="records"),
            "rolling_returns": {
                name: {
                    "36m": {
                        str(index.date()): value
                        for index, value in rolling_returns(path.returns, 36).dropna().items()
                    },
                    "60m": {
                        str(index.date()): value
                        for index, value in rolling_returns(path.returns, 60).dropna().items()
                    },
                }
                for name, path in paths.items()
            },
        },
        "benchmark_analytics": {
            **benchmark_summary,
            "active_returns": {
                name: table.reset_index(names="date").to_dict(orient="records")
                for name, table in active_tables.items()
            },
        },
        "correlations": correlation.to_dict(),
        "return_decomposition": return_decomp,
        "risk_decomposition": risk_decomp,
    }

    benchmark_table = (
        pd.DataFrame(benchmark_summary).T.rename_axis("portfolio").reset_index()
        if benchmark_summary
        else pd.DataFrame()
    )

    rolling_summary = pd.DataFrame(
        [
            {
                "roll_period_years": years,
                **{
                    f"{name}_{metric}": value
                    for name, path in paths.items()
                    for metric, value in rolling_return_summary(
                        path.returns, years
                    ).items()
                },
            }
            for years in (1, 3, 5, 7)
        ]
    )

    def rolling_review(years: int) -> pd.DataFrame:
        series = [
            rolling_returns(path.returns, years * 12).rename(
                f"{name}_annualized_return_pct"
            )
            * 100
            for name, path in paths.items()
        ]
        return pd.concat(series, axis=1).dropna(how="all").reset_index(names="date")

    result["_tables"] = {
        "correlations": correlation.reset_index(names="series"),
        "portfolio_performance": performance_table,
        "annual_returns": annual_table,
        "monthly_returns": monthly_calendar,
        "monthly_return_series": monthly_series,
        "drawdowns": drawdowns,
        "return_decomposition": pd.DataFrame(return_decomp)
        .rename_axis("asset")
        .reset_index(),
        "risk_decomposition": pd.DataFrame(risk_decomp)
        .rename_axis("asset")
        .reset_index(),
        "benchmark_analytics": benchmark_table,
        "rolling_returns_summary": rolling_summary,
        "rolling_returns_3y": rolling_review(3),
        "rolling_returns_5y": rolling_review(5),
        "active_returns": (
            pd.concat(active_tables, names=["portfolio", "date"]).reset_index()
            if active_tables
            else pd.DataFrame()
        ),
        "portfolio_growth": growth,
        "drawdown_series": drawdown_series_output,
        "annual_asset_returns": annual_assets,
        "active_return_contribution": active_contribution,
        "up_down_market_performance": up_down_market,
        "portfolio_metrics": metrics_table,
    }
    return result
