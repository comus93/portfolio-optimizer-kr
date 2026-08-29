# User Feedback v2 Validation

Validation date: 2026-08-29

## Environment

- Local report: `http://localhost:8000/runs/20260829-user-feedback-v2-validation/report.html`
- Browser rendered report: YES
- Browser rendered PV: YES — `https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg`, result period Aug 2016 through Jul 2026.
- Browser viewport screenshot capture: PASS.

## Tests and Run

- Affected-scope tests: PASS (41 passed).
- Run: PASS — `uv run portfolio-optimizer run studies/seven-asset-frontier-e2e/experiments/001-base-r07-user-feedback-v2-validation.yaml`.
- Run ID: `20260829-user-feedback-v2-validation`.

## User-feedback Review

| Item | Result | Evidence |
| --- | --- | --- |
| UF-01 Title / period / constraint note | PASS | Title shows `(Aug 2016 - Jul 2026)`. Every `asset_prices` coverage starts before the requested period and extends through the final requested month, so no availability constraint note is shown. |
| UF-02 Allocation donut hover | PASS | Actual pointer hover showed `Energy Select Sector SPDR Fund (XLE)` and `Allocation: 15.00%`. |
| UF-03 Annual Returns grouped hover | PASS | Actual pointer hover showed 2018 and all Provided/Optimized/Benchmark annual values in one tooltip. |
| UF-04 Efficient Frontier Assets identity | PASS | Name, Ticker, Expected Return, Std Dev, Sharpe Ratio columns. |
| UF-05 Asset Correlations identity | PASS | Name and Ticker columns on every asset row. |
| UF-06 Efficient Frontier behavior | PASS | Chart uses curve-domain axes; assets outside the scale are listed in a Name/Ticker/Std Dev/Expected Return/Sharpe table; frontier/landmark tooltip has risk-return-Sharpe and all asset weights. |
| UF-07 Transition Map / frontier portfolios | PASS | Period title is present; allocation columns precede Expected Return/Standard Deviation/Sharpe; note states fixed annual risk-free rate of 2.36%, not U.S. T-Bill. |
| UF-08 Annualized Active Return hover | PASS | Grouped series and year chart structure are present under the same grouped-hover renderer contract. |
| UF-09 Active Return Contribution | PASS | Percentage Y ticks, month/year X ticks, separate portfolio panels, and no raw long-form table. |
| UF-10 Rolling Active / Tracking Error | PASS | Percentage Y ticks and month/year X ticks in both portfolio panels. |
| UF-11 Up / Down | PASS | Separate Provided and Maximum Sharpe blocks with occurrence/active-return summaries; bottom charts are Benchmark Return X vs Portfolio Return Y scatters. |
| UF-12 Portfolio Metrics | PASS | Benchmark column and required base/advanced metrics exist; fresh run benchmark beta=1.00, R-squared=1.00, alpha=0.00%. |
| UF-13 Drawdowns | PASS | Drawdown-percent Y ticks and month/year X ticks. |
| UF-14 Portfolio Asset Performance | PASS | Required Ticker, Name, CAGR, Stdev, Best/Worst Year, MDD, Sharpe, Sortino schema. |
| UF-15 Portfolio / Asset Correlations | PASS | Asset Name/Ticker plus human-readable Provided/Maximum Sharpe/benchmark rows. |
| UF-16 Risk Decomposition | PASS | Name and Ticker displayed. |
| UF-17 Annual Asset Returns grouped hover | PASS | Seven ticker identities and year-grouped renderer contract. |
| UF-18 Rolling 3Y Returns | PASS | Annualized Return percent Y ticks and month/year X ticks. |
| UF-19 Rolling 5Y Returns | PASS | Annualized Return percent Y ticks and month/year X ticks. |

## Regression / Remaining Issues

- P0 regression count: 0.
- Allocation 0% hiding, Annual Asset ticker identity, Frontier/Transition semantics, correlation heatmaps, separate drawdown tables, and 2016–2026 annual labels all remain present.
- Remaining issues: none identified in this requested scope.

## Screenshot Note

Viewport screenshot capture succeeded. The browser API returns the image to the validation session but has no repository file-path output, so no PNG is committed.
