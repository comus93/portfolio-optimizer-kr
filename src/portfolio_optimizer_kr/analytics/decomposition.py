from __future__ import annotations

import pandas as pd


def risk_contribution(weights: pd.Series, covariance: pd.DataFrame) -> pd.Series:
    symbols = list(weights.index)
    w = weights.to_numpy(dtype=float)
    sigma = covariance.loc[symbols, symbols].to_numpy(dtype=float)
    total_variance = float(w @ sigma @ w)
    if total_variance <= 0:
        raise ValueError("portfolio variance must be positive")
    contribution = w * (sigma @ w) / total_variance
    return pd.Series(contribution, index=symbols, name="risk_contribution")


def return_decomposition(
    asset_returns: pd.DataFrame, weight_history: pd.DataFrame, initial_value: float = 1.0
) -> pd.DataFrame:
    weights = weight_history.loc[asset_returns.index, asset_returns.columns]
    pct = weights * asset_returns
    portfolio_returns = pct.sum(axis=1)
    prior_value = initial_value * (1.0 + portfolio_returns).cumprod().shift(1, fill_value=1.0)
    pnl = pct.mul(prior_value, axis=0)
    out = pnl.cumsum()
    out.columns = [f"contribution_{c}" for c in out.columns]
    return out
