from __future__ import annotations

import pandas as pd

from portfolio_optimizer_kr.viewer.backtest_renderer import (
    _active_returns_presentation,
    _allocation_matrix,
    _growth_svg,
    _metrics_matrix,
    _performance_summary,
    _trailing_returns_table,
)


PORTFOLIOS = ["Growth 70/30", "Balanced 50/50"]
BENCHMARK = "SPDR S&P 500 ETF Trust"


def test_allocation_and_performance_preserve_input_order_and_hide_storage_metadata():
    allocations = pd.DataFrame(
        [
            {"portfolio": "Balanced 50/50", "ticker": "QQQ", "name": "Invesco QQQ Trust", "target_weight_pct": 50.0},
            {"portfolio": "Balanced 50/50", "ticker": "GLD", "name": "SPDR Gold Shares", "target_weight_pct": 50.0},
            {"portfolio": "Growth 70/30", "ticker": "QQQ", "name": "Invesco QQQ Trust", "target_weight_pct": 70.0},
            {"portfolio": "Growth 70/30", "ticker": "GLD", "name": "SPDR Gold Shares", "target_weight_pct": 30.0},
        ]
    )
    performance = pd.DataFrame(
        [
            {"metric": "Start Balance", "unit": "balance", "Balanced 50/50": 10000, "Growth 70/30": 10000, "benchmark": 10000},
            {"metric": "CAGR", "unit": "pct", "Balanced 50/50": 12.3, "Growth 70/30": 15.4, "benchmark": 10.1},
        ]
    )
    benchmark = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "active_return_pct": 5.3, "tracking_error_pct": 7.1, "information_ratio": 0.74},
            {"portfolio": "Balanced 50/50", "active_return_pct": 2.2, "tracking_error_pct": 5.4, "information_ratio": 0.41},
        ]
    )

    allocation_html = _allocation_matrix(allocations, PORTFOLIOS)
    summary_html = _performance_summary(performance, benchmark, PORTFOLIOS, BENCHMARK)

    assert allocation_html.index("Growth 70/30") < allocation_html.index("Balanced 50/50")
    assert summary_html.index("Growth 70/30") < summary_html.index("Balanced 50/50") < summary_html.index(BENCHMARK)
    assert "<th>unit</th>" not in summary_html.lower()
    assert "$10,000" in summary_html
    assert "15.40%" in summary_html


def test_trailing_returns_and_metrics_use_human_labels_and_units():
    trailing = pd.DataFrame(
        [
            {
                "portfolio": "Growth 70/30",
                "3m_pct": 5.96,
                "1y_pct": 34.14,
                "3y_pct": 33.80,
                "5y_pct": 16.54,
                "10y_pct": None,
                "ytd_pct": 34.14,
                "full_period_pct": 20.40,
                "3y_annualized_volatility_pct": 11.38,
                "5y_annualized_volatility_pct": 14.62,
            },
            {
                "portfolio": "Balanced 50/50",
                "3m_pct": 7.74,
                "1y_pct": 42.65,
                "3y_pct": 33.85,
                "5y_pct": 17.10,
                "10y_pct": None,
                "ytd_pct": 42.65,
                "full_period_pct": 20.21,
                "3y_annualized_volatility_pct": 10.07,
                "5y_annualized_volatility_pct": 12.65,
            },
            {
                "portfolio": "benchmark",
                "3m_pct": 3.43,
                "1y_pct": 18.60,
                "3y_pct": 23.18,
                "5y_pct": 14.51,
                "10y_pct": None,
                "ytd_pct": 18.60,
                "full_period_pct": 15.13,
                "3y_annualized_volatility_pct": 11.93,
                "5y_annualized_volatility_pct": 15.13,
            },
        ]
    )
    metrics = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "metric": "beta", "value": 0.82},
            {"portfolio": "Balanced 50/50", "metric": "beta", "value": 0.63},
            {"portfolio": "Growth 70/30", "metric": "alpha", "value": 0.0713},
            {"portfolio": "Balanced 50/50", "metric": "alpha", "value": 0.0962},
            {"portfolio": "Growth 70/30", "metric": "historical_var_95", "value": 0.0597},
            {"portfolio": "Balanced 50/50", "metric": "historical_var_95", "value": 0.0508},
        ]
    )

    trailing_html = _trailing_returns_table(trailing, PORTFOLIOS, BENCHMARK)
    metrics_html = _metrics_matrix(metrics, PORTFOLIOS, BENCHMARK)

    for label in ["Portfolio", "3 Month", "YTD", "1 Year", "3 Year Annualized Return", "Full Period CAGR"]:
        assert label in trailing_html
    assert "3m_pct" not in trailing_html
    assert "_pct" not in trailing_html
    assert "34.14%" in trailing_html
    assert BENCHMARK in trailing_html

    assert "Metric" in metrics_html
    assert "Beta" in metrics_html
    assert "Alpha" in metrics_html
    assert "Historical VaR 95" in metrics_html
    assert "<th>portfolio</th>" not in metrics_html.lower()
    assert "<th>value</th>" not in metrics_html.lower()
    assert "7.13%" in metrics_html


def test_growth_chart_uses_calendar_anchors_and_human_benchmark_identity():
    dates = pd.date_range("2020-01-31", "2022-12-31", freq="ME")
    growth = pd.DataFrame(
        {
            "date": dates,
            "Growth 70/30_balance": [10000 + index * 250 for index in range(len(dates))],
            "Balanced 50/50_balance": [10000 + index * 200 for index in range(len(dates))],
            "benchmark_balance": [10000 + index * 150 for index in range(len(dates))],
        }
    )

    chart = _growth_svg(
        growth,
        PORTFOLIOS,
        {"benchmark": BENCHMARK},
    )

    assert "Jan 2020" in chart
    assert "Jul 2020" in chart
    assert "Jan 2021" in chart
    assert "Jun 2020" not in chart
    assert BENCHMARK in chart
    assert ">benchmark<" not in chart


def test_active_returns_primary_presentation_does_not_dump_monthly_storage_schema():
    active_returns = pd.DataFrame(
        [
            {
                "portfolio": "Growth 70/30",
                "date": "2024-01-31",
                "portfolio_return": 0.02,
                "benchmark_return": 0.01,
                "active_return": 0.01,
                "cumulative_active_return": 0.01,
                "annual_active_return": 0.12,
                "rolling_active_return": None,
                "rolling_tracking_error_pct": None,
            },
            {
                "portfolio": "Growth 70/30",
                "date": "2024-12-31",
                "portfolio_return": 0.03,
                "benchmark_return": 0.02,
                "active_return": 0.01,
                "cumulative_active_return": 0.13,
                "annual_active_return": 0.12,
                "rolling_active_return": None,
                "rolling_tracking_error_pct": None,
            },
        ]
    )
    active_contribution = pd.DataFrame(
        [
            {"date": "2024-12-31", "portfolio": "Growth 70/30", "ticker": "QQQ", "cumulative_active_contribution_pct": 9.2},
            {"date": "2024-12-31", "portfolio": "Growth 70/30", "ticker": "GLD", "cumulative_active_contribution_pct": 3.8},
        ]
    )
    benchmark = pd.DataFrame(
        [{"portfolio": "Growth 70/30", "active_return_pct": 5.3, "tracking_error_pct": 7.1, "information_ratio": 0.74}]
    )
    up_down = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "market_type": "up", "portfolio_return": 0.04, "benchmark_return": 0.03, "active_return": 0.01, "occurrences": 8},
            {"portfolio": "Growth 70/30", "market_type": "down", "portfolio_return": -0.02, "benchmark_return": -0.03, "active_return": 0.01, "occurrences": 4},
        ]
    )

    rendered = _active_returns_presentation(
        active_returns,
        active_contribution,
        benchmark,
        up_down,
        PORTFOLIOS,
        BENCHMARK,
    )

    assert "Benchmark Summary" in rendered
    assert "Annual Active Return" in rendered
    assert "Active Return Contribution" in rendered
    assert "Up / Down Market Performance" in rendered
    for storage_name in [
        "portfolio_return",
        "benchmark_return",
        "active_return",
        "rolling_tracking_error_pct",
        "cumulative_active_contribution_pct",
    ]:
        assert storage_name not in rendered
