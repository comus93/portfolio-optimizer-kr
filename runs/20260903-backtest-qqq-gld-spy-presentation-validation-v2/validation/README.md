# Full Backtest visual acceptance evidence

- Regenerated from the persisted, byte-identical `input.yaml` on 2026-09-03.
- `desktop.png`: full-page desktop Chromium capture (Summary, Active Returns,
  Drawdowns, Assets, and Rolling Returns are included in document order).
- `mobile.png`: full-page Android portrait Chromium capture.
- Browser validation: `BACKTEST_REPORT_PATH=runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html npm run verify:browser:report` — 2 passed, 2 skipped (fixture-only cases).
- Manual browser review used the locally served regenerated report; shared-x
  chart tooltips and section hierarchy were checked in the rendered UI.
