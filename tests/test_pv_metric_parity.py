from __future__ import annotations

import math

import numpy as np
import pandas as pd

from portfolio_optimizer_kr.analytics.pv_metric_parity import apply_pv_metric_parity
from portfolio_optimizer_kr.analytics.pv_metrics import risk_and_return_metrics_table


def _metric(frame: pd.DataFrame, name: str, series: str) -> float:
    row = frame.loc[frame["metric"] == name, series].iloc[0]
    return float(row)


def test_pv_ratio_and_withdrawal_semantics():
    index = pd.date_range("2020-01-31", periods=24, freq="ME")
    portfolio = pd.Series(
        [0.02, -0.01, 0.03, 0.01, -0.02, 0.015] * 4,
        index=index,
        dtype=float,
        name="Portfolio",
    )
    benchmark = pd.Series(
        [0.015, -0.015, 0.02, 0.005, -0.01, 0.01] * 4,
        index=index,
        dtype=float,
        name="benchmark",
    )
    cpi_index = pd.date_range("2019-12-31", periods=25, freq="ME")
    cpi = pd.Series(np.linspace(100.0, 106.0, len(cpi_index)), index=cpi_index)
    annual_rf = 0.02

    series = {"Portfolio": portfolio, "benchmark": benchmark}
    base = risk_and_return_metrics_table(
        series,
        benchmark,
        annual_rf,
        inflation_index=cpi,
    )
    corrected = apply_pv_metric_parity(
        base,
        series,
        benchmark,
        annual_rf,
        cpi,
    )

    monthly_rf = (1.0 + annual_rf) ** (1.0 / 12.0) - 1.0
    beta = portfolio.cov(benchmark) / benchmark.var(ddof=1)
    expected_alpha = (portfolio.mean() - beta * benchmark.mean()) * 12.0
    expected_sharpe = (
        (portfolio.mean() - monthly_rf)
        / portfolio.std(ddof=1)
        * math.sqrt(12.0)
    )
    excess = portfolio - monthly_rf
    downside = np.sqrt(np.mean(np.minimum(excess.to_numpy(), 0.0) ** 2))
    expected_sortino = (portfolio.mean() - monthly_rf) / downside * math.sqrt(12.0)

    assert _metric(corrected, "Alpha (annualized)", "Portfolio") == pytest.approx(expected_alpha)
    assert _metric(corrected, "Sharpe Ratio", "Portfolio") == pytest.approx(expected_sharpe)
    assert _metric(corrected, "Sortino Ratio", "Portfolio") == pytest.approx(expected_sortino)

    annual = portfolio.groupby(portfolio.index.year).apply(lambda values: (1.0 + values).prod() - 1.0)
    factor_2020 = cpi.loc[:"2020-12-31"].iloc[-1] / cpi.loc["2019-12-31"]
    factor_2021 = cpi.loc[:"2021-12-31"].iloc[-1] / cpi.loc["2019-12-31"]
    expected_swr = (
        (1.0 + annual.loc[2020]) * (1.0 + annual.loc[2021])
        / (factor_2020 * (1.0 + annual.loc[2021]) + factor_2021)
    )
    terminal_factor = factor_2021
    terminal_without_withdrawals = (1.0 + annual.loc[2020]) * (1.0 + annual.loc[2021])
    expected_pwr = 1.0 - math.sqrt(terminal_factor / terminal_without_withdrawals)

    assert _metric(corrected, "Safe Withdrawal Rate", "Portfolio") == pytest.approx(expected_swr)
    assert _metric(corrected, "Perpetual Withdrawal Rate", "Portfolio") == pytest.approx(expected_pwr)


import pytest
