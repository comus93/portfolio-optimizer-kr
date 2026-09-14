import numpy as np
import pytest

from portfolio_optimizer_kr.models import OptimizationObjective
from portfolio_optimizer_kr.optimize import (
    maximum_return,
    maximum_sharpe,
    minimum_variance,
    minimum_variance_for_return,
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


def test_reused_frontier_matches_cold_point_solves(diagonal_moments):
    mu, covariance = diagonal_moments
    rf = 0.01
    points = 7

    reused = frontier_module.build_efficient_frontier(
        mu,
        covariance,
        annual_rf=rf,
        points=points,
    )
    gmv = minimum_variance(mu, covariance, annual_rf=rf)
    max_ret = maximum_return(mu, covariance, annual_rf=rf)
    targets = np.linspace(gmv.expected_return, max_ret.expected_return, points)

    for row, target in zip(reused.to_dict(orient="records"), targets):
        cold = minimum_variance_for_return(
            mu,
            covariance,
            float(target),
            annual_rf=rf,
        )
        assert row["expected_return"] == pytest.approx(cold.expected_return, abs=2e-6)
        assert row["volatility"] == pytest.approx(cold.volatility, abs=2e-6)
        assert row["sharpe"] == pytest.approx(cold.sharpe, abs=2e-5)
        for symbol, weight in cold.weights.items():
            assert row[f"weight_{symbol}"] == pytest.approx(weight, abs=2e-5)
