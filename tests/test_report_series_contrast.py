from portfolio_optimizer_kr.viewer.final_renderer import _SERIES_CONTRAST_SCRIPT


def test_secondary_portfolio_series_uses_existing_green_palette_color():
    script = _SERIES_CONTRAST_SCRIPT

    assert "const SECONDARY_OLD = '#7c3aed';" in script
    assert "const SECONDARY_GREEN = '#22c55e';" in script

    for section_id in (
        "portfolio-growth",
        "annual-returns",
        "annualized-active-return",
        "drawdown-chart",
        "rolling-returns-3y",
        "rolling-returns-5y",
    ):
        assert f"'{section_id}'" in script

    assert "node.setAttribute('stroke', SECONDARY_GREEN)" in script
    assert "node.setAttribute('fill', SECONDARY_GREEN)" in script
    assert "span.style.setProperty('--color', SECONDARY_GREEN)" in script
