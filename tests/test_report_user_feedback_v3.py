import math

from portfolio_optimizer_kr import viewer
from portfolio_optimizer_kr.viewer.feedback_v3 import (
    _USER_FEEDBACK_V3_SCRIPT,
    _inject_user_feedback_v3_script,
)
from portfolio_optimizer_kr.viewer.final_renderer import _normalize_frontier_assets
from portfolio_optimizer_kr.viewer.report_model import FrontierAssetPoint, ReportModel


def test_viewer_routes_report_generation_through_final_renderer():
    assert viewer.generate_report.__module__.endswith("final_renderer")
    assert viewer.render_report.__module__.endswith("final_renderer")


def test_final_renderer_fills_missing_frontier_asset_ex_ante_sharpe_from_effective_rf():
    model = ReportModel(
        run_id="test",
        objective_name="Maximum Sharpe Ratio",
        metadata={"configuration": {"risk_free": {"effective_annual_rate": 0.02}}},
        frontier_assets=(
            FrontierAssetPoint(
                symbol="AAA",
                name="Asset A",
                expected_return_pct=12.0,
                standard_deviation_pct=20.0,
                sharpe_ratio=float("nan"),
            ),
        ),
    )
    normalized = _normalize_frontier_assets(model)
    assert math.isclose(normalized.frontier_assets[0].sharpe_ratio, 0.5)


def test_feedback_v3_is_injected_once_and_remains_self_contained():
    html = "<html><body><main>report</main></body></html>"
    injected = _inject_user_feedback_v3_script(html)
    assert 'id="report-user-feedback-v3"' in injected
    assert _inject_user_feedback_v3_script(injected) == injected
    assert "http://www.w3.org/2000/svg" not in _USER_FEEDBACK_V3_SCRIPT


def test_frontier_assets_restore_constraint_columns():
    script = _USER_FEEDBACK_V3_SCRIPT
    assert "Min Weight" in script
    assert "Max Weight" in script
    assert "limits.min_weight_pct" in script
    assert "limits.max_weight_pct" in script


def test_frontier_viewport_is_curve_anchored_but_uses_padded_snapped_display_domain():
    script = _USER_FEEDBACK_V3_SCRIPT
    assert "curveMinX" in script and "curveMaxX" in script
    assert "outwardDomain(curveMinX, curveMaxX" in script
    assert "lowerPad: Math.max(xSpan * 0.10, 2.0)" in script
    assert "upperPad: Math.max(xSpan * 0.20, 4.0)" in script
    assert "lowerPad: Math.max(ySpan * 0.25, 4.5)" in script
    assert "const inside = (vx, vy) => vx >= xDomain.min" in script
    assert "if (!inside(vx,vy)) { hidden.push(asset); return; }" in script


def test_annual_asset_returns_are_real_ticker_series_with_stable_identity():
    script = _USER_FEEDBACK_V3_SCRIPT
    assert "const tickers = assetOrder.filter" in script
    assert "fill:assetColor(ticker)" in script
    assert "assetName(t)" in script
    assert "Annual Return %" in script


def test_up_down_return_vs_benchmark_uses_pv_style_equal_frequency_paired_bars():
    script = _USER_FEEDBACK_V3_SCRIPT
    assert "returnVsBenchmarkBins = (rows, targetBins=20)" in script
    assert ".sort((a,b)=>Number(a.benchmark_return_pct)-Number(b.benchmark_return_pct))" in script
    assert "Math.floor(index*sorted.length/binCount)" in script
    assert "portfolio_return_pct:mean(members,'portfolio_return_pct')" in script
    assert "benchmark_return_pct:mean(members,'benchmark_return_pct')" in script
    assert "v3-return-bars" in script
    assert "Return vs. Benchmark" in script
    assert "Months in group" in script
