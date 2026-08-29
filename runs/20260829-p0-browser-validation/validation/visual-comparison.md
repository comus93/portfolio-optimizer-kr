# Interactive Report Browser Validation

Validation date: 2026-08-29

## Render Environment

- Local HTTP URL: `http://127.0.0.1:8765/runs/20260829-p0-browser-validation/report.html`
- Browser actually rendered report: YES
- PV live URL: `https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg`
- Browser actually rendered PV: YES (`Portfolio Optimization Results (Aug 2016 - Jul 2026)`)
- `file://` was not used.

## Inputs

- Run ID: `20260829-p0-browser-validation`
- Period: `2016-08-01` through `2026-07-31`
- Objective: Maximum Sharpe Ratio; monthly rebalancing; SPY benchmark; fixed 2.35595% annual risk-free rate; 100 frontier points.

## Automated Validation

- `uv run pytest tests/test_interactive_report_contract.py tests/test_report_presentation_upstream.py tests/test_report_visual_identity.py -q`: PASS (18 passed)
- Full pytest: intentionally not run, following the user's instruction to validate only the changed/affected scope.

## 11-Section Browser Review

| Section | Browser review |
| --- | --- |
| Portfolio Growth | PASS — rendered SVG; balance axis; provided/optimized/benchmark series; real hover showed date and dollar balances. |
| Annual Returns | PASS — grouped annual-return bars; three series and matching blue/purple/gray legend identities. |
| Efficient Frontier | PASS — blue frontier curve, gray individual-asset markers, red portfolio/benchmark landmarks; matching legend identities. |
| Efficient Frontier Transition Map | PASS — allocation stack by volatility; asset legend colors match areas. |
| Annualized Active Return | PASS — provided/optimized bars with matching blue/purple legends. |
| Active Return Contribution | PASS — distinct Provided and Optimized panels; ticker paths are portfolio-scoped. |
| Rolling Active Return / Tracking Error | PASS — two portfolio panels with blue active-return and orange tracking-error series. |
| Up vs. Down Market | PASS — two scatter panels; blue up-month and red down-month points/legends. |
| Drawdown | PASS — three rendered drawdown series with portfolio identities. |
| Annual Asset Returns | PASS — rendered annual-return bars and unit-aware chart presentation. |
| Rolling 3Y / 5Y Returns | PASS — both rolling return charts rendered with provided/optimized/benchmark series. |

## PV Live Comparison

PV live was submitted from the shared URL and rendered the same Aug 2016–Jul 2026 study. Its provided input, bounds, SPY benchmark, and Maximum Sharpe objective match this run. The optimized allocation remains directionally aligned with the FDR output: PV approximately QQQ 24.9%, SPMO 40.6%, GLD 30.0%, XLE 4.5%; FDR run QQQ 24.38%, SPMO 41.09%, GLD 30.0%, XLE 4.53%.

PV live comparison: PASS for chart/section semantics and visual identity.

Legend/marker identity validation: PASS.

P0 mismatches: 0

Remaining P1 differences: none assessed in this focused P0 validation.

## Notes

- Browser screenshot capture timed out, so no screenshots are included. This does not affect the recorded successful report/PV rendering and DOM-level chart review.
- No Agent code change was necessary.
