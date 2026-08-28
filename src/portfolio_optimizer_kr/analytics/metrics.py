from __future__ import annotations

import numpy as np
import pandas as pd


TRAILING_PERIODS = {"3m": 3, "1y": 12, "3y": 36, "5y": 60, "10y": 120}


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
        "start_balance": 1.0,
        "end_balance": float((1.0 + monthly_returns).prod()),
        "cagr": cagr(monthly_returns),
        "annualized_return": annualized_mean,
        "annualized_volatility": annualized_vol,
        "best_year": float(ann_returns.max()) if not ann_returns.empty else float("nan"),
        "worst_year": float(ann_returns.min()) if not ann_returns.empty else float("nan"),
        "max_drawdown": max_drawdown(monthly_returns),
        "sharpe_ex_post": (annualized_mean - annual_rf) / annualized_vol if annualized_vol > 0 else float("nan"),
        "sortino": (annualized_mean - annual_rf) / downside_vol if downside_vol > 0 else float("nan"),
    }


def trailing_returns(monthly_returns: pd.Series) -> dict[str, float | None]:
    """Compound trailing returns; multi-year windows are annualized."""
    out: dict[str, float | None] = {}
    for label, months in TRAILING_PERIODS.items():
        if len(monthly_returns) < months:
            out[label] = None
            continue
        value = float((1.0 + monthly_returns.iloc[-months:]).prod() - 1.0)
        out[label] = value if months <= 12 else (1.0 + value) ** (12.0 / months) - 1.0
    current_year = monthly_returns[monthly_returns.index.year == monthly_returns.index[-1].year]
    out["ytd"] = float((1.0 + current_year).prod() - 1.0) if not current_year.empty else None
    out["full_period"] = cagr(monthly_returns) if not monthly_returns.empty else None
    for label, months in (("3y_annualized_volatility", 36), ("5y_annualized_volatility", 60)):
        out[label] = float(monthly_returns.iloc[-months:].std(ddof=1) * np.sqrt(12.0)) if len(monthly_returns) >= months else None
    return out


def monthly_returns_table(monthly_returns: pd.Series) -> pd.DataFrame:
    rows = []
    for year, values in monthly_returns.groupby(monthly_returns.index.year):
        row: dict[str, float | int | None] = {"year": int(year)}
        for month in range(1, 13):
            selected = values[values.index.month == month]
            row[pd.Timestamp(2000, month, 1).strftime("%b")] = float(selected.iloc[0]) if not selected.empty else None
        row["ytd"] = float((1.0 + values).prod() - 1.0)
        rows.append(row)
    return pd.DataFrame(rows)


def drawdown_episodes(monthly_returns: pd.Series) -> pd.DataFrame:
    wealth = (1.0 + monthly_returns).cumprod()
    drawdown = wealth / wealth.cummax() - 1.0
    episodes: list[dict[str, object]] = []
    start = None
    for when, value in drawdown.items():
        if value < 0 and start is None:
            start = when
        if start is not None and value >= -1e-12:
            segment = drawdown.loc[start:when]
            bottom = segment.idxmin()
            episodes.append({"start": start, "bottom": bottom, "recovery": when, "maximum_drawdown": float(segment.min()), "duration_months": len(segment)})
            start = None
    if start is not None:
        segment = drawdown.loc[start:]
        episodes.append({"start": start, "bottom": segment.idxmin(), "recovery": None, "maximum_drawdown": float(segment.min()), "duration_months": len(segment)})
    ordered = sorted(episodes, key=lambda row: row["maximum_drawdown"])
    for rank, row in enumerate(ordered, start=1):
        row["rank"] = rank
    return pd.DataFrame(ordered, columns=["rank", "start", "bottom", "recovery", "maximum_drawdown", "duration_months"])


def rolling_returns(monthly_returns: pd.Series, months: int) -> pd.Series:
    if months < 1:
        raise ValueError("rolling window must be positive")
    values = (1.0 + monthly_returns).rolling(months).apply(np.prod, raw=True) - 1.0
    return values if months <= 12 else (1.0 + values) ** (12.0 / months) - 1.0


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


def active_analytics(portfolio: pd.Series, benchmark: pd.Series, window: int = 36) -> pd.DataFrame:
    joined = pd.concat([portfolio.rename("portfolio"), benchmark.rename("benchmark")], axis=1, join="inner").dropna()
    active = joined["portfolio"] - joined["benchmark"]
    annual = joined.groupby(joined.index.year).apply(
        lambda x: float((1.0 + x["portfolio"]).prod() - (1.0 + x["benchmark"]).prod())
    )
    rolling_portfolio = (1.0 + joined["portfolio"]).rolling(window).apply(np.prod, raw=True) - 1.0
    rolling_benchmark = (1.0 + joined["benchmark"]).rolling(window).apply(np.prod, raw=True) - 1.0
    return pd.DataFrame({
        "portfolio_return": joined["portfolio"],
        "benchmark_return": joined["benchmark"],
        "active_return": active,
        "cumulative_active_return": (1.0 + joined["portfolio"]).cumprod() - (1.0 + joined["benchmark"]).cumprod(),
        "annual_active_return": active.index.year.map(annual),
        "rolling_active_return": rolling_portfolio - rolling_benchmark,
        "rolling_tracking_error": active.rolling(window).std(ddof=1) * np.sqrt(12.0),
    })
