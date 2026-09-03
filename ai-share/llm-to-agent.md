# AI Share

state: active
id: 20260903T153500+0900-llm
created_at: 2026-09-03T15:35:00+09:00
type: request
reply_to: 20260903T121200+0900-agent

## Context

The user completed a direct visual review of the Backtest report against the captured Portfolio Visualizer Backtest reference and supplied multiple PV screenshots. The LLM has now implemented the entire accepted visual/UI correction batch directly on `bt-module`.

This request **supersedes** the previous Active-only handoff in this file.

Primary acceptance contract:

- `docs/validation/20260903-pv-backtest-user-visual-acceptance.md`

Reference material:

- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml`
- extracted `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/page.part-*.html`
- `docs/validation/20260903-1356-KST-pv-backtest-content-comparison-run-20260903-backtest-qqq-gld-spy-presentation-validation-v2.md`

Important architecture rule:

> canonical finance calculations remain upstream; report/browser code may perform presentation-only transforms but must not invent financial values.

The new PV historical visual components are shared between Backtest and the Optimization historical overlay where canonical meanings match.

LLM-side affected regression at implementation baseline:

```text
104 passed in 3.43s
```

GitHub Actions validation run: `33726674460`.

## Agent task

### 1. Sync and record baseline

Pull the latest `bt-module` before doing anything else.

Record:

- start HEAD
- current dirty/clean state
- current Python/Node/Playwright environment relevant to validation

Do not reset or overwrite newer remote work.

### 2. Run changed-scope regression first

At minimum run:

```text
uv run python -m compileall -q src/portfolio_optimizer_kr
uv run python -m pytest -q \
  tests/test_analytics.py \
  tests/test_pipeline.py \
  tests/test_reporting.py \
  tests/test_interactive_report_contract.py \
  tests/test_report_visual_identity.py \
  tests/test_report_golden_fidelity.py \
  tests/test_report_p1_polish.py \
  tests/test_report_user_feedback_v2.py \
  tests/test_report_user_feedback_v3.py \
  tests/test_report_user_feedback_v4.py \
  tests/test_backtest.py \
  tests/test_backtest_execution.py \
  tests/test_backtest_input_persistence.py \
  tests/test_backtest_report_presentation.py \
  tests/test_backtest_report_content_contract.py \
  tests/test_active_visual_reference_contract.py \
  tests/test_shared_historical_capabilities.py \
  tests/test_shared_artifact_persistence.py \
  tests/test_backtest_shared_end_to_end.py \
  tests/test_shared_market_data_preparation.py
```

If the local environment requires the established Windows-safe equivalent, use it without changing project semantics.

### 3. Regenerate both representative Backtests from unchanged persisted inputs

Regenerate exactly these runs, keeping the same run IDs and financial inputs:

**US benchmarked run**

`runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/input.yaml`

Expected role:

- QQQ / GLD
- multiple compared portfolios
- SPY benchmark
- USD
- exercises all benchmark-relative Active content

**KRX no-benchmark run**

`runs/20260903-backtest-069500-krx-etf-smoke-v2/input.yaml`

Expected role:

- `069500` KODEX 200
- KRW
- no benchmark
- exercises no-benchmark conditional behavior and leading-zero ticker identity

Use the existing safe local procedure if deleting/recreating a run directory would remove its input: copy the unchanged input to a safe temporary location, regenerate the same run ID, then verify the persisted input is semantically identical.

Do not change test data, date range, portfolio weights, benchmark, RF, currency, rebalancing, or run ID to make the UI pass.

### 4. Run Playwright against the freshly regenerated reports

For each regenerated report run at minimum:

- `verification/browser/backtest-report-content.spec.mjs`
- `verification/browser/backtest-report.spec.mjs`

using `BACKTEST_REPORT_PATH` for the actual regenerated `report.html`.

Validate desktop and a normal modern Android portrait/mobile width. Do not use an unusually narrow Fold cover display as the primary mobile reference.

### 5. Perform an actual first-pass visual review, not DOM-only verification

Open the freshly generated report in a real browser and visually compare it to the PV MHTML fragments/screenshots. The user expects a real visual judgment.

Pixel-perfect cloning is not required. Information hierarchy, chart grammar, axes, tooltip behavior, grouping, readability and semantic equivalence are required.

Explicitly inspect and report PASS/FAIL for **every item 1–15** below.

#### 1. Target Allocation

- one union-asset matrix
- same asset occupies one row across portfolio columns
- portfolio order preserved
- non-held 0% assets visually muted (`—` acceptable)
- multi-portfolio comparison remains readable

#### 2. Portfolio Growth

- readable calendar x-axis and currency y-axis/grid
- shared month hover/nearest-x behavior
- hovering a month shows **all displayed portfolios + benchmark** balances in one tooltip
- user does not have to precisely hit one series point

#### 3. Annual Returns directly under Growth

- grouped Annual Returns chart appears directly below Portfolio Growth in Summary
- dedicated Annual Returns section may also exist for detail

#### 4. Trailing Returns

PV grouped headers:

- Total Return: 3 Month / Year To Date / 1 Year
- Annualized Return: 3 Year / 5 Year / Full
- Annualized Standard Deviation: 3 Year / 5 Year
- as-of last completed calendar month note

#### 5. Annualized Active Return — US run

- grouped annual bars
- readable percent y-axis/ticks/grid
- shared year hover lists every compared portfolio
- benchmark comparison context visible

#### 6. Cumulative Active Return / contribution — US run

For each portfolio:

- separate panel vs benchmark
- monthly asset contributions are **diverging stacked bars**
- not a line chart
- not side-by-side grouped asset bars
- positive stack above zero, negative below zero
- readable axes/calendar labels
- shared month hover lists all asset contributions
- compact 1Y/3Y/5Y contribution information, where rendered, is readable and numerically plausible

#### 7. Rolling Active Return and Risk — US run

Per portfolio:

- Active Return bars on left percent scale
- Tracking Error line on right percent scale
- both scales/ticks visible and unclipped
- shared month hover shows both values

#### 8. Up / Down Market Performance — US run

Table:

- grouped `Occurrences` header
- Above Benchmark / Below Benchmark / Total / % Above Benchmark
- grouped `Average Active Return` header
- Above / Below / Total
- explicit `Total` row across Up + Down

Return vs Benchmark:

- paired bars
- readable axes
- shared hover shows paired values and observation count where available

#### 9. Drawdown charts

For every portfolio and benchmark panel:

- x-axis/calendar ticks
- Drawdown % y-axis/ticks
- horizontal grid
- visible 0% baseline
- hover/inspect works
- labels are not clipped

#### 10. Drawdown episode recovery information

Worst drawdown table includes:

- Rank
- Start
- End
- Length
- Recovery By
- Recovery Time
- Underwater Period
- Drawdown

Unrecovered episodes use `N/A`; default view is worst 10 or fewer if fewer episodes exist.

#### 11. Assets section split

**Portfolio Assets** contains:

- Ticker / Name / CAGR / Stdev / Best Year / Worst Year / Max Drawdown / Sharpe / Sortino

**Portfolio Asset Performance** contains grouped trailing returns:

- Total Return: 3 Month / YTD / 1 Year
- Annualized Return: 3 Year / 5 Year
- as-of note

Confirm Expense Ratio is **not fabricated**.

#### 12. Monthly Correlations

- PV-style heatmap matrix
- readable two-decimal coefficients
- identities distinguish assets, portfolios, benchmark
- blue intensity useful/readable
- horizontal scrolling does not destroy header/row readability

#### 13. Portfolio Return / Risk Decomposition

Both are present and readable:

- Portfolio Return Decomposition
- Portfolio Risk Decomposition

Confirm ticker/name identities and portfolio columns are understandable and storage labels do not leak into user-facing UI.

#### 14. Annual Asset Returns

This **replaces** the old duplicate UI:

- grouped bars by year
- asset colors stable
- percent y-axis/grid
- bottom legend
- shared year hover lists every asset for that year
- no duplicate legacy Annual Asset Returns presentation beside it

#### 15. Rolling Returns

Top summary:

- rows 1 Year / 3 Years / 5 Years
- each portfolio and benchmark grouped into Average / High / Low
- negative lows remain legible

Charts below:

- Annualized Rolling Return - 3 Years
- Annualized Rolling Return - 5 Years
- readable axes/grid/legend
- shared month hover lists all portfolios + benchmark
- no raw rolling time-series dump as primary UI

### 6. Cross-cutting checks

US and KRX as applicable:

- structured tooltips are visible in browser, not only `aria-label`
- tooltip color dots match chart/legend identity
- shared-x tooltip semantics are consistent across Growth, annual grouped charts and rolling charts
- no clipped y-axis labels at desktop/mobile widths
- no chart missing y ticks/grid where the acceptance contract requires them
- portfolio identity is not color-only
- benchmark appears after portfolio series
- KRX report has **no Active Returns section**
- `069500` remains exactly `069500`, never `69500` / `69500.0`
- KRW formatting remains KRW; US remains USD
- no raw `_pct`, snake_case or storage/debug labels leak into primary UI

### 7. Architecture sanity

Inspect the changed files, especially:

- `src/portfolio_optimizer_kr/viewer/pv_visual.py`
- `src/portfolio_optimizer_kr/viewer/historical_active_components.py`
- `src/portfolio_optimizer_kr/viewer/backtest_renderer.py`
- `src/portfolio_optimizer_kr/viewer/shared_historical_overlay.py`

Confirm that shared canonical historical views are actually reused between Backtest and Optimization where their contracts match.

If you discover a changed-scope case where a renderer is calculating a new financial metric rather than merely formatting/selecting persisted canonical values, treat it as a real defect: move that calculation to the proper upstream shared analytics/artifact boundary, add the smallest regression, and rerun validation.

Do not create a new module merely to avoid editing an existing shared analytics module unless there is a genuine cohesive module boundary.

### 8. Fix real defects found during validation

You are authorized to fix actual defects exposed by this validation **within this visual-review/shared-historical scope**.

For every fix:

1. identify the root cause
2. add/update the smallest regression that would have caught it
3. rerun the affected Python tests
4. regenerate the affected report
5. rerun Playwright/visual inspection

Do not do unrelated cleanup, broad refactors or redesign.

### 9. Evidence

Capture fresh evidence from the regenerated reports:

- US desktop screenshot(s), enough to review Summary + Active + Drawdowns + Assets + Rolling
- US mobile screenshot(s)
- KRX desktop screenshot(s)
- KRX mobile screenshot(s)

Store evidence in the established validation/evidence location under the corresponding run or `docs/validation` convention already used by the repo. Do not commit transient Playwright traces unless they are needed to explain a defect.

### 10. Commit, push and Pages

Commit/push:

- regenerated US/KRX run artifacts/reports
- validation evidence
- any changed-scope fixes and regressions
- Agent validation report

Push `bt-module`.

Confirm:

- `Validate bt-module refactor` succeeds on the final functional HEAD
- `Publish research reports` succeeds
- GitHub Pages contains the newly generated reports

Expected public URLs:

```text
https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html
https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-069500-krx-etf-smoke-v2/report.html
```

### 11. Report back

Replace `ai-share/agent-to-llm.md` with the result.

Report all of the following:

- request id: `20260903T153500+0900-llm`
- start HEAD
- final functional HEAD
- any subsequent handoff/report-only HEAD separately
- exact pytest commands + pass counts
- exact Playwright commands + results for US and KRX
- **1–15 visual acceptance checklist with PASS/FAIL and concise evidence**
- desktop/mobile visual review conclusion
- defects discovered and exact fixes
- architecture sanity conclusion, including whether any finance calculation was found in renderer scope
- screenshot/evidence paths
- final US/KRX report paths
- Validate workflow run id/status
- Publish Pages workflow run id/status
- final public US/KRX URLs
- remaining P0/P1/P2 issues

Do not report overall PASS if any P0/P1 visual requirement above is still known to fail.
