# KAW Target Reconstruction Study

Reconstruct the current Kim Seong-il K-All Weather portfolio as a reproducible benchmark for comparison against the user's TO-BE portfolio and for longer-horizon behavior analysis.

## Canonical portfolio definitions

### 1. KAW Native Proxy — current recent-period benchmark

`KAW Native Proxy` is the current canonical recent-period representation of the KAW target portfolio. Older documents and runs may call earlier versions `KAW Direct Proxy`; those artifacts remain historical evidence and must not be silently relabeled as the current definition.

The design goal is to preserve the current economic sleeves as directly as practical while using a common dataset that can be executed reproducibly in the internal engine.

For Korean-listed ETFs, the date below is the KRX **listing date**. For US-listed ETFs, the date is the issuer-reported **fund inception / listing date** used as the practical history-start marker.

| Sleeve | Code / Ticker | Native Proxy | Weight | Listing / Inception date |
|---|---|---|---:|---|
| Nasdaq 100 | `133690` | TIGER 미국나스닥100 | 10.0% | 2010-10-18 |
| US dividend | `402970` | ACE 미국배당다우존스 | 10.0% | **2021-10-21** |
| Korea | `069500` | KODEX 200 | 8.0% | 2002-10-14 |
| China / CSI 300 | `192090` | TIGER 차이나CSI300 | 8.5% | 2014-02-17 |
| India / Nifty 50 | `200250` | KIWOOM 인도Nifty50(합성) | 8.5% | 2014-06-26 |
| Japan | `101280` | KODEX 일본TOPIX100 | 5.0% | 2008-02-20 |
| US long Treasury | `267440` | RISE 미국장기국채선물(H) | 15.0% | 2017-04-20 |
| KR 30Y Treasury | `385560` | RISE KIS국고채30년Enhanced | 15.0% | 2021-05-26 |
| Gold | `GLD` | SPDR Gold Shares | 20.0% | 2004-11-18 |
| **Total** |  |  | **100.0%** |  |

#### 1.1 Native Proxy usable period

The latest-listed constituent is **402970 ACE 미국배당다우존스**, listed on **2021-10-21**.

Therefore:

- earliest date on which every Native Proxy constituent exists: **2021-10-21**
- earliest **complete calendar month** for Month-to-Month research: **2021-11**
- canonical Native Proxy usable period: **2021-11 onward**
- standard completed bridge/recent test window currently used by this study: **2021-11-01 through 2026-08-31**
- first monthly observation in that convention: **2021-11-30**

This period is derived from constituent availability, not chosen to improve backtest performance.

Important revisions:

- China Native Proxy changed from `168580 ACE 중국본토CSI300` to **`192090 TIGER 차이나CSI300`** because recent common-period return-path fidelity against the intended CSI 300 exposure was materially better than the US-listed ASHR proxy.
- India Native Proxy remains **`200250 KIWOOM 인도Nifty50(합성)`**. The US-listed `INDY` is useful for Portfolio Visualizer validation but showed material return-path divergence from the native Korean proxy in recent comparison.
- Gold is now **GLD in both Native Proxy and Core**. This intentionally removes the prior mismatch between `132030 KODEX 골드선물(H)` and GLD when the purpose is Native-vs-Core reconstruction fidelity.
- The US long-Treasury native sleeve remains `267440` and the KR long-bond native sleeve remains `385560`.

### 2. KAW Core — revised long-history / compressed benchmark

The old Core definition `QQQ / SPY / EWY / EEM / EWJ / TLT / GLD` is retired as the current canonical Core because `SPY` was a weak proxy for the US-dividend sleeve and `EEM 17%` introduced substantial unintended Taiwan/Korea/other-EM exposure when standing in for China + India.

The revised Core preserves the same economic sleeves more faithfully while still allowing a longer test horizon than the Native Proxy.

#### 2.1 Portfolio Visualizer definition

Use US-listed ETFs when validating in Portfolio Visualizer:

| Sleeve | Ticker | Core PV Proxy | Weight | Inception date |
|---|---|---|---:|---|
| Nasdaq 100 | `QQQ` | Invesco QQQ | 10.0% | 1999-03-10 |
| US dividend | `SCHD` | Schwab U.S. Dividend Equity ETF | 10.0% | 2011-10-20 |
| Korea | `EWY` | iShares MSCI South Korea ETF | 8.0% | 2000-05-09 |
| China / CSI 300 | `ASHR` | Xtrackers Harvest CSI 300 China A-Shares ETF | 8.5% | 2013-11-06 |
| India / Nifty 50 | `INDY` | iShares India 50 ETF | 8.5% | 2009-11-18 |
| Japan | `EWJ` | iShares MSCI Japan ETF | 5.0% | 1996-03-12 |
| Combined US + KR long-duration bond sleeve | `TLT` | iShares 20+ Year Treasury Bond ETF | 30.0% | 2002-07-22 |
| Gold | `GLD` | SPDR Gold Shares | 20.0% | 2004-11-18 |
| **Total** |  |  | **100.0%** |  |

ASHR is the history bottleneck for the PV implementation. The first complete month after its 2013-11-06 inception is 2013-12. For consistency with the previously adopted conservative convention, the default revised Core-PV study start remains **2014-01** unless an experiment explicitly documents a different start.

#### 2.2 Internal-engine definition

For internal-engine research, preserve the same Core roles but use the higher-fidelity Korean-listed China and India proxies instead of forcing the US-listed PV proxies:

| Sleeve | Code / Ticker | Core Internal Proxy | Weight | Listing / Inception date |
|---|---|---|---:|---|
| Nasdaq 100 | `QQQ` | Invesco QQQ | 10.0% | 1999-03-10 |
| US dividend | `SCHD` | Schwab U.S. Dividend Equity ETF | 10.0% | 2011-10-20 |
| Korea | `EWY` | iShares MSCI South Korea ETF | 8.0% | 2000-05-09 |
| China / CSI 300 | `192090` | TIGER 차이나CSI300 | 8.5% | 2014-02-17 |
| India / Nifty 50 | `200250` | KIWOOM 인도Nifty50(합성) | 8.5% | **2014-06-26** |
| Japan | `EWJ` | iShares MSCI Japan ETF | 5.0% | 1996-03-12 |
| Combined US + KR long-duration bond sleeve | `TLT` | iShares 20+ Year Treasury Bond ETF | 30.0% | 2002-07-22 |
| Gold | `GLD` | SPDR Gold Shares | 20.0% | 2004-11-18 |
| **Total** |  |  | **100.0%** |  |

The latest-listed Internal-Core constituent is **200250**, listed on 2014-06-26. Therefore the first complete Month-to-Month calendar month is **2014-07**, and the canonical Internal-Core usable period is **2014-07 onward**.

This split is intentional:

- **PV validation** prioritizes compatibility with Portfolio Visualizer and therefore uses `ASHR` / `INDY`.
- **Internal-engine validation** prioritizes return-path fidelity to the native portfolio and therefore uses `192090` / `200250`.
- These are two implementations of the same economic Core definition, not two different investment theses.

### 3. Canonical research usage rule

Use the KAW representations by research purpose, not interchangeably.

| Research purpose | Canonical KAW representation | Default usable period | Reason |
|---|---|---|---|
| **Recent / short-period comparison in the internal engine** | **KAW Native Proxy** | **2021-11 onward** | Highest fidelity to the current KAW sleeves; use whenever both portfolios have sufficient recent common history. |
| **Long-history comparison in the internal engine** | **KAW Core Revised Internal** | **2014-07 onward** | Extends history while preserving higher-fidelity China/India paths with `192090` / `200250`. |
| **Portfolio Visualizer validation / optimization** | **KAW Core PV** | **2014-01 onward** | Uses US-listed ETFs required for practical PV compatibility, with `ASHR` / `INDY` for China/India. |

Operational interpretation:

1. If the research question is about **recent behavior, current portfolio comparison, or the period after every Native constituent exists**, use **KAW Native Proxy**.
2. If the research question is about **longer historical behavior inside `portfolio-optimizer-kr`**, use **KAW Core Revised Internal**, not the PV implementation.
3. If the research is being run **inside Portfolio Visualizer**, use **KAW Core PV**.
4. Do not use Core merely because it is available when Native covers the intended recent comparison window.
5. Do not force Native backward before 2021-11 through stitching or synthetic substitution.
6. Do not use the PV implementation as the default internal-engine Core merely for consistency with PV. The PV and Internal Core implementations have different tool constraints and are intentionally distinct.

This routing rule is part of the canonical study definition. Future KAW experiments should state which of these three representations is being used and why.

### 4. Bond-sleeve interpretation

The Core keeps **TLT 30%** as a compressed proxy for the combined native bond sleeve:

```text
Native bond sleeve = 267440 15% + 385560 15%
Core bond sleeve   = TLT 30%
```

TLT is not claimed to reproduce either native bond component individually. It is a coarse long-duration proxy for the **aggregate 30% bond engine**.

Recent bridge diagnostics showed that TLT does not provide a high-fidelity month-by-month replication of the Native bond sleeve when all assets are evaluated consistently in KRW. Nevertheless, its volatility and drawdown magnitude were materially closer to the combined Native bond sleeve than the more duration-aggressive EDV/ZROZ alternatives. Because the bond sleeve is 30% of the whole portfolio, final acceptance is based on **whole-portfolio bridge fidelity**, not on forcing a perfect fit at the individual bond-proxy level.

No asset-specific FX exception is allowed merely to improve recent-period correlation.

### 5. FX / reporting-currency rule

For internal-engine comparisons:

- Reporting currency is **KRW**.
- USD assets are converted using the same USD/KRW rule across the whole portfolio.
- Korean-listed KRW assets remain in KRW.
- Do **not** exempt TLT, GLD, QQQ, SCHD, EWY, EWJ, or any other USD asset from FX conversion just because doing so improves a specific bridge metric.

Reason: introducing an asset-specific FX exception after observing a better recent-period fit is a form of ex-post model tuning and increases overfitting risk. The research design therefore favors one simple portfolio-wide currency rule.

### 6. Versioning / historical evidence

Earlier runs remain immutable historical evidence:

- Direct Proxy v1 used TLT 15% for the US long-Treasury native sleeve.
- Direct Proxy v2 used 267440 but still used the older China and Gold definitions.
- The current `KAW Native Proxy` definition in this document supersedes those earlier portfolio definitions for new research.
- Historical run artifacts must retain the definitions under which they were actually generated.
