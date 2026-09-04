from __future__ import annotations

import pandas as pd

from portfolio_optimizer_kr.viewer import asset_display as ad
from portfolio_optimizer_kr.viewer import backtest_renderer as br
from portfolio_optimizer_kr.viewer import pv_visual as pv


EXPECTED = [
    "QQQ",
    "SPMO",
    "GDX",
    "GLD",
    "SLV",
    "AIA",
    "XLE",
    "TLT",
    "IEF",
    "LQD",
    "HYG",
    "DBC",
]
NAMES = {
    "QQQ": "Invesco QQQ Trust",
    "SPMO": "Invesco S&P 500 Momentum ETF",
    "GDX": "VanEck Gold Miners ETF",
    "GLD": "SPDR Gold Shares",
    "SLV": "iShares Silver Trust",
    "AIA": "iShares Asia 50 ETF",
    "XLE": "Energy Select Sector SPDR Fund",
    "TLT": "iShares 20+ Year Treasury Bond ETF",
    "IEF": "iShares 7-10 Year Treasury Bond ETF",
    "LQD": "iShares iBoxx $ Investment Grade Corporate Bond ETF",
    "HYG": "iShares iBoxx $ High Yield Corporate Bond ETF",
    "DBC": "Invesco DB Commodity Index Tracking Fund",
}


def _result():
    return {
        "configuration": {
            "assets": [
                {"symbol": ticker, "name": NAMES[ticker], "currency": "USD"}
                for ticker in EXPECTED
            ],
            "benchmark": {
                "symbol": "SPY",
                "name": "SPY Benchmark",
                "currency": "USD",
            },
        },
        "portfolio_order": ["Sample Portfolio", "Portfolio 2", "Portfolio 3"],
        "portfolio_definitions": {
            "Sample Portfolio": {
                "target_weights": {ticker: 1 / len(EXPECTED) for ticker in EXPECTED}
            },
            "Portfolio 2": {
                "target_weights": {ticker: 1 / len(EXPECTED) for ticker in EXPECTED}
            },
            "Portfolio 3": {
                "target_weights": {ticker: 1 / len(EXPECTED) for ticker in EXPECTED}
            },
        },
    }


def test_target_allocation_uses_global_asset_order():
    result = _result()
    rows = []
    for portfolio, definition in result["portfolio_definitions"].items():
        for ticker in reversed(EXPECTED):
            rows.append(
                {
                    "portfolio": portfolio,
                    "ticker": ticker,
                    "name": NAMES[ticker],
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
    assert 'data-correlation-columns="12"' in html
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
