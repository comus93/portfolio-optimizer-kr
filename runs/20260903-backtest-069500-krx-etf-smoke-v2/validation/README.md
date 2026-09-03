# Full Backtest visual acceptance evidence

- Regenerated from the persisted, byte-identical `input.yaml` on 2026-09-03.
- `desktop.png`: full-page desktop Chromium capture.
- `mobile.png`: full-page Android portrait Chromium capture.
- Browser validation: `BACKTEST_REPORT_PATH=runs/20260903-backtest-069500-krx-etf-smoke-v2/report.html npm run verify:browser:report` — 2 passed, 2 skipped (fixture-only cases).
- Manual browser review used the locally served regenerated report; it confirms
  the no-benchmark layout, exact `069500` identity, and KRW formatting.
