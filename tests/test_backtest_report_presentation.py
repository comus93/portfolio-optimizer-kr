from __future__ import annotations

import html

import pandas as pd

from portfolio_optimizer_kr.viewer.backtest_renderer import (
    _active_returns_presentation,
    _allocation_matrix,
    _annual_asset_returns_table,
    _correlations_table,
    _decomposition_table,
    _display_option,
    _growth_svg,
    _metrics_matrix,
    _money,
    _performance_summary,
    _portfolio_asset_trailing_table,
    _portfolio_assets_table,
    _trailing_returns_table,
)


PORTFOLIOS = ["Growth 70/30", "Balanced 50/50"]
BENCHMARK = "SPDR S&P 500 ETF Trust"
BENCHMARK_HTML = html.escape(BENCHMARK)


def test_renderer_prefers_explicit_portfolio_order_over_sorted_definition_keys():
    from portfolio_optimizer_kr.viewer.backtest_renderer import _result_portfolio_order

    assert _result_portfolio_order(
        {
            "portfolio_order": PORTFOLIOS,
            "portfolio_definitions": {"Balanced 50/50": {}, "Growth 70/30": {}},
        }
    ) == PORTFOLIOS


def test_allocation_uses_union_assets_preserves_order_and_mutes_non_holdings():
    allocations = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "ticker": "QQQ", "name": "Invesco QQQ Trust", "target_weight_pct": 70.0},
            {"portfolio": "Growth 70/30", "ticker": "GLD", "name": "SPDR Gold Shares", "target_weight_pct": 30.0},
            {"portfolio": "Growth 70/30", "ticker": "TLT", "name": "iShares 20+ Year Treasury", "target_weight_pct": 0.0},
            {"portfolio": "Balanced 50/50", "ticker": "QQQ", "name": "Invesco QQQ Trust", "target_weight_pct": 0.0},
            {"portfolio": "Balanced 50/50", "ticker": "GLD", "name": "SPDR Gold Shares", "target_weight_pct": 50.0},
            {"portfolio": "Balanced 50/50", "ticker": "TLT", "name": "iShares 20+ Year Treasury", "target_weight_pct": 50.0},
        ]
    )
    rendered = _allocation_matrix(allocations, PORTFOLIOS)
    assert rendered.index("Growth 70/30") < rendered.index("Balanced 50/50")
    assert rendered.count("Invesco QQQ Trust (QQQ)") == 1
    assert rendered.count("SPDR Gold Shares (GLD)") == 1
    assert rendered.count("iShares 20+ Year Treasury (TLT)") == 1
    assert "70.00%" in rendered and "50.00%" in rendered
    assert "—" in rendered


def test_performance_summary_preserves_human_units_and_benchmark_identity():
    performance = pd.DataFrame(
        [
            {"metric": "Start Balance", "unit": "balance", "Growth 70/30": 10000, "Balanced 50/50": 10000, "benchmark": 10000},
            {"metric": "CAGR", "unit": "pct", "Growth 70/30": 15.4, "Balanced 50/50": 12.3, "benchmark": 10.1},
        ]
    )
    benchmark = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "active_return_pct": 5.3, "tracking_error_pct": 7.1, "information_ratio": 0.74},
            {"portfolio": "Balanced 50/50", "active_return_pct": 2.2, "tracking_error_pct": 5.4, "information_ratio": 0.41},
        ]
    )
    summary = _performance_summary(performance, benchmark, PORTFOLIOS, BENCHMARK)
    assert summary.index("Growth 70/30") < summary.index("Balanced 50/50") < summary.index(BENCHMARK_HTML)
    assert "<th>unit</th>" not in summary.lower()
    assert "$10,000" in summary
    assert "15.40%" in summary


def test_trailing_returns_use_pv_grouped_headers():
    trailing = pd.DataFrame(
        [
            {
                "portfolio": "Growth 70/30", "3m_pct": 5.96, "1y_pct": 34.14,
                "3y_pct": 33.80, "5y_pct": 16.54, "ytd_pct": 34.14,
                "full_period_pct": 20.40, "3y_annualized_volatility_pct": 11.38,
                "5y_annualized_volatility_pct": 14.62,
            },
            {
                "portfolio": "Balanced 50/50", "3m_pct": 7.74, "1y_pct": 42.65,
                "3y_pct": 33.85, "5y_pct": 17.10, "ytd_pct": 42.65,
                "full_period_pct": 20.21, "3y_annualized_volatility_pct": 10.07,
                "5y_annualized_volatility_pct": 12.65,
            },
            {
                "portfolio": "benchmark", "3m_pct": 3.43, "1y_pct": 18.60,
                "3y_pct": 23.18, "5y_pct": 14.51, "ytd_pct": 18.60,
                "full_period_pct": 15.13, "3y_annualized_volatility_pct": 11.93,
                "5y_annualized_volatility_pct": 15.13,
            },
        ]
    )
    rendered = _trailing_returns_table(trailing, PORTFOLIOS, BENCHMARK)
    assert "Total Return" in rendered
    assert "Annualized Return" in rendered
    assert "Annualized Standard Deviation" in rendered
    for label in ["3 Month", "Year To Date", "1 Year", "3 Year", "5 Year", "Full"]:
        assert label in rendered
    assert "34.14%" in rendered
    assert BENCHMARK_HTML in rendered
    assert "_pct" not in rendered


def test_growth_chart_uses_calendar_ticks_and_shared_month_hover_for_all_series():
    dates = pd.date_range("2020-01-31", "2022-12-31", freq="ME")
    growth = pd.DataFrame(
        {
            "date": dates,
            "Growth 70/30_balance": [10000 + index * 250 for index in range(len(dates))],
            "Balanced 50/50_balance": [10000 + index * 200 for index in range(len(dates))],
            "benchmark_balance": [10000 + index * 150 for index in range(len(dates))],
        }
    )
    chart = _growth_svg(growth, PORTFOLIOS, {"benchmark": BENCHMARK})
    assert "Jan 2020" in chart and "Jul 2020" in chart and "Jan 2021" in chart
    # Jun is valid hover content, but should not be emitted as a semantic axis tick.
    assert ">Jun 2020</text>" not in chart
    assert BENCHMARK_HTML in chart
    assert "growth-hover-zone" in chart
    assert "data-tooltip-json=" in chart
    assert "Growth 70/30" in chart and "Balanced 50/50" in chart


def test_active_returns_primary_presentation_does_not_dump_storage_schema():
    dates = pd.date_range("2021-01-31", periods=40, freq="ME")
    active_rows = []
    contribution_rows = []
    observation_rows = []
    for index, date in enumerate(dates):
        active_rows.append(
            {
                "portfolio": "Growth 70/30",
                "date": date,
                "annual_active_return": 0.12,
                "rolling_active_return_pct": 4.0 if index >= 35 else None,
                "rolling_tracking_error_pct": 5.0 if index >= 35 else None,
            }
        )
        contribution_rows.extend(
            [
                {"date": date, "portfolio": "Growth 70/30", "ticker": "QQQ", "cumulative_active_contribution_pct": index * 0.4},
                {"date": date, "portfolio": "Growth 70/30", "ticker": "GLD", "cumulative_active_contribution_pct": index * -0.1},
            ]
        )
        observation_rows.append(
            {"date": date, "portfolio": "Growth 70/30", "benchmark_return_pct": -3 + index % 8, "portfolio_return_pct": -2.5 + index % 8}
        )
    benchmark = pd.DataFrame(
        [{"portfolio": "Growth 70/30", "active_return_pct": 5.3, "tracking_error_pct": 7.1, "information_ratio": 0.74}]
    )
    up_down = pd.DataFrame(
        [
            {"portfolio": "Growth 70/30", "market_type": "up", "above_benchmark_count": 8, "below_benchmark_count": 4, "total_count": 12, "pct_above_benchmark": 66.67, "above_active_return_pct": 1.2, "below_active_return_pct": -0.8, "overall_active_return_pct": 0.5},
            {"portfolio": "Growth 70/30", "market_type": "down", "above_benchmark_count": 5, "below_benchmark_count": 3, "total_count": 8, "pct_above_benchmark": 62.5, "above_active_return_pct": 2.0, "below_active_return_pct": -0.5, "overall_active_return_pct": 1.1},
        ]
    )
    rendered = _active_returns_presentation(
        pd.DataFrame(active_rows),
        pd.DataFrame(contribution_rows),
        benchmark,
        up_down,
        ["Growth 70/30"],
        BENCHMARK,
        {"QQQ": "Invesco QQQ Trust", "GLD": "SPDR Gold Shares"},
        pd.DataFrame(observation_rows),
    )
    for label in [
        "Benchmark Summary", "Annualized Active Return", "Cumulative Active Return",
        "Rolling Active Return and Risk", "Up / Down Market Performance",
    ]:
        assert label in rendered
    for storage_name in ["portfolio_return", "benchmark_return", "rolling_tracking_error_pct", "cumulative_active_contribution_pct"]:
        assert storage_name not in rendered


def test_assets_split_long_term_characteristics_from_trailing_performance():
    frame = pd.DataFrame(
        [
            {
                "ticker": "069500", "name": "KODEX 200", "cagr_pct": 12.5,
                "annualized_volatility_pct": 15.0, "best_year": 0.20,
                "worst_year": -0.10, "max_drawdown_pct": -18.0,
                "sharpe_ratio": 0.8, "sortino_ratio": 1.1,
                "3m": 0.02, "ytd": 0.05, "1y": 0.07, "3y": 0.08, "5y": None,
            }
        ]
    )
    assets = _portfolio_assets_table(frame)
    trailing = _portfolio_asset_trailing_table(frame)
    assert 'id="portfolio-assets"' in assets
    for label in ["Ticker", "Name", "CAGR", "Stdev", "Best Year", "Worst Year", "Max Drawdown", "Sharpe Ratio", "Sortino Ratio"]:
        assert label in assets
    assert 'id="portfolio-asset-performance"' in trailing
    assert "Total Return" in trailing and "Annualized Return" in trailing
    assert "3 Month" in trailing and "Year To Date" in trailing and "5 Year" in trailing
    assert "069500" in assets and "69500.0" not in assets
    assert "2.00%" in trailing


def test_asset_tables_and_correlations_preserve_identity_and_readable_units():
    annual_assets = pd.DataFrame([{"year": 2025, "ticker": "069500", "return": 0.3556325823223574}])
    correlations = pd.DataFrame(
        [
            {"series": "QQQ", "QQQ": 1.0, "benchmark": 0.9181795019152512},
            {"series": "benchmark", "QQQ": 0.9181795019152512, "benchmark": 1.0},
        ]
    )
    annual_html = _annual_asset_returns_table(annual_assets)
    correlation_html = _correlations_table(correlations, BENCHMARK)
    assert "069500" in annual_html and "69500.0" not in annual_html
    assert "35.56%" in annual_html
    assert 'id="correlations-heatmap"' in correlation_html
    assert "0.92" in correlation_html
    assert "0.9181795019152512" not in correlation_html


def test_decomposition_tables_remove_storage_labels_and_format_values():
    returns = pd.DataFrame([{"asset": "contribution_QQQ", "Growth 70/30_contribution_balance": 13881.150834305976}])
    risk = pd.DataFrame([{"asset": "QQQ", "Growth 70/30_risk_contribution_pct": 87.76956876859154}])
    returns_html = _decomposition_table(returns, ["Growth 70/30"], currency="USD")
    risk_html = _decomposition_table(risk, ["Growth 70/30"], currency="USD")
    assert "contribution_QQQ" not in returns_html
    assert "$13,881" in returns_html
    assert "87.77%" in risk_html


def test_report_options_and_money_are_human_facing():
    assert _display_option("month_to_month") == "Month-to-Month"
    assert _display_option("year_to_year") == "Year-to-Year"
    assert _display_option("canonical_total_return") == "Total Return"
    assert _display_option("semiannual") == "Semiannual"
    assert _money(10000, "USD") == "$10,000"
    assert _money(10000, "KRW") == "₩10,000"


def test_growth_chart_uses_configured_currency_without_duplicate_symbol():
    dates = pd.date_range("2025-01-31", "2025-03-31", freq="ME")
    growth = pd.DataFrame({"date": dates, "KODEX 200 100%_balance": [10000, 11000, 12000]})
    chart = _growth_svg(growth, ["KODEX 200 100%"], currency="KRW")
    assert "Portfolio Balance (₩)" in chart
    assert "₩10,000" in chart
    assert "$10,000" not in chart
