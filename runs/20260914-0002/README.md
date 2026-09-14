# Provided Portfolio v1 - AIA + SCHD + Soybean Maximum Return Vol 11.5 2015-11

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260914-0002` |
| Product | Optimization |
| Study | `provided-portfolio-v1-optimization` |
| Experiment | `008-aia-schd-soybean-max-return-vol11_5-2015_11` |
| Period | 2015-11-01 ~ 2026-08-31 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-14 |

## Purpose

Evaluate the eight-asset TOBE portfolio from 2015-11 through 2026-08 with KODEX Soybean Futures(H) added at 5% and SCHD reduced to 5%, maximizing return under an 11.5% annualized volatility ceiling.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | 138920 5%, 144600 5%, AIA 15%, GLD 15%, QQQ 20%, SCHD 5%, SPMO 20%, XLE 15% |
| Optimized Portfolio | 138920 0%, 144600 0%, AIA 4.51%, GLD 39.48%, QQQ 31.06%, SCHD 2.39%, SPMO 19.82%, XLE 2.73% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 17.65% | 17.08% | 17.08% | 11.98% | -14.86% | 1.105 | 1.846 |
| optimized | 19.01% | 18.19% | 18.19% | 11.50% | -11.64% | 1.248 | 2.197 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.20% | -17.41% | 0.897 | 1.451 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

Pages publication was explicitly refreshed after the run artifact was persisted so this run is included in the deployed report set.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260914-0002/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
