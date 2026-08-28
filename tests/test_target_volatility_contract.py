import numpy as np
import pytest

from portfolio_optimizer_kr.errors import InfeasibleOptimizationError
from portfolio_optimizer_kr.optimize import maximum_return, minimum_variance, target_volatility


def test_target_volatility_interior_solution_is_return_maximizing_and_binding(diagonal_moments):
    mu, covariance = diagonal_moments
    target = 0.07

    result = target_volatility(mu, covariance, target)

    # For w_A=x, w_B=1-x, variance is
    # 0.01*x^2 + 0.004*(1-x)^2. Since A has the higher return,
    # the maximum-return feasible portfolio uses the positive cap root.
    expected_a = (0.008 + np.sqrt(0.008**2 + 4 * 0.014 * 0.0009)) / (2 * 0.014)
    assert result.weights["A"] == pytest.approx(expected_a, abs=2e-4)
    assert result.weights["B"] == pytest.approx(1.0 - expected_a, abs=2e-4)
    assert result.volatility == pytest.approx(target, abs=5e-5)


def test_target_at_gmv_returns_gmv_neighborhood(diagonal_moments):
    mu, covariance = diagonal_moments
    gmv = minimum_variance(mu, covariance)

    result = target_volatility(mu, covariance, gmv.volatility + 1e-7)

    assert result.weights["A"] == pytest.approx(gmv.weights["A"], abs=5e-4)
    assert result.weights["B"] == pytest.approx(gmv.weights["B"], abs=5e-4)
    assert result.volatility <= gmv.volatility + 5e-5


def test_target_above_maximum_return_volatility_returns_maximum_return_portfolio(diagonal_moments):
    mu, covariance = diagonal_moments
    max_return = maximum_return(mu, covariance)

    result = target_volatility(mu, covariance, max_return.volatility + 0.01)

    assert result.weights["A"] == pytest.approx(max_return.weights["A"], abs=5e-5)
    assert result.weights["B"] == pytest.approx(max_return.weights["B"], abs=5e-5)
    assert result.expected_return == pytest.approx(max_return.expected_return, abs=1e-6)


def test_target_volatility_respects_bounds(diagonal_moments):
    mu, covariance = diagonal_moments
    bounds = {"A": (0.0, 0.5), "B": (0.5, 1.0)}

    result = target_volatility(mu, covariance, 0.09, bounds=bounds)

    assert result.weights["A"] == pytest.approx(0.5, abs=5e-5)
    assert result.weights["B"] == pytest.approx(0.5, abs=5e-5)


def test_target_volatility_is_deterministic(diagonal_moments):
    mu, covariance = diagonal_moments

    first = target_volatility(mu, covariance, 0.07)
    second = target_volatility(mu, covariance, 0.07)

    assert first.weights.to_numpy() == pytest.approx(second.weights.to_numpy(), abs=1e-8)
    assert first.expected_return == pytest.approx(second.expected_return, abs=1e-10)
    assert first.volatility == pytest.approx(second.volatility, abs=1e-10)


def test_target_below_gmv_is_explicitly_infeasible(diagonal_moments):
    mu, covariance = diagonal_moments
    gmv = minimum_variance(mu, covariance)

    with pytest.raises(InfeasibleOptimizationError):
        target_volatility(mu, covariance, gmv.volatility - 0.001)
