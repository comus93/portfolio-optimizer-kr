# KAW Target Reconstruction Report

> Living report. This file is the canonical research report for the KAW target-reconstruction study. Historical run artifacts remain immutable; this report reflects the current interpretation and current canonical proxy definitions.

## 1. Research question

This study asks whether the current Kim Seong-il K-All Weather portfolio can be represented in two useful forms:

1. **KAW Native Proxy**: a relatively faithful recent-period representation of the current nine economic sleeves.
2. **KAW Core**: a compressed proxy intended to extend the same economic structure backward while remaining simple enough for Portfolio Visualizer and the internal engine.

The Core is not required to reproduce Native absolute performance exactly. The main acceptance question is whether it preserves whole-portfolio behavior well enough for long-horizon comparison: return scale, volatility, monthly co-movement, direction, tracking error, and drawdown path.

No stitched Native/Core NAV is used.

---

## 2. Current target allocation

| Sleeve | Weight |
|---|---:|
| Nasdaq 100 | 10.0% |
| US dividend | 10.0% |
| Korea | 8.0% |
| China / CSI 300 | 8.5% |
| India / Nifty 50 | 8.5% |
| Japan | 5.0% |
| US long Treasury | 15.0% |
| KR 30Y Treasury | 15.0% |
| Gold | 20.0% |
| **Total** | **100.0%** |

Strategic cash is 0%.

---

## 3. Current canonical proxy definitions

Full listing/inception-date details and usable-period derivation are maintained in `studies/kaw-target-reconstruction/study.md`.

### 3.1 KAW Native Proxy

| Sleeve | Code / Ticker | Proxy | Weight |
|---|---|---|---:|
| Nasdaq 100 | `133690` | TIGER 미국나스닥100 | 10.0% |
| US dividend | `402970` | ACE 미국배당다우존스 | 10.0% |
| Korea | `069500` | KODEX 200 | 8.0% |
| China / CSI 300 | `192090` | TIGER 차이나CSI300 | 8.5% |
| India / Nifty 50 | `200250` | KIWOOM 인도Nifty50(합성) | 8.5% |
| Japan | `101280` | KODEX 일본TOPIX100 | 5.0% |
| US long Treasury | `267440` | RISE 미국장기국채선물(H) | 15.0% |
| KR 30Y Treasury | `385560` | RISE KIS국고채30년Enhanced | 15.0% |
| Gold | `GLD` | SPDR Gold Shares | 20.0% |

The latest-listed constituent is `402970`, listed 2021-10-21. Therefore the first complete Month-to-Month month is **2021-11**.

Canonical Native usable period: **2021-11 onward**.

Standard completed bridge window in this study: **2021-11-01 through 2026-08-31**, 58 monthly observations.

### 3.2 KAW Core — Portfolio Visualizer implementation

| Sleeve | Ticker | Proxy | Weight |
|---|---|---|---:|
| Nasdaq 100 | `QQQ` | Invesco QQQ | 10.0% |
| US dividend | `SCHD` | Schwab U.S. Dividend Equity ETF | 10.0% |
| Korea | `EWY` | iShares MSCI South Korea ETF | 8.0% |
| China / CSI 300 | `ASHR` | Xtrackers Harvest CSI 300 China A-Shares ETF | 8.5% |
| India / Nifty 50 | `INDY` | iShares India 50 ETF | 8.5% |
| Japan | `EWJ` | iShares MSCI Japan ETF | 5.0% |
| Combined long-duration bond sleeve | `TLT` | iShares 20+ Year Treasury Bond ETF | 30.0% |
| Gold | `GLD` | SPDR Gold Shares | 20.0% |

Conservative Core-PV study start: **2014-01**.

### 3.3 KAW Core — internal-engine implementation

For internal-engine validation, China and India use the Korean-listed proxies because they reproduced the intended Native return path better than ASHR/INDY in recent-period observation.

| Sleeve | Code / Ticker | Proxy | Weight |
|---|---|---|---:|
| Nasdaq 100 | `QQQ` | Invesco QQQ | 10.0% |
| US dividend | `SCHD` | Schwab U.S. Dividend Equity ETF | 10.0% |
| Korea | `EWY` | iShares MSCI South Korea ETF | 8.0% |
| China / CSI 300 | `192090` | TIGER 차이나CSI300 | 8.5% |
| India / Nifty 50 | `200250` | KIWOOM 인도Nifty50(합성) | 8.5% |
| Japan | `EWJ` | iShares MSCI Japan ETF | 5.0% |
| Combined long-duration bond sleeve | `TLT` | iShares 20+ Year Treasury Bond ETF | 30.0% |
| Gold | `GLD` | SPDR Gold Shares | 20.0% |

Conservative Internal-Core usable period: **2014-07 onward**, constrained by the 2014-06-26 listing of `200250`.

PV Core and Internal Core are two implementations of the same economic Core definition, not two different theses.

---

## 4. Bond and FX conventions

Native bond sleeve:

```text
267440 15% + 385560 15%
```

Core bond sleeve:

```text
TLT 30%
```

TLT is a coarse proxy for the aggregate 30% long-duration bond engine, not a literal proxy for either Native bond component individually.

Recent diagnostics found that removing USD/KRW conversion from TLT increased recent-period correlation, but this is not adopted as a model rule because it would be an asset-specific ex-post adjustment. The research convention is intentionally simpler:

- reporting currency: **KRW**
- all USD assets use the same USD/KRW conversion rule
- Korean-listed KRW assets remain in KRW
- no asset-specific FX exception is allowed merely to improve bridge fit

---

## 5. Common experiment conditions

Unless an experiment explicitly says otherwise:

- time-period mode: Month-to-Month
- rebalancing: monthly, calendar aligned
- reporting currency: KRW
- benchmark: SPY
- bridge period: 2021-11 through 2026-08
- initial balance: 10,000
- fixed annual risk-free rate: **3.8394827586206895%**

The fixed RF value is the previously resolved US 3M T-bill value used as the project default convention for repeated deterministic research. Explicit `us_3m_tbill` mode remains available separately. GitHub Issue #1 tracks robustness/caching of the dynamic provider path.

---

## 6. Current canonical Native vs revised Core bridge

### 6.1 Run

Experiment:

`studies/kaw-target-reconstruction/experiments/020-kaw-native-vs-revised-core-backtest.yaml`

Canonical run:

`runs/20260910-0001`

Pages:

https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0001/report.html

Conditions:

- 2021-11 through 2026-08
- 58 monthly observations
- Month-to-Month
- monthly rebalancing
- KRW reporting
- uniform USD/KRW conversion
- fixed RF 3.8394827586206895%
- SPY benchmark

### 6.2 Performance

| Metric | KAW Native Proxy | KAW Core Revised Internal | Gap, Core - Native |
|---|---:|---:|---:|
| CAGR | **9.60%** | **10.28%** | **+0.68%p** |
| Annualized arithmetic return | 9.67% | 10.41% | +0.74%p |
| Standard deviation | **9.70%** | **10.80%** | +1.09%p |
| Maximum drawdown | **-13.83%** | **-12.80%** | +1.03%p shallower |
| Sharpe | **0.600** | **0.608** | +0.008 |
| Sortino | 0.898 | 0.876 | -0.022 |
| End balance from 10,000 | **15,575** | **16,046** | **+471** |

SPY benchmark over the same period:

- CAGR 16.74%
- standard deviation 14.30%
- maximum drawdown -13.40%
- Sharpe 0.891

### 6.3 Whole-portfolio movement fidelity

Calculated from all 58 monthly portfolio returns:

| Bridge metric | Revised bridge result |
|---|---:|
| Monthly return correlation | **0.9168** |
| Up/down direction agreement | **51 / 58 = 87.9%** |
| Native beta on Core | **0.8240** |
| OLS R² | **0.8406** |
| Annualized tracking error | **4.32%** |
| Drawdown-series correlation | **0.9430** |
| Volatility ratio, Core / Native | **1.113** |
| Maximum-drawdown trough | **Both 2022-12** |

Interpretation:

- Correlation is now above 0.91 and R² above 0.84.
- Direction agreement improved materially but remains just below the informal 90% target.
- Core still runs modestly hotter than Native, with about 11% higher realized volatility.
- Tracking error is not trivial, but is substantially lower than the earlier flawed mapping.
- The largest drawdown bottoms in the same month and drawdown paths are highly correlated.

This is strong enough to treat the revised Core as a materially improved behavioral proxy, while retaining a clear warning that it is not a literal replica.

---

## 7. Improvement versus the superseded 20260909-0013 bridge

The earlier run `20260909-0013` used the now-retired mapping:

- Native China: 168580
- Native Gold: 132030 Gold Futures (H)
- Core US dividend: SPY
- Core China + India: EEM 17%
- Core Gold: GLD
- Core bonds: TLT 30%

That run is retained as diagnostic historical evidence, not current calibration evidence.

| Metric | Old 0013 | Revised 0001 | Change |
|---|---:|---:|---:|
| Native CAGR | 8.26% | **9.60%** | +1.34%p |
| Core CAGR | 12.11% | **10.28%** | -1.83%p |
| CAGR gap | **3.86%p** | **0.68%p** | **82.4% smaller** |
| End-balance gap | 2,705 | **471** | **82.6% smaller** |
| Monthly correlation | 0.8517 | **0.9168** | +0.0651 |
| Direction agreement | 81.0% | **87.9%** | +6.9%p |
| Native-on-Core beta | 0.7016 | **0.8240** | closer to 1 |
| OLS R² | 0.7255 | **0.8406** | +0.1151 |
| Tracking error | 6.28% | **4.32%** | **31.2% lower** |
| Drawdown correlation | 0.9095 | **0.9430** | +0.0335 |
| Core / Native vol ratio | 1.214 | **1.113** | closer to 1 |

The revision therefore improved both **performance-scale fidelity** and **movement fidelity**. The earlier apparent Core outperformance was largely a proxy-definition artifact rather than evidence that the compressed Core intrinsically outperformed the current KAW structure.

---

## 8. Residual return-gap decomposition

The revised run leaves only **+471** of Core end-balance advantage from a 10,000 start.

Grouped contribution difference, Core minus Native:

| Sleeve | Core - Native contribution balance |
|---|---:|
| Nasdaq | -13.7 |
| US dividend | +40.2 |
| Korea | -39.1 |
| China | -25.2 |
| India | -7.7 |
| Japan | -34.9 |
| **Bond** | **+613.4** |
| Gold | -61.9 |
| **Net** | **+471.0** |

The key result is structural:

- The non-bond sleeves collectively favor Native by about **142**.
- The coarse `TLT 30%` bond proxy favors Core by about **613**.
- Therefore the remaining Core advantage is concentrated in the already-known bond-compression approximation.

This is substantially cleaner than run 0013, where China/India, gold, and bonds together created most of the gap.

---

## 9. Current conclusion

1. **KAW Native Proxy** in `study.md` is the current canonical recent-period benchmark.
2. **KAW Core Revised Internal** is the current internal-engine Core implementation.
3. The old `QQQ / SPY / EWY / EEM / EWJ / TLT / GLD` Core is retired for new canonical research.
4. The revised bridge run `20260910-0001` materially improves fidelity versus `20260909-0013`.
5. The current whole-portfolio bridge has correlation **0.917**, direction match **87.9%**, tracking error **4.32%**, and drawdown correlation **0.943**.
6. Native and Core CAGR are now **9.60% vs 10.28%**, only **0.68%p** apart over the 58-month bridge period.
7. The remaining performance gap is dominated by the intentionally coarse bond proxy `TLT 30%`.
8. No scalar multiplier such as the previously explored `Core × 0.70` is currently justified or needed. That earlier calibration idea remains discarded.
9. Final long-history use should treat Core as a **behavioral approximation**, not as a synthetic reconstruction of Native NAV.

---

## 10. Historical evidence retained

### 10.1 Direct Proxy v1

Older Direct Proxy v1 experiments used TLT 15% for the US long-Treasury sleeve. Their optimization results remain historical evidence only and must not be relabeled as current Native results.

### 10.2 Direct Proxy v2 / run 0013

Run `20260909-0013` used 267440 but retained older China/Gold and old Core mapping. It is now classified as a **flawed-bridge diagnostic** that helped identify EEM exposure mismatch, gold hedge/exposure mismatch, bond compression issues, and the need to replace SPY with SCHD.

### 10.3 All-USD FX bug

An older all-USD Core execution path failed to apply configured USD/KRW conversion. That bug was corrected before current canonical bridge work. Pre-fix all-USD Core results are invalid for research conclusions.

---

## 11. Next research step

The revised bridge is now sufficiently coherent to resume portfolio-level research.

Next work should use the current canonical definitions and, where relevant:

- compare KAW Native against the user's TO-BE portfolio over the recent common period
- compare KAW Core against a TO-BE Core-compatible portfolio over the longer common period
- use the user-selected **11.5% annual volatility** as the main risk-matched optimization target
- examine rolling robustness and drawdowns
- add regime analysis only when it answers a specific research question

Do not reintroduce retired SPY/EEM mappings or asset-specific FX exceptions merely to improve fit.
