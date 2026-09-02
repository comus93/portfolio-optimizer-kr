# Validation evidence

- Generated at the current `bt-module` HEAD with QQQ/GLD, SPY, two portfolios, monthly rebalancing, calendar alignment, and an initial balance of $10,000.
- FinanceDataReader returned `Adj Close` for QQQ, GLD, and SPY; the canonical loader therefore used the adjusted-price path.
- Effective coverage is 72 monthly observations from 2020-01-31 through 2025-12-31.
- Sanity values: Growth 70/30 end balance $30,468.89 and CAGR 20.40%; Balanced 50/50 end balance $30,181.47 and CAGR 20.21%; SPY end balance $23,293.16 and CAGR 15.13%.
- `BACKTEST_REPORT_PATH=runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html npx playwright test`: 1 passed, 2 skipped (external-report mode).
- `desktop.png` and `mobile.png` are the Playwright report screenshots. Semantic/responsive assertions passed; LLM first-pass visual acceptance remains pending.
