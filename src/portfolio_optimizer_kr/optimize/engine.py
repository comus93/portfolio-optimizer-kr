from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from portfolio_optimizer_kr.models import OptimizationObjective, OptimizationResult

from .solver import maximum_sharpe, target_volatility as maximum_return_at_target_volatility


def solve_optimization(
    objective: OptimizationObjective,
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    *,
    bounds: Mapping[str, tuple[float, float]] | None = None,
    annual_rf: float = 0.0,
    target_volatility: float | None = None,
) -> OptimizationResult:
    """Solve one canonical optimization objective from prepared moments.

    This is the single objective-routing boundary shared by the normal
    Optimization product and lightweight repeated analyses such as robustness
    checks. Data preparation, frontier generation, simulation and reporting
    intentionally live outside this function.
    """
    if objective is OptimizationObjective.MAX_SHARPE:
        return maximum_sharpe(
            expected_returns,
            covariance,
            bounds=bounds,
            annual_rf=annual_rf,
        )

    if objective is OptimizationObjective.TARGET_VOLATILITY:
        if target_volatility is None:
            raise ValueError("target-volatility objective requires target_volatility")
        return maximum_return_at_target_volatility(
            expected_returns,
            covariance,
            target_volatility,
            bounds=bounds,
            annual_rf=annual_rf,
        )

    raise ValueError(f"unsupported optimization objective: {objective}")
