import pandas as pd
import pytest

from portfolio_optimizer_kr import backtest, pipeline, runner
from portfolio_optimizer_kr.data import preparation
from portfolio_optimizer_kr.models import (
    AssetSpec,
    BacktestPortfolio,
    BacktestRequest,
    OptimizationRequest,
    RiskFreeConfig,
    RiskFreeMode,
)


def _prices():
    index = pd.to_datetime(
        [
            "2023-12-29",
            "2024-01-31",
            "2024-02-29",
            "2024-03-29",
        ]
    )
    return {
        "A": pd.Series([100.0, 105.0, 110.0, 121.0], index=index),
        "B": pd.Series([100.0, 98.0, 102.0, 104.0], index=index),
        "BM": pd.Series([100.0, 101.0, 103.0, 106.0], index=index),
    }


def _optimization_request():
    return OptimizationRequest(
        assets=(AssetSpec("A", currency="USD"), AssetSpec("B", currency="USD")),
        benchmark=AssetSpec("BM", currency="USD"),
        start="2024-01-01",
        end="2024-03-31",
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
    )


def _backtest_request():
    return BacktestRequest(
        assets=(AssetSpec("A", currency="USD"), AssetSpec("B", currency="USD")),
        portfolios=(BacktestPortfolio("P1", {"A": 0.5, "B": 0.5}),),
        benchmark=AssetSpec("BM", currency="USD"),
        start="2024-01-01",
        end="2024-03-31",
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
    )


def test_products_and_runner_use_same_market_data_preparation_functions():
    assert pipeline.prepare_monthly_returns is preparation.prepare_monthly_returns
    assert backtest.prepare_monthly_returns is preparation.prepare_monthly_returns
    assert runner.prepare_monthly_returns is preparation.prepare_monthly_returns
    assert pipeline._benchmark_returns is preparation.prepare_benchmark_returns
    assert backtest._benchmark_returns is preparation.prepare_benchmark_returns
    assert pipeline._asset_price_coverage is preparation.asset_price_coverage
    assert backtest._asset_price_coverage is preparation.asset_price_coverage
    assert pipeline._annual_rf is preparation.resolve_annual_rf
    assert backtest._annual_rf is preparation.resolve_annual_rf


def test_optimizer_and_backtest_share_identical_prepared_market_data_contract():
    prices = _prices()
    optimizer = _optimization_request()
    backtester = _backtest_request()

    optimizer_returns = preparation.prepare_monthly_returns(optimizer, prices)
    backtest_returns = preparation.prepare_monthly_returns(backtester, prices)
    pd.testing.assert_frame_equal(optimizer_returns, backtest_returns)

    optimizer_benchmark = preparation.prepare_benchmark_returns(
        optimizer, prices, None
    )
    backtest_benchmark = preparation.prepare_benchmark_returns(
        backtester, prices, None
    )
    pd.testing.assert_series_equal(optimizer_benchmark, backtest_benchmark)

    assert preparation.resolve_annual_rf(optimizer, None) == pytest.approx(0.02)
    assert preparation.resolve_annual_rf(backtester, None) == pytest.approx(0.02)


def test_market_data_coverage_is_product_neutral():
    prices = _prices()
    optimizer_coverage = preparation.asset_price_coverage(
        _optimization_request(), prices
    )
    backtest_coverage = preparation.asset_price_coverage(
        _backtest_request(), prices
    )
    assert optimizer_coverage == backtest_coverage
    assert set(optimizer_coverage) == {"A", "B"}
