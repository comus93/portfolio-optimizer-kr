# Provided Portfolio v1 - AIA + SCHD Maximum Sharpe

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260910-0007` |
| Product | Optimization |
| Study | `provided-portfolio-v1-optimization` |
| Experiment | `004-aia-schd-max-sharpe` |
| Period | 2015-11-01 ~ 2026-08-31 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-10 |

## Purpose

Replace ACE 아시아TOP50 with AIA, move 10 percentage points from QQQ to SCHD, extend the common sample to 2015-11 through 2026-08, and maximize ex-ante Sharpe ratio over the seven-asset universe.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | 144600 5%, AIA 15%, GLD 15%, QQQ 20%, SCHD 10%, SPMO 20%, XLE 15% |
| Optimized Portfolio | 144600 0%, AIA 7.29%, GLD 38.63%, QQQ 23.62%, SCHD 13.9%, SPMO 16.25%, XLE 0.3% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 18.27% | 17.67% | 17.67% | 12.49% | -15.67% | 1.107 | 1.84 |
| optimized | 18.34% | 17.55% | 17.55% | 10.93% | -10.81% | 1.255 | 2.231 |
| benchmark | 16.74% | 16.58% | 16.58% | 14.20% | -17.41% | 0.897 | 1.451 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0007/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
