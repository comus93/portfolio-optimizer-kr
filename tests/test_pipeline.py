import pandas as pd
import pytest

from portfolio_optimizer_kr.models import (
    AssetSpec,
    OptimizationRequest,
    RiskFreeConfig,
    RiskFreeMode,
)
from portfolio_optimizer_kr.pipeline import analyze_prices, prepare_monthly_returns


def _prices():
    idx = pd.date_range("2023-12-29", periods=400, freq="D")
    a = pd.Series(100.0 + pd.Series(range(len(idx)), index=idx).to_numpy() * 0.1, index=idx, name="A")
    b = pd.Series(100.0 + pd.Series(range(len(idx)), index=idx).to_numpy() * 0.05, index=idx, name="B")
    return {"A": a, "B": b}


def test_prepare_monthly_returns_is_source_agnostic():
    request = OptimizationRequest(assets=(AssetSpec("A"), AssetSpec("B")))
    returns = prepare_monthly_returns(request, _prices())
    assert list(returns.columns) == ["A", "B"]
    assert len(returns) >= 10


def test_analysis_start_keeps_prior_month_end_as_return_baseline():
    index = pd.to_datetime(["2024-07-31", "2024-08-30", "2024-09-30"])
    request = OptimizationRequest(assets=(AssetSpec("A"),), start="2024-08-01", end="2024-09-30")
    returns = prepare_monthly_returns(request, {"A": pd.Series([100.0, 110.0, 121.0], index=index)})
    assert returns.index.tolist() == list(pd.to_datetime(["2024-08-31", "2024-09-30"]))
    assert returns["A"].tolist() == pytest.approx([0.1, 0.1])


def test_prepare_monthly_returns_excludes_incomplete_current_month_by_default():
    current_month_start = pd.Timestamp.today().normalize().to_period("M").start_time
    previous_month_end = current_month_start - pd.Timedelta(days=1)
    prior_month_end = previous_month_end.to_period("M").start_time - pd.Timedelta(days=1)
    index = pd.DatetimeIndex([prior_month_end, previous_month_end, current_month_start])
    request = OptimizationRequest(assets=(AssetSpec("A"),))

    returns = prepare_monthly_returns(
        request,
        {"A": pd.Series([100.0, 110.0, 220.0], index=index)},
    )

    assert returns.index.tolist() == [previous_month_end]
    assert returns["A"].tolist() == pytest.approx([0.1])


def test_prepare_monthly_returns_excludes_incomplete_current_month_with_future_end():
    current_month_start = pd.Timestamp.today().normalize().to_period("M").start_time
    previous_month_end = current_month_start - pd.Timedelta(days=1)
    prior_month_end = previous_month_end.to_period("M").start_time - pd.Timedelta(days=1)
    future_end = (current_month_start + pd.offsets.MonthEnd(4)).date().isoformat()
    index = pd.DatetimeIndex([prior_month_end, previous_month_end, current_month_start])
    request = OptimizationRequest(
        assets=(AssetSpec("A"),),
        end=future_end,
    )

    returns = prepare_monthly_returns(
        request,
        {"A": pd.Series([100.0, 110.0, 220.0], index=index)},
    )

    assert returns.index.tolist() == [previous_month_end]
    assert returns["A"].tolist() == pytest.approx([0.1])


def test_prepare_monthly_returns_excludes_partial_terminal_month_for_midmonth_end():
    index = pd.to_datetime(["2024-07-31", "2024-08-30", "2024-09-13"])
    request = OptimizationRequest(
        assets=(AssetSpec("A"),),
        end="2024-09-15",
    )

    returns = prepare_monthly_returns(
        request,
        {"A": pd.Series([100.0, 110.0, 220.0], index=index)},
    )

    assert returns.index.tolist() == [pd.Timestamp("2024-08-31")]
    assert returns["A"].tolist() == pytest.approx([0.1])


def test_end_to_end_synthetic_pipeline():
    request = OptimizationRequest(
        assets=(AssetSpec("A"), AssetSpec("B")),
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
        frontier_points=5,
    )
    result = analyze_prices(request, _prices())
    assert set(result["optimization_result"]["weights"]) == {"A", "B"}
    assert len(result["efficient_frontier"]) == 5
    assert "optimized" in result["portfolio_performance"]
