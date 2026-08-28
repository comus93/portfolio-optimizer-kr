import numpy as np
import pandas as pd
import pytest

from portfolio_optimizer_kr.analytics import active_return_metrics, return_decomposition, risk_contribution
from portfolio_optimizer_kr.portfolio import build_portfolio_path


def test_active_return_metrics_match_independent_formula():
    idx = pd.date_range("2024-01-31", periods=4, freq="ME")
    portfolio = pd.Series([0.02, 0.01, 0.03, -0.01], index=idx)
    benchmark = pd.Series([0.01, 0.00, 0.01, -0.01], index=idx)
    active = portfolio - benchmark
    out = active_return_metrics(portfolio, benchmark)
    assert out["active_return"] == pytest.approx(active.mean() * 12.0)
    assert out["tracking_error"] == pytest.approx(active.std(ddof=1) * np.sqrt(12.0))


def test_risk_contribution_sums_to_one(diagonal_moments):
    _, covariance = diagonal_moments
    weights = pd.Series({"A": 0.4, "B": 0.6})
    rc = risk_contribution(weights, covariance)
    assert rc.sum() == pytest.approx(1.0)


def test_return_decomposition_sums_to_terminal_gain():
    idx = pd.date_range("2024-01-31", periods=3, freq="ME")
    asset_returns = pd.DataFrame({"A": [0.10, 0.00, 0.05], "B": [0.00, 0.02, 0.00]}, index=idx)
    path = build_portfolio_path(asset_returns, {"A": 0.5, "B": 0.5})
    decomposition = return_decomposition(asset_returns, path.weights, initial_value=100.0)
    total_contribution = decomposition.iloc[-1].sum()
    terminal_gain = 100.0 * (1.0 + path.returns).prod() - 100.0
    assert total_contribution == pytest.approx(terminal_gain)
