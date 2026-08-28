from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StatisticsSnapshot:
    expected_returns: pd.Series
    covariance: pd.DataFrame
    volatility: pd.Series
    correlation: pd.DataFrame


def annualized_statistics(monthly_returns: pd.DataFrame) -> StatisticsSnapshot:
    expected = monthly_returns.mean() * 12.0
    covariance = monthly_returns.cov() * 12.0
    volatility = monthly_returns.std(ddof=1) * np.sqrt(12.0)
    correlation = monthly_returns.corr()
    return StatisticsSnapshot(expected, covariance, volatility, correlation)


def portfolio_expected_return(weights, expected_returns) -> float:
    w = np.asarray(weights, dtype=float)
    mu = np.asarray(expected_returns, dtype=float)
    return float(w @ mu)


def portfolio_volatility(weights, covariance) -> float:
    w = np.asarray(weights, dtype=float)
    sigma = np.asarray(covariance, dtype=float)
    variance = float(w @ sigma @ w)
    return float(np.sqrt(max(variance, 0.0)))
