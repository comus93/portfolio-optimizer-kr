# Validation evidence

- Regenerated at `68c65af` from the unchanged persisted QQQ/GLD, SPY, two-portfolio input with monthly rebalancing, calendar alignment, and a $10,000 initial balance.
- Effective coverage is 72 monthly observations from 2020-01-31 through 2025-12-31.
- `uv run python -m pytest -q tests/test_active_visual_reference_contract.py tests/test_backtest_report_content_contract.py tests/test_backtest_shared_end_to_end.py`: 14 passed.
- `BACKTEST_REPORT_PATH=runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html npm run verify:browser:report`: 2 passed, 2 skipped (fixture-only tests in external-report mode).
- Desktop browser inspection verified readable percent ticks/grids for Annual Active Return; time-series contribution bars with calendar ticks; dual left/right scales, bars, and Tracking Error line for both rolling panels; paired Return vs. Benchmark bars; and a focused Active Contribution tooltip.
- `desktop.png` and `mobile.png` are the regenerated real-run Playwright screenshots. The mobile check found no document or chart overflow, and scrollable tables retained horizontal access.
- LLM first-pass visual acceptance and User second-pass visual review remain separate required gates; this evidence does not claim either completion.
