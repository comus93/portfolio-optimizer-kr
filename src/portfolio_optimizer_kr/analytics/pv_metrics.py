from __future__ import annotations

from collections.abc import Mapping
import math

import numpy as np
import pandas as pd

from .metrics import cagr, max_drawdown


METRIC_SPECS: tuple[tuple[str, str], ...] = (
    ("Arithmetic Mean (monthly)", "pct"),
    ("Arithmetic Mean (annualized)", "pct"),
    ("Geometric Mean (monthly)", "pct"),
    ("Geometric Mean (annualized)", "pct"),
    ("Standard Deviation (monthly)", "pct"),
    ("Standard Deviation (annualized)", "pct"),
    ("Downside Deviation (monthly)", "pct"),
    ("Maximum Drawdown", "pct"),
    ("Benchmark Correlation", "ratio"),
    ("Beta(*)", "ratio"),
    ("Alpha (annualized)", "pct"),
    ("R2", "pct"),
    ("Sharpe Ratio", "ratio"),
    ("Sortino Ratio", "ratio"),
    ("Treynor Ratio (%)", "percent_number"),
    ("Calmar Ratio", "ratio"),
    ("Modigliani–Modigliani Measure", "pct"),
    ("Active Return", "pct"),
    ("Tracking Error", "pct"),
    ("Information Ratio", "ratio"),
    ("Skewness", "ratio"),
    ("Excess Kurtosis", "ratio"),
    ("Historical Value-at-Risk (5%)", "pct"),
    ("Analytical Value-at-Risk (5%)", "pct"),
    ("Conditional Value-at-Risk (5%)", "pct"),
    ("Upside Capture Ratio (%)", "percent_number"),
    ("Downside Capture Ratio (%)", "percent_number"),
    ("Safe Withdrawal Rate", "pct"),
    ("Perpetual Withdrawal Rate", "pct"),
    ("Positive Periods", "count"),
    ("Gain/Loss Ratio", "ratio"),
)


def _geometric_monthly(returns: pd.Series) -> float:
    values = returns.dropna().astype(float)
    if values.empty:
        return float("nan")
    return float((1.0 + values).prod() ** (1.0 / len(values)) - 1.0)


def _downside_deviation_monthly(returns: pd.Series) -> float:
    values = returns.dropna().astype(float).to_numpy()
    if values.size == 0:
        return float("nan")
    downside = np.minimum(values, 0.0)
    return float(np.sqrt(np.mean(downside**2)))


def _capture_ratio(portfolio: pd.Series, benchmark: pd.Series, *, upside: bool) -> float:
    joined = pd.concat(
        [portfolio.rename("portfolio"), benchmark.rename("benchmark")],
        axis=1,
        join="inner",
    ).dropna()
    selected = joined[joined["benchmark"] > 0] if upside else joined[joined["benchmark"] < 0]
    if selected.empty:
        return float("nan")
    p = _geometric_monthly(selected["portfolio"])
    b = _geometric_monthly(selected["benchmark"])
    if not math.isfinite(b) or abs(b) < 1e-12:
        return float("nan")
    return float(p / b * 100.0)


def _annual_inflation_factors(
    inflation_index: pd.Series | None,
    years: list[int],
) -> dict[int, float]:
    if inflation_index is None or inflation_index.dropna().empty:
        return {year: 1.0 for year in years}
    levels = pd.to_numeric(inflation_index, errors="coerce").dropna().astype(float)
    levels.index = pd.DatetimeIndex(levels.index)
    levels = levels.sort_index()
    if levels.empty:
        return {year: 1.0 for year in years}
    base = float(levels.iloc[0])
    out: dict[int, float] = {}
    for year in years:
        available = levels[levels.index.year <= year]
        if available.empty or base <= 0:
            out[year] = 1.0
        else:
            out[year] = float(available.iloc[-1] / base)
    return out


def _withdrawal_survives(
    annual_returns: pd.Series,
    inflation_factors: Mapping[int, float],
    rate: float,
    *,
    perpetual: bool,
) -> bool:
    balance = 1.0
    years = [int(year) for year in annual_returns.index]
    for year in years:
        withdrawal = rate * float(inflation_factors.get(year, 1.0))
        if perpetual:
            balance *= 1.0 + float(annual_returns.loc[year])
            balance -= withdrawal
        else:
            balance -= withdrawal
            if balance <= 0:
                return False
            balance *= 1.0 + float(annual_returns.loc[year])
        if balance <= 0:
            return False
    if perpetual:
        terminal_floor = float(inflation_factors.get(years[-1], 1.0)) if years else 1.0
        return balance >= terminal_floor
    return balance > 0


def _withdrawal_rate(
    returns: pd.Series,
    inflation_index: pd.Series | None,
    *,
    perpetual: bool,
) -> float:
    values = returns.dropna().astype(float)
    if values.empty:
        return float("nan")
    annual = values.groupby(values.index.year).apply(
        lambda part: float((1.0 + part).prod() - 1.0)
    )
    annual.index = annual.index.astype(int)
    factors = _annual_inflation_factors(inflation_index, list(annual.index))
    low, high = 0.0, 1.0
    for _ in range(60):
        mid = (low + high) / 2.0
        if _withdrawal_survives(annual, factors, mid, perpetual=perpetual):
            low = mid
        else:
            high = mid
    return float(low)


def _series_metrics(
    returns: pd.Series,
    benchmark: pd.Series,
    annual_rf: float,
    inflation_index: pd.Series | None,
    *,
    is_benchmark: bool,
) -> dict[str, object]:
    joined = pd.concat(
        [returns.rename("portfolio"), benchmark.rename("benchmark")],
        axis=1,
        join="inner",
    ).dropna()
    portfolio = joined["portfolio"].astype(float)
    benchmark_values = joined["benchmark"].astype(float)
    if portfolio.empty:
        return {}

    arithmetic_monthly = float(portfolio.mean())
    arithmetic_annualized = float((1.0 + arithmetic_monthly) ** 12 - 1.0)
    geometric_monthly = _geometric_monthly(portfolio)
    geometric_annualized = float((1.0 + geometric_monthly) ** 12 - 1.0)
    stdev_monthly = float(portfolio.std(ddof=1))
    stdev_annualized = float(stdev_monthly * np.sqrt(12.0))
    downside_monthly = _downside_deviation_monthly(portfolio)
    downside_annualized = float(downside_monthly * np.sqrt(12.0))
    maximum_drawdown = max_drawdown(portfolio)

    variance = float(benchmark_values.var(ddof=1))
    correlation = float(portfolio.corr(benchmark_values)) if variance > 0 else float("nan")
    beta = float(portfolio.cov(benchmark_values) / variance) if variance > 0 else float("nan")
    r2 = correlation**2 if math.isfinite(correlation) else float("nan")
    monthly_rf = (1.0 + annual_rf) ** (1.0 / 12.0) - 1.0
    alpha_monthly = float(
        (portfolio - monthly_rf).mean()
        - beta * (benchmark_values - monthly_rf).mean()
    ) if math.isfinite(beta) else float("nan")
    alpha_annualized = float((1.0 + alpha_monthly) ** 12 - 1.0) if math.isfinite(alpha_monthly) else float("nan")

    sharpe = (
        (geometric_annualized - annual_rf) / stdev_annualized
        if stdev_annualized > 0
        else float("nan")
    )
    sortino = (
        (geometric_annualized - annual_rf) / downside_annualized
        if downside_annualized > 0
        else float("nan")
    )
    treynor = (
        (geometric_annualized - annual_rf) / beta * 100.0
        if math.isfinite(beta) and abs(beta) > 1e-12
        else float("nan")
    )

    window = portfolio.iloc[-36:]
    window_dd = max_drawdown(window) if not window.empty else float("nan")
    calmar = (
        cagr(window) / abs(window_dd)
        if len(window) and math.isfinite(window_dd) and window_dd < 0
        else float("nan")
    )

    benchmark_stdev = float(benchmark_values.std(ddof=1) * np.sqrt(12.0))
    m2 = float(annual_rf + sharpe * benchmark_stdev) if math.isfinite(sharpe) else float("nan")

    benchmark_cagr = cagr(benchmark_values)
    active_return = float(geometric_annualized - benchmark_cagr)
    active = portfolio - benchmark_values
    tracking_error = float(active.std(ddof=1) * np.sqrt(12.0))
    information_ratio = active_return / tracking_error if tracking_error > 0 else float("nan")

    q05 = float(portfolio.quantile(0.05))
    historical_var = max(0.0, -q05)
    analytical_var = max(0.0, -(arithmetic_monthly - 1.6448536269514722 * stdev_monthly))
    tail = portfolio[portfolio <= q05]
    conditional_var = max(0.0, -float(tail.mean())) if not tail.empty else float("nan")

    gains = portfolio[portfolio > 0]
    losses = portfolio[portfolio < 0]
    gain_loss = (
        float(gains.mean() / abs(losses.mean()))
        if not gains.empty and not losses.empty and abs(float(losses.mean())) > 0
        else float("nan")
    )
    positive_count = int((portfolio > 0).sum())
    total_count = int(len(portfolio))
    positive_periods = f"{positive_count} out of {total_count} ({positive_count / total_count * 100.0:.2f}%)"

    if is_benchmark:
        active_return_value: float | None = None
        tracking_error_value: float | None = None
        information_ratio_value: float | None = None
        correlation = 1.0
        beta = 1.0
        alpha_annualized = 0.0
        r2 = 1.0
        upside_capture = 100.0
        downside_capture = 100.0
    else:
        active_return_value = active_return
        tracking_error_value = tracking_error
        information_ratio_value = float(information_ratio)
        upside_capture = _capture_ratio(portfolio, benchmark_values, upside=True)
        downside_capture = _capture_ratio(portfolio, benchmark_values, upside=False)

    return {
        "Arithmetic Mean (monthly)": arithmetic_monthly,
        "Arithmetic Mean (annualized)": arithmetic_annualized,
        "Geometric Mean (monthly)": geometric_monthly,
        "Geometric Mean (annualized)": geometric_annualized,
        "Standard Deviation (monthly)": stdev_monthly,
        "Standard Deviation (annualized)": stdev_annualized,
        "Downside Deviation (monthly)": downside_monthly,
        "Maximum Drawdown": maximum_drawdown,
        "Benchmark Correlation": correlation,
        "Beta(*)": beta,
        "Alpha (annualized)": alpha_annualized,
        "R2": r2,
        "Sharpe Ratio": float(sharpe),
        "Sortino Ratio": float(sortino),
        "Treynor Ratio (%)": float(treynor),
        "Calmar Ratio": float(calmar),
        "Modigliani–Modigliani Measure": m2,
        "Active Return": active_return_value,
        "Tracking Error": tracking_error_value,
        "Information Ratio": information_ratio_value,
        "Skewness": float(portfolio.skew()),
        "Excess Kurtosis": float(portfolio.kurt()),
        "Historical Value-at-Risk (5%)": historical_var,
        "Analytical Value-at-Risk (5%)": analytical_var,
        "Conditional Value-at-Risk (5%)": conditional_var,
        "Upside Capture Ratio (%)": float(upside_capture),
        "Downside Capture Ratio (%)": float(downside_capture),
        "Safe Withdrawal Rate": _withdrawal_rate(portfolio, inflation_index, perpetual=False),
        "Perpetual Withdrawal Rate": _withdrawal_rate(portfolio, inflation_index, perpetual=True),
        "Positive Periods": positive_periods,
        "Gain/Loss Ratio": gain_loss,
    }


def risk_and_return_metrics_table(
    series_returns: Mapping[str, pd.Series],
    benchmark: pd.Series,
    annual_rf: float,
    *,
    inflation_index: pd.Series | None = None,
) -> pd.DataFrame:
    values: dict[str, dict[str, object]] = {}
    for name, returns in series_returns.items():
        values[name] = _series_metrics(
            returns,
            benchmark,
            annual_rf,
            inflation_index,
            is_benchmark=name == "benchmark",
        )

    rows: list[dict[str, object]] = []
    for metric, unit in METRIC_SPECS:
        row: dict[str, object] = {"metric": metric, "unit": unit}
        for name, metrics in values.items():
            row[name] = metrics.get(metric)
        rows.append(row)
    return pd.DataFrame(rows)


def annual_inflation_yoy(inflation_index: pd.Series | None) -> dict[int, float]:
    if inflation_index is None or inflation_index.dropna().empty:
        return {}
    levels = pd.to_numeric(inflation_index, errors="coerce").dropna().astype(float)
    levels.index = pd.DatetimeIndex(levels.index)
    levels = levels.sort_index()
    monthly = levels.groupby(levels.index.to_period("M")).last()
    yoy = monthly.pct_change(12)
    out: dict[int, float] = {}
    for year in sorted({period.year for period in monthly.index}):
        part = yoy[[period.year == year for period in yoy.index]].dropna()
        if not part.empty:
            out[year] = float(part.iloc[-1])
    return out
