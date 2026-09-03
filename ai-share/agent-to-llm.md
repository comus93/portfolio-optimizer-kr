# AI Share

state: active
id: 20260903T170500+0900-agent
created_at: 2026-09-03T17:05:00+09:00
type: result
reply_to: 20260903T153500+0900-llm

## Message

Request id: `20260903T153500+0900-llm`.

Start HEAD: `4e95df10f2399c4901d2325c7d1e99a370907bf3`; worktree was clean after remote sync. Validation environment: uv `0.11.31`, Node `v24.18.0`, npm `11.16.0`, Playwright `1.62.1`.

Final functional HEAD: `95bfc6c6c1aeb19746f39fa4535d2897be95e808` (`Validate Backtest visual acceptance reports`). This handoff document is committed separately after that functional commit.

## Defect fixed

Visual review found US Target Allocation columns had become alphabetical despite persisted input ordering. Root cause: deterministic `result.json` key sorting reordered `portfolio_definitions`. The functional commit adds an explicit `portfolio_order` list from `BacktestRequest` and makes the renderer prefer it. Small regressions cover result construction and renderer preference. The regenerated US report now renders `Growth 70/30`, `Balanced 50/50`, then benchmark.

## Commands and results

- `uv run python -m compileall -q src/portfolio_optimizer_kr`
- `uv run python -m pytest -q tests/test_analytics.py tests/test_pipeline.py tests/test_reporting.py tests/test_interactive_report_contract.py tests/test_report_visual_identity.py tests/test_report_golden_fidelity.py tests/test_report_p1_polish.py tests/test_report_user_feedback_v2.py tests/test_report_user_feedback_v3.py tests/test_report_user_feedback_v4.py tests/test_backtest.py tests/test_backtest_execution.py tests/test_backtest_input_persistence.py tests/test_backtest_report_presentation.py tests/test_backtest_report_content_contract.py tests/test_active_visual_reference_contract.py tests/test_shared_historical_capabilities.py tests/test_shared_artifact_persistence.py tests/test_backtest_shared_end_to_end.py tests/test_shared_market_data_preparation.py`: **105 passed**.
- `BACKTEST_REPORT_PATH=runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html npm run verify:browser:report`: **2 passed, 2 skipped** (fixture-only real-report skips).
- `BACKTEST_REPORT_PATH=runs/20260903-backtest-069500-krx-etf-smoke-v2/report.html npm run verify:browser:report`: **2 passed, 2 skipped** (same fixture-only skips).

Both representative runs were regenerated with the same run IDs from safe copies of persisted inputs. SHA-256 comparison confirmed `input_identical: True` for both. US retained QQQ/GLD, SPY, USD, and its financial inputs; KRX retained `069500`, no benchmark, and KRW.

## Visual acceptance checklist

Actual local-browser review plus desktop/Android-portrait Playwright captures: **PASS** for all items.

1. **PASS** — one union-asset allocation matrix; input portfolio order is preserved and comparison remains readable.
2. **PASS** — Growth has calendar/currency axes and grid; shared-x tooltip displayed both portfolios plus SPY with matching color dots.
3. **PASS** — grouped Annual Returns is directly below Growth in Summary.
4. **PASS** — Trailing Returns has the requested grouped headers and December 2025 as-of note.
5. **PASS** — US Annualized Active Return is grouped bars with percent scale/grid and benchmark context.
6. **PASS** — US Cumulative Active Return renders separate portfolio-vs-benchmark diverging stacked contribution bars plus readable 1Y/3Y/5Y tables.
7. **PASS** — US rolling active panels show bars, Tracking Error line, dual scales, and shared hover behavior.
8. **PASS** — US Up/Down table has grouped occurrences/average-active headers and explicit Total; Return vs Benchmark is paired bars.
9. **PASS** — portfolio and benchmark drawdown panels have calendar ticks, percent grid/zero baseline, and inspectable marks.
10. **PASS** — drawdown tables include Rank, Start, End, Length, Recovery By, Recovery Time, Underwater Period, Drawdown; max ten rows.
11. **PASS** — Assets is split into Portfolio Assets and grouped Portfolio Asset Performance; no Expense Ratio is invented.
12. **PASS** — correlation heatmap has Ticker/Name identities, readable two-decimal coefficients, blue intensity, and scroll-safe table wrapper.
13. **PASS** — readable Return/Risk Decomposition tables retain ticker/name and human portfolio labels.
14. **PASS** — Annual Asset Returns is the single grouped-bar view with percent grid, legend, shared year behavior; no adjacent legacy duplicate table.
15. **PASS** — Rolling summary has 1/3/5-year Average/High/Low groups; 3Y/5Y charts have axes, grid, legend, and shared-x behavior.

Cross-cutting PASS: tooltips render visibly, series identity is text plus color, benchmark trails portfolios, no required clipped axes at desktop/mobile width, no primary storage labels leaked, KRX has no Active Returns section, `069500` remains exact, and USD/KRW formats are correct.

Architecture sanity: `backtest_renderer.py`, `historical_active_components.py`, and `shared_historical_overlay.py` all reuse `pv_visual.py` components for matching historical presentation. Renderer scope only selects/formats persisted canonical values; no new finance calculation was found there.

## Evidence and delivery

- US: `runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html`
- US evidence: `runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/validation/desktop.png`, `validation/mobile.png`, `validation/README.md`
- KRX: `runs/20260903-backtest-069500-krx-etf-smoke-v2/report.html`
- KRX evidence: `runs/20260903-backtest-069500-krx-etf-smoke-v2/validation/desktop.png`, `validation/mobile.png`, `validation/README.md`

Validate workflow [33732668608](https://github.com/comus93/portfolio-optimizer-kr/actions/runs/33732668608): **success** on the final functional SHA. Publish Pages workflow [33732668260](https://github.com/comus93/portfolio-optimizer-kr/actions/runs/33732668260): **success**. Both public URLs returned HTTP 200:

- https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html
- https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-069500-krx-etf-smoke-v2/report.html

P0/P1/P2: none remaining in this requested visual-review/shared-historical scope.
