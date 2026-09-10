# 001-base-r02

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260828-0001` |
| Product | Optimization |
| Study | `seven-asset-frontier-e2e` |
| Experiment | `001-base-r02` |
| Period | N/A |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | USD |
| Created | 2026-08-28 |

## Purpose

Portfolio optimization and historical evaluation using the persisted run configuration.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | AIA 15%, GDX 10%, GLD 0%, QQQ 40%, SLV 10%, SPMO 10%, XLE 15% |
| Optimized Portfolio | AIA 0%, GDX 3.01%, GLD 30%, QQQ 21.93%, SLV 0%, SPMO 41.44%, XLE 3.62% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 18.50% | 18.42% | 18.42% | 16.41% | -22.48% | 0.979 | 1.694 |
| optimized | 18.02% | 17.51% | 17.51% | 13.04% | -18.48% | 1.163 | 2.092 |
| benchmark | 10.87% | 11.46% | 11.46% | 14.74% | -50.78% | 0.617 | 0.92 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
