from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import pandas as pd

from portfolio_optimizer_kr.analytics import (
    drawdown_episodes,
    monthly_returns_table,
    return_decomposition,
    risk_contribution,
    rolling_returns,
    trailing_returns,
)
from portfolio_optimizer_kr.analytics import historical
from portfolio_optimizer_kr.data.preparation import (
    asset_price_coverage as _asset_price_coverage,
    prepare_benchmark_returns as _benchmark_returns,
    prepare_monthly_returns,
    resolve_annual_rf as _annual_rf,
)
from portfolio_optimizer_kr.models import BacktestRequest
from portfolio_optimizer_kr.portfolio import PortfolioPath, build_portfolio_path
from portfolio_optimizer_kr.stats import annualized_statistics


@dataclass(frozen=True)
class _BenchmarkPath:
    returns: pd.Series


# Compatibility names remain public, but implementation is shared with
# Optimization through analytics.historical.
_annual_asset_returns = historical.annual_asset_returns_table
_active_contribution_table = historical.active_contribution_table
_up_down_market_table = historical.up_down_market_table
_up_down_scatter_table = historical.up_down_market_observations
_portfolio_metrics_table = historical.portfolio_metrics_table
_correlations = historical.correlations_table
_growth_table = historical.growth_table
_drawdown_series_table = historical.drawdown_series_table


def analyze_backtest_prices(
    request: BacktestRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
    annual_rf: float | None = None,
) -> dict:
    """Backtest product orchestration over shared data/simulation/analytics."""
    monthly_returns = prepare_monthly_returns(request, prices, usdkrw)
    rf = _annual_rf(request, annual_rf)

    paths: dict[str, PortfolioPath | _BenchmarkPath] = {}
    for portfolio in request.portfolios:
        paths[portfolio.name] = build_portfolio_path(
            monthly_returns,
            portfolio.target_weights,
            request.rebalancing,
            calendar_aligned=request.calendar_aligned,
        )

    benchmark_returns = _benchmark_returns(request, prices, usdkrw)
    if benchmark_returns is not None:
        benchmark_returns = benchmark_returns.loc[
            monthly_returns.index.min() : monthly_returns.index.max()
        ]
        paths["benchmark"] = _BenchmarkPath(benchmark_returns)

    performance, performance_table = historical.performance_table(
        paths,
        rf,
        initial_balance=request.initial_balance,
    )

    benchmark_summary, active_tables = historical.active_tables(
        paths, benchmark_returns
    )
    if benchmark_returns is not None:
        first_portfolio = request.portfolios[0].name
        overlap = pd.concat(
            [paths[first_portfolio].returns, benchmark_returns],
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
    asset_names = {asset.symbol: asset.name for asset in request.assets}
    asset_performance_table = historical.asset_performance_table(
        monthly_returns,
        rf,
        asset_names=asset_names,
    )
    asset_performance = historical.asset_performance_mapping(
        asset_performance_table
    )

    annual_table = pd.DataFrame(
        {
            name: historical.annual_returns(path.returns)
            for name, path in paths.items()
        }
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
        wealth = historical.wealth_with_initial(
            path.returns,
            request.initial_balance,
            include_initial_anchor=True,
        )
        portfolio_paths[portfolio.name] = {
            "returns": {
                str(index.date()): float(value)
                for index, value in path.returns.items()
            },
            "weights": [
                {
                    "date": str(pd.Timestamp(index).date()),
                    **{
                        symbol: float(value)
                        for symbol, value in row.items()
                    },
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
            pd.Series(
                portfolio.target_weights,
                index=monthly_returns.columns,
            ),
            stats.covariance,
        ).to_dict()

    correlation = historical.correlations_table(
        monthly_returns, paths, benchmark_returns
    )
    growth = historical.growth_table(
        paths,
        initial_balance=request.initial_balance,
        include_initial_anchor=True,
    )
    drawdown_series_output = historical.drawdown_series_table(paths)
    annual_assets = historical.annual_asset_returns_table(monthly_returns)
    active_contribution = historical.active_contribution_table(
        monthly_returns, paths, benchmark_returns
    )
    up_down_market = historical.up_down_market_table(
        paths, benchmark_returns
    )
    up_down_scatter = historical.up_down_market_observations(
        paths, benchmark_returns
    )
    metrics_table = historical.portfolio_metrics_table(
        paths, benchmark_returns, rf
    )
    asset_price_coverage = _asset_price_coverage(request, prices)

    portfolio_definitions = {
        portfolio.name: {
            "target_weights": dict(portfolio.target_weights),
        }
        for portfolio in request.portfolios
    }
    target_allocations = pd.DataFrame(
        [
            {
                "portfolio": portfolio.name,
                "ticker": asset.symbol,
                "name": asset.name,
                "target_weight": float(
                    portfolio.target_weights.get(asset.symbol, 0.0)
                ),
                "target_weight_pct": float(
                    portfolio.target_weights.get(asset.symbol, 0.0)
                ) * 100.0,
            }
            for portfolio in request.portfolios
            for asset in request.assets
        ]
    )

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
                name: trailing_returns(path.returns)
                for name, path in paths.items()
            },
            "annual_returns": annual_table.to_dict(orient="records"),
            "monthly_returns": monthly_series.to_dict(orient="records"),
            "drawdowns": drawdowns.to_dict(orient="records"),
            "rolling_returns": {
                name: {
                    "36m": {
                        str(index.date()): value
                        for index, value in rolling_returns(
                            path.returns, 36
                        ).dropna().items()
                    },
                    "60m": {
                        str(index.date()): value
                        for index, value in rolling_returns(
                            path.returns, 60
                        ).dropna().items()
                    },
                }
                for name, path in paths.items()
            },
        },
        "benchmark_analytics": {
            **benchmark_summary,
            "active_returns": {
                name: table.reset_index(names="date").to_dict(
                    orient="records"
                )
                for name, table in active_tables.items()
            },
        },
        "correlations": correlation.to_dict(),
        "return_decomposition": return_decomp,
        "risk_decomposition": risk_decomp,
    }

    benchmark_table = (
        pd.DataFrame(benchmark_summary)
        .T.rename_axis("portfolio")
        .reset_index()
        if benchmark_summary
        else pd.DataFrame()
    )

    result["_tables"] = {
        "target_allocations": target_allocations,
        "correlations": correlation.reset_index(names="series"),
        "portfolio_performance": performance_table,
        "portfolio_asset_performance": asset_performance_table,
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
        "rolling_returns_summary": historical.rolling_summary_table(paths),
        "rolling_returns_3y": historical.rolling_review_table(paths, 3),
        "rolling_returns_5y": historical.rolling_review_table(paths, 5),
        "active_returns": (
            pd.concat(active_tables, names=["portfolio", "date"])
            .reset_index()
            if active_tables
            else pd.DataFrame()
        ),
        "portfolio_growth": growth,
        "drawdown_series": drawdown_series_output,
        "annual_asset_returns": annual_assets,
        "active_return_contribution": active_contribution,
        "up_down_market_performance": up_down_market,
        "up_down_market_scatter": up_down_scatter,
        "portfolio_metrics": metrics_table,
    }
    return result