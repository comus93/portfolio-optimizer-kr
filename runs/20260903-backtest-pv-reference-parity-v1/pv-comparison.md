# Portfolio Visualizer parity comparison

Captured PV reference: Jan 2020 - Jul 2026, UI setting Year-to-Year 2020-2026, annual rebalancing, $10,000 initial balance, no cashflows, SPY benchmark.

Parity note: this run locks the effective endpoint to Jul 2026 with month-to-month period input because the current engine's Year-to-Year mode expands 2026 through year-end/current available data, while the captured PV result stops at Jul 2026.

Our effective coverage: 2020-01-31 -> 2026-07-31 (79 observations)

| Series | Metric | PV | Ours | Difference |
| --- | --- | ---: | ---: | ---: |
| Sample Portfolio | End Balance | $20,830 | $20,811.19 | $-18.81 |
| Sample Portfolio | CAGR | 11.79% | 11.78% | -0.01pp |
| Sample Portfolio | Standard Deviation | 12.44% | 12.44% | +0.00pp |
| Sample Portfolio | Best Year | 24.21% | 24.22% | +0.01pp |
| Sample Portfolio | Worst Year | -17.31% | -17.31% | +0.00pp |
| Sample Portfolio | Maximum Drawdown | -22.25% | -22.25% | +0.00pp |
| Sample Portfolio | Sharpe Ratio (ex-post) | 0.74 | 0.733 | -0.007 |
| Sample Portfolio | Sortino Ratio | 1.15 | 1.142 | -0.008 |
| Portfolio 2 | End Balance | $32,393 | $32,331.24 | $-61.76 |
| Portfolio 2 | CAGR | 19.55% | 19.51% | -0.04pp |
| Portfolio 2 | Standard Deviation | 17.40% | 17.41% | +0.01pp |
| Portfolio 2 | Best Year | 54.37% | 54.38% | +0.01pp |
| Portfolio 2 | Worst Year | -9.91% | -9.96% | -0.05pp |
| Portfolio 2 | Maximum Drawdown | -22.30% | -22.35% | -0.05pp |
| Portfolio 2 | Sharpe Ratio (ex-post) | 0.96 | 0.954 | -0.006 |
| Portfolio 2 | Sortino Ratio | 1.62 | 1.608 | -0.012 |
| Portfolio 3 | End Balance | $31,454 | $31,546.69 | $92.69 |
| Portfolio 3 | CAGR | 19.01% | 19.07% | +0.06pp |
| Portfolio 3 | Standard Deviation | 17.04% | 17.02% | -0.02pp |
| Portfolio 3 | Best Year | 42.56% | 42.55% | -0.01pp |
| Portfolio 3 | Worst Year | -11.62% | -11.60% | +0.02pp |
| Portfolio 3 | Maximum Drawdown | -20.06% | -20.05% | +0.01pp |
| Portfolio 3 | Sharpe Ratio (ex-post) | 0.95 | 0.950 | +0.000 |
| Portfolio 3 | Sortino Ratio | 1.58 | 1.576 | -0.004 |
| benchmark | End Balance | $25,478 | $25,280.72 | $-197.28 |
| benchmark | CAGR | 15.26% | 15.13% | -0.13pp |
| benchmark | Standard Deviation | 17.04% | 17.05% | +0.01pp |
| benchmark | Best Year | 28.75% | 28.73% | -0.02pp |
| benchmark | Worst Year | -18.17% | -18.18% | -0.01pp |
| benchmark | Maximum Drawdown | -23.93% | -23.93% | +0.00pp |
| benchmark | Sharpe Ratio (ex-post) | 0.76 | 0.749 | -0.011 |
| benchmark | Sortino Ratio | 1.22 | 1.196 | -0.024 |
