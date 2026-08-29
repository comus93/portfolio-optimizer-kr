from portfolio_optimizer_kr.viewer.renderer import (
    _VISUAL_IDENTITY_SCRIPT,
    _inject_visual_identity_script,
)


def test_visual_identity_script_is_injected_inside_self_contained_report():
    html = "<html><body><main>report</main></body></html>"
    rendered = _inject_visual_identity_script(html)

    assert rendered.count('id="report-legend-identity"') == 1
    assert rendered.endswith("</body></html>")
    assert "http://" not in _VISUAL_IDENTITY_SCRIPT
    assert "https://" not in _VISUAL_IDENTITY_SCRIPT


def test_visual_identity_script_locks_plot_and_legend_series_colors():
    # Fixed renderer identities must be repeated exactly in the corresponding
    # legends. This prevents the fallback palette from mislabeling a series.
    assert "paintSectionLegends('annual-returns', [BLUE, PURPLE, GRAY])" in _VISUAL_IDENTITY_SCRIPT
    assert "paintSectionLegends('annualized-active-return', [BLUE, PURPLE])" in _VISUAL_IDENTITY_SCRIPT
    assert "paintSectionLegends('rolling-active-return', [BLUE, ORANGE])" in _VISUAL_IDENTITY_SCRIPT
    assert "paintSectionLegends('up-down-market', [BLUE, RED])" in _VISUAL_IDENTITY_SCRIPT
    assert "paintSectionLegends('annual-asset-returns', [BLUE])" in _VISUAL_IDENTITY_SCRIPT

    # Frontier assets and landmarks have intentionally different marker
    # identities, and the legend must follow the same distinction.
    assert "frontierAssets.has(label)" in _VISUAL_IDENTITY_SCRIPT
    assert "label === 'Efficient Frontier'" in _VISUAL_IDENTITY_SCRIPT
    assert "? GRAY" in _VISUAL_IDENTITY_SCRIPT
    assert ": RED" in _VISUAL_IDENTITY_SCRIPT
