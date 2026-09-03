from __future__ import annotations

import html

import pandas as pd

from portfolio_optimizer_kr.analytics import historical
from portfolio_optimizer_kr.viewer.backtest_renderer import (
    _active_returns_presentation,
    _annual_asset_returns_chart,
    _annual_returns_chart,
    _calendar_ticks,
    _correlations_table,
    _drawdown_presentation,
    _portfolio_asset_trailing_table,
    _portfolio_assets_table,
    _rolling_returns_chart,
)


PORTFOLIOS = ["Growth 70/30", "Balanced 50/50"]
BENCHMARK = "SPDR S&P 500 ETF Trust"


def test_calendar_ticks_deduplicate_initial_anchor_and_same_month_end():
    dates = pd.Series(pd.to_datetime(["2020-01-01", "2020-01-31", "2020-02-29", "2020-07-31", "2021-01-31"]))
    ticks = _calendar_ticks(dates)
    month_keys = [(tick.year, tick.month) for tick in ticks]
    assert month_keys.count((2020, 1)) == 1
    assert len(month_keys) == len(set(month_keys))
    assert (2020, 7) in month_keys


def test_annual_returns_is_grouped_chart_with_year_shared_hover():
    annual = pd.DataFrame(
        [
            {"year": 2024, "Growth 70/30_return_pct": 12.0, "Balanced 50/50_return_pct": 8.0, "benchmark_return_pct": 10.0},
            {"year": 2025, "Growth 70/30_return_pct": 14.0, "Balanced 50/50_return_pct": 9.0, "benchmark_return_pct": 11.0},
        ]
    )
    rendered = _annual_returns_chart(annual, PORTFOLIOS, BENCHMARK)
    assert 'data-chart="annual-returns-chart"' in rendered
    assert 'class="chart-mark shared-hover-zone grouped-hover-zone"' in rendered
    assert 'data-tooltip-json=' in rendered
    assert "2024" in rendered
    assert "Growth 70/30" in rendered
    assert "Balanced 50/50" in rendered
    assert html.escape(BENCHMARK) in rendered


def test_drawdowns_have_axes_calendar_ticks_and_recovery_episode_fields():
    series = pd.DataFrame(
        [
            {"date": "2024-01-31", "Growth 70/30_drawdown_pct": -2.0, "Balanced 50/50_drawdown_pct": -1.0, "benchmark_drawdown_pct": -3.0},
            {"date": "2024-02-29", "Growth 70/30_drawdown_pct": -4.0, "Balanced 50/50_drawdown_pct": -2.0, "benchmark_drawdown_pct": -5.0},
            {"date": "2024-03-31", "Growth 70/30_drawdown_pct": 0.0, "Balanced 50/50_drawdown_pct": 0.0, "benchmark_drawdown_pct": -1.0},
        ]
    )
    episodes = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "rank": 1, "start": "2024-01-31", "bottom": "2024-02-29", "recovery": "2024-03-31", "maximum_drawdown_pct": -4.0},
            {"portfolio": "Balanced 50/50", "rank": 1, "start": "2024-01-31", "bottom": "2024-02-29", "recovery": "2024-03-31", "maximum_drawdown_pct": -2.0},
            {"portfolio": "benchmark", "rank": 1, "start": "2024-01-31", "bottom": "2024-02-29", "recovery": None, "maximum_drawdown_pct": -5.0},
        ]
    )
    rendered = _drawdown_presentation(series, episodes, PORTFOLIOS, BENCHMARK)
    assert rendered.count("drawdown-panel") == 3
    assert 'data-chart="drawdown-Growth 70/30"' in rendered
    assert "Drawdown %" in rendered
    assert "Month / Year" in rendered
    assert "drawdown-hover-zone" in rendered
    for header in ["Start", "End", "Length", "Recovery By", "Recovery Time", "Underwater Period", "Drawdown"]:
        assert header in rendered
    assert "Mar 2024" in rendered
    assert "Worst 10 drawdowns" in rendered


def test_annual_asset_returns_preserve_ticker_series_and_shared_year_hover():
    annual_assets = pd.DataFrame(
        [
            {"year": 2025, "ticker": "QQQ", "return": 0.20},
            {"year": 2025, "ticker": "GLD", "return": 0.10},
        ]
    )
    rendered = _annual_asset_returns_chart(annual_assets, {"QQQ": "Invesco QQQ Trust", "GLD": "SPDR Gold Shares"})
    assert 'data-chart="annual-asset-returns-chart"' in rendered
    assert "Invesco QQQ Trust (QQQ)" in rendered
    assert "SPDR Gold Shares (GLD)" in rendered
    assert 'class="chart-mark shared-hover-zone grouped-hover-zone"' in rendered
    assert 'data-tooltip-json=' in rendered


def test_active_return_section_contains_all_accepted_views():
    dates = pd.date_range("2021-01-31", periods=40, freq="ME")
    active_rows = []
    contrib_rows = []
    observations = []
    up_down_rows = []
    for portfolio, scale in [(PORTFOLIOS[0], 1.0), (PORTFOLIOS[1], 0.7)]:
        for index, date in enumerate(dates):
            benchmark_return = -0.03 + (index % 8) * 0.01
            portfolio_return = benchmark_return + (0.004 * scale if index % 3 else -0.002 * scale)
            active_rows.append(
                {
                    "portfolio": portfolio,
                    "date": date,
                    "annual_active_return": 0.06 * scale,
                    "rolling_active_return_pct": 4.0 * scale if index >= 35 else None,
                    "rolling_tracking_error_pct": 5.0 * scale if index >= 35 else None,
                }
            )
            observations.append(
                {"date": date, "portfolio": portfolio, "benchmark_return_pct": benchmark_return * 100, "portfolio_return_pct": portfolio_return * 100}
            )
            for ticker, contribution in [("QQQ", 0.06 * scale), ("GLD", -0.02 * scale)]:
                contrib_rows.append(
                    {"date": date, "portfolio": portfolio, "ticker": ticker, "cumulative_active_contribution_pct": contribution * (index + 1)}
                )
        for market_type in ["up", "down"]:
            up_down_rows.append(
                {
                    "portfolio": portfolio,
                    "market_type": market_type,
                    "above_benchmark_count": 10,
                    "below_benchmark_count": 5,
                    "total_count": 15,
                    "pct_above_benchmark": 66.67,
                    "above_active_return_pct": 1.2 * scale,
                    "below_active_return_pct": -0.8 * scale,
                    "overall_active_return_pct": 0.4 * scale,
                }
            )
    benchmark = pd.DataFrame(
        [
            {"portfolio": PORTFOLIOS[0], "active_return_pct": 5.0, "tracking_error_pct": 6.0, "information_ratio": 0.8},
            {"portfolio": PORTFOLIOS[1], "active_return_pct": 3.0, "tracking_error_pct": 4.0, "information_ratio": 0.7},
        ]
    )
    rendered = _active_returns_presentation(
        pd.DataFrame(active_rows),
        pd.DataFrame(contrib_rows),
        benchmark,
        pd.DataFrame(up_down_rows),
        PORTFOLIOS,
        BENCHMARK,
        {"QQQ": "Invesco QQQ Trust", "GLD": "SPDR Gold Shares"},
        pd.DataFrame(observations),
    )
    assert 'data-chart="annual-active-return-chart"' in rendered
    assert rendered.count("active-contribution-panel") == 2
    assert rendered.count("rolling-active-risk-panel") == 2
    assert rendered.count("up-down-panel") == 2
    assert "Cumulative Active Return" in rendered
    assert "Occurrences" in rendered
    assert "Average Active Return" in rendered
    assert "Above Benchmark" in rendered
    assert "Below Benchmark" in rendered
    assert "Return vs. Benchmark" in rendered
    assert "active-contribution-hover-zone" in rendered
    assert "rolling-active-hover-zone" in rendered


def test_asset_performance_is_shared_finance_output_and_split_for_presentation():
    monthly = pd.DataFrame(
        {"QQQ": [0.01] * 72, "069500": [0.005] * 72},
        index=pd.date_range("2020-01-31", periods=72, freq="ME"),
    )
    canonical = historical.asset_performance_table(
        monthly,
        annual_rf=0.0,
        asset_names={"QQQ": "Invesco QQQ Trust", "069500": "KODEX 200"},
    )
    assert list(canonical["ticker"]) == ["QQQ", "069500"]
    for column in [
        "cagr", "annualized_return", "annualized_volatility", "best_year", "worst_year",
        "max_drawdown", "sharpe_ratio", "sortino_ratio", "3m", "ytd", "1y", "3y", "5y", "10y",
    ]:
        assert column in canonical.columns

    assets = _portfolio_assets_table(canonical)
    trailing = _portfolio_asset_trailing_table(canonical)
    assert 'id="portfolio-assets"' in assets
    for label in ["Ticker", "Name", "CAGR", "Stdev", "Best Year", "Worst Year", "Max Drawdown", "Sharpe Ratio", "Sortino Ratio"]:
        assert label in assets
    assert 'id="portfolio-asset-performance"' in trailing
    for label in ["Total Return", "Annualized Return", "3 Month", "Year To Date", "1 Year", "3 Year", "5 Year"]:
        assert label in trailing
    assert "069500" in assets
    assert "69500.0" not in assets


def test_asset_renderer_accepts_mixed_persisted_fraction_and_percent_columns():
    frame = pd.DataFrame(
        [{
            "ticker": "069500", "name": "KODEX 200", "cagr_pct": 12.5,
            "annualized_volatility_pct": 15.0, "best_year": 0.2, "worst_year": -0.1,
            "max_drawdown_pct": -18.0, "sharpe_ratio": 0.8, "sortino_ratio": 1.1,
            "3m": 0.02, "ytd": 0.05, "1y": 0.07, "3y": 0.08, "5y": None,
        }]
    )
    assets = _portfolio_assets_table(frame)
    trailing = _portfolio_asset_trailing_table(frame)
    assert "20.00%" in assets
    assert "2.00%" in trailing
    assert "069500" in assets
    assert "69500.0" not in assets


def test_correlations_are_readable_monthly_heatmap():
    correlations = pd.DataFrame(
        [
            {"series": "QQQ", "QQQ": 1.0, "benchmark": 0.9181795019152512},
            {"series": "benchmark", "QQQ": 0.9181795019152512, "benchmark": 1.0},
        ]
    )
    rendered = _correlations_table(correlations, BENCHMARK)
    assert 'id="correlations-heatmap"' in rendered
    assert 'class="heatmap-cell"' in rendered
    assert "0.92" in rendered
    assert "0.9181795019152512" not in rendered
    assert html.escape(BENCHMARK) in rendered


def test_rolling_returns_render_shared_hover_line_chart():
    frame = pd.DataFrame(
        [
            {"date": "2024-01-31", "Growth 70/30_annualized_return_pct": 10.0, "Balanced 50/50_annualized_return_pct": 8.0, "benchmark_annualized_return_pct": 7.0},
            {"date": "2024-07-31", "Growth 70/30_annualized_return_pct": 11.0, "Balanced 50/50_annualized_return_pct": 9.0, "benchmark_annualized_return_pct": 8.0},
        ]
    )
    rendered = _rolling_returns_chart(frame, PORTFOLIOS, BENCHMARK, 3)
    assert 'data-chart="rolling-3y-annualized-return"' in rendered
    assert "Growth 70/30" in rendered
    assert html.escape(BENCHMARK) in rendered
    assert "Month / Year" in rendered
    assert "Annualized Return %" in rendered
    assert "line-hover-zone" in rendered
    assert "data-tooltip-json=" in rendered
