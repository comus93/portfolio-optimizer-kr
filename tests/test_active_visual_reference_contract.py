from __future__ import annotations

import pandas as pd

from portfolio_optimizer_kr.viewer import historical_active_components as active


PORTFOLIO = "Growth 70/30"


def test_annual_active_return_exposes_readable_y_scale():
    frame = pd.DataFrame(
        [
            {"portfolio": PORTFOLIO, "date": "2024-12-31", "annual_active_return_pct": 4.0},
            {"portfolio": PORTFOLIO, "date": "2025-12-31", "annual_active_return_pct": -2.0},
        ]
    )
    rendered = active.annual_active_return(frame, [PORTFOLIO])
    assert 'data-chart="annual-active-return-chart"' in rendered
    assert 'data-axis="y-left"' in rendered
    assert 'class="axis y-axis-line"' in rendered
    assert 'y-axis-label' in rendered
    assert 'class="chart-mark grouped-bar"' in rendered


def test_active_contribution_is_time_bar_chart_with_y_scale_not_line_chart():
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
    assert 'class="chart-mark active-contribution-bar"' in rendered
    assert 'data-axis="y-left"' in rendered
    assert 'y-axis-label' in rendered
    assert '<polyline' not in rendered


def test_rolling_active_risk_has_both_visible_y_scales():
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
    assert 'class="chart-mark active-return-bar"' in rendered
    assert 'class="tracking-error-line"' in rendered


def test_return_vs_benchmark_keeps_y_scale_and_paired_bars():
    observations = pd.DataFrame(
        [
            {"portfolio": PORTFOLIO, "benchmark_return_pct": -3.0, "portfolio_return_pct": -2.0},
            {"portfolio": PORTFOLIO, "benchmark_return_pct": -1.0, "portfolio_return_pct": -1.5},
            {"portfolio": PORTFOLIO, "benchmark_return_pct": 1.0, "portfolio_return_pct": 2.0},
            {"portfolio": PORTFOLIO, "benchmark_return_pct": 3.0, "portfolio_return_pct": 2.5},
        ]
    )
    rendered = active.up_down_paired_chart(observations, PORTFOLIO)
    assert f'data-chart="return-vs-benchmark-{PORTFOLIO}"' in rendered
    assert 'data-axis="y-left"' in rendered
    assert 'y-axis-label' in rendered
    assert rendered.count('class="chart-mark grouped-bar"') >= 2
    assert "Benchmark Return" in rendered
