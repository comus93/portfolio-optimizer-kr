import numpy as np
import pytest

from portfolio_optimizer_kr.errors import InfeasibleOptimizationError
from portfolio_optimizer_kr.optimize import maximum_sharpe, minimum_variance, target_volatility


def test_minimum_variance_known_solution(diagonal_moments):
    mu, covariance = diagonal_moments
    result = minimum_variance(mu, covariance)
    assert result.weights.sum() == pytest.approx(1.0, abs=1e-6)
    assert result.weights["A"] == pytest.approx(2.0 / 7.0, abs=2e-4)
    assert result.weights["B"] == pytest.approx(5.0 / 7.0, abs=2e-4)


def test_max_sharpe_known_unconstrained_tangency(diagonal_moments):
    mu, covariance = diagonal_moments
    result = maximum_sharpe(mu, covariance, annual_rf=0.0)
    expected = np.array([12.0, 20.0]) / 32.0
    assert result.weights["A"] == pytest.approx(expected[0], abs=5e-4)
    assert result.weights["B"] == pytest.approx(expected[1], abs=5e-4)


def test_weight_bounds_are_respected(diagonal_moments):
    mu, covariance = diagonal_moments
    bounds = {"A": (0.4, 0.6), "B": (0.4, 0.6)}
    result = maximum_sharpe(mu, covariance, bounds=bounds)
    assert 0.4 - 1e-5 <= result.weights["A"] <= 0.6 + 1e-5
    assert 0.4 - 1e-5 <= result.weights["B"] <= 0.6 + 1e-5


def test_target_volatility_does_not_exceed_target(diagonal_moments):
    mu, covariance = diagonal_moments
    target = 0.07
    result = target_volatility(mu, covariance, target)
    assert result.volatility <= target + 5e-5
    assert result.weights.sum() == pytest.approx(1.0, abs=1e-5)


def test_infeasible_target_below_gmv_fails(diagonal_moments):
    mu, covariance = diagonal_moments
    gmv = minimum_variance(mu, covariance)
    with pytest.raises(InfeasibleOptimizationError):
        target_volatility(mu, covariance, gmv.volatility - 0.01)
