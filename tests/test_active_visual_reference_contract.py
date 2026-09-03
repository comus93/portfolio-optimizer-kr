from __future__ import annotations

import pandas as pd

from portfolio_optimizer_kr.viewer import historical_active_components as active


PORTFOLIO = "Growth 70/30"


def test_annual_active_return_has_readable_axis_and_shared_year_hover():
    frame = pd.DataFrame(
        [
            {"portfolio": PORTFOLIO, "date": "2024-12-31", "annual_active_return_pct": 4.0},
            {"portfolio": PORTFOLIO, "date": "2025-12-31", "annual_active_return_pct": -2.0},
        ]
    )
    rendered = active.annual_active_return(frame, [PORTFOLIO])
    assert 'data-chart="annual-active-return-chart"' in rendered
    assert 'class="axis y-axis-line"' in rendered
    assert 'y-tick-label' in rendered
    assert 'class="chart-mark shared-hover-zone grouped-hover-zone"' in rendered
    assert 'data-tooltip-json=' in rendered
    assert "Active Return %" in rendered


def test_active_contribution_is_portfolio_stacked_bar_with_axis_and_shared_month_hover():
    dates = pd.date_range("2024-01-31", periods=6, freq="ME")
    rows = []
    for index, date in enumerate(dates, start=1):
        rows.extend(
            [
                {
                    "date": date,
                    "portfolio": PORTFOLIO,
                    "ticker": "QQQ",
                    "cumulative_active_contribution_pct": index * 1.2,
                },
                {
                    "date": date,
                    "portfolio": PORTFOLIO,
                    "ticker": "GLD",
                    "cumulative_active_contribution_pct": index * -0.4,
                },
            ]
        )
    rendered = active.active_contribution(
        pd.DataFrame(rows),
        [PORTFOLIO],
        {"QQQ": "Invesco QQQ Trust", "GLD": "SPDR Gold Shares"},
    )
    assert 'class="analysis-chart active-contribution-chart"' in rendered
    assert 'class="active-contribution-bar stacked-bar"' in rendered
    assert 'class="axis y-axis-line"' in rendered
    assert 'y-axis-label' in rendered
    assert 'active-contribution-hover-zone' in rendered
    assert 'data-tooltip-json=' in rendered
    assert "1 Year" in rendered and "3 Year" in rendered and "5 Year" in rendered
    assert '<polyline' not in rendered


def test_rolling_active_risk_has_dual_scales_bar_line_and_shared_month_hover():
    dates = pd.date_range("2024-01-31", periods=4, freq="ME")
    frame = pd.DataFrame(
        {
            "portfolio": [PORTFOLIO] * len(dates),
            "date": dates,
            "rolling_active_return_pct": [-2.0, 1.0, 3.0, 2.0],
            "rolling_tracking_error_pct": [4.0, 4.5, 5.0, 5.5],
        }
    )
    rendered = active.rolling_active_risk_panel(frame, PORTFOLIO, "SPY")
    assert 'data-axis="y-left"' in rendered
    assert 'data-axis="y-right"' in rendered
    assert 'left-axis-label' in rendered
    assert 'right-axis-label' in rendered
    assert rendered.count('class="axis y-axis-line"') == 2
    assert 'class="active-return-bar"' in rendered
    assert 'class="tracking-error-line"' in rendered
    assert 'rolling-active-hover-zone' in rendered
    assert 'data-tooltip-json=' in rendered


def test_up_down_table_has_group_headers_total_and_paired_chart_shared_hover():
    up_down = pd.DataFrame(
        [
            {
                "portfolio": PORTFOLIO,
                "market_type": "up",
                "above_benchmark_count": 8,
                "below_benchmark_count": 4,
                "total_count": 12,
                "pct_above_benchmark": 66.67,
                "above_active_return_pct": 1.2,
                "below_active_return_pct": -0.8,
                "overall_active_return_pct": 0.5,
            },
            {
                "portfolio": PORTFOLIO,
                "market_type": "down",
                "above_benchmark_count": 5,
                "below_benchmark_count": 3,
                "total_count": 8,
                "pct_above_benchmark": 62.5,
                "above_active_return_pct": 2.0,
                "below_active_return_pct": -0.5,
                "overall_active_return_pct": 1.1,
            },
        ]
    )
    table = active.up_down_statistics_table(up_down, PORTFOLIO)
    assert "Occurrences" in table
    assert "Average Active Return" in table
    assert "Above Benchmark" in table
    assert "Below Benchmark" in table
    assert "Total" in table
    assert ">Total</td>" in table

    observations = pd.DataFrame(
        [
            {"portfolio": PORTFOLIO, "benchmark_return_pct": -3.0, "portfolio_return_pct": -2.0},
            {"portfolio": PORTFOLIO, "benchmark_return_pct": -1.0, "portfolio_return_pct": -1.5},
            {"portfolio": PORTFOLIO, "benchmark_return_pct": 1.0, "portfolio_return_pct": 2.0},
            {"portfolio": PORTFOLIO, "benchmark_return_pct": 3.0, "portfolio_return_pct": 2.5},
        ]
    )
    rendered = active.up_down_paired_chart(observations, PORTFOLIO, "S&P 500")
    assert f'data-chart="return-vs-benchmark-{PORTFOLIO}"' in rendered
    assert 'class="axis y-axis-line"' in rendered
    assert 'y-tick-label' in rendered
    assert 'class="chart-mark shared-hover-zone grouped-hover-zone"' in rendered
    assert "Benchmark Return" in rendered
    assert "S&amp;P 500" in rendered
