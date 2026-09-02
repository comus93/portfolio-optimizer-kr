# Backtest Browser Validation

- Report: `runs/20260902-backtest-qqq-gld-spy-renderer-v2/report.html`
- Command: `uv run python scripts/verify.py --browser-report runs/20260902-backtest-qqq-gld-spy-renderer-v2/report.html`
- Automated result: Playwright real-report semantic and responsive acceptance passed.
- Evidence: `desktop.png`, `mobile.png`.

## Agent observations

- P0: none observed.
- P1: none observed.
- P2: none observed.
- The full-page evidence contains long data tables; Playwright confirmed 390px document-level clipping is absent and wide tables/charts retain horizontal-scroll access.

## Visual acceptance

LLM first-pass visual acceptance is pending against the published GitHub Pages report. User second-pass visual acceptance remains pending after the LLM review.
