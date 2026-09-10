# Backtest run: Sample Portfolio vs Portfolio 2 vs Portfolio 3

## Metadata

| Field | Value |
|---|---|
| Run ID | `20260903-backtest-pv-reference-parity-v1` |
| Product | Backtest |
| Study | `N/A` |
| Experiment | `N/A` |
| Period | 2020-01 ~ 2026-07 |
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
| Sample Portfolio | 11.78% | 11.95% | 12.44% | -22.25% | 0.733 | 1.142 |
| Portfolio 2 | 19.51% | 19.45% | 17.41% | -22.35% | 0.954 | 1.608 |
| Portfolio 3 | 19.07% | 19.01% | 17.02% | -20.05% | 0.95 | 1.576 |
| benchmark | 15.13% | 15.61% | 17.05% | -23.93% | 0.749 | 1.196 |

## Notes

Generated from persisted run artifacts for human/LLM navigation. Canonical values remain in `result.json` and `raw/`.

## Artifacts

- [Public Report](https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-pv-reference-parity-v1/report.html)
- [Report](report.html)
- [Input](input.yaml)
- [Result](result.json)
- [Raw tables](raw/)
- [Review tables](review/)
