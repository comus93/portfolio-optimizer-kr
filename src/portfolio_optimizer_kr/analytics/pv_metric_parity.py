from __future__ import annotations

from collections.abc import Mapping
import math

import numpy as np
import pandas as pd


def _geometric_monthly(values: pd.Series) -> float:
    clean = values.dropna().astype(float)
    if clean.empty:
        return float("nan")
    return float((1.0 + clean).prod() ** (1.0 / len(clean)) - 1.0)


def _capture(portfolio: pd.Series, benchmark: pd.Series, *, upside: bool) -> float:
    joined = pd.concat([portfolio.rename("p"), benchmark.rename("b")], axis=1).dropna()
    selected = joined[joined["b"] > 0] if upside else joined[joined["b"] < 0]
    if selected.empty:
        return float("nan")
    p = (1.0 + _geometric_monthly(selected["p"])) ** 12 - 1.0
    b = (1.0 + _geometric_monthly(selected["b"])) ** 12 - 1.0
    return float(p / b * 100.0) if abs(b) > 1e-12 else float("nan")


def _inflation_path(
    inflation_index: pd.Series | None,
    returns: pd.Series,
) -> tuple[dict[int, float], float]:
    dates = pd.DatetimeIndex(returns.dropna().index).sort_values()
    years = sorted(set(int(year) for year in dates.year))
    if len(dates) == 0 or inflation_index is None or inflation_index.dropna().empty:
        return {year: 1.0 for year in years}, 1.0
    levels = pd.to_numeric(inflation_index, errors="coerce").dropna().astype(float)
    levels.index = pd.DatetimeIndex(levels.index)
    levels = levels.sort_index()
    base_cutoff = (dates.min().to_period("M") - 1).end_time
    prior = levels[levels.index <= base_cutoff]
    base = float(prior.iloc[-1] if not prior.empty else levels.iloc[0])
    if base <= 0:
        return {year: 1.0 for year in years}, 1.0
    factors: dict[int, float] = {}
    for year in years:
        available = levels[levels.index <= pd.Timestamp(year=year, month=12, day=31)]
        factors[year] = float(available.iloc[-1] / base) if not available.empty else 1.0
    terminal_values = levels[levels.index <= dates.max().to_period("M").end_time]
    terminal = float(terminal_values.iloc[-1] / base) if not terminal_values.empty else 1.0
    return factors, terminal


def _annual_path(returns: pd.Series) -> list[tuple[int, float, bool]]:
    rows: list[tuple[int, float, bool]] = []
    for year, part in returns.dropna().astype(float).groupby(returns.dropna().index.year):
        months = set(pd.DatetimeIndex(part.index).month)
        rows.append(
            (
                int(year),
                float((1.0 + part).prod() - 1.0),
                months == set(range(1, 13)),
            )
        )
    return rows


def _withdrawal_rate(
    returns: pd.Series,
    inflation_index: pd.Series | None,
    *,
    perpetual: bool,
) -> float:
    values = returns.dropna().astype(float)
    if values.empty:
        return float("nan")
    path = _annual_path(values)
    factors, terminal = _inflation_path(inflation_index, values)
    low, high = 0.0, 1.0
    for _ in range(70):
        rate = (low + high) / 2.0
        balance = 1.0
        ok = True
        for year, annual_return, complete in path:
            balance *= 1.0 + annual_return
            if complete:
                if perpetual:
                    balance *= 1.0 - rate
                else:
                    balance -= rate * factors.get(year, 1.0)
            if balance <= 0:
                ok = False
                break
        if perpetual and ok:
            ok = balance >= terminal
        if ok:
            low = rate
        else:
            high = rate
    return float(low)


def apply_pv_metric_parity(
    frame: pd.DataFrame,
    series_returns: Mapping[str, pd.Series],
    benchmark: pd.Series,
    annual_rf: float,
    inflation_index: pd.Series | None,
) -> pd.DataFrame:
    """Correct PV-specific metric semantics without moving finance into the renderer."""
    if frame.empty or "metric" not in frame:
        return frame
    out = frame.copy()
    benchmark_values = benchmark.dropna().astype(float)
    monthly_rf = (1.0 + annual_rf) ** (1.0 / 12.0) - 1.0
    benchmark_stdev = float(benchmark_values.std(ddof=1) * np.sqrt(12.0))

    corrected: dict[str, dict[str, object]] = {}
    for name, source in series_returns.items():
        joined = pd.concat([source.rename("p"), benchmark_values.rename("b")], axis=1).dropna()
        p = joined["p"].astype(float)
        b = joined["b"].astype(float)
        variance = float(b.var(ddof=1))
        beta = float(p.cov(b) / variance) if variance > 0 else float("nan")
        monthly_mean = float(p.mean())
        monthly_excess = monthly_mean - monthly_rf
        stdev = float(p.std(ddof=1))
        sharpe = monthly_excess / stdev * math.sqrt(12.0) if stdev > 0 else float("nan")
        excess = p - monthly_rf
        downside = float(np.sqrt(np.mean(np.minimum(excess.to_numpy(), 0.0) ** 2)))
        sortino = monthly_excess / downside * math.sqrt(12.0) if downside > 0 else float("nan")
        alpha = (monthly_mean - beta * float(b.mean())) * 12.0 if math.isfinite(beta) else float("nan")
        treynor = monthly_excess * 12.0 / beta * 100.0 if math.isfinite(beta) and abs(beta) > 1e-12 else float("nan")
        values: dict[str, object] = {
            "Alpha (annualized)": 0.0 if name == "benchmark" else alpha,
            "Sharpe Ratio": sharpe,
            "Sortino Ratio": sortino,
            "Treynor Ratio (%)": treynor,
            "Modigliani–Modigliani Measure": annual_rf + sharpe * benchmark_stdev,
            "Upside Capture Ratio (%)": 100.0 if name == "benchmark" else _capture(p, b, upside=True),
            "Downside Capture Ratio (%)": 100.0 if name == "benchmark" else _capture(p, b, upside=False),
            "Safe Withdrawal Rate": _withdrawal_rate(p, inflation_index, perpetual=False),
            "Perpetual Withdrawal Rate": _withdrawal_rate(p, inflation_index, perpetual=True),
        }
        corrected[name] = values

    for row_index, row in out.iterrows():
        metric = str(row["metric"])
        for name, values in corrected.items():
            if metric in values and name in out.columns:
                out.at[row_index, name] = values[metric]
    return out
