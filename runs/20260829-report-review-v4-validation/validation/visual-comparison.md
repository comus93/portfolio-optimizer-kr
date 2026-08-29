# Report review v4 visual comparison

## Environment and execution

- Local report (HTTP): `http://localhost:8000/runs/20260829-report-review-v4-validation/report.html`
- GitHub Pages: `https://comus93.github.io/portfolio-optimizer-kr/runs/20260829-report-review-v4-validation/report.html`
- PV live behavioral golden: `https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5`
- Browser report: YES. Browser PV: YES. No screen blocker appeared during local screenshot/hover validation.
- Targeted test command:
  `uv run pytest tests/test_reporting.py tests/test_interactive_report_contract.py tests/test_report_visual_identity.py tests/test_report_golden_fidelity.py tests/test_report_p1_polish.py tests/test_report_user_feedback_v2.py tests/test_report_user_feedback_v3.py tests/test_report_user_feedback_v4.py -q`
- Targeted result: **45 passed**.
- Fresh run command:
  `uv run portfolio-optimizer run studies/seven-asset-frontier-e2e/experiments/001-base-r10-report-review-v4-validation.yaml`

## Fresh run

- Run ID: `20260829-report-review-v4-validation`
- Effective input: QQQ/SPMO/GDX/GLD/SLV/AIA/XLE; provided 40/10/10/0/10/15/15; 0 minimums, 50% QQQ/SPMO caps and 30% other caps; SPY; Maximum Sharpe; monthly; fixed 2.35595% annual RF; 100 frontier points; 2016-08-01 through 2026-07-31.

## Browser evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Efficient Frontier physical presentation | PASS | Browser SVG height was 560px at the validation viewport. Actual domain X 12.0%–22.5%, Y 11.0%–22.0%, matching the requested live-PV range in meaning without hard-coded input values. |
| Frontier visible/outside | PASS | Visible: QQQ, SPMO, GLD, AIA. Outside table only: GDX, SLV, XLE. Table is based on final display domain. |
| Frontier schema / hover | PASS | Assets table contains Name, Ticker, Expected Return, Std Dev, Sharpe Ratio, Min Weight, Max Weight. Actual curve hover exposed Expected Return, Standard Deviation, Sharpe Ratio, and all seven allocations. |
| Rolling Active calculation and UI | PASS | Two independent panels use title `Rolling Active Return and Risk (36 months)`, left Active Return bar axis and right Tracking Error mint-line axis. Actual hover contains the same-month values. End values: Provided 2026-07 Active Return 9.15%, Tracking Error 8.24%; Maximum Sharpe 11.68%, 5.96%. The tracking-error ranges align broadly with PV's about-8% / about-6% endpoint ranges. |
| Balance / metric semantics | PASS | Start Balance renders $10,000 for all portfolios; End Balance is dollar-scaled. Benchmark Active Return, Tracking Error and Information Ratio render N/A. Performance Summary includes all 14 required rows. |
| Asset Performance | PASS | Browser table headers: Ticker, Name, CAGR, Annualized Return, Stdev, Best Year, Worst Year, Max Drawdown, Sharpe Ratio, Sortino Ratio, 3M, YTD, 1Y, 3Y Ann., 5Y Ann., 10Y Ann.; percentages use percentage-point display. |
| Identity consistency | PASS | Report table identities are Provided Portfolio / Maximum Sharpe Ratio / State Street SPDR S&P 500 ETF; no exact generic Optimized or Benchmark table/header labels remained. |
| Annual Asset Returns v3 sanity | PASS | Seven ticker series/legend entries: QQQ, SPMO, GDX, GLD, SLV, AIA, XLE. |
| Up/Down v3 sanity | PASS | Two paired-bar SVG panels, 40 bars each = 20 equal-frequency groups × two series; no scatter chart. |
| Other v3 sanity | PASS | Frontier Min/Max columns, correlation Name/Ticker, risk decomposition Name/Ticker, active contribution chart with no raw table, and rolling 3Y/5Y chart axes remain present. |
| PV live comparison | PASS | PV browser opened `Portfolio Optimization Results (Aug 2016 - Jul 2026)` and showed the same dual-axis Rolling Active presentation and paired Return-vs-Benchmark bars. |
| Static golden | PENDING USER REFRESH | Current instruction explicitly defers a new full-page static golden. No stale or unavailable URL was used as a pass/fail source. |

## Difference record

- Intentional deviation: local FDR uses 84 positive / 36 negative benchmark months versus PV 85 / 35. The known classification difference is July 2026: local SPY -0.68027%, PV +0.03%; this is a data-source/price-series difference, not a local UI or classification defect.

## Summary

- P0 mismatches: 0
- P1 mismatches: 0 observed in this browser validation
- Intentional deviations: 1 (July 2026 local FDR/PV SPY return sign)
- Remaining issues: static full-page Golden awaits the user refresh.
