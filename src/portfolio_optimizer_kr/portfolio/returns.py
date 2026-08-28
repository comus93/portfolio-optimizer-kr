from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping

import numpy as np
import pandas as pd

from portfolio_optimizer_kr.models import RebalancingPeriod


@dataclass(frozen=True)
class PortfolioPath:
    returns: pd.Series
    weights: pd.DataFrame


def _target_vector(columns, target_weights: Mapping[str, float]) -> np.ndarray:
    missing = set(columns) - set(target_weights)
    if missing:
        raise ValueError(f"missing target weights for: {sorted(missing)}")
    target = np.array([target_weights[c] for c in columns], dtype=float)
    if np.any(target < 0) or not np.isclose(target.sum(), 1.0, atol=1e-8):
        raise ValueError("target weights must be long-only and sum to one")
    return target


def build_portfolio_path(
    asset_returns: pd.DataFrame,
    target_weights: Mapping[str, float],
    rebalancing: RebalancingPeriod | str = RebalancingPeriod.MONTHLY,
) -> PortfolioPath:
    if asset_returns.empty:
        raise ValueError("asset returns are empty")
    columns = list(asset_returns.columns)
    target = _target_vector(columns, target_weights)
    period = RebalancingPeriod(rebalancing)

    realized = []
    history = []
    weights = target.copy()
    previous_year = None

    for timestamp, row in asset_returns.iterrows():
        if period is RebalancingPeriod.MONTHLY or (
            period is RebalancingPeriod.YEARLY and previous_year != timestamp.year
        ):
            weights = target.copy()
        history.append(weights.copy())
        values = row.to_numpy(dtype=float)
        portfolio_return = float(weights @ values)
        realized.append(portfolio_return)

        if period is RebalancingPeriod.YEARLY:
            gross = weights * (1.0 + values)
            denominator = 1.0 + portfolio_return
            if denominator <= 0:
                raise ValueError("portfolio gross return is non-positive")
            weights = gross / denominator
        previous_year = timestamp.year

    return PortfolioPath(
        returns=pd.Series(realized, index=asset_returns.index, name="portfolio_return"),
        weights=pd.DataFrame(history, index=asset_returns.index, columns=columns),
    )
