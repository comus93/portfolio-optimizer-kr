# Backtest run: Sample Portfolio vs Portfolio 2 vs Portfolio 3

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260903-backtest-pv-reference-parity-yty-v4` |
| Product | Backtest |
| Study | `N/A` |
| Experiment | `N/A` |
| Period | 2020 ~ 2026 |
| Benchmark | State Street SPDR S&P 500 ETF (SPY) |
| Rebalancing | yearly (calendar aligned: Yes) |
| Currency | USD |
| Created | 2026-09-03 |

## Purpose

Historical comparison of Sample Portfolio, Portfolio 2, Portfolio 3 against State Street SPDR S&P 500 ETF (SPY).

## Portfolios

| Portfolio | Allocation |
|---|---|
| Sample Portfolio | SPY 60%, GLD 20%, TLT 20% |
| Portfolio 2 | GLD 10%, QQQ 30%, SLV 10%, GDX 10%, AIA 20%, XLF 10%, XLE 10% |
| Portfolio 3 | GLD 10%, QQQ 40%, SLV 10%, EWY 10%, XLE 10%, EWJ 10%, INDY 10% |

## Key Results

| Portfolio | CAGR | Annualized Return | Standard Deviation | Maximum Drawdown | Sharpe Ratio (ex-post) | Sortino Ratio |
|---|---:|---:|---:|---:|---:|---:|
| Sample Portfolio | 12.23% | 12.35% | 12.40% | -22.25% | 0.767 | 1.198 |
| Portfolio 2 | 20.60% | 20.37% | 17.46% | -22.35% | 1.004 | 1.708 |
| Portfolio 3 | 19.95% | 19.77% | 17.06% | -20.05% | 0.992 | 1.655 |
| benchmark | 15.51% | 15.92% | 16.94% | -23.93% | 0.772 | 1.232 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-pv-reference-parity-yty-v4/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Raw tables](raw/)
- [Review tables](review/)
