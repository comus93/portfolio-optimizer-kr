# PV Backtest round-one validation

Run: `20260903-backtest-pv-reference-parity-yty-v3`

## Automated checks

- Coverage: 2020-01-31 through 2026-08-31, 80 monthly observations.
- Focused regression: PASS.
- Complete PV Risk and Return Metrics comparison: PASS within explicit parity tolerances.
- Generated report HTML contract for the user-requested first-pass review items: PASS.
- Monthly Returns default pagination contract: 12 rows with First / Previous / Next / Last controls.
- Drawdowns: one combined portfolio/benchmark chart plus per-series episode tables, no duplicate per-series charts.
- Active Returns Benchmark Summary removed.
- Annual Asset Returns follows Portfolio Risk Decomposition.
- Right-edge chart tooltip flip contract present.

See `../pv-round1-complete-metric-comparison.md` for the full metric-by-metric comparison.

## Known source-level variance

Perpetual Withdrawal Rate differs from the captured Portfolio Visualizer values by roughly 0.12 to 0.14 percentage points in this run. The implementation uses the decoded PV withdrawal semantics and current CPI/market observations rather than hard-coded reference values.
