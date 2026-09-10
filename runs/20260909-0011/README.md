# 015-tobe-vs-kaw-direct-backtest

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0011` |
| Product | Backtest |
| Study | `kaw-target-reconstruction` |
| Experiment | `015-tobe-vs-kaw-direct-backtest` |
| Period | 2022-06 ~ 2026-08 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-09 |

## Purpose

Historical comparison of TO-BE Direct, KAW Direct Proxy against State Street SPDR S&P 500 ETF Trust (SPY).

## Portfolios

| Portfolio | Allocation |
|---|---|
| TO-BE Direct | SPMO 20%, 426030 30%, 277540 15%, 132030 15%, 144600 5%, XLE 15% |
| KAW Direct Proxy | 133690 10%, 402970 10%, 069500 8%, 168580 8.5%, 200250 8.5%, 101280 5%, TLT 15%, 385560 15%, 132030 20% |

## Key Results

| Portfolio | CAGR | Annualized Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|
| TO-BE Direct | 31.06% | 28.69% | 16.63% | -12.27% | 1.495 | 2.972 |
| KAW Direct Proxy | 11.81% | 11.70% | 9.94% | -8.40% | 0.791 | 1.232 |
| benchmark | 20.31% | 19.63% | 14.22% | -11.82% | 1.11 | 1.879 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0011/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
