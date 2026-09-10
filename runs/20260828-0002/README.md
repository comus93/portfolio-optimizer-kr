# 001-base-r02

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260828-0002` |
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
| Optimized Portfolio | AIA 0%, GDX 1.93%, GLD 30%, QQQ 22.01%, SLV 0%, SPMO 42.29%, XLE 3.77% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 17.65% | 17.67% | 17.67% | 16.28% | -22.48% | 0.94 | 1.609 |
| optimized | 17.29% | 16.87% | 16.87% | 12.89% | -18.41% | 1.126 | 2.001 |
| benchmark | 14.50% | 14.74% | 14.74% | 15.05% | -23.93% | 0.823 | 1.299 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
