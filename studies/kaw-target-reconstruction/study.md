# KAW Target Reconstruction Study

Reconstruct the current Kim Seong-il K-All Weather portfolio as a reproducible benchmark for comparison against the user's TO-BE portfolio and for longer-horizon behavior analysis.

## Canonical portfolio definitions

### 1. KAW Native Proxy — current recent-period benchmark

`KAW Native Proxy` is the current canonical recent-period representation of the KAW target portfolio. Older documents and runs may call earlier versions `KAW Direct Proxy`; those artifacts remain historical evidence and must not be silently relabeled as the current definition.

The design goal is to preserve the current economic sleeves as directly as practical while using a common dataset that can be executed reproducibly in the internal engine.

| Sleeve | Native Proxy | Weight |
|---|---|---:|
| Nasdaq 100 | 133690 TIGER 미국나스닥100 | 10.0% |
| US dividend | 402970 ACE 미국배당다우존스 | 10.0% |
| Korea | 069500 KODEX 200 | 8.0% |
| China / CSI 300 | **192090 TIGER 차이나CSI300** | **8.5%** |
| India / Nifty 50 | **200250 KIWOOM 인도Nifty50(합성)** | **8.5%** |
| Japan | 101280 KODEX 일본TOPIX100 | 5.0% |
| US long Treasury | 267440 RISE 미국장기국채선물(H) | 15.0% |
| KR 30Y Treasury | 385560 RISE KIS국고채30년Enhanced | 15.0% |
| Gold | **GLD** | **20.0%** |
| **Total** |  | **100.0%** |

Current common recent-period baseline remains **2021-11 onward** unless a later experiment explicitly changes the period.

Important revisions:

- China Native Proxy changed from `168580 ACE 중국본토CSI300` to **`192090 TIGER 차이나CSI300`** because recent common-period return-path fidelity against the intended CSI 300 exposure was materially better than the US-listed ASHR proxy.
- India Native Proxy remains **`200250 KIWOOM 인도Nifty50(합성)`**. The US-listed `INDY` is useful for Portfolio Visualizer validation but showed material return-path divergence from the native Korean proxy in recent comparison.
- Gold is now **GLD in both Native Proxy and Core**. This intentionally removes the prior mismatch between `132030 KODEX 골드선물(H)` and unhedged physical-gold GLD when the purpose is Native-vs-Core reconstruction fidelity.
- The US long-Treasury native sleeve remains `267440` and the KR long-bond native sleeve remains `385560`.

### 2. KAW Core — revised long-history / compressed benchmark

The old Core definition `QQQ / SPY / EWY / EEM / EWJ / TLT / GLD` is retired as the current canonical Core because `SPY` was a weak proxy for the US-dividend sleeve and `EEM 17%` introduced substantial unintended Taiwan/Korea/other-EM exposure when standing in for China + India.

The revised Core preserves the same economic sleeves more faithfully while still allowing a longer test horizon than the Native Proxy.

#### 2.1 Portfolio Visualizer definition

Use US-listed ETFs when validating in Portfolio Visualizer:

| Sleeve | Core PV Proxy | Weight |
|---|---|---:|
| Nasdaq 100 | QQQ | 10.0% |
| US dividend | **SCHD** | **10.0%** |
| Korea | EWY | 8.0% |
| China / CSI 300 | **ASHR** | **8.5%** |
| India / Nifty 50 | **INDY** | **8.5%** |
| Japan | EWJ | 5.0% |
| Combined US + KR long-duration bond sleeve | **TLT** | **30.0%** |
| Gold | **GLD** | **20.0%** |
| **Total** |  | **100.0%** |

Key listing constraints:

- SCHD inception: 2011-10-20.
- ASHR inception: 2013-11.
- INDY inception: 2009-11.

For a clean complete-month PV study, use **2014-01 onward** as the conservative revised Core-PV start unless a specific experiment documents another start convention.

#### 2.2 Internal-engine definition

For internal-engine research, preserve the same Core roles but use the higher-fidelity Korean-listed China and India proxies instead of forcing the US-listed PV proxies:

| Sleeve | Core Internal Proxy | Weight |
|---|---|---:|
| Nasdaq 100 | QQQ | 10.0% |
| US dividend | **SCHD** | **10.0%** |
| Korea | EWY | 8.0% |
| China / CSI 300 | **192090 TIGER 차이나CSI300** | **8.5%** |
| India / Nifty 50 | **200250 KIWOOM 인도Nifty50(합성)** | **8.5%** |
| Japan | EWJ | 5.0% |
| Combined US + KR long-duration bond sleeve | **TLT** | **30.0%** |
| Gold | **GLD** | **20.0%** |
| **Total** |  | **100.0%** |

Because 200250 was listed in 2014-06, a conservative complete-month internal-Core start is **2014-07 onward**.

This split is intentional:

- **PV validation** prioritizes compatibility with Portfolio Visualizer and therefore uses `ASHR` / `INDY`.
- **Internal-engine validation** prioritizes return-path fidelity to the native portfolio and therefore uses `192090` / `200250`.
- These are two implementations of the same economic Core definition, not two different investment theses.

### 3. Bond-sleeve interpretation

The Core keeps **TLT 30%** as a compressed proxy for the combined native bond sleeve:

```text
Native bond sleeve = 267440 15% + 385560 15%
Core bond sleeve   = TLT 30%
```

TLT is not claimed to reproduce either native bond component individually. It is a coarse long-duration proxy for the **aggregate 30% bond engine**.

Recent bridge diagnostics showed that TLT does not provide a high-fidelity month-by-month replication of the Native bond sleeve when all assets are evaluated consistently in KRW. Nevertheless, its volatility and drawdown magnitude were materially closer to the combined Native bond sleeve than the more duration-aggressive EDV/ZROZ alternatives. Because the bond sleeve is 30% of the whole portfolio, final acceptance is based on **whole-portfolio bridge fidelity**, not on forcing a perfect fit at the individual bond-proxy level.

No asset-specific FX exception is allowed merely to improve recent-period correlation.

### 4. FX / reporting-currency rule

For internal-engine comparisons:

- Reporting currency is **KRW**.
- USD assets are converted using the same USD/KRW rule across the whole portfolio.
- Korean-listed KRW assets remain in KRW.
- Do **not** exempt TLT, GLD, QQQ, SCHD, EWY, EWJ, or any other USD asset from FX conversion just because doing so improves a specific bridge metric.

Reason: introducing an asset-specific FX exception after observing a better recent-period fit is a form of ex-post model tuning and increases overfitting risk. The research design therefore favors one simple portfolio-wide currency rule.

### 5. Versioning / historical evidence

Earlier runs remain immutable historical evidence:

- Direct Proxy v1 used TLT 15% for the US long-Treasury native sleeve.
- Direct Proxy v2 used 267440 but still used the older China and Gold definitions.
- Old Core used SPY 10% and EEM 17% and supported a 2006-01 start.

Those historical results must not be cited as performance for the revised current Native Proxy or revised current Core.

The revised Core intentionally gives up part of the old 2006-2013 history in exchange for materially better sleeve fidelity. No stitched Native/Core NAV is used.

## Canonical report

Research results, interpretation, corrections, evidence links, and follow-up findings are maintained in:

- `studies/kaw-target-reconstruction/report.md`

When historical tables in that report refer to SPY/EEM/132030 or an older Direct/Core version, treat them as explicitly versioned historical evidence. The portfolio definitions in this `study.md` are the current authoritative definitions until the corresponding report sections are refreshed.

## Study-wide risk-free-rate convention

The framework supports two YAML-selectable risk-free-rate modes for both optimization and backtest execution:

```yaml
# Dynamic provider mode: fetch the US 3M T-bill series for the run.
risk_free:
  mode: us_3m_tbill
```

or:

```yaml
# Deterministic fixed mode: do not fetch FRED/FDR economic-series data.
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

Until the FinanceDataReader/FRED `TB3MS` dependency issue is fixed, KAW-related follow-up experiments should use the fixed mode above unless explicitly overridden.

- **Annual RF: 3.8394827586206895%**
- Decimal: `0.038394827586206895`
- Source: successful historical run `runs/20260908-0002/result.json`
- Tracking issue: GitHub Issue #1

## Current phase

The next canonical bridge run must use the **revised Native Proxy** and the **revised Core Internal definition** above over their common period. It should measure whole-portfolio behavior before any scalar calibration is reconsidered.

Primary bridge diagnostics:

- monthly return correlation
- direction agreement
- beta
- annualized tracking error
- volatility ratio
- drawdown-series correlation
- MDD timing and depth
- CAGR / realized-return gap as a secondary, not forced, acceptance metric

Do not tune individual proxy rules after seeing the bridge result merely to maximize the recent-period correlation. If a proxy mismatch is accepted, document it and evaluate whether its impact is tolerable at the whole-portfolio level.
