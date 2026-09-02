from __future__ import annotations

import html

import pandas as pd

from portfolio_optimizer_kr.viewer.backtest_renderer import (
    _active_returns_presentation,
    _annual_asset_returns_chart,
    _annual_returns_chart,
    _asset_performance_from_monthly_returns,
    _asset_performance_table,
    _calendar_ticks,
    _correlations_table,
    _drawdown_presentation,
    _rolling_returns_chart,
)


PORTFOLIOS = ["Growth 70/30", "Balanced 50/50"]
BENCHMARK = "SPDR S&P 500 ETF Trust"


def test_calendar_ticks_deduplicate_initial_anchor_and_same_month_end():
    dates = pd.Series(
        pd.to_datetime(
            ["2020-01-01", "2020-01-31", "2020-02-29", "2020-07-31", "2021-01-31"]
        )
    )
    ticks = _calendar_ticks(dates)
    month_keys = [(tick.year, tick.month) for tick in ticks]
    assert month_keys.count((2020, 1)) == 1
    assert len(month_keys) == len(set(month_keys))
    assert (2020, 7) in month_keys


def test_annual_returns_is_chart_and_grouped_year_tooltip():
    annual = pd.DataFrame(
        [
            {
                "year": 2024,
                "Growth 70/30_return_pct": 12.0,
                "Balanced 50/50_return_pct": 8.0,
                "benchmark_return_pct": 10.0,
            },
            {
                "year": 2025,
                "Growth 70/30_return_pct": 14.0,
                "Balanced 50/50_return_pct": 9.0,
                "benchmark_return_pct": 11.0,
            },
        ]
    )
    rendered = _annual_returns_chart(annual, PORTFOLIOS, BENCHMARK)
    assert 'data-chart="annual-returns-chart"' in rendered
    assert 'class="chart-mark grouped-bar"' in rendered
    assert (
        "2024 | Growth 70/30: 12.00% | Balanced 50/50: 8.00% | "
        "SPDR S&amp;P 500 ETF Trust: 10.00%"
    ) in rendered


def test_drawdowns_are_separate_portfolio_panels_with_series_charts():
    series = pd.DataFrame(
        [
            {
                "date": "2024-01-31",
                "Growth 70/30_drawdown_pct": -2.0,
                "Balanced 50/50_drawdown_pct": -1.0,
                "benchmark_drawdown_pct": -3.0,
            },
            {
                "date": "2024-02-29",
                "Growth 70/30_drawdown_pct": -4.0,
                "Balanced 50/50_drawdown_pct": -2.0,
                "benchmark_drawdown_pct": -5.0,
            },
        ]
    )
    episodes = pd.DataFrame(
        [
            {
                "portfolio": "Growth 70/30",
                "rank": 1,
                "start": "2024-01-31",
                "bottom": "2024-02-29",
                "recovery": None,
                "max_drawdown_pct": -4.0,
                "duration_months": 2,
            },
            {
                "portfolio": "Balanced 50/50",
                "rank": 1,
                "start": "2024-01-31",
                "bottom": "2024-02-29",
                "recovery": None,
                "max_drawdown_pct": -2.0,
                "duration_months": 2,
            },
            {
                "portfolio": "benchmark",
                "rank": 1,
                "start": "2024-01-31",
                "bottom": "2024-02-29",
                "recovery": None,
                "max_drawdown_pct": -5.0,
                "duration_months": 2,
            },
        ]
    )
    rendered = _drawdown_presentation(series, episodes, PORTFOLIOS, BENCHMARK)
    assert rendered.count("drawdown-panel") == 3
    assert 'data-chart="drawdown-Growth 70/30"' in rendered
    assert 'data-chart="drawdown-Balanced 50/50"' in rendered
    assert 'data-chart="drawdown-benchmark"' in rendered
    assert rendered.count("Drawdown Episodes") == 3


def test_annual_asset_returns_preserve_ticker_series_and_grouped_tooltip():
    annual_assets = pd.DataFrame(
        [
            {"year": 2025, "ticker": "QQQ", "return": 0.20},
            {"year": 2025, "ticker": "GLD", "return": 0.10},
        ]
    )
    rendered = _annual_asset_returns_chart(
        annual_assets,
        {"QQQ": "Invesco QQQ Trust", "GLD": "SPDR Gold Shares"},
    )
    assert 'data-chart="annual-asset-returns-chart"' in rendered
    assert "Invesco QQQ Trust (QQQ)" in rendered
    assert "SPDR Gold Shares (GLD)" in rendered
    assert (
        "2025 | Invesco QQQ Trust (QQQ): 20.00% | "
        "SPDR Gold Shares (GLD): 10.00%"
    ) in rendered


def test_active_return_section_contains_all_canonical_historical_views():
    dates = pd.date_range("2021-01-31", periods=40, freq="ME")
    active_rows = []
    contrib_rows = []
    for portfolio, scale in [(PORTFOLIOS[0], 1.0), (PORTFOLIOS[1], 0.7)]:
        for index, date in enumerate(dates):
            benchmark_return = -0.03 + (index % 8) * 0.01
            portfolio_return = benchmark_return + (
                0.004 * scale if index % 3 else -0.002 * scale
            )
            active_rows.append(
                {
                    "portfolio": portfolio,
                    "date": date,
                    "portfolio_return": portfolio_return,
                    "benchmark_return": benchmark_return,
                    "active_return": portfolio_return - benchmark_return,
                    "annual_active_return": 0.06 * scale,
                    "rolling_active_return": 0.04 * scale if index >= 35 else None,
                    "rolling_tracking_error_pct": 5.0 * scale if index >= 35 else None,
                }
            )
            for ticker, contribution in [("QQQ", 0.06 * scale), ("GLD", 0.02 * scale)]:
                contrib_rows.append(
                    {
                        "date": date,
                        "portfolio": portfolio,
                        "ticker": ticker,
                        "cumulative_active_contribution_pct": contribution * (index + 1),
                    }
                )
    benchmark = pd.DataFrame(
        [
            {
                "portfolio": PORTFOLIOS[0],
                "active_return_pct": 5.0,
                "tracking_error_pct": 6.0,
                "information_ratio": 0.8,
            },
            {
                "portfolio": PORTFOLIOS[1],
                "active_return_pct": 3.0,
                "tracking_error_pct": 4.0,
                "information_ratio": 0.7,
            },
        ]
    )
    rendered = _active_returns_presentation(
        pd.DataFrame(active_rows),
        pd.DataFrame(contrib_rows),
        benchmark,
        pd.DataFrame(),
        PORTFOLIOS,
        BENCHMARK,
        {"QQQ": "Invesco QQQ Trust", "GLD": "SPDR Gold Shares"},
    )
    assert 'data-chart="annual-active-return-chart"' in rendered
    assert rendered.count("active-contribution-panel") == 2
    assert rendered.count("rolling-active-risk-panel") == 2
    assert "Active Return %" in rendered
    assert "Tracking Error %" in rendered
    assert rendered.count("up-down-panel") == 2
    for header in [
        "Above Benchmark Count",
        "Below Benchmark Count",
        "% Above Benchmark",
        "Average Active Return Above",
        "Average Active Return Below",
        "Average Active Return Total",
        "Return vs. Benchmark",
    ]:
        assert header in rendered


def test_asset_performance_is_persistable_server_side_finance_output_with_required_columns():
    dates = pd.date_range("2020-01-31", periods=72, freq="ME")
    monthly = pd.DataFrame(
        {
            "date": dates,
            "asset_QQQ": [0.01] * 72,
            "asset_069500": [0.005] * 72,
        }
    )
    configuration = {
        "assets": [
            {"symbol": "QQQ", "name": "Invesco QQQ Trust"},
            {"symbol": "069500", "name": "KODEX 200"},
        ],
        "risk_free": {"effective_annual_rate": 0.0},
    }
    frame = _asset_performance_from_monthly_returns(monthly, configuration)
    assert list(frame["ticker"]) == ["QQQ", "069500"]
    assert frame.loc[0, "name"] == "Invesco QQQ Trust"
    for column in [
        "cagr_pct",
        "annualized_return_pct",
        "annualized_volatility_pct",
        "best_year_pct",
        "worst_year_pct",
        "max_drawdown_pct",
        "sharpe_ratio",
        "sortino_ratio",
        "3m_pct",
        "ytd_pct",
        "1y_pct",
        "3y_pct",
        "5y_pct",
        "10y_pct",
    ]:
        assert column in frame.columns
    rendered = _asset_performance_table(frame)
    for label in [
        "Ticker",
        "Name",
        "CAGR",
        "Annualized Return",
        "Standard Deviation",
        "Maximum Drawdown",
        "Sharpe Ratio",
        "Sortino Ratio",
        "3M",
        "YTD",
        "1Y",
        "3Y Annualized",
        "5Y Annualized",
        "10Y Annualized",
    ]:
        assert label in rendered
    assert "069500" in rendered
    assert "69500.0" not in rendered


def test_correlations_are_numeric_readable_heatmap_not_plain_matrix_only():
    correlations = pd.DataFrame(
        [
            {"series": "QQQ", "QQQ": 1.0, "benchmark": 0.9181795019152512},
            {
                "series": "benchmark",
                "QQQ": 0.9181795019152512,
                "benchmark": 1.0,
            },
        ]
    )
    rendered = _correlations_table(correlations, BENCHMARK)
    assert 'id="correlations-heatmap"' in rendered
    assert rendered.count('class="heatmap-cell"') == 4
    assert "0.92" in rendered
    assert "0.9181795019152512" not in rendered
    assert html.escape(BENCHMARK) in rendered


def test_rolling_returns_render_historical_chart_not_table_only():
    frame = pd.DataFrame(
        [
            {
                "date": "2024-01-31",
                "Growth 70/30_annualized_return_pct": 10.0,
                "Balanced 50/50_annualized_return_pct": 8.0,
                "benchmark_annualized_return_pct": 7.0,
            },
            {
                "date": "2024-07-31",
                "Growth 70/30_annualized_return_pct": 11.0,
                "Balanced 50/50_annualized_return_pct": 9.0,
                "benchmark_annualized_return_pct": 8.0,
            },
        ]
    )
    rendered = _rolling_returns_chart(frame, PORTFOLIOS, BENCHMARK, 3)
    assert 'data-chart="rolling-3y-annualized-return"' in rendered
    assert "Growth 70/30" in rendered
    assert html.escape(BENCHMARK) in rendered
    assert "Month / Year" in rendered
    assert "Annualized Return %" in rendered
