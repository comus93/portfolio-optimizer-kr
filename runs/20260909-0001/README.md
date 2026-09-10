# 008-core-max-return-vol12

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0001` |
| Product | Optimization |
| Study | `kaw-target-reconstruction` |
| Experiment | `008-core-max-return-vol12` |
| Period | 2021-11-01 ~ 2026-08-31 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | USD |
| Created | 2026-09-09 |

## Purpose

Portfolio optimization and historical evaluation using the persisted run configuration.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | EEM 17%, EWJ 5%, EWY 8%, GLD 20%, QQQ 10%, SPY 10%, TLT 30% |
| Optimized Portfolio | EEM 0%, EWJ 0%, EWY 0%, GLD 39.19%, QQQ 0%, SPY 42.25%, TLT 18.56% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 8.29% | 9.01% | 9.01% | 14.43% | -26.12% | 0.359 | 0.545 |
| optimized | 12.05% | 12.14% | 12.14% | 12.00% | -19.42% | 0.692 | 1.043 |
| benchmark | 12.76% | 13.28% | 13.28% | 15.70% | -23.93% | 0.601 | 0.94 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0001/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
