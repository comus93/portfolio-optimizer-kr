from pathlib import Path


def _template() -> str:
    return (Path(__file__).resolve().parents[1] / "site" / "report-template.html").read_text(
        encoding="utf-8"
    )


def _p1_script() -> str:
    template = _template()
    start = template.index('<script id="report-p1-polish">')
    end = template.index("</script>", start) + len("</script>")
    return template[start:end]


def test_p1_polish_replaces_generic_tables_with_readable_purpose_specific_views():
    script = _p1_script()

    assert "renderReadableTables();" in script
    assert "renderPurposeSpecificAssetTables();" in script
    assert "Performance Summary" not in script  # data-driven, not duplicated markup
    assert "Historical asset performance and risk statistics." in script
    assert "Risk/return fields used to position the individual assets" in script
    assert "Full Period CAGR" in script


def test_p1_polish_renders_correlation_heatmaps_and_separate_drawdown_tables():
    script = _p1_script()

    assert "renderCorrelationHeatmaps();" in script
    assert "renderHeatmap('asset-correlations', assetNames)" in script
    assert "renderHeatmap('portfolio-asset-correlations', allNames)" in script
    assert "Blue = positive correlation, red = negative correlation" in script
    assert "renderWorstDrawdowns();" in script
    assert "const order = ['provided','optimized','benchmark']" in script
    assert "slice(0,10)" in script


def test_p1_polish_removes_duplicate_transition_frame_and_uses_nice_ticks():
    script = _p1_script()

    assert "const niceStep" in script
    assert "const niceTicks" in script
    assert "const cleanFrame" in script
    assert "svg.querySelectorAll('.grid-line,.tick-label')" in script
    assert "polishTransitionAxes();" in script
    assert "yTicks:[0,25,50,75,100]" in script


def test_p1_polish_keeps_all_year_labels_for_decade_scale_reports():
    script = _p1_script()

    assert "const allYears = rows.length <= 15" in script
    assert "const stride=allYears?1:Math.ceil(rows.length/12)" in script
    assert "polishGroupedBars('annual-returns'" in script
    assert "polishGroupedBars('annual-asset-returns'" in script


def test_p1_polish_resolves_frontier_label_collisions_and_remains_self_contained():
    script = _p1_script()

    assert "resolveFrontierLabelCollisions" in script
    assert "label.getBBox()" in script
    assert "requestAnimationFrame(resolveFrontierLabelCollisions)" in script
    assert "http://" not in script
    assert "https://" not in script
