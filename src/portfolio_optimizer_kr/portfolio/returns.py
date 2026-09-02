from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

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


def _calendar_bucket(timestamp: pd.Timestamp, period: RebalancingPeriod):
    if period is RebalancingPeriod.YEARLY:
        return timestamp.year
    if period is RebalancingPeriod.SEMIANNUAL:
        return (timestamp.year, (timestamp.month - 1) // 6)
    if period is RebalancingPeriod.QUARTERLY:
        return (timestamp.year, (timestamp.month - 1) // 3)
    if period is RebalancingPeriod.MONTHLY:
        return (timestamp.year, timestamp.month)
    return None


def _interval_months(period: RebalancingPeriod) -> int | None:
    if period is RebalancingPeriod.YEARLY:
        return 12
    if period is RebalancingPeriod.SEMIANNUAL:
        return 6
    if period is RebalancingPeriod.QUARTERLY:
        return 3
    if period is RebalancingPeriod.MONTHLY:
        return 1
    return None


def build_portfolio_path(
    asset_returns: pd.DataFrame,
    target_weights: Mapping[str, float],
    rebalancing: RebalancingPeriod | str = RebalancingPeriod.MONTHLY,
    *,
    calendar_aligned: bool = True,
) -> PortfolioPath:
    if asset_returns.empty:
        raise ValueError("asset returns are empty")
    columns = list(asset_returns.columns)
    target = _target_vector(columns, target_weights)
    period = RebalancingPeriod(rebalancing)

    realized: list[float] = []
    history: list[np.ndarray] = []
    weights = target.copy()
    previous_bucket = None
    interval = _interval_months(period)

    for position, (timestamp, row) in enumerate(asset_returns.iterrows()):
        when = pd.Timestamp(timestamp)
        if position == 0:
            rebalance = True
        elif period is RebalancingPeriod.NONE:
            rebalance = False
        elif calendar_aligned:
            bucket = _calendar_bucket(when, period)
            rebalance = bucket != previous_bucket
        else:
            rebalance = interval is not None and position % interval == 0

        if rebalance:
            weights = target.copy()

        history.append(weights.copy())
        values = row.to_numpy(dtype=float)
        portfolio_return = float(weights @ values)
        realized.append(portfolio_return)

        gross = weights * (1.0 + values)
        denominator = 1.0 + portfolio_return
        if denominator <= 0:
            raise ValueError("portfolio gross return is non-positive")
        weights = gross / denominator
        previous_bucket = _calendar_bucket(when, period)

    return PortfolioPath(
        returns=pd.Series(realized, index=asset_returns.index, name="portfolio_return"),
        weights=pd.DataFrame(history, index=asset_returns.index, columns=columns),
    )
