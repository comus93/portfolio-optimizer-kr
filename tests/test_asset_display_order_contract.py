"""Presentation contract for report-level asset ordering and color identity."""

import pandas as pd

from portfolio_optimizer_kr.viewer import asset_display as ad
from portfolio_optimizer_kr.viewer import backtest_renderer as br
from portfolio_optimizer_kr.viewer import pv_visual as pv

EXPECTED = [
    "QQQ",
    "SPY",
    "GLD",
    "XLE",
    "TLT",
    "AIA",
    "SLV",
    "XLF",
    "INDY",
    "EWJ",
    "EWY",
    "GDX",
]
NAMES = {
    "SPY": "State Street SPDR S&P 500 ETF",
    "GLD": "SPDR Gold Shares",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "QQQ": "Invesco QQQ Trust",
    "SLV": "iShares Silver Trust",
    "GDX": "VanEck Gold Miners ETF",
    "AIA": "iShares Asia 50 ETF",
    "XLF": "Financial Select Sector SPDR Fund",
    "XLE": "Energy Select Sector SPDR Fund",
    "EWY": "iShares MSCI South Korea ETF",
    "EWJ": "iShares MSCI Japan ETF",
    "INDY": "iShares India 50 ETF",
}


def result_fixture():
    return {
        "configuration": {
            "assets": [{"symbol": ticker, "name": name} for ticker, name in NAMES.items()]
        },
        "portfolio_definitions": {
            "Sample Portfolio": {
                "target_weights": {"SPY": 0.60, "GLD": 0.20, "TLT": 0.20}
            },
            "Portfolio 2": {
                "target_weights": {
                    "GLD": 0.10,
                    "QQQ": 0.30,
                    "SLV": 0.10,
                    "GDX": 0.10,
                    "AIA": 0.20,
                    "XLF": 0.10,
                    "XLE": 0.10,
                }
            },
            "Portfolio 3": {
                "target_weights": {
                    "GLD": 0.10,
                    "QQQ": 0.40,
                    "SLV": 0.10,
                    "EWY": 0.10,
                    "XLE": 0.10,
                    "EWJ": 0.10,
                    "INDY": 0.10,
                }
            },
        },
    }


def test_global_asset_order_and_unique_colors():
    assert ad.asset_display_order(result_fixture(), NAMES) == EXPECTED
    colors = ad.asset_color_map(EXPECTED)
    assert len(set(colors.values())) == len(EXPECTED)


def test_target_allocation_uses_global_order():
    result = result_fixture()
    rows = []
    for portfolio, definition in result["portfolio_definitions"].items():
        for ticker, name in NAMES.items():
            rows.append(
                {
                    "portfolio": portfolio,
                    "ticker": ticker,
                    "name": name,
                    "target_weight_pct": definition["target_weights"].get(ticker, 0) * 100,
                }
            )
    html = br._allocation_matrix(pd.DataFrame(rows), list(result["portfolio_definitions"]))
    positions = [html.index(f"({ticker})") for ticker in EXPECTED]
    assert positions == sorted(positions)


def test_correlation_order_and_adaptive_width_contract():
    ordered_names = ad.ordered_asset_names(NAMES, EXPECTED)
    columns = EXPECTED + [
        "Sample Portfolio",
        "Portfolio 2",
        "Portfolio 3",
        "benchmark",
    ]
    rows = []
    for ticker in EXPECTED:
        row = {"series": ticker}
        row.update({column: 1.0 if column == ticker else 0.25 for column in columns})
        rows.append(row)
    html = pv.correlations_table(
        pd.DataFrame(rows),
        "SPY Benchmark",
        ordered_names,
        ["Sample Portfolio", "Portfolio 2", "Portfolio 3"],
    )
    header = html.split("</thead>", 1)[0]
    body = html.split("<tbody>", 1)[1]
    header_positions = [header.index(f">{ticker}<") for ticker in EXPECTED]
    body_positions = [body.index(f">{ticker}<") for ticker in EXPECTED]
    assert header_positions == sorted(header_positions)
    assert body_positions == sorted(body_positions)
    assert 'data-correlation-columns="16"' in html
    assert 'min-width:1002px' in html


def test_annual_asset_legend_uses_global_order_and_colors():
    ordered_names = ad.ordered_asset_names(NAMES, EXPECTED)
    frame = pd.DataFrame(
        [
            {"year": 2025, "ticker": ticker, "return_pct": index + 1}
            for index, ticker in enumerate(reversed(EXPECTED))
        ]
    )
    html = pv.annual_asset_returns_chart(frame, ordered_names)
    legend = html.split('<div class="legend">', 1)[1].split("</div>", 1)[0]
    positions = [legend.index(f"({ticker})") for ticker in EXPECTED]
    assert positions == sorted(positions)
    colors = ad.asset_color_map(EXPECTED)
    assert all(colors[ticker] in html for ticker in EXPECTED)
