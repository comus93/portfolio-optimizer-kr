import inspect
import math

import pandas as pd

from portfolio_optimizer_kr.analytics.metrics import active_analytics
from portfolio_optimizer_kr.viewer import final_renderer
from portfolio_optimizer_kr.viewer.feedback_v4 import (
    _USER_FEEDBACK_V4_SCRIPT,
    _inject_user_feedback_v4_script,
)


def test_rolling_active_return_annualizes_each_36m_leg_before_subtracting():
    index = pd.date_range("2020-01-31", periods=36, freq="ME")
    portfolio = pd.Series([0.01] * 36, index=index)
    benchmark = pd.Series([0.005] * 36, index=index)

    result = active_analytics(portfolio, benchmark, window=36)
    expected = (1.01**12 - 1.0) - (1.005**12 - 1.0)

    assert math.isclose(result["rolling_active_return"].iloc[-1], expected, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(result["rolling_tracking_error"].iloc[-1], 0.0, rel_tol=0, abs_tol=1e-12)


def test_v4_report_layer_is_injected_once_and_final_renderer_uses_it():
    html = "<html><body><main>report</main></body></html>"
    injected = _inject_user_feedback_v4_script(html)
    assert 'id="report-user-feedback-v4"' in injected
    assert _inject_user_feedback_v4_script(injected) == injected
    assert "_render_feedback_v4" in inspect.getsource(final_renderer.render_report)


def test_v4_semantic_fixes_are_locked_in_contract():
    script = _USER_FEEDBACK_V4_SCRIPT
    assert "Number(value) * 10000" in script
    assert "add('Active Return','pct'" in script
    assert "add('Tracking Error','pct'" in script
    assert "information_ratio,null" in script
    assert "Annualized Return" in script
    assert "3M" in script and "YTD" in script and "10Y Ann." in script
    assert "providedLabel = 'Provided Portfolio'" in script
    assert "optimizedLabel = data.objective_name" in script
    assert "benchmarkLabel = data.benchmark_name" in script


def test_v4_frontier_and_rolling_active_match_current_pv_presentation_contract():
    script = _USER_FEEDBACK_V4_SCRIPT
    assert "v4-frontier-svg" in script
    assert "contextRight=cmax+Math.max(span,4.0)" in script
    assert "height=500" in script
    assert "Rolling Active Return and Risk (36 months)" in script
    assert "Active Return" in script
    assert "Tracking Error" in script
    assert "stroke:MINT" in script
    assert "v4-rolling-panel" in script


def test_final_renderer_growth_hover_uses_plot_wide_nearest_date_overlay():
    script = final_renderer._SERIES_CONTRAST_SCRIPT
    assert "final-growth-hover-overlay" in script
    assert "fixPortfolioGrowthHover" in script
    assert "targetTime" in script
    assert "const nearest" in script
    assert "circle[fill=\"transparent\"]" in script
    assert "Provided Portfolio" in script
    assert "data.objective_name" in script
