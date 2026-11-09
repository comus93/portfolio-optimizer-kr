# 001-qld-psq-hedge

## Metadata

| Field | Value |
|---|---|
| Run ID | `20261109-0001` |
| Product | Backtest |
| Study | `qld-psq-hedge-comparison` |
| Experiment | `001-qld-psq-hedge` |
| Period | 2015-11 ~ 2026-08 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-11-09 |

## Purpose

Historical comparison of A - QLD Core, B - QLD PSQ 3% against SPDR S&P 500 ETF Trust (SPY).

## Portfolios

| Portfolio | Allocation |
|---|---|
| A - QLD Core | QLD 35%, SPMO 15%, AIA 5%, XLE 5%, SCHD 5%, GLD 30%, 138920 5% |
| B - QLD PSQ 3% | QLD 35%, SPMO 15%, AIA 5%, XLE 5%, SCHD 5%, GLD 27%, PSQ 3%, 138920 5% |

## Key Results

| Portfolio | CAGR | Annualized Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|
| A - QLD Core | 23.39% | 22.59% | 16.73% | -19.38% | 1.12 | 1.912 |
| B - QLD PSQ 3% | 22.41% | 21.69% | 16.18% | -18.28% | 1.103 | 1.873 |
| benchmark | 16.74% | 16.58% | 14.20% | -17.41% | 0.897 | 1.451 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20261109-0001/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
