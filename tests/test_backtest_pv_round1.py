from __future__ import annotations

import numpy as np
import pandas as pd

from portfolio_optimizer_kr.backtest_pv import analyze_backtest_prices
from portfolio_optimizer_kr.config import request_from_config
from portfolio_optimizer_kr.report import write_analysis_run
from portfolio_optimizer_kr.viewer import generate_report


def _price_series(returns: list[float], index: pd.DatetimeIndex) -> pd.Series:
    values = [100.0]
    for value in returns:
        values.append(values[-1] * (1.0 + value))
    return pd.Series(values, index=index, dtype=float)


def test_pv_round1_artifacts_and_report_contract(tmp_path):
    months = 72
    index = pd.date_range("2019-12-31", periods=months + 1, freq="ME")
    phase = np.arange(months, dtype=float)
    a = (0.012 + np.sin(phase / 4.0) * 0.018).tolist()
    b = (0.005 + np.cos(phase / 5.0) * 0.014).tolist()
    bm = (0.008 + np.sin(phase / 6.0) * 0.013).tolist()
    cpi_index = pd.date_range("2018-12-31", periods=85, freq="ME")
    cpi = pd.Series(np.linspace(250.0, 310.0, len(cpi_index)), index=cpi_index)

    spec = request_from_config(
        {
            "product_mode": "backtest",
            "run_id": "pv-round1",
            "time_period": {"mode": "month_to_month", "start_year": 2020, "first_month": 1, "end_year": 2025, "last_month": 12},
            "assets": [
                {"symbol": "A", "name": "Asset A", "currency": "USD"},
                {"symbol": "B", "name": "Asset B", "currency": "USD"},
            ],
            "portfolios": [
                {"name": "Only A", "weights_pct": {"A": 100}},
                {"name": "A B Mix", "weights_pct": {"A": 50, "B": 50}},
            ],
            "benchmark": {"symbol": "BM", "name": "Benchmark Market", "currency": "USD"},
            "initial_balance": 10000,
            "rebalancing": {"period": "yearly", "calendar_aligned": True},
            "risk_free": {"mode": "fixed", "annual_rate_pct": 2.0},
        }
    )
    result = analyze_backtest_prices(
        spec.request,
        {"A": _price_series(a, index), "B": _price_series(b, index), "BM": _price_series(bm, index)},
        annual_rf=0.02,
        inflation_series=cpi,
    )
    write_analysis_run(result, tmp_path)
    report = generate_report(tmp_path)

    for name in (
        "risk_and_return_metrics.csv",
        "annual_returns_detail.csv",
        "monthly_returns_detail.csv",
    ):
        assert (tmp_path / "raw" / name).is_file()

    metrics = pd.read_csv(tmp_path / "raw/risk_and_return_metrics.csv")
    expected = {
        "Arithmetic Mean (monthly)",
        "Arithmetic Mean (annualized)",
        "Geometric Mean (monthly)",
        "Geometric Mean (annualized)",
        "Downside Deviation (monthly)",
        "Benchmark Correlation",
        "Beta(*)",
        "Alpha (annualized)",
        "R2",
        "Treynor Ratio (%)",
        "Modigliani–Modigliani Measure",
        "Active Return",
        "Tracking Error",
        "Information Ratio",
        "Historical Value-at-Risk (5%)",
        "Analytical Value-at-Risk (5%)",
        "Conditional Value-at-Risk (5%)",
        "Upside Capture Ratio (%)",
        "Downside Capture Ratio (%)",
        "Safe Withdrawal Rate",
        "Perpetual Withdrawal Rate",
        "Positive Periods",
        "Gain/Loss Ratio",
    }
    assert expected <= set(metrics["metric"])

    contribution = pd.read_csv(tmp_path / "raw/active_return_contribution.csv")
    only_a = contribution[contribution["portfolio"] == "Only A"]
    assert set(only_a["ticker"]) == {"A"}

    annual = pd.read_csv(tmp_path / "raw/annual_returns_detail.csv")
    assert {
        "inflation",
        "series::Only A::return",
        "series::Only A::balance",
        "series::benchmark::return",
        "series::benchmark::balance",
        "asset::A::return",
        "asset::B::return",
    } <= set(annual.columns)

    monthly = pd.read_csv(tmp_path / "raw/monthly_returns_detail.csv")
    assert {
        "year",
        "month",
        "series::A B Mix::return",
        "series::A B Mix::balance",
        "asset::A::return",
        "asset::B::return",
    } <= set(monthly.columns)

    html = report.read_text(encoding="utf-8")
    assert "Annualized Return (CAGR)" in html
    assert '<h2>Risk and Return Metrics</h2>' in html
    assert "Portfolio return and risk metrics" in html
    assert "Benchmark Summary" not in html
    assert "Active Return Contribution" in html
    assert 'id="annual-returns-detail"' in html
    assert 'id="monthly-returns-detail"' in html
    assert 'data-chart="drawdown-combined"' in html
    assert "drawdown-panel" not in html
    assert "drawdown-episodes-panel" in html
    assert html.index("Portfolio Risk Decomposition") < html.index("Annual Asset Returns")
    assert "tipWidth" in html and "pointerX - tipWidth - 12" in html

    annual_chart = html.index('data-chart="annual-returns-chart"')
    annual_legend = html.find('<div class="legend">', annual_chart)
    assert annual_legend > annual_chart
