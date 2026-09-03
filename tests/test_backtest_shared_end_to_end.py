from __future__ import annotations

import numpy as np
import pandas as pd

from portfolio_optimizer_kr.backtest import analyze_backtest_prices
from portfolio_optimizer_kr.config import request_from_config
from portfolio_optimizer_kr.report import write_analysis_run
from portfolio_optimizer_kr.viewer import generate_report


def _price_series(returns: list[float], index: pd.DatetimeIndex) -> pd.Series:
    values = [100.0]
    for value in returns:
        values.append(values[-1] * (1.0 + value))
    return pd.Series(values, index=index, dtype=float)


def test_backtest_full_path_uses_shared_outputs_and_renders_complete_report(tmp_path):
    months = 72
    price_index = pd.date_range("2019-12-31", periods=months + 1, freq="ME")
    phase = np.arange(months, dtype=float)
    returns_a = (0.011 + np.sin(phase / 4.0) * 0.018).tolist()
    returns_b = (0.006 + np.cos(phase / 5.0) * 0.012).tolist()
    returns_benchmark = (0.008 + np.sin(phase / 6.0) * 0.014).tolist()

    spec = request_from_config(
        {
            "product_mode": "backtest",
            "run_id": "shared-e2e",
            "time_period": {"mode": "month_to_month", "start_year": 2020, "first_month": 1, "end_year": 2025, "last_month": 12},
            "assets": [
                {"symbol": "A", "name": "Asset A", "currency": "USD"},
                {"symbol": "B", "name": "Asset B", "currency": "USD"},
            ],
            "portfolios": [
                {"name": "Growth 70/30", "weights_pct": {"A": 70, "B": 30}},
                {"name": "Balanced 50/50", "weights_pct": {"A": 50, "B": 50}},
            ],
            "benchmark": {"symbol": "BM", "name": "Benchmark Market", "currency": "USD"},
            "initial_balance": 10000,
            "rebalancing": {"period": "monthly", "calendar_aligned": True},
            "risk_free": {"mode": "fixed", "annual_rate_pct": 0},
        }
    )
    prices = {
        "A": _price_series(returns_a, price_index),
        "B": _price_series(returns_b, price_index),
        "BM": _price_series(returns_benchmark, price_index),
    }

    result = analyze_backtest_prices(spec.request, prices, annual_rf=0.0)
    write_analysis_run(result, tmp_path)
    report_path = generate_report(tmp_path)

    for relative in [
        "raw/target_allocations.csv",
        "review/target_allocations.csv",
        "review/portfolio_asset_performance.csv",
        "review/up_down_market_performance.csv",
        "review/up_down_market_scatter.csv",
        "review/active_returns.csv",
        "review/active_return_contribution.csv",
        "review/rolling_returns_summary.csv",
    ]:
        assert (tmp_path / relative).is_file(), relative

    allocation_review = pd.read_csv(tmp_path / "review/target_allocations.csv")
    assert allocation_review.loc[
        (allocation_review["portfolio"] == "Growth 70/30") & (allocation_review["ticker"] == "A"),
        "target_weight_pct",
    ].iloc[0] == 70.0

    up_down = pd.read_csv(tmp_path / "review/up_down_market_performance.csv")
    assert {
        "above_benchmark_count", "below_benchmark_count", "total_count", "pct_above_benchmark",
        "above_active_return_pct", "below_active_return_pct", "overall_active_return_pct",
    }.issubset(up_down.columns)

    html = report_path.read_text(encoding="utf-8")
    for marker in [
        'id="allocation-matrix"',
        'id="portfolio-assets"',
        'id="portfolio-asset-performance"',
        'id="rolling-returns-summary"',
        'data-chart="annual-returns-chart"',
        'data-chart="annual-asset-returns-chart"',
        'id="correlations-heatmap"',
        'id="portfolio-return-decomposition"',
        'id="portfolio-risk-decomposition"',
        'data-chart="rolling-3y-annualized-return"',
        'data-chart="rolling-5y-annualized-return"',
        'data-chart="drawdown-combined"',
    ]:
        assert marker in html
    assert "drawdown-panel" not in html
    assert html.count("drawdown-episodes-panel") >= 3
    assert html.count("active-contribution-panel") == 2
    assert html.count("rolling-active-risk-panel") == 2
    assert html.count("up-down-panel") == 2
    assert "Active Return Contribution" in html
    assert "Occurrences" in html
    assert "Above Benchmark" in html
    assert "Below Benchmark" in html
    assert "Return vs. Benchmark" in html
    assert "Recovery By" in html
    assert "Underwater Period" in html
    assert "Growth 70/30" in html
    assert "Balanced 50/50" in html
    assert "Benchmark Market" in html
    assert "data-tooltip-json" in html
