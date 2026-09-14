import pytest

from portfolio_optimizer_kr.models import OptimizationObjective
from portfolio_optimizer_kr.optimize import (
    maximum_sharpe,
    solve_optimization,
    target_volatility,
)
from portfolio_optimizer_kr.optimize import frontier as frontier_module


def test_shared_engine_max_sharpe_matches_canonical_solver(diagonal_moments):
    mu, covariance = diagonal_moments

    expected = maximum_sharpe(mu, covariance, annual_rf=0.01)
    actual = solve_optimization(
        OptimizationObjective.MAX_SHARPE,
        mu,
        covariance,
        annual_rf=0.01,
    )

    assert actual.weights.to_dict() == pytest.approx(expected.weights.to_dict(), abs=1e-8)
    assert actual.expected_return == pytest.approx(expected.expected_return, abs=1e-10)
    assert actual.volatility == pytest.approx(expected.volatility, abs=1e-10)
    assert actual.sharpe == pytest.approx(expected.sharpe, abs=1e-10)
    assert actual.solver == expected.solver


def test_shared_engine_target_volatility_matches_canonical_solver(diagonal_moments):
    mu, covariance = diagonal_moments
    target = 0.07

    expected = target_volatility(mu, covariance, target, annual_rf=0.01)
    actual = solve_optimization(
        OptimizationObjective.TARGET_VOLATILITY,
        mu,
        covariance,
        annual_rf=0.01,
        target_volatility=target,
    )

    assert actual.weights.to_dict() == pytest.approx(expected.weights.to_dict(), abs=1e-8)
    assert actual.expected_return == pytest.approx(expected.expected_return, abs=1e-10)
    assert actual.volatility == pytest.approx(expected.volatility, abs=1e-10)
    assert actual.sharpe == pytest.approx(expected.sharpe, abs=1e-10)
    assert actual.solver == expected.solver


def test_shared_engine_requires_target_for_target_volatility(diagonal_moments):
    mu, covariance = diagonal_moments

    with pytest.raises(ValueError, match="requires target_volatility"):
        solve_optimization(
            OptimizationObjective.TARGET_VOLATILITY,
            mu,
            covariance,
        )


def test_frontier_reuses_one_parameterized_qp(diagonal_moments, monkeypatch):
    mu, covariance = diagonal_moments
    original = frontier_module.MinimumVarianceForReturnSolver
    calls = {"init": 0, "solve": 0}

    class SpySolver:
        def __init__(self, *args, **kwargs):
            calls["init"] += 1
            self.delegate = original(*args, **kwargs)

        def solve(self, target_return):
            calls["solve"] += 1
            return self.delegate.solve(target_return)

    monkeypatch.setattr(
        frontier_module,
        "MinimumVarianceForReturnSolver",
        SpySolver,
    )

    result = frontier_module.build_efficient_frontier(
        mu,
        covariance,
        annual_rf=0.01,
        points=7,
    )

    assert len(result) == 7
    assert calls == {"init": 1, "solve": 7}
