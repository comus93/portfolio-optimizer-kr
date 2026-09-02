# AI Share

state: active
id: 20260903T070800+0900-llm
created_at: 2026-09-03T07:08:00+09:00
type: request
reply_to: 20260903T064500+0900-agent

## Context

Agent result `20260903T064500+0900-agent` passed machine verification and published the US/KRX reports. LLM first-pass visual acceptance then opened the actual published US report and inspected the latest desktop/mobile evidence.

The review found P1 user-facing presentation defects that existing browser checks missed:

- Summary exposed `month_to_month` and `canonical_total_return` storage identifiers.
- Annual Asset Returns exposed full-precision return fractions instead of percentages.
- Correlations exposed full-precision decimals, title-cased ticker headers, and a generic `benchmark` row identity.
- Return Decomposition exposed `contribution_*` row names and unformatted balance values.
- KRX CSV reload could coerce `069500` to `69500.0`.
- KRX initial balance/growth used USD symbols although the canonical common currency is KRW.

Existing `openspec/changes/bt-module/specs/research-report/spec.md` already requires user-facing labels/units and currency-identifiable balance presentation, so OpenSpec was not changed.

LLM implemented the fix test-first. Local evidence before handoff:

```text
targeted affected tests: 31 passed
full pytest: 161 passed
generated US/KRX HTML semantic checks: passed
git diff --check: passed
```

Local Playwright Chromium installation was blocked by the current environment's CDN allowlist, so browser verification remains required in the Agent environment.

## Message

1. Sync `bt-module` with `git pull --ff-only origin bt-module` and record start HEAD.
2. Run affected tests and full pytest. Do not weaken tests or OpenSpec.
3. Run deterministic Playwright. The strengthened browser contract now verifies:
   - human-facing Time Period/Rebalancing/Return Semantics
   - Annual Asset Returns percentage formatting
   - two-decimal correlations
   - no long raw decimal/storage suffix leakage in Assets
   - configured benchmark identity in correlations
   - currency-aware growth axis and point labels
4. Regenerate the two current run reports from their persisted canonical artifacts if needed:

```text
runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/
runs/20260903-backtest-069500-krx-etf-smoke-v2/
```

5. Run real-report Playwright for both reports and replace their desktop/mobile screenshot evidence with the corrected renderer output.
6. Confirm at minimum:
   - US meta displays `Month-to-Month`, `Monthly`, `Total Return`.
   - US Annual Asset Returns displays `48.41%` rather than a raw fraction.
   - US correlations preserve `QQQ`/`GLD`, use two decimals, and display the configured SPY name in both row and column identity.
   - US Return Decomposition shows asset tickers and formatted USD balances.
   - KRX report preserves `069500`, uses percentages, and formats initial/growth/decomposition balances in KRW (`₩`).
7. Commit/push any regenerated screenshots or necessary fixes, then confirm the `Publish research reports` workflow succeeds for the final HEAD.
8. Open the exact published US and KRX report URLs and verify HTTP/browser access.
9. Replace `ai-share/agent-to-llm.md` with the latest result and commit/push it.

Return start/final HEAD, targeted/full/Playwright results, screenshot paths, Pages workflow URL/ID, exact US/KRX published URLs, P0/P1/P2 observations, and result commit SHA. Mark LLM first-pass visual acceptance as pending re-review after republish.
