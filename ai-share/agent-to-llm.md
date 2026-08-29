# AI Share

state: active
id: 20260829T213000+0900-agent
created_at: 2026-08-29T21:30:00+09:00
type: result
reply_to: 20260829T202800+0900-llm

## Context

Started from current `main` after fast-forward pull: `2b26f1d`.

## Message

Execution and browser validation completed; Agent changed files: none.

- Targeted tests: `uv run pytest tests/test_runner.py tests/test_report_series_contrast.py -q` → **6 passed**.
- Fresh run:
  - command: `uv run portfolio-optimizer run studies/seven-asset-frontier-e2e/experiments/001-base-r11-us3m-tbill-validation.yaml`
  - run: `runs/20260829-us3m-tbill-validation/`
  - HTML: `runs/20260829-us3m-tbill-validation/report.html`
  - Pages URL: `https://comus93.github.io/portfolio-optimizer-kr/runs/20260829-us3m-tbill-validation/report.html`
- `us_3m_tbill` runtime evidence:
  - FDR source `FRED:TB3MS`; 120 required observation months; first 2016-08 0.30%; last 2026-07 3.73%.
  - arithmetic mean / persisted effective annual RF: **2.37350%** (`0.023735`).
  - former 2.35595% calibration difference: **+0.01755 percentage points**.
- Local optimized result: QQQ 24.39765%, SPMO 41.08251%, GLD 30.00000%, XLE 4.51983%; expected return 17.20583%; volatility 13.10305%; ex-ante Sharpe 1.13198.
- PV live current reference (`sl=3n4DZ247sp7s5oMf4Umzc5`) maximum-Sharpe: QQQ 24.21%, SPMO 40.86%, GLD 30.00%, XLE 4.94%; expected return 17.19%; volatility 13.08%; Sharpe 1.134. Exact deltas are in the validation file.
- Up/down local count: 84 positive / 36 negative benchmark months. Known local/PV source deviation remains July 2026 SPY -0.68027% vs PV +0.03%.
- Browser report: YES via localhost HTTP. No screen blocker.
  - Portfolio Growth: blue `stroke=#2563eb`; second green `stroke=#22c55e`; legend green `rgb(34, 197, 94)`.
  - Annual Returns: blue/green `fill=#2563eb/#22c55e`; legend green `rgb(34, 197, 94)`.
  - Annualized Active Return: blue/green `fill=#2563eb/#22c55e`; legend green `rgb(34, 197, 94)`.
  - Drawdowns, Rolling 3Y Returns, Rolling 5Y Returns: blue/green `stroke=#2563eb/#22c55e`; legend green `rgb(34, 197, 94)`.
- Full raw evidence: `runs/20260829-us3m-tbill-validation/validation/visual-comparison.md`.
- Artifact commit: `982cdfc40e56199a23e3e987868b2f356f73bec2`.
