# Provided Portfolio v1 - AIA + SCHD Maximum Return Vol 11.5 Same Period

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260910-0016` |
| Product | Optimization |
| Study | `provided-portfolio-v1-optimization` |
| Experiment | `006-aia-schd-max-return-vol11_5-same-period` |
| Period | 2017-09-01 ~ 2026-08-31 |
| Benchmark | SPDR S&P 500 ETF Trust (SPY) |
| Rebalancing | monthly |
| Currency | KRW (USD/KRW normalized) |
| Created | 2026-09-10 |

## Purpose

Evaluate the same seven-asset universe and identical 2017-09 through 2026-08 sample used by experiment 005, changing only the optimization objective from Maximum Sharpe to Maximum Return with an 11.5% annualized volatility ceiling.

## Portfolios

| Portfolio | Allocation |
|---|---|
| Provided Portfolio | 144600 5%, AIA 15%, GLD 15%, QQQ 20%, SCHD 10%, SPMO 20%, XLE 15% |
| Optimized Portfolio | 144600 0%, AIA 0%, GLD 47.62%, QQQ 15.81%, SCHD 5.26%, SPMO 27.05%, XLE 4.27% |

## Key Results

| Portfolio | CAGR | Annualized Return | Expected Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| provided | 19.94% | 19.21% | 19.21% | 13.40% | -15.67% | 1.147 | 1.886 |
| optimized | 20.31% | 19.29% | 19.29% | 11.50% | -11.22% | 1.343 | 2.42 |
| benchmark | 17.88% | 17.69% | 17.69% | 15.06% | -17.41% | 0.919 | 1.466 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0016/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Context](context.yaml)
- [Raw tables](raw/)
- [Review tables](review/)
