import pytest

from portfolio_optimizer_kr.config import (
    PINNED_US_3M_TBILL_ANNUAL_RATE_PCT,
    request_from_config,
)
from portfolio_optimizer_kr.models import ProductMode, RiskFreeMode


def test_optimization_without_user_rf_uses_pinned_us3m_rate():
    spec = request_from_config(
        {
            "product_mode": "optimization",
            "run_id": "default-rf-opt",
            "assets": [{"symbol": "A"}, {"symbol": "B"}],
        }
    )

    assert spec.product_mode is ProductMode.OPTIMIZATION
    assert spec.request.risk_free.mode is RiskFreeMode.FIXED
    assert spec.request.risk_free.annual_rate == pytest.approx(
        PINNED_US_3M_TBILL_ANNUAL_RATE_PCT / 100.0
    )


def test_backtest_without_user_rf_uses_pinned_us3m_rate():
    spec = request_from_config(
        {
            "product_mode": "backtest",
            "run_id": "default-rf-backtest",
            "assets": [{"symbol": "A"}, {"symbol": "B"}],
            "portfolios": [
                {
                    "name": "Portfolio 1",
                    "weights_pct": {"A": 50, "B": 50},
                }
            ],
        }
    )

    assert spec.product_mode is ProductMode.BACKTEST
    assert spec.request.risk_free.mode is RiskFreeMode.FIXED
    assert spec.request.risk_free.annual_rate == pytest.approx(
        PINNED_US_3M_TBILL_ANNUAL_RATE_PCT / 100.0
    )


def test_explicit_dynamic_us3m_mode_is_preserved():
    spec = request_from_config(
        {
            "product_mode": "optimization",
            "run_id": "dynamic-rf",
            "assets": [{"symbol": "A"}, {"symbol": "B"}],
            "risk_free": {"mode": "us_3m_tbill"},
        }
    )

    assert spec.request.risk_free.mode is RiskFreeMode.US_3M_TBILL
    assert spec.request.risk_free.annual_rate is None


def test_explicit_custom_fixed_rate_is_preserved():
    spec = request_from_config(
        {
            "product_mode": "optimization",
            "run_id": "custom-rf",
            "assets": [{"symbol": "A"}, {"symbol": "B"}],
            "risk_free": {"mode": "fixed", "annual_rate_pct": 2.25},
        }
    )

    assert spec.request.risk_free.mode is RiskFreeMode.FIXED
    assert spec.request.risk_free.annual_rate == pytest.approx(0.0225)
