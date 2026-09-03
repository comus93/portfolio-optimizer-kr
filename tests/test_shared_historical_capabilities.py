from __future__ import annotations

from types import SimpleNamespace

import pandas as pd

from portfolio_optimizer_kr import backtest, pipeline
from portfolio_optimizer_kr.analytics import historical
from portfolio_optimizer_kr.viewer import backtest_renderer
from portfolio_optimizer_kr.viewer import historical_active_components
from portfolio_optimizer_kr.viewer import pv_visual
from portfolio_optimizer_kr.viewer import shared_historical_overlay
from portfolio_optimizer_kr.viewer.shared_historical_overlay import build_optimizer_shared_sections


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


def test_shared_portfolio_metrics_preserve_optimizer_matrix_contract():
    benchmark = pd.Series(
        [0.01, -0.005, 0.012, 0.004] * 6,
        index=pd.date_range("2020-01-31", periods=24, freq="ME"),
    )
    paths = {
        "provided": SimpleNamespace(returns=benchmark + 0.001),
        "optimized": SimpleNamespace(returns=benchmark + 0.002),
    }
    table = historical.portfolio_metrics_table(paths, benchmark, 0.02)
    assert {"metric", "provided", "optimized", "benchmark"}.issubset(table.columns)


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
        "portfolio", "market_type", "portfolio_return", "benchmark_return",
        "active_return", "occurrences", "above_benchmark_count",
        "below_benchmark_count", "total_count", "pct_above_benchmark",
        "above_active_return", "below_active_return", "above_active_return_pct",
        "below_active_return_pct", "overall_active_return_pct",
    }
    assert required.issubset(table.columns)
    assert set(table["portfolio"]) == {"Growth 70/30", "Balanced 50/50"}


def test_asset_performance_is_shared_analytics_output_not_renderer_finance_calculation():
    monthly = pd.DataFrame(
        {"AAA": [0.01] * 72, "BBB": [0.005] * 72},
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
        "cagr", "annualized_return", "annualized_volatility", "best_year",
        "worst_year", "max_drawdown", "sharpe_ratio", "sortino_ratio",
        "3m", "ytd", "1y", "3y", "5y", "10y", "full_period",
        "3y_annualized_volatility", "5y_annualized_volatility",
    }.issubset(table.columns)
    mapping = historical.asset_performance_mapping(table)
    assert "full_period" in mapping["AAA"]["trailing_returns"]
    assert "3y_annualized_volatility" in mapping["AAA"]["trailing_returns"]
    assert not hasattr(backtest_renderer, "_asset_performance_from_monthly_returns")


def test_backtest_and_optimizer_reuse_same_pv_historical_visual_components():
    shared_pairs = [
        (backtest_renderer._growth_svg, shared_historical_overlay._growth_svg, pv_visual.growth_svg),
        (backtest_renderer._annual_returns_chart, shared_historical_overlay._annual_returns_chart, pv_visual.annual_returns_chart),
        (backtest_renderer._trailing_returns_table, shared_historical_overlay._trailing_returns_table, pv_visual.trailing_returns_table),
        (backtest_renderer._drawdown_presentation, shared_historical_overlay._drawdown_presentation, pv_visual.drawdown_presentation),
        (backtest_renderer._annual_asset_returns_chart, shared_historical_overlay._annual_asset_returns_chart, pv_visual.annual_asset_returns_chart),
        (backtest_renderer._rolling_returns_chart, shared_historical_overlay._rolling_returns_chart, pv_visual.rolling_returns_chart),
    ]
    for backtest_component, optimizer_component, shared_component in shared_pairs:
        assert backtest_component is shared_component
        assert optimizer_component is shared_component
    assert backtest_renderer._active_returns_presentation is historical_active_components.active_returns_presentation


def test_optimizer_overlay_does_not_replace_sections_without_shared_artifacts(tmp_path):
    assert build_optimizer_shared_sections(
        tmp_path,
        objective_name="Maximum Sharpe Ratio",
        benchmark_label="SPDR S&P 500 ETF Trust",
    ) == {}


def test_shared_up_down_observations_are_product_neutral():
    benchmark = pd.Series(
        [0.02, -0.03],
        index=pd.date_range("2024-01-31", periods=2, freq="ME"),
    )
    paths = {"Portfolio X": _path([0.03, -0.01])}
    observations = historical.up_down_market_observations(paths, benchmark)
    assert list(observations["portfolio"].unique()) == ["Portfolio X"]
    assert set(observations["market_type"]) == {"up", "down"}
    assert {"benchmark_return_pct", "portfolio_return_pct", "active_return_pct"}.issubset(observations.columns)
