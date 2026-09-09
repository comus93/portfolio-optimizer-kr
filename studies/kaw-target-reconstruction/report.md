# KAW Target Reconstruction Report

> Living report. This file is the canonical research report for the KAW target-reconstruction study and will be updated or appended as follow-up validation proceeds.

## 1. Research question

This study asks whether the current Kim Seong-il K-All Weather portfolio can be reconstructed in two useful forms:

1. **KAW Direct Proxy**: a relatively faithful representation of the current portfolio for recent-period testing.
2. **KAW Core**: a reduced long-history proxy that preserves the portfolio's economic behavior well enough to study long-run trends, regime strengths, and weaknesses.

The Core is **not** required to reproduce Direct Proxy absolute performance exactly. The main bridge criterion is whether it preserves broad market behavior such as monthly direction, drawdown timing, and response to market regimes.

---

## 2. Current KAW target structure

Current target weights used as the reconstruction anchor:

| Sleeve | Current target |
|---|---:|
| Gold | 20.0% |
| US long Treasury | 15.0% |
| KR 30Y Treasury | 15.0% |
| Nasdaq 100 | 10.0% |
| China | 8.5% |
| Korea | 8.0% |
| US dividend | 10.0% |
| India | 8.5% |
| Japan | 5.0% |
| **Total** | **100.0%** |

Strategic cash is 0%. Small cash balances caused only by integer-share execution are not part of the strategic allocation.

---

## 3. Proxy definitions

### 3.1 KAW Direct Proxy

Design principle: preserve the current nine sleeves as directly as practical while extending the common usable history beyond the current native ETF set.

| Sleeve | Proxy | Weight |
|---|---|---:|
| Nasdaq 100 | 133690 TIGER 미국나스닥100 | 10.0% |
| US dividend | 402970 ACE 미국배당다우존스 | 10.0% |
| Korea | 069500 KODEX 200 | 8.0% |
| China | 168580 ACE 중국본토CSI300 | 8.5% |
| India | 200250 KIWOOM 인도Nifty50(합성) | 8.5% |
| Japan | 101280 KODEX 일본TOPIX100 | 5.0% |
| US long Treasury | TLT | 15.0% |
| KR 30Y Treasury | 385560 RISE KIS국고채30년Enhanced | 15.0% |
| Gold | 132030 KODEX 골드선물(H) | 20.0% |

**Common valid test period:** 2021-11 onward.

For the bridge tests in this report, the analysis period is **2021-11-01 to 2026-08-31**.

### 3.2 KAW Core

Design principle: compress sleeves when necessary to obtain substantially longer history while preserving the portfolio's major economic engines.

| Sleeve representation | Proxy | Weight |
|---|---|---:|
| Nasdaq | QQQ | 10.0% |
| US equity / current dividend predecessor | SPY | 10.0% |
| Korea | EWY | 8.0% |
| China + India | EEM | 17.0% |
| Japan | EWJ | 5.0% |
| US + KR long-duration bonds | TLT | 30.0% |
| Gold | GLD | 20.0% |

**Long-history usable period:** 2006-01 onward.

All Core assets existed before 2006, so 2006-01 is used as the conservative long-horizon study start. For bridge validation against Direct Proxy, Core is restricted to the same **2021-11-01 to 2026-08-31** period.

---

## 4. Common experiment conditions

Unless a later experiment explicitly states otherwise, KAW reconstruction studies use:

- Rebalancing: monthly
- Asset bounds for optimization: 0% to 60%
- Reporting currency: KRW
- USD assets: converted through USD/KRW when KRW reporting is requested
- Benchmark: SPY
- Common bridge period: 2021-11-01 to 2026-08-31

### 4.1 Study-wide risk-free-rate convention

The dynamic `risk_free.mode: us_3m_tbill` path currently depends on FinanceDataReader/FRED resolving `TB3MS` on every run. This caused a reproducibility failure during the Core rerun.

Until that provider/caching issue is fixed, **all KAW-related follow-up research should reuse the same fixed annual risk-free rate unless explicitly overridden:**

- **Annual risk-free rate: 3.8394827586206895%**
- Decimal form: `0.038394827586206895`
- Source: successful Direct Proxy run `runs/20260908-0002/result.json`

This is a study-level convention, not a new framework-wide economic assumption.

Tracking issue:
- GitHub Issue #1: https://github.com/comus93/portfolio-optimizer-kr/issues/1

---

## 5. Real Kim Seong-il direct-account reference

Reference performance supplied from the actual direct-investment account:

- Operation period: 2024-01-26 to 2026-07-31
- Total return: 51.89%
- Annualized return: 18.11%
- Annual volatility: 10.52%
- Maximum drawdown: -9.14%
- Longest loss period: 3 months
- Sharpe ratio: 1.72

Because the real-account period is shorter than the proxy bridge period, this is used primarily as a **risk-budget and plausibility reference**, not as a strict performance winner/loser comparison.

---

## 6. Direct Proxy optimization results

### 6.1 Main results

| Objective | CAGR | Std Dev | Sharpe | MDD |
|---|---:|---:|---:|---:|
| Provided KAW Direct Proxy | 8.60% | 9.95% | 0.50 | -15.78% |
| Max Sharpe | 16.66% | 9.37% | 1.29 | -8.23% |
| Max Return @ 10.5% vol | 17.79% | 10.50% | 1.26 | -10.28% |
| Max Return @ 11.0% vol | 18.20% | 11.00% | 1.24 | -10.86% |
| Max Return @ 11.5% vol | 18.57% | 11.50% | 1.21 | -11.40% |
| Max Return @ 13.0% vol | 19.53% | 13.00% | 1.15 | -12.83% |
| SPY benchmark | 16.74% | 14.30% | 0.89 | -13.40% |

Interpretation:

- The real account reported annual volatility of **10.52%** over a shorter period.
- Therefore **10.5% to 11.5%** is treated as the main fairness region for Max Return comparisons.
- **13%** is retained as an aggressive reference rather than the primary fairness target.
- The Max Sharpe result is kept independent of the target-volatility fairness exercise.

### 6.2 Direct Proxy evidence

- Max Sharpe: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0002/report.html
- Max Return @ 10.5%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0004/report.html
- Max Return @ 11.0%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0005/report.html
- Max Return @ 11.5%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0002/report.html
- Max Return @ 13.0%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0003/report.html

---

## 7. KAW Core bridge-period results

After correcting the all-USD FX handling bug described later in this report, KAW Core was rerun in KRW terms using the same fixed risk-free rate.

| Objective | CAGR | Std Dev | Sharpe | MDD |
|---|---:|---:|---:|---:|
| Provided KAW Core | 12.11% | 12.19% | 0.69 | -16.58% |
| Max Sharpe | 21.69% | 11.10% | 1.49 | -11.12% |
| Max Return @ 11.5% vol | 22.25% | 11.50% | 1.48 | -11.92% |
| SPY benchmark | 16.74% | 14.30% | 0.89 | -13.40% |

Core therefore does **not** reproduce Direct Proxy absolute return/efficient-frontier levels closely. Its optimized frontier is materially stronger over this specific 2021-11 to 2026-08 sample.

### 7.1 Core evidence

- Core Max Sharpe: https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0009/report.html
- Core Max Return @ 11.5%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0010/report.html

### 7.2 Invalidated earlier Core result

An earlier all-USD Core run, including the temporary 12% target-volatility experiment, was generated before the FX bug was fixed. Those metrics were USD-based even though KRW reporting was intended and are **not used for research conclusions**.

The old 12% run is retained only as an audit artifact, not as valid evidence.

---

## 8. Direct Proxy vs Core movement fidelity

Absolute performance differs, but the behavior bridge is much stronger than the performance tables alone suggest.

Using the **provided-weight portfolios** over the same 58 monthly observations:

| Comparison | Result |
|---|---:|
| **Monthly return correlation** | **0.898** |
| **Up/down direction match** | **52 / 58 months = 89.7%** |
| **Core beta vs Direct** | **1.10** |
| **Annualized tracking error** | **5.45%** |
| **Drawdown-series correlation** | **0.944** |
| **Maximum-drawdown trough** | **Both 2022-12** |

Interpretation:

- Core and Direct Proxy usually move in the same direction.
- Drawdown timing is especially similar.
- Core behaves as a somewhat higher-amplitude version of Direct Proxy, consistent with beta near 1.10.
- Therefore Core is **not a precise absolute-performance substitute**, but it is a plausible **behavior proxy** for studying long-term trend, regime response, strengths, and weaknesses.

This distinction is central to all future long-horizon interpretation.

---

## 9. Sleeve decomposition: Direct to Core, one-at-a-time

To identify which proxy substitutions alter behavior, each sleeve was replaced independently while keeping the rest of Direct Proxy unchanged.

| Single replacement | Provided Std Dev | Change vs Direct | Max Sharpe Std Dev | Max Sharpe |
|---|---:|---:|---:|---:|
| Direct baseline | 9.95% | baseline | 9.37% | 1.291 |
| Gold -> GLD | 10.11% | +0.16%p | 10.80% | 1.485 |
| Bond -> TLT 30% | 9.95% | ~0.00%p | 9.37% | 1.291 |
| China + India -> EEM 17% | 11.01% | +1.06%p | 9.37% | 1.291 |
| US dividend -> SPY | 10.45% | +0.50%p | 9.89% | 1.287 |
| Korea -> EWY | 10.00% | +0.05%p | 9.37% | 1.291 |
| Japan -> EWJ | 9.97% | +0.02%p | 9.35% | 1.285 |

Key observation:

- Most individual replacements have limited effect on the baseline risk structure.
- The largest individual increase in provided volatility comes from compressing China + India into EEM.
- The larger gap between Full Core and Direct Proxy therefore appears to reflect **interaction among multiple proxy substitutions**, not one obviously broken sleeve.

---

## 10. Implementation and data corrections discovered during the study

### 10.1 All-USD FX bug

The runner previously loaded USD/KRW only when KRW and USD assets were mixed. As a result, an all-USD portfolio such as KAW Core silently remained in USD terms even when `fx.usdkrw_symbol: USD/KRW` was configured.

Impact:

- Earlier Full Core volatility and frontier results were not comparable to KRW-based Direct Proxy results.

Fix:

- All-USD + explicit FX configuration now converts to KRW.
- All-USD without FX configuration preserves the prior USD behavior.
- Regression tests were added.

Real-data validation:

- After the fix, the Core SPY benchmark returned approximately **16.74% CAGR / 14.30% Std Dev**, matching the Direct Proxy benchmark over the same period.

### 10.2 TB3MS risk-free provider failure

The `us_3m_tbill` mode attempted to fetch FRED `TB3MS` through FinanceDataReader on every run and failed during this study.

Temporary study convention:

- Use fixed annual RF **3.8394827586206895%** for all KAW follow-up research.

Longer-term solution is tracked in GitHub Issue #1.

---

## 11. Interim conclusion

Current evidence supports the following working interpretation:

1. **Direct Proxy** is the preferred recent-period representation of the current KAW structure.
2. **Core** should not be interpreted as an exact performance replica of Direct Proxy.
3. Despite different CAGR, volatility, Sharpe, and optimized frontier results, Core shows strong movement similarity to Direct Proxy:
   - monthly correlation 0.898
   - direction agreement 89.7%
   - drawdown correlation 0.944
   - same maximum-drawdown trough month
4. This level of movement fidelity is sufficient to justify testing Core as a **long-history behavior proxy** for trend, regime sensitivity, strengths, weaknesses, and structural robustness.
5. Long-horizon Core results must continue to be interpreted as behavior evidence, not as a literal reconstruction of the current KAW account's historical absolute return.

---

## 12. Next experiments

This report will be extended in place. Planned follow-up work includes:

- 2006-01 onward long-horizon KAW Core optimization/backtest
- long-horizon Max Sharpe and target-volatility frontier analysis
- regime-based strength/weakness analysis
- rolling-window robustness
- start/end-period sensitivity where useful
- additional proxy interaction tests only if long-horizon results indicate a material fidelity problem

Future results should be appended or used to update the relevant sections above rather than creating a parallel report.
