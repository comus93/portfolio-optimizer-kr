from __future__ import annotations

import numpy as np
import pandas as pd


def cagr(monthly_returns: pd.Series) -> float:
    if monthly_returns.empty:
        return float("nan")
    growth = float((1.0 + monthly_returns).prod())
    years = len(monthly_returns) / 12.0
    return growth ** (1.0 / years) - 1.0


def annual_returns(monthly_returns: pd.Series) -> pd.Series:
    return monthly_returns.groupby(monthly_returns.index.year).apply(
        lambda values: float((1.0 + values).prod() - 1.0)
    )


def max_drawdown(monthly_returns: pd.Series) -> float:
    wealth = (1.0 + monthly_returns).cumprod()
    drawdown = wealth / wealth.cummax() - 1.0
    return float(drawdown.min())


def performance_summary(monthly_returns: pd.Series, annual_rf: float = 0.0) -> dict[str, float]:
    ann_returns = annual_returns(monthly_returns)
    annualized_mean = float(monthly_returns.mean() * 12.0)
    annualized_vol = float(monthly_returns.std(ddof=1) * np.sqrt(12.0))
    downside = monthly_returns[monthly_returns < 0]
    downside_vol = float(downside.std(ddof=1) * np.sqrt(12.0)) if len(downside) > 1 else float("nan")
    return {
        "cagr": cagr(monthly_returns),
        "annualized_return": annualized_mean,
        "annualized_volatility": annualized_vol,
        "best_year": float(ann_returns.max()) if not ann_returns.empty else float("nan"),
        "worst_year": float(ann_returns.min()) if not ann_returns.empty else float("nan"),
        "max_drawdown": max_drawdown(monthly_returns),
        "sharpe_ex_post": (annualized_mean - annual_rf) / annualized_vol if annualized_vol > 0 else float("nan"),
        "sortino": (annualized_mean - annual_rf) / downside_vol if downside_vol > 0 else float("nan"),
    }


def active_return_metrics(portfolio: pd.Series, benchmark: pd.Series) -> dict[str, float]:
    joined = pd.concat([portfolio.rename("portfolio"), benchmark.rename("benchmark")], axis=1, join="inner").dropna()
    active = joined["portfolio"] - joined["benchmark"]
    annualized_active = float(active.mean() * 12.0)
    tracking_error = float(active.std(ddof=1) * np.sqrt(12.0))
    information_ratio = annualized_active / tracking_error if tracking_error > 0 else float("nan")
    return {
        "active_return": annualized_active,
        "tracking_error": tracking_error,
        "information_ratio": float(information_ratio),
    }
