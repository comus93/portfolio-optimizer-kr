# 018-kaw-bond-usd-local-proxy-backtest

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260909-0015` |
| Product | Backtest |
| Study | `kaw-target-reconstruction` |
| Experiment | `018-kaw-bond-usd-local-proxy-backtest` |
| Period | 2021-11 ~ 2026-08 |
| Benchmark | State Street SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | USD |
| Created | 2026-09-09 |

## Purpose

Historical comparison of TLT Local USD, EDV Local USD, ZROZ Local USD against State Street SPDR S&P 500 ETF Trust (SPY).

## Portfolios

| Portfolio | Allocation |
|---|---|
| TLT Local USD | TLT 100% |
| EDV Local USD | EDV 100% |
| ZROZ Local USD | ZROZ 100% |

## Key Results

| Portfolio | CAGR | Annualized Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|
| TLT Local USD | -8.07% | -7.33% | 14.65% | -42.04% | -0.762 | -0.942 |
| EDV Local USD | -12.58% | -11.35% | 20.25% | -53.23% | -0.75 | -0.939 |
| ZROZ Local USD | -14.60% | -13.32% | 21.94% | -56.23% | -0.782 | -0.975 |
| benchmark | 12.76% | 13.28% | 15.70% | -23.93% | 0.601 | 0.94 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0015/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
