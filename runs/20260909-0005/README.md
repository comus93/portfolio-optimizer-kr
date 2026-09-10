# 011-decomp-em-to-core-max-sharpe

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0005` |
| Product | Optimization |
| Study | `kaw-target-reconstruction` |
| Experiment | `011-decomp-em-to-core-max-sharpe` |
| Period | 2021-11-01 ~ 2026-08-31 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-09 |

## Purpose

Portfolio optimization and historical evaluation using the persisted run configuration.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | 069500 8%, 101280 5%, 132030 20%, 133690 10%, 385560 15%, 402970 10%, EEM 17%, TLT 15% |
| Optimized Portfolio | 069500 0%, 101280 14%, 132030 36.57%, 133690 17.04%, 385560 0%, 402970 32.39%, EEM 0%, TLT 0% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 10.17% | 10.32% | 10.32% | 11.01% | -16.20% | 0.588 | 0.914 |
| optimized | 16.66% | 15.93% | 15.93% | 9.37% | -8.23% | 1.291 | 2.355 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0005/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
