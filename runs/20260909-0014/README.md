# 017-kaw-bond-sleeve-proxy-backtest

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0014` |
| Product | Backtest |
| Study | `kaw-target-reconstruction` |
| Experiment | `017-kaw-bond-sleeve-proxy-backtest` |
| Period | 2021-11 ~ 2026-08 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-09 |

## Purpose

Historical comparison of Native Bond 50/50, TLT Proxy, EDV Proxy, ZROZ Proxy against State Street SPDR S&P 500 ETF Trust (SPY).

## Portfolios

| Portfolio | Allocation |
|---|---|
| Native Bond 50/50 | 267440 50%, 385560 50% |
| TLT Proxy | TLT 100% |
| EDV Proxy | EDV 100% |
| ZROZ Proxy | ZROZ 100% |

## Key Results

| Portfolio | CAGR | Annualized Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|
| Native Bond 50/50 | -7.25% | -6.47% | 14.55% | -34.18% | -0.709 | -0.93 |
| TLT Proxy | -4.82% | -3.97% | 13.90% | -34.38% | -0.562 | -0.689 |
| EDV Proxy | -9.49% | -8.17% | 18.82% | -47.05% | -0.638 | -0.789 |
| ZROZ Proxy | -11.59% | -10.19% | 20.38% | -50.45% | -0.688 | -0.845 |
| benchmark | 16.74% | 16.58% | 14.30% | -13.40% | 0.891 | 1.47 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0014/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
