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

### 3.1 KAW Direct Proxy v2 — current canonical definition

Design principle: preserve the current nine sleeves as directly as practical while extending the common usable history beyond the current native ETF set.

| Sleeve | Proxy | Weight |
|---|---|---:|
| Nasdaq 100 | 133690 TIGER 미국나스닥100 | 10.0% |
| US dividend | 402970 ACE 미국배당다우존스 | 10.0% |
| Korea | 069500 KODEX 200 | 8.0% |
| China | 168580 ACE 중국본토CSI300 | 8.5% |
| India | 200250 KIWOOM 인도Nifty50(합성) | 8.5% |
| Japan | 101280 KODEX 일본TOPIX100 | 5.0% |
| US long Treasury | **267440 RISE 미국장기국채선물(H)** | **15.0%** |
| KR 30Y Treasury | 385560 RISE KIS국고채30년Enhanced | 15.0% |
| Gold | 132030 KODEX 골드선물(H) | 20.0% |

**Common valid test period:** 2021-11 onward.

267440 was listed in 2017, so replacing TLT with 267440 does not shorten the existing 2021-11 common start.

For bridge and recent-period comparison, the standard analysis period remains **2021-11-01 to 2026-08-31** unless explicitly changed.

#### Direct Proxy versioning note

Earlier experiments in this report used **TLT 15%** for the US long-Treasury sleeve. Those runs are retained as **Direct Proxy v1** historical evidence.

They must not be silently interpreted as results for the new canonical Direct Proxy v2. Key Direct optimization and Direct-vs-Core movement-fidelity metrics should be rerun with 267440 before being used as current comparison evidence against the user's TO-BE portfolio.

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

### 4.1 Risk-free-rate convention

The dynamic `risk_free.mode: us_3m_tbill` path currently depends on FinanceDataReader/FRED resolving `TB3MS` on every run. This caused a reproducibility failure during the Core rerun.

For repeated KAW research over the already-resolved bridge period, use the following fixed rate unless explicitly overridden:

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

- Annual risk-free rate: **3.8394827586206895%**
- Decimal form: `0.038394827586206895`
- Source: successful Direct Proxy v1 run `runs/20260908-0002/result.json`

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

## 6. Direct Proxy v1 optimization results — TLT-based historical evidence

The following results use the former Direct Proxy definition with **TLT 15%**. They remain useful as historical study evidence but are **not current Direct Proxy v2 results**.

| Objective | CAGR | Std Dev | Sharpe | MDD |
|---|---:|---:|---:|---:|
| Provided KAW Direct Proxy v1 | 8.60% | 9.95% | 0.50 | -15.78% |
| Max Sharpe | 16.66% | 9.37% | 1.29 | -8.23% |
| Max Return @ 10.5% vol | 17.79% | 10.50% | 1.26 | -10.28% |
| Max Return @ 11.0% vol | 18.20% | 11.00% | 1.24 | -10.86% |
| Max Return @ 11.5% vol | 18.57% | 11.50% | 1.21 | -11.40% |
| Max Return @ 13.0% vol | 19.53% | 13.00% | 1.15 | -12.83% |
| SPY benchmark | 16.74% | 14.30% | 0.89 | -13.40% |

Interpretation at the time:

- The real account reported annual volatility of **10.52%** over a shorter period.
- Therefore **10.5% to 11.5%** was treated as the main fairness region for Max Return comparisons.
- **13%** was retained as an aggressive reference.

### 6.1 Direct Proxy v1 evidence

- Max Sharpe: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0002/report.html
- Max Return @ 10.5%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0004/report.html
- Max Return @ 11.0%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0005/report.html
- Max Return @ 11.5%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0002/report.html
- Max Return @ 13.0%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260908-0003/report.html

### 6.2 Direct Proxy v2 rerun status

Not yet executed after the 267440 revision.

Required before the next canonical recent-period TO-BE comparison:

- Provided-weight Direct v2 performance
- Max Sharpe
- Main target-volatility comparison around 10.5% to 11.5%
- Direct v2 vs Core movement-fidelity metrics

---

## 7. KAW Core bridge-period results

After correcting the all-USD FX handling bug described later in this report, KAW Core was rerun in KRW terms using the same fixed risk-free rate.

| Objective | CAGR | Std Dev | Sharpe | MDD |
|---|---:|---:|---:|---:|
| Provided KAW Core | 12.11% | 12.19% | 0.69 | -16.58% |
| Max Sharpe | 21.69% | 11.10% | 1.49 | -11.12% |
| Max Return @ 11.5% vol | 22.25% | 11.50% | 1.48 | -11.92% |
| SPY benchmark | 16.74% | 14.30% | 0.89 | -13.40% |

### 7.1 Core evidence

- Core Max Sharpe: https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0009/report.html
- Core Max Return @ 11.5%: https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0010/report.html

### 7.2 Invalidated earlier Core result

An earlier all-USD Core run, including the temporary 12% target-volatility experiment, was generated before the FX bug was fixed. Those metrics were USD-based even though KRW reporting was intended and are **not used for research conclusions**.

---

## 8. Direct Proxy v1 vs Core movement fidelity — historical bridge evidence

The original bridge used TLT-based Direct Proxy v1. Using the provided-weight portfolios over the same 58 monthly observations:

| Comparison | Result |
|---|---:|
| **Monthly return correlation** | **0.898** |
| **Up/down direction match** | **52 / 58 months = 89.7%** |
| **Core beta vs Direct** | **1.10** |
| **Annualized tracking error** | **5.45%** |
| **Drawdown-series correlation** | **0.944** |
| **Maximum-drawdown trough** | **Both 2022-12** |

These figures established that the original Core mapping was behaviorally promising, but they now belong specifically to **Direct Proxy v1 vs Core**.

The same movement-fidelity table must be recomputed for **Direct Proxy v2 (267440) vs Core** before being cited as the current canonical bridge result.

---

## 9. Sleeve decomposition — Direct Proxy v1 to Core

The following decomposition also used the old TLT-based Direct baseline and is retained for provenance.

| Single replacement | Provided Std Dev | Change vs Direct | Max Sharpe Std Dev | Max Sharpe |
|---|---:|---:|---:|---:|
| Direct baseline v1 | 9.95% | baseline | 9.37% | 1.291 |
| Gold -> GLD | 10.11% | +0.16%p | 10.80% | 1.485 |
| Bond -> TLT 30% | 9.95% | ~0.00%p | 9.37% | 1.291 |
| China + India -> EEM 17% | 11.01% | +1.06%p | 9.37% | 1.291 |
| US dividend -> SPY | 10.45% | +0.50%p | 9.89% | 1.287 |
| Korea -> EWY | 10.00% | +0.05%p | 9.37% | 1.291 |
| Japan -> EWJ | 9.97% | +0.02%p | 9.35% | 1.285 |

Because the Direct bond sleeve is now 267440 rather than TLT, the bond substitution question changes materially and should be reconsidered only if needed after the v2 bridge rerun.

---

## 10. Implementation and data corrections discovered during the study

### 10.1 All-USD FX bug

The runner previously loaded USD/KRW only when KRW and USD assets were mixed. As a result, an all-USD portfolio such as KAW Core silently remained in USD terms even when `fx.usdkrw_symbol: USD/KRW` was configured.

Fix:

- All-USD + explicit FX configuration now converts to KRW.
- All-USD without FX configuration preserves the prior USD behavior.
- Regression tests were added.

Real-data validation:

- After the fix, the Core SPY benchmark returned approximately **16.74% CAGR / 14.30% Std Dev**, matching the Direct Proxy benchmark over the same period.

### 10.2 TB3MS risk-free provider failure

The `us_3m_tbill` mode attempted to fetch FRED `TB3MS` through FinanceDataReader on every run and failed during this study.

Repeated bridge-period KAW studies therefore use fixed annual RF **3.8394827586206895%** unless explicitly overridden.

Longer-term solution is tracked in GitHub Issue #1.

---

## 11. Current interim conclusion

1. **Direct Proxy v2**, using 267440 for the US long-Treasury sleeve, is now the canonical recent-period KAW representation.
2. **Direct Proxy v1** results remain valid only as historical TLT-based study evidence.
3. **Core** remains the long-history behavior proxy using QQQ, SPY, EWY, EEM, EWJ, TLT, and GLD from 2006-01 onward.
4. The v1 bridge showed strong movement similarity, but the current canonical bridge must be refreshed using Direct Proxy v2 before final recent-period TO-BE comparison.
5. No stitched Direct/Core NAV is used.

---

## 12. Next experiments

Immediate prerequisite before the user's TO-BE portfolio comparison:

- rerun Direct Proxy v2 over 2021-11-01 to 2026-08-31 with 267440
- recompute movement fidelity against KAW Core
- update the Direct v2 result tables in this report

Then proceed to:

- recent-period TO-BE vs KAW Direct Proxy v2
- 2006-01 onward TO-BE Core-compatible vs KAW Core
- rolling robustness and drawdown comparison
- target-volatility / Max Sharpe comparison where appropriate
- regime-based strengths and weaknesses if needed

Future KAW findings should continue to update this living report rather than create a parallel KAW summary.
