# 020-kaw-native-vs-revised-core-backtest

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260910-0001` |
| Product | Backtest |
| Study | `kaw-target-reconstruction` |
| Experiment | `020-kaw-native-vs-revised-core-backtest` |
| Period | 2021-11 ~ 2026-08 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-10 |

## Purpose

Historical comparison of KAW Native Proxy Canonical, KAW Core Revised Internal against State Street SPDR S&P 500 ETF Trust (SPY).

## Portfolios

| Portfolio | Allocation |
|---|---|
| KAW Native Proxy Canonical | 133690 10%, 402970 10%, 069500 8%, 192090 8.5%, 200250 8.5%, 101280 5%, 267440 15%, 385560 15%, GLD 20% |
| KAW Core Revised Internal | QQQ 10%, SCHD 10%, EWY 8%, 192090 8.5%, 200250 8.5%, EWJ 5%, TLT 30%, GLD 20% |

## Key Results

| Portfolio | CAGR | Annualized Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|
| KAW Native Proxy Canonical | 9.60% | 9.67% | 9.70% | -13.83% | 0.6 | 0.898 |
| KAW Core Revised Internal | 10.28% | 10.41% | 10.80% | -12.80% | 0.608 | 0.876 |
| benchmark | 16.74% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0001/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
