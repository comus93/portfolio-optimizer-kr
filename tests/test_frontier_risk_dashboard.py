from __future__ import annotations

import json

import pandas as pd
import pytest

from portfolio_optimizer_kr.viewer.frontier_risk_dashboard import (
    build_frontier_interactive_payload,
    inject_frontier_risk_dashboard,
    write_frontier_interactive_payload,
)


def _sample_inputs():
    frontier = pd.DataFrame(
        [
            {
                "point": 1,
                "sharpe": 0.5,
                "expected_return_pct": 5.0,
                "volatility_pct": 6.0,
                "weight_A_pct": 40.0,
                "weight_B_pct": 60.0,
            },
            {
                "point": 2,
                "sharpe": 0.7,
                "expected_return_pct": 6.0,
                "volatility_pct": 7.0,
                "weight_A_pct": 70.0,
                "weight_B_pct": 30.0,
            },
        ]
    )
    overlay = pd.DataFrame(
        [
            {
                "point": 1,
                "cagr_pct": 8.0,
                "ex_post_sharpe": 0.8,
                "monthly_gain_to_pain_ratio": 1.2,
                "pain_ratio": 3.0,
                "maximum_drawdown_pct": -5.0,
                "mdd_depth_pct": 5.0,
                "tuw_pct": 40.0,
                "pain_index_pct": 1.5,
                "max_underwater_months": 4,
                "expected_return_pct": 5.0,
                "volatility_pct": 6.0,
                "segment": "gmv_to_max_sharpe",
            },
            {
                "point": 2,
                "cagr_pct": 10.0,
                "ex_post_sharpe": 1.0,
                "monthly_gain_to_pain_ratio": 1.5,
                "pain_ratio": 4.0,
                "maximum_drawdown_pct": -6.0,
                "mdd_depth_pct": 6.0,
                "tuw_pct": 45.0,
                "pain_index_pct": 1.7,
                "max_underwater_months": 5,
                "expected_return_pct": 6.0,
                "volatility_pct": 7.0,
                "segment": "gmv_to_max_sharpe",
            },
        ]
    )
    dates = pd.date_range("2024-01-31", periods=3, freq="ME")
    returns = pd.DataFrame(
        {1: [0.01, -0.02, 0.03], 2: [0.02, -0.03, 0.04]},
        index=dates,
    )
    return frontier, overlay, returns


def test_frontier_interactive_payload_is_columnar_and_json_safe(tmp_path) -> None:
    frontier, overlay, returns = _sample_inputs()
    payload = build_frontier_interactive_payload(
        frontier,
        overlay,
        returns,
        ["A", "B"],
    )

    assert payload["schema_version"] == 2
    assert payload["points"] == [1, 2]
    assert payload["symbols"] == ["A", "B"]
    assert payload["weights_pct"] == [[40.0, 60.0], [70.0, 30.0]]
    assert payload["default_point"] == 2
    assert len(payload["monthly_returns_pct"]) == 2
    assert len(payload["monthly_returns_pct"][0]) == 3
    assert len(payload["drawdown_pct"]) == 2
    assert payload["drawdown_pct"][0] == pytest.approx([0.0, -2.0, 0.0])
    assert payload["drawdown_pct"][1] == pytest.approx([0.0, -3.0, 0.0])

    path = tmp_path / "frontier_interactive.json"
    write_frontier_interactive_payload(path, payload)
    decoded = json.loads(path.read_text(encoding="utf-8"))
    assert decoded["metrics"]["monthly_gain_to_pain_ratio"] == [1.2, 1.5]
    assert decoded["definitions"]["cagr_pct"] == "연복리 수익률 (%)"
    assert "총 손실 1단위당" in decoded["definitions"]["monthly_gain_to_pain_ratio"]
    assert "연환산 초과수익" in decoded["definitions"]["pain_ratio"]


def test_dashboard_injection_is_idempotent_and_near_frontier(tmp_path) -> None:
    frontier, overlay, returns = _sample_inputs()
    payload = build_frontier_interactive_payload(
        frontier,
        overlay,
        returns,
        ["A", "B"],
    )
    report = tmp_path / "report.html"
    report.write_text(
        '<html><body><main><section id="efficient-frontier"><h2>Efficient Frontier</h2></section><section id="next"></section></main></body></html>',
        encoding="utf-8",
    )

    inject_frontier_risk_dashboard(report, payload)
    inject_frontier_risk_dashboard(report, payload)
    html = report.read_text(encoding="utf-8")

    assert html.count('id="frontier-risk-dashboard"') == 1
    assert html.count('id="frontier-risk-dashboard-data"') == 1
    assert html.index('id="efficient-frontier"') < html.index('id="frontier-risk-dashboard"')
    assert html.index('id="frontier-risk-dashboard"') < html.index('id="next"')
    assert "Monthly Gain-to-Pain" in html
    assert "Pain Ratio" in html
    assert "손실이 난 달들의 총 손실 1단위당" in html
    assert "전고점 아래에서 겪은 낙폭 부담 1단위당" in html
    assert "연환산 변동성 (%)" in html
    assert "최장 미회복 기간 (개월)" in html
    assert "drawdown_pct" in html
    assert "drawdownSeries" not in html
    assert "nearestIndexByVol" in html
