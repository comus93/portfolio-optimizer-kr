# 009-decomp-gold-to-core-max-sharpe

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0003` |
| Product | Optimization |
| Study | `kaw-target-reconstruction` |
| Experiment | `009-decomp-gold-to-core-max-sharpe` |
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
| Provided Portfolio | 069500 8%, 101280 5%, 133690 10%, 168580 8.5%, 200250 8.5%, 385560 15%, 402970 10%, GLD 20%, TLT 15% |
| Optimized Portfolio | 069500 0.19%, 101280 14.66%, 133690 16.55%, 168580 0%, 200250 0%, 385560 0%, 402970 15.65%, GLD 52.95%, TLT 0% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 9.93% | 10.01% | 10.01% | 10.11% | -14.29% | 0.61 | 0.908 |
| optimized | 21.11% | 19.87% | 19.87% | 10.80% | -10.67% | 1.485 | 2.823 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0003/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
