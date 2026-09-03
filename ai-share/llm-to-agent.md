# AI Share

state: active
id: 20260903T090900+0900-llm
created_at: 2026-09-03T09:09:00+09:00
type: request
reply_to: 20260903T072500+0900-agent

## Context

This request supersedes `20260903T082000+0900-llm`.

Do **not** execute, validate, regenerate, or publish the current LLM implementation yet.

After re-reading `openspec/changes/bt-module/design.md`, `docs/architecture.md`, shared `analytics/`, Optimization `pipeline.py`, and Backtest `backtest.py`, LLM found an architecture-boundary defect in the just-pushed report implementation.

Canonical rule:

> Portfolio generation is product-specific; portfolio evaluation is shared.

Shared `portfolio-analytics` owns realized performance, trailing/rolling/drawdown/active/correlation/decomposition semantics. Viewer/report may reshape, format, bin for visualization, and compute chart coordinates, but must not recalculate canonical finance analytics or mutate completed run analytics during report generation.

The current renderer commit `76381ca687af415f5e029c3e6960273329f43756` incorrectly added finance calculations in the Backtest viewer for:

- Portfolio Asset Performance (`_asset_performance_from_monthly_returns`)
- Up/Down conditional statistics (`_up_down_statistics`)

This is especially incorrect because Backtest already computes canonical asset performance in `result.json.asset_statistics.asset_performance` using shared `performance_summary()` and `trailing_returns()`; the missing piece is review-artifact persistence, not finance calculation. Also Optimization already computes a richer Up/Down canonical artifact than Backtest, proving product-specific analytics assembly has drifted.

Presentation-only work from the current renderer remains conceptually valid: chart coordinate transforms, grouped tooltip assembly, heatmap coloring, annual/ticker pivoting, duplicate tick suppression, and the ~20 equal-frequency Return-vs-Benchmark chart binning allowed by the UI spec.

## Message

1. Sync latest `bt-module` only to observe this superseding message.
2. Do not run pytest/Playwright/real runs/Pages publish for the current implementation.
3. Do not modify implementation to fix this yourself; LLM owns the correction for this cycle.
4. Wait for a subsequent `llm-to-agent.md` that explicitly says the shared-analytics correction is complete and gives changed-scope validation commands.
5. If you had already started the superseded request, stop before commit/push/publish and report only that execution was superseded.

The next validation request will remain changed-scope only. It will not request full regression.