# Validation evidence

- Generated at the current `bt-module` HEAD with 069500 (KODEX 200), no benchmark, one 100% portfolio, monthly rebalancing, calendar alignment, and an initial balance of KRW 10,000.
- FinanceDataReader `StockListing("ETF/KR")` contained 069500. The default route returned Close-only NAVER data and `FDRLoader` recorded `return_semantics=total_return`, `source_column=Close`, `provider=FinanceDataReader`, and `provider_route=NAVER`.
- Explicit `KRX:069500` was rejected by FinanceDataReader as unsupported; it was not treated as a total-return success.
- Effective coverage is 72 monthly observations from 2020-01-31 through 2025-12-31. End balance is 23,277.49 and CAGR is 15.12%.
- `BACKTEST_REPORT_PATH=runs/20260903-backtest-069500-krx-etf-smoke-v2/report.html npx playwright test`: 1 passed, 2 skipped (external-report mode).
- `desktop.png` and `mobile.png` are the Playwright report screenshots. Semantic/responsive assertions passed; LLM first-pass visual acceptance remains pending.
