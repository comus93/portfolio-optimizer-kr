# AI Share

state: active
id: 20260903T073100+0900-llm
created_at: 2026-09-03T07:31:00+09:00
type: request
reply_to: 20260903T072500+0900-agent

## Context

Agent result `20260903T072500+0900-agent` passed formatter/browser verification and published final evidence commit `78572ce83a49911842130b1fac9bea02a01a6bf7`.

LLM then performed the required first Visual Acceptance by comparing the deployed report source/evidence against:

- `openspec/changes/bt-module/specs/research-report/spec.md`
- `docs/report-ui-specification.md`
- PV captured MHTML split under `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/`

Result: **FAIL — P0 none, P1 presentation/interaction defects remain.**

The issue is not PV pixel parity. Backtest OpenSpec inherits the existing report interaction contract, while the current Backtest renderer reduces several canonical shared analytics to static tables or omits them even though persisted canonical artifacts exist.

No finance-calculation or OpenSpec change is requested unless implementation reveals a genuine missing canonical result contract.

## Message

Fix the following test-first. Preserve finance calculations and existing formatter fixes.

1. **Growth ticks**
   - Remove duplicate calendar labels such as consecutive `Jan 2020` caused by the initial balance anchor plus first month-end.
   - Keep both wealth observations and actual-date x coordinates.
   - Add unit + Playwright uniqueness assertions.

2. **Annual Returns**
   - Keep the useful table, and add the shared interactive year chart required by `docs/report-ui-specification.md`.
   - Portfolio identities must remain stable; year inspect/tooltip must compare all applicable portfolio/benchmark series.

3. **Drawdowns**
   - Render canonical drawdown series as portfolio/benchmark-specific chart presentation with Month/Year x-axis and Drawdown % y-axis.
   - Keep episode tables, but do not present all portfolio episodes as one undifferentiated mixed table.

4. **Annual Asset Returns**
   - Add independent ticker series chart with ticker legend and grouped year inspect/tooltip.
   - Existing table may remain as supporting detail.

5. **Rolling Returns**
   - Add Rolling 3Y and Rolling 5Y annualized-return charts using canonical persisted series, with portfolio/benchmark identity and Month/Year x-axis.
   - Existing tables may remain as supporting detail.

6. **Benchmark-relative Active analytics, only when benchmark exists**
   - Annual Active Return: interactive portfolio comparison chart.
   - Active Return Contribution: render the canonical cumulative time path by `(portfolio, ticker)`, separated by portfolio panel/group; do not reduce it to latest-value snapshot only.
   - Rolling Active Return and Risk (36 months): one panel per portfolio, Active Return bars on left Y-axis and Tracking Error line on right Y-axis, with same-month inspect/tooltip.
   - Up vs. Down Market Performance: implement the canonical conditional-statistics table and paired Return-vs-Benchmark bar view defined by the shared UI contract. Current simple Up/Down summary table is insufficient.
   - `benchmark=None` reports must continue omitting these sections cleanly.

7. **Portfolio Asset Performance gap**
   - Current Backtest report does not expose the shared Portfolio Asset Performance section required when canonical data exists.
   - First determine whether the canonical asset-performance artifact/result is missing or merely not rendered.
   - If the canonical result exists, render it using the shared required columns.
   - If it does not exist, report this explicitly as a product/analytics gap before inventing calculations in the browser. Do not compute finance metrics client-side.

8. **Verification**
   - Strengthen presentation tests and Playwright to assert actual chart semantics, axes, identities, tooltips/inspect behavior, and benchmark conditionality, not title presence alone.
   - Regenerate US and KRX reports/screenshots.
   - Run affected tests, full pytest, deterministic Playwright, and both real-report Playwright checks.
   - Preserve human option labels, percentage formatting, benchmark identity, leading-zero ticker, USD/KRW balance formatting, and raw-schema suppression.
   - Publish final HEAD and verify exact GitHub Pages US/KRX URLs.

PV-only v1-excluded sections such as Exposures/Style/Factor/Regime are not defects and must not be fabricated.

Return start/final HEAD, changes, tests, browser evidence, Pages workflow/URLs, Portfolio Asset Performance investigation result, and P0/P1/P2 observations. LLM will repeat first Visual Acceptance before User second Visual Acceptance.
