from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from portfolio_optimizer_kr import backtest, pipeline
from portfolio_optimizer_kr.analytics import historical
from portfolio_optimizer_kr.viewer import backtest_renderer
from portfolio_optimizer_kr.viewer import historical_components


def _path(returns: list[float], weights: list[list[float]] | None = None):
    index = pd.date_range("2024-01-31", periods=len(returns), freq="ME")
    if weights is None:
        weights = [[0.5, 0.5] for _ in returns]
    return SimpleNamespace(
        returns=pd.Series(returns, index=index),
        weights=pd.DataFrame(weights, index=index, columns=["AAA", "BBB"]),
    )


def test_optimizer_and_backtest_use_same_historical_table_builders():
    assert pipeline._annual_asset_returns is historical.annual_asset_returns_table
    assert backtest._annual_asset_returns is historical.annual_asset_returns_table
    assert pipeline._active_contribution_table is historical.active_contribution_table
    assert backtest._active_contribution_table is historical.active_contribution_table
    assert pipeline._up_down_market_table is historical.up_down_market_table
    assert backtest._up_down_market_table is historical.up_down_market_table
    assert pipeline._portfolio_metrics_table is historical.portfolio_metrics_table
    assert backtest._portfolio_metrics_table is historical.portfolio_metrics_table


def test_shared_up_down_preserves_optimizer_richer_contract_for_any_portfolio_names():
    benchmark = pd.Series(
        [0.02, -0.03, 0.01, -0.02],
        index=pd.date_range("2024-01-31", periods=4, freq="ME"),
    )
    paths = {
        "Growth 70/30": _path([0.03, -0.02, 0.005, -0.04]),
        "Balanced 50/50": _path([0.01, -0.01, 0.02, -0.01]),
    }
    table = historical.up_down_market_table(paths, benchmark)
    required = {
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
    }
    assert required.issubset(table.columns)
    assert set(table["portfolio"]) == {"Growth 70/30", "Balanced 50/50"}


def test_asset_performance_is_shared_analytics_output_not_renderer_finance_calculation():
    monthly = pd.DataFrame(
        {
            "AAA": [0.01] * 72,
            "BBB": [0.005] * 72,
        },
        index=pd.date_range("2020-01-31", periods=72, freq="ME"),
    )
    table = historical.asset_performance_table(
        monthly,
        annual_rf=0.0,
        asset_names={"AAA": "Asset A", "BBB": "Asset B"},
    )
    assert list(table["ticker"]) == ["AAA", "BBB"]
    assert list(table["name"]) == ["Asset A", "Asset B"]
    assert {
        "cagr",
        "annualized_return",
        "annualized_volatility",
        "best_year",
        "worst_year",
        "max_drawdown",
        "sharpe_ratio",
        "sortino_ratio",
        "3m",
        "ytd",
        "1y",
        "3y",
        "5y",
        "10y",
    }.issubset(table.columns)
    assert not hasattr(backtest_renderer, "_asset_performance_from_monthly_returns")


def test_backtest_renderer_reuses_shared_historical_report_components():
    assert backtest_renderer._annual_returns_chart is historical_components.annual_returns_chart
    assert backtest_renderer._drawdown_presentation is historical_components.drawdown_presentation
    assert backtest_renderer._annual_asset_returns_chart is historical_components.annual_asset_returns_chart
    assert backtest_renderer._correlations_table is historical_components.correlations_table
    assert backtest_renderer._rolling_returns_chart is historical_components.rolling_returns_chart
    assert backtest_renderer._asset_performance_table is historical_components.asset_performance_table


def test_shared_up_down_observations_are_product_neutral():
    benchmark = pd.Series(
        [0.02, -0.03],
        index=pd.date_range("2024-01-31", periods=2, freq="ME"),
    )
    paths = {"Portfolio X": _path([0.03, -0.01])}
    observations = historical.up_down_market_observations(paths, benchmark)
    assert list(observations["portfolio"].unique()) == ["Portfolio X"]
    assert set(observations["market_type"]) == {"up", "down"}
    assert {
        "benchmark_return_pct",
        "portfolio_return_pct",
        "active_return_pct",
    }.issubset(observations.columns)
