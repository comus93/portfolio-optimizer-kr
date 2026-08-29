from portfolio_optimizer_kr.viewer.renderer import _VISUAL_IDENTITY_SCRIPT


def test_golden_fidelity_script_rebuilds_known_visual_mismatches():
    script = _VISUAL_IDENTITY_SCRIPT

    assert "renderAllocationSummary('provided-portfolio','provided_weight_pct')" in script
    assert "renderAllocationSummary('optimized-portfolio','optimized_weight_pct')" in script
    assert "renderPortfolioGrowth();" in script
    assert "renderAnnualReturns();" in script
    assert "renderAnnualAssetReturns();" in script
    assert "renderEfficientFrontier();" in script
    assert "renderTransitionMap();" in script
    assert "renderUpDown();" in script


def test_annual_asset_returns_preserve_year_and_ticker_identity():
    script = _VISUAL_IDENTITY_SCRIPT

    assert "point.returns_pct" in script
    assert "series:tickers.map(ticker=>({key:ticker,label:ticker,color:assetColor(ticker)}))" in script
    assert "xTitle:'Year'" in script
    assert "yTitle:'Asset Return %'" in script


def test_golden_fidelity_axes_have_readable_intermediate_ticks():
    script = _VISUAL_IDENTITY_SCRIPT

    assert "linearTicks(min,max,5)" in script
    assert "linearTicks(minX,maxX,5)" in script
    assert "yTicks:[0,25,50,75,100]" in script
    assert "xTitle:'Standard Deviation %'" in script
    assert "yTitle:'Allocation %'" in script


def test_allocation_summary_hides_zero_weight_assets_and_formats_percentages():
    script = _VISUAL_IDENTITY_SCRIPT

    assert "Number(row[weightKey]) > 0.00005" in script
    assert "<th>Allocation</th><th>Min</th><th>Max</th>" in script
    assert "${pct(row.allocation)}" in script
    assert "allocation-donut" in script


def test_visual_fidelity_enhancement_remains_self_contained():
    script = _VISUAL_IDENTITY_SCRIPT

    assert "http://" not in script
    assert "https://" not in script
    assert "createElementNS(NS" in script
