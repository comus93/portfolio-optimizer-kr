from __future__ import annotations

from collections.abc import Mapping

import cvxpy as cp
import numpy as np
import pandas as pd

from portfolio_optimizer_kr.errors import InfeasibleOptimizationError, SolverError
from portfolio_optimizer_kr.models import OptimizationResult
from portfolio_optimizer_kr.stats import portfolio_expected_return, portfolio_volatility

TOL = 1e-6


def _arrays(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    bounds: Mapping[str, tuple[float, float]] | None,
):
    symbols = list(expected_returns.index)
    sigma = covariance.loc[symbols, symbols].to_numpy(dtype=float)
    sigma = (sigma + sigma.T) / 2.0
    if bounds is None:
        lo = np.zeros(len(symbols))
        hi = np.ones(len(symbols))
    else:
        lo = np.array([bounds[s][0] for s in symbols], dtype=float)
        hi = np.array([bounds[s][1] for s in symbols], dtype=float)
    if np.any(lo < -TOL) or np.any(hi > 1 + TOL) or np.any(lo > hi):
        raise InfeasibleOptimizationError("invalid long-only weight bounds")
    if lo.sum() > 1 + TOL or hi.sum() < 1 - TOL:
        raise InfeasibleOptimizationError("weight bounds cannot sum to one")
    return symbols, expected_returns.to_numpy(dtype=float), sigma, lo, hi


def _status(problem: cp.Problem) -> None:
    if problem.status not in {cp.OPTIMAL, cp.OPTIMAL_INACCURATE}:
        if problem.status in {cp.INFEASIBLE, cp.INFEASIBLE_INACCURATE}:
            raise InfeasibleOptimizationError(f"optimization status: {problem.status}")
        raise SolverError(f"optimization status: {problem.status}")


def _validated_result(
    symbols, weights, mu, sigma, lo, hi, annual_rf, solver, status, target_vol=None
) -> OptimizationResult:
    w = np.asarray(weights, dtype=float).reshape(-1)
    if not np.all(np.isfinite(w)):
        raise SolverError("solver returned non-finite weights")
    w[np.abs(w) < TOL] = 0.0
    if abs(w.sum() - 1.0) > 5e-5:
        raise SolverError(f"weight sum residual too large: {w.sum() - 1.0}")
    if np.any(w < lo - 5e-5) or np.any(w > hi + 5e-5):
        raise SolverError("solver result violates weight bounds")
    er = portfolio_expected_return(w, mu)
    vol = portfolio_volatility(w, sigma)
    if target_vol is not None and vol > target_vol + 5e-5:
        raise SolverError("solver result violates target volatility")
    sharpe = (er - annual_rf) / vol if vol > 0 else float("nan")
    return OptimizationResult(
        weights=pd.Series(w, index=symbols),
        expected_return=er,
        volatility=vol,
        sharpe=float(sharpe),
        solver=solver,
        status=status,
    )


def minimum_variance(expected_returns, covariance, bounds=None, annual_rf=0.0):
    symbols, mu, sigma, lo, hi = _arrays(expected_returns, covariance, bounds)
    w = cp.Variable(len(symbols))
    problem = cp.Problem(
        cp.Minimize(cp.quad_form(w, cp.psd_wrap(sigma))),
        [cp.sum(w) == 1, w >= lo, w <= hi],
    )
    problem.solve(solver=cp.OSQP)
    _status(problem)
    return _validated_result(symbols, w.value, mu, sigma, lo, hi, annual_rf, "OSQP", problem.status)


def minimum_variance_for_return(
    expected_returns, covariance, target_return, bounds=None, annual_rf=0.0
):
    symbols, mu, sigma, lo, hi = _arrays(expected_returns, covariance, bounds)
    w = cp.Variable(len(symbols))
    problem = cp.Problem(
        cp.Minimize(cp.quad_form(w, cp.psd_wrap(sigma))),
        [cp.sum(w) == 1, mu @ w == float(target_return), w >= lo, w <= hi],
    )
    problem.solve(solver=cp.OSQP)
    _status(problem)
    return _validated_result(symbols, w.value, mu, sigma, lo, hi, annual_rf, "OSQP", problem.status)


def maximum_return(expected_returns, covariance, bounds=None, annual_rf=0.0):
    symbols, mu, sigma, lo, hi = _arrays(expected_returns, covariance, bounds)
    w = cp.Variable(len(symbols))
    problem = cp.Problem(cp.Maximize(mu @ w), [cp.sum(w) == 1, w >= lo, w <= hi])
    problem.solve(solver=cp.CLARABEL)
    _status(problem)
    return _validated_result(symbols, w.value, mu, sigma, lo, hi, annual_rf, "CLARABEL", problem.status)


def maximum_sharpe(expected_returns, covariance, bounds=None, annual_rf=0.0):
    symbols, mu, sigma, lo, hi = _arrays(expected_returns, covariance, bounds)
    excess = mu - float(annual_rf)
    if excess.max() <= 0:
        raise InfeasibleOptimizationError("maximum Sharpe requires positive excess return")

    y = cp.Variable(len(symbols))
    k = cp.Variable(nonneg=True)
    constraints = [
        excess @ y == 1,
        cp.sum(y) == k,
        y >= cp.multiply(lo, k),
        y <= cp.multiply(hi, k),
        k >= 1e-10,
    ]
    problem = cp.Problem(cp.Minimize(cp.quad_form(y, cp.psd_wrap(sigma))), constraints)
    problem.solve(solver=cp.OSQP)
    _status(problem)
    if k.value is None or float(k.value) <= 0:
        raise SolverError("invalid transformed scale in maximum Sharpe solution")
    w = np.asarray(y.value, dtype=float) / float(k.value)
    return _validated_result(symbols, w, mu, sigma, lo, hi, annual_rf, "OSQP", problem.status)


def target_volatility(
    expected_returns, covariance, target_vol, bounds=None, annual_rf=0.0
):
    symbols, mu, sigma, lo, hi = _arrays(expected_returns, covariance, bounds)
    gmv = minimum_variance(expected_returns, covariance, bounds, annual_rf)
    if target_vol < gmv.volatility - 5e-6:
        raise InfeasibleOptimizationError(
            f"target volatility {target_vol:.6f} is below GMV {gmv.volatility:.6f}"
        )

    eigenvalues, eigenvectors = np.linalg.eigh(sigma)
    factor = np.diag(np.sqrt(np.clip(eigenvalues, 0.0, None))) @ eigenvectors.T
    w = cp.Variable(len(symbols))
    constraints = [
        cp.sum(w) == 1,
        w >= lo,
        w <= hi,
        cp.norm(factor @ w, 2) <= float(target_vol),
    ]
    problem = cp.Problem(cp.Maximize(mu @ w), constraints)
    problem.solve(solver=cp.CLARABEL)
    _status(problem)
    return _validated_result(
        symbols, w.value, mu, sigma, lo, hi, annual_rf, "CLARABEL", problem.status, target_vol
    )
