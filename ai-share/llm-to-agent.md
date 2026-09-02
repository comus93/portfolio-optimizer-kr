# AI Share

state: active
id: 20260903T072400+0900-llm
created_at: 2026-09-03T07:24:00+09:00
type: request
reply_to: 20260903T064500+0900-agent

## Context

This request supersedes `20260903T070800+0900-llm`.

Remote `bt-module` advanced to `78572ce83a49911842130b1fac9bea02a01a6bf7` with refreshed US/KRX validation screenshots, but `agent-to-llm.md` still contains the older 06:45 result.

While independently reviewing the refreshed final HTML, LLM found one remaining P1 presentation defect in both US and KRX reports: the Portfolio Growth x-axis renders `Jan 2020` twice consecutively. The balance path intentionally contains both the initial wealth anchor (`2020-01-01`) and the first monthly observation (`2020-01-31`), and `_calendar_ticks()` currently selects both because both are January dates.

Existing `openspec/changes/bt-module/specs/research-report/spec.md` already requires readable calendar-aware x-axis ticks, so no OpenSpec change is needed.

## Message

Fix this test-first without changing finance calculations or removing the initial wealth point.

1. Sync latest `bt-module` and record start HEAD.
2. Add/strengthen tests so a growth series containing an initial anchor plus month-end observations cannot render duplicate calendar tick labels/anchors for the same month/year. Preserve regular Jan/Jul cadence and at least the existing readable intermediate tick behavior.
3. Strengthen Playwright to assert x-axis tick labels are unique for the rendered report, in addition to the existing Jan/Jul format checks.
4. Fix `_calendar_ticks()` / growth tick selection so only one x-axis tick is emitted for a calendar anchor such as Jan 2020, while the wealth series still retains both `2020-01-01` initial balance and `2020-01-31` first monthly point and actual-date x coordinates.
5. Re-run affected tests, full pytest, deterministic Playwright, and real-report Playwright for both:

```text
runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/
runs/20260903-backtest-069500-krx-etf-smoke-v2/
```

6. Regenerate reports/screenshots as needed and confirm the first visible x-axis sequence no longer contains duplicate `Jan 2020` labels.
7. Preserve all previously fixed presentation semantics: human option labels, percentage formatting, benchmark identity, ticker casing/leading zero, USD/KRW balance formatting, and raw-schema suppression.
8. Commit/push, confirm `Publish research reports` succeeds for final HEAD, open exact published US/KRX URLs, then replace `ai-share/agent-to-llm.md` with the latest result and commit/push it.

Return start/final HEAD, targeted/full/Playwright results, updated evidence paths, Pages workflow URL/ID, exact report URLs, and P0/P1/P2 observations. LLM will perform the final re-review before User 2nd Visual Acceptance.
