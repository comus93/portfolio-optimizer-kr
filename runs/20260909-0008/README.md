# 014-decomp-japan-to-core-max-sharpe

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0008` |
| Product | Optimization |
| Study | `kaw-target-reconstruction` |
| Experiment | `014-decomp-japan-to-core-max-sharpe` |
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
| Provided Portfolio | 069500 8%, 132030 20%, 133690 10%, 168580 8.5%, 200250 8.5%, 385560 15%, 402970 10%, EWJ 5%, TLT 15% |
| Optimized Portfolio | 069500 0%, 132030 37.13%, 133690 18.25%, 168580 0%, 200250 0%, 385560 0%, 402970 33.81%, EWJ 10.81%, TLT 0% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 8.54% | 8.71% | 8.71% | 9.97% | -15.72% | 0.489 | 0.724 |
| optimized | 16.57% | 15.85% | 15.85% | 9.35% | -8.27% | 1.285 | 2.343 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0008/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
