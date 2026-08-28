from __future__ import annotations

import numpy as np
import pandas as pd

from .solver import maximum_return, minimum_variance, minimum_variance_for_return


def build_efficient_frontier(
    expected_returns: pd.Series,
    covariance: pd.DataFrame,
    bounds=None,
    annual_rf: float = 0.0,
    points: int = 100,
) -> pd.DataFrame:
    if points < 2:
        raise ValueError("frontier requires at least two points")
    gmv = minimum_variance(expected_returns, covariance, bounds, annual_rf)
    max_ret = maximum_return(expected_returns, covariance, bounds, annual_rf)
    targets = np.linspace(gmv.expected_return, max_ret.expected_return, points)
    rows = []
    for number, target in enumerate(targets, start=1):
        result = minimum_variance_for_return(
            expected_returns, covariance, target, bounds, annual_rf
        )
        row = {
            "point": number,
            "expected_return": result.expected_return,
            "volatility": result.volatility,
            "sharpe": result.sharpe,
        }
        row.update({f"weight_{symbol}": weight for symbol, weight in result.weights.items()})
        rows.append(row)
    return pd.DataFrame(rows)
