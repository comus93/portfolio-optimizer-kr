# Report review v3 visual comparison

## Environment

- Local report (HTTP): `http://localhost:8000/runs/20260829-report-review-v3-validation-r2/report.html`
- GitHub Pages: `https://comus93.github.io/portfolio-optimizer-kr/runs/20260829-report-review-v3-validation-r2/report.html`
- PV live: `https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=2FhGh05AdETg8OYDXpuLJg`
- Browser render: PASS for local report and PV. Browser screenshots were captured in the validation session; no screen blocker appeared. The browser surface cannot persist those screenshots at a repository path.
- Test command: `uv run pytest tests/test_reporting.py tests/test_interactive_report_contract.py tests/test_report_visual_identity.py tests/test_report_golden_fidelity.py tests/test_report_p1_polish.py tests/test_report_user_feedback_v2.py tests/test_report_user_feedback_v3.py -q`
- Result: **41 passed**.

## Fresh run

- Command: `uv run portfolio-optimizer run studies/seven-asset-frontier-e2e/experiments/001-base-r09-report-review-v3-validation-r2.yaml`
- Run ID: `20260829-report-review-v3-validation-r2`
- Input: requested seven-asset Golden input; 2016-08-01 through 2026-07-31; monthly; fixed annual RF 2.35595%; 100 frontier points.

## Validation results

| Check | Result | Evidence |
| --- | --- | --- |
| Frontier Assets schema and Sharpe | PASS | Browser table shows Name, Ticker, Expected Return, Std Dev, Sharpe Ratio, Min Weight, Max Weight; values are populated. |
| Frontier display domain | PASS | Actual snapped domain: X = 10.0%–22.0%, Y = 11.0%–22.0%. The raw curve is shown with context rather than filling the viewport. |
| Asset visibility / outsider classification | PASS | Visible: QQQ (19.01%, 20.42%), SPMO (17.98%, 19.51%), GLD (15.10%, 11.90%), AIA (21.74%, 14.77%). Outside only: GDX (33.93%, 15.71%), SLV (29.87%, 14.51%), XLE (29.98%, 14.18%). |
| Frontier curve hover | PASS | Actual browser hover showed Expected Return, Standard Deviation, Sharpe Ratio, and all seven asset allocations. |
| Annual Asset Returns | PASS | Seven distinct ticker legend entries/colors (QQQ, SPMO, GDX, GLD, SLV, AIA, XLE); actual year hover showed every Name/Ticker/annual return in one tooltip. |
| Up/Down presentation | PASS | Each Provided / Maximum Sharpe block has conditional-statistics table plus paired Return vs. Benchmark bars. Two SVGs each contain 40 bars: 20 groups × Portfolio/Benchmark, with 6 observations per group. Actual hover included both returns and group count. |
| 84/36 vs PV 85/35 | Intentional deviation | Local canonical SPY count is 84 positive / 36 negative (120 months). Exact divergent month: 2026-07: local FDR SPY = -0.68027%, PV = +0.03%. This is a data-source/price-series difference, not a local classification-logic defect. |
| PV live comparison | PASS | Actual PV browser result opened as `Portfolio Optimization Results (Aug 2016 - Jul 2026)` and showed 85/35 and PV-style paired bars. |
| Static Golden comparison | FAIL | The required GitHub Golden URL was opened in the browser and returned `Page not found · GitHub · GitHub`; no static-image comparison could be made. |

## Renderer integration fix

The v3 overlay initially left the preceding renderer's `.frontier-hidden` table in the document. That stale table used pre-v3 raw-curve classification and incorrectly listed visible assets. The minimal integration fix removes both prior and v3 outsider containers before adding the final snapped-domain table. No finance semantics or viewport design were changed.

## Mismatch summary

- P0 mismatches: 0
- P1 mismatches: 0
- Intentional deviations: 1 — July 2026 local FDR/PV SPY return sign difference.
- Remaining issue: static Golden reference URL is unavailable (HTTP GitHub page-not-found), so static Golden comparison is FAIL rather than PASS.
