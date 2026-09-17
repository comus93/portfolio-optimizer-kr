# Provided Portfolio v1 - AIA + SCHD + Soybean Maximum Sharpe 2015-11

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260917-0001` |
| Product | Optimization |
| Study | `provided-portfolio-v1-optimization` |
| Experiment | `009-aia-schd-soybean-max-sharpe-2015_11` |
| Period | 2015-11-01 ~ 2026-08-31 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-17 |

## Purpose

Evaluate the same eight-asset TOBE portfolio and provided weights as experiment 008 from 2015-11 through 2026-08, optimizing for maximum Sharpe ratio with the same asset bounds and monthly rebalancing.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | 138920 5%, 144600 5%, AIA 15%, GLD 15%, QQQ 20%, SCHD 5%, SPMO 20%, XLE 15% |
| Optimized Portfolio | 138920 4.1%, 144600 0%, AIA 6.12%, GLD 37.28%, QQQ 23.61%, SCHD 12.96%, SPMO 15.93%, XLE 0% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 17.65% | 17.08% | 17.08% | 11.98% | -14.86% | 1.105 | 1.846 |
| optimized | 17.80% | 17.04% | 17.04% | 10.49% | -10.49% | 1.258 | 2.242 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.20% | -17.41% | 0.897 | 1.451 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260917-0001/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
