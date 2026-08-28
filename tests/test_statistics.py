import numpy as np
import pandas as pd
import pytest

from portfolio_optimizer_kr.stats import (
    annualized_statistics,
    portfolio_expected_return,
    portfolio_volatility,
)


def test_annualization_matches_specification(simple_monthly_returns):
    stats = annualized_statistics(simple_monthly_returns)
    pd.testing.assert_series_equal(
        stats.expected_returns, simple_monthly_returns.mean() * 12.0
    )
    pd.testing.assert_frame_equal(
        stats.covariance, simple_monthly_returns.cov() * 12.0
    )
    pd.testing.assert_series_equal(
        stats.volatility, simple_monthly_returns.std(ddof=1) * np.sqrt(12.0)
    )


def test_portfolio_matrix_formulas():
    weights = np.array([0.25, 0.75])
    mu = np.array([0.12, 0.08])
    sigma = np.array([[0.04, 0.01], [0.01, 0.01]])
    assert portfolio_expected_return(weights, mu) == pytest.approx(0.09)
    expected_variance = weights @ sigma @ weights
    assert portfolio_volatility(weights, sigma) == pytest.approx(np.sqrt(expected_variance))
