# 016-kaw-direct-v2-vs-core-backtest

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0013` |
| Product | Backtest |
| Study | `kaw-target-reconstruction` |
| Experiment | `016-kaw-direct-v2-vs-core-backtest` |
| Period | 2021-11 ~ 2026-08 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-09 |

## Purpose

Historical comparison of KAW Direct Proxy v2, KAW Core against State Street SPDR S&P 500 ETF Trust (SPY).

## Portfolios

| Portfolio | Allocation |
|---|---|
| KAW Direct Proxy v2 | 133690 10%, 402970 10%, 069500 8%, 168580 8.5%, 200250 8.5%, 101280 5%, 267440 15%, 385560 15%, 132030 20% |
| KAW Core | QQQ 10%, SPY 10%, EWY 8%, EEM 17%, EWJ 5%, TLT 30%, GLD 20% |

## Key Results

| Portfolio | CAGR | Annualized Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|
| KAW Direct Proxy v2 | 8.26% | 8.44% | 9.85% | -15.70% | 0.467 | 0.689 |
| KAW Core | 12.11% | 12.20% | 11.96% | -14.66% | 0.699 | 1.04 |
| benchmark | 16.74% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0013/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
