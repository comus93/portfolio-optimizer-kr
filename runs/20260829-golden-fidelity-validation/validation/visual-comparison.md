# Golden Fidelity Validation

Validation date: 2026-08-29

## Run and Browser State

- Run ID: `20260829-golden-fidelity-validation`
- Period: `2016-08-01` through `2026-07-31`
- Objective: Maximum Sharpe; monthly rebalancing; SPY; fixed 2.35595% annual risk-free rate; 100 frontier points.
- Local HTTP URL: `http://127.0.0.1:8765/runs/20260829-golden-fidelity-validation/report.html`
- Browser rendered local report: YES (29 sections; changed visual sections rendered as SVG charts).
- PV live URL: `https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg`
- Browser rendered PV: YES (`Portfolio Optimization Results (Aug 2016 - Jul 2026)`).

## Automated Validation

`uv run pytest tests/test_interactive_report_contract.py tests/test_report_presentation_upstream.py tests/test_report_visual_identity.py tests/test_report_golden_fidelity.py -q`: PASS (23 passed)

Full pytest was not run because this is a rendering-only change and the requested validation scope is limited to affected tests.

## Changed-section Review

| Section | Result | Evidence |
| --- | --- | --- |
| Provided Portfolio | PASS | 0% GLD is hidden; readable percent summary, donut, and allocation table. |
| Optimized Portfolio | PASS | 0% assets are hidden; readable percent summary, donut, and allocation table. |
| Portfolio Growth | PASS | Year ticks, multiple dollar-balance ticks, and three portfolio identities render. |
| Annual Returns | PASS | Year labels, numeric percent ticks, and provided/optimized/benchmark identity render. |
| Annualized Active Return | PASS | Year labels, numeric percent ticks, and provided/optimized identity render. |
| Annual Asset Returns | PASS | Year X-axis, seven ticker series, and distinct ticker legend/color identities render. |
| Efficient Frontier | PASS | Intermediate volatility/expected-return ticks; blue curve, gray assets, red landmarks; grouped legend identity. |
| Efficient Frontier Transition Map | PASS | Standard-deviation X ticks, 0/25/50/75/100% Y ticks, and ticker allocations render. |
| Up vs. Down Market Performance | PASS | Provided/Optimized scatter panels, numeric X/Y ticks, blue/red month identities, and explicit unit-bearing table headers render. |

## PV / Static Golden Comparison

PV live was opened and submitted from the required shared URL. It rendered the same Aug 2016 through Jul 2026 study and exposes the same relevant chart sections. The report does not attempt a pixel clone; its section structure, axes, units, series separation, and color identities permit the same information to be read.

Static Golden comparison: PASS for the requested semantic fidelity scope.

P0 mismatches: 0

P1 remaining: none identified in this focused changed-section review.

## Screenshot Note

Browser screenshot capture timed out in this environment. No screenshot files are included. Local report and PV live rendering were both directly confirmed, so this is evidence-capture limitation only.
