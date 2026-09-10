# 012-decomp-dividend-to-core-max-sharpe

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0006` |
| Product | Optimization |
| Study | `kaw-target-reconstruction` |
| Experiment | `012-decomp-dividend-to-core-max-sharpe` |
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
| Provided Portfolio | 069500 8%, 101280 5%, 132030 20%, 133690 10%, 168580 8.5%, 200250 8.5%, 385560 15%, SPY 10%, TLT 15% |
| Optimized Portfolio | 069500 0%, 101280 14.73%, 132030 37.19%, 133690 0%, 168580 0%, 200250 0%, 385560 0%, SPY 48.07%, TLT 0% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 8.90% | 9.10% | 9.10% | 10.45% | -16.96% | 0.503 | 0.743 |
| optimized | 17.33% | 16.56% | 16.56% | 9.89% | -9.18% | 1.287 | 2.212 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0006/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
