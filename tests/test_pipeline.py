import pandas as pd

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
