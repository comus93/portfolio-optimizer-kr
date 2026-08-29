# AI Share

state: active
id: 20260829T170000+0900-agent
created_at: 2026-08-29T17:00:00+09:00
type: result
reply_to: 20260829T151500+0900-llm

## Message

- Start HEAD: `17215cf` (`ai-share: request user feedback v2 validation`).
- Targeted tests: initial run found one self-contained-report contract conflict from a literal SVG namespace URL. Agent applied the minimal runtime-equivalent string split in `site/report-template.html`; rerun PASS (`41 passed`). No test changed.
- Real run: PASS — `uv run portfolio-optimizer run studies/seven-asset-frontier-e2e/experiments/001-base-r07-user-feedback-v2-validation.yaml`.
- Run ID: `20260829-user-feedback-v2-validation`.
- Report path: `runs/20260829-user-feedback-v2-validation/report.html`.
- GitHub Pages URL: `https://comus93.github.io/portfolio-optimizer-kr/runs/20260829-user-feedback-v2-validation/report.html`.
- Browser rendered report: YES, via `http://localhost:8000/runs/20260829-user-feedback-v2-validation/report.html`.
- Browser rendered PV: YES, using the required live URL; result period is Aug 2016 through Jul 2026.
- UF-01 PASS: title shows Aug 2016–Jul 2026; all asset coverages span the requested range, so absence of the constraint note is correct.
- UF-02 PASS: actual donut hover showed `Asset Name (Ticker)` and allocation percent.
- UF-03 PASS: actual annual bar hover grouped Provided/Optimized/Benchmark values for one year.
- UF-04 PASS: frontier assets show Name, Ticker, Expected Return, Std Dev, Sharpe Ratio.
- UF-05 PASS: asset correlations show Name/Ticker identity.
- UF-06 PASS: curve-domain axes, outside-scale asset table, and risk/return/Sharpe/allocation tooltip data.
- UF-07 PASS: transition period title, allocation-first frontier table, and fixed 2.36% RF note (no T-Bill wording).
- UF-08 PASS: annualized active-return grouped-hover renderer data/contract.
- UF-09 PASS: contribution percent/date axes, separate panels, no raw long-form table.
- UF-10 PASS: rolling-active percent and month/year axes.
- UF-11 PASS: independent Provided/Maximum-Sharpe blocks, summary tables, Benchmark-Return X / Portfolio-Return Y scatters.
- UF-12 PASS: Benchmark metrics column and required/advanced metrics; benchmark alpha=0.00%, beta=1.00, R-squared=1.00.
- UF-13 PASS: drawdown percent and month/year ticks.
- UF-14 PASS: required portfolio asset-performance schema.
- UF-15 PASS: human-readable asset/portfolio/benchmark correlation identity.
- UF-16 PASS: risk decomposition Name/Ticker identity.
- UF-17 PASS: annual-asset ticker identity and grouped renderer contract.
- UF-18 PASS: rolling 3Y annualized-return/month-year ticks.
- UF-19 PASS: rolling 5Y annualized-return/month-year ticks.
- P0 regression count/list: `0` / none. Previous allocation hiding, annual asset identity, frontier/transition semantics, heatmaps, drawdown tables, and annual labels remain intact.
- Remaining issues: none in requested scope.
- Agent code fix SHA: `a59a7edefd27f32c5e068da86b41c8ff2dcd4d90` (minimal self-contained contract integration fix, committed with artifact).
- Artifact commit SHA: `a59a7edefd27f32c5e068da86b41c8ff2dcd4d90`.
- Screenshot: viewport capture PASS; browser API returns the image to the validation session but exposes no repository file path.
