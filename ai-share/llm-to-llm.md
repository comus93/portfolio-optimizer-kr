# Session Handover

created_at: 2026-09-10
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## Current State

KAW target reconstruction is complete enough to use as the project's reusable portfolio baseline / benchmark for future Backtest research.

Canonical sources:

```text
studies/kaw-target-reconstruction/study.md
studies/kaw-target-reconstruction/report.md
docs/kaw-benchmark-presets.md
```

`study.md` owns current KAW definitions, listing/inception-derived usable periods, routing rules, and the KAW-equivalent risk budget. `report.md` owns current bridge interpretation/evidence. Historical runs remain immutable under their original definitions.

Reusable Backtest benchmark presets are implemented:

```yaml
benchmark: kaw_short   # KAW Native Proxy
benchmark: kaw_long    # KAW Core Revised Internal
```

Aliases:

```text
kaw_short = kaw_native
kaw_long  = kaw_core
```

The default benchmark remains SPY when omitted. No hidden date-based switch is performed.

A reporting bug that caused the PV-style `Risk and Return Metrics` section to disappear was fixed. Root cause: fixed RF from the parsed YAML request was not propagated when no external annual_rf override was supplied. `runner._resolve_annual_rf()` now uses the request's fixed annual rate in that case. Post-fix KAW benchmark smoke runs are `20260910-0004` and `20260910-0005`.

## Decisions

### 1. KAW Native Proxy — canonical recent / short-period baseline

| Sleeve | Code / Ticker | Instrument | Weight | Listing / Inception |
|---|---|---|---:|---|
| Nasdaq 100 | `133690` | TIGER 미국나스닥100 | 10.0% | 2010-10-18 |
| US dividend | `402970` | ACE 미국배당다우존스 | 10.0% | 2021-10-21 |
| Korea | `069500` | KODEX 200 | 8.0% | 2002-10-14 |
| China / CSI 300 | `192090` | TIGER 차이나CSI300 | 8.5% | 2014-02-17 |
| India / Nifty 50 | `200250` | KIWOOM 인도Nifty50(합성) | 8.5% | 2014-06-26 |
| Japan | `101280` | KODEX 일본TOPIX100 | 5.0% | 2008-02-20 |
| US long Treasury | `267440` | RISE 미국장기국채선물(H) | 15.0% | 2017-04-20 |
| KR 30Y Treasury | `385560` | RISE KIS국고채30년Enhanced | 15.0% | 2021-05-26 |
| Gold | `GLD` | SPDR Gold Shares | 20.0% | 2004-11-18 |

History bottleneck: `402970`, listed 2021-10-21.

Canonical usable period:

```text
2021-11 onward
```

Standard completed recent/bridge window used so far:

```text
2021-11-01 through 2026-08-31
58 monthly observations
```

### 2. KAW Core Revised Internal — canonical long-history baseline

| Sleeve | Code / Ticker | Instrument | Weight | Listing / Inception |
|---|---|---|---:|---|
| Nasdaq 100 | `QQQ` | Invesco QQQ | 10.0% | 1999-03-10 |
| US dividend | `SCHD` | Schwab U.S. Dividend Equity ETF | 10.0% | 2011-10-20 |
| Korea | `EWY` | iShares MSCI South Korea ETF | 8.0% | 2000-05-09 |
| China / CSI 300 | `192090` | TIGER 차이나CSI300 | 8.5% | 2014-02-17 |
| India / Nifty 50 | `200250` | KIWOOM 인도Nifty50(합성) | 8.5% | 2014-06-26 |
| Japan | `EWJ` | iShares MSCI Japan ETF | 5.0% | 1996-03-12 |
| Combined long-duration bond sleeve | `TLT` | iShares 20+ Year Treasury Bond ETF | 30.0% | 2002-07-22 |
| Gold | `GLD` | SPDR Gold Shares | 20.0% | 2004-11-18 |

History bottleneck: `200250`, listed 2014-06-26.

Canonical usable period:

```text
2014-07 onward
```

Core bond convention:

```text
Native bond = 267440 15% + 385560 15%
Core bond   = TLT 30%
```

TLT is a coarse aggregate behavioral proxy for the 30% bond sleeve, not a literal proxy for either Native bond component.

### 3. KAW Core PV — Portfolio Visualizer-only implementation

```text
QQQ 10 / SCHD 10 / EWY 8 / ASHR 8.5 / INDY 8.5 / EWJ 5 / TLT 30 / GLD 20
```

Use only for Portfolio Visualizer compatibility. Conservative study start: `2014-01`.

Do not substitute the PV definition for the internal-engine Core. Internal research uses `192090` / `200250`; PV uses `ASHR` / `INDY`.

### 4. Canonical representation routing

```text
Recent / short-period internal comparison
-> KAW Native Proxy
-> benchmark: kaw_short
-> usable 2021-11 onward

Long-history internal comparison
-> KAW Core Revised Internal
-> benchmark: kaw_long
-> usable 2014-07 onward

Portfolio Visualizer research
-> KAW Core PV holdings
-> conservative start 2014-01
```

Do not stitch Native backward before 2021-11. Do not use Core merely because it has longer history when Native covers the intended recent period.

### 5. FX and RF conventions

Internal research:

- reporting currency: KRW
- every USD asset uses the same USD/KRW conversion rule
- no asset-specific FX exception to improve fit
- pinned default fixed risk-free rate: `3.8394827586206895%` annual

### 6. KAW-equivalent risk budget — UPDATED

The canonical recommended risk budget for **Maximum Return subject to volatility** experiments is now:

```text
annualized standard deviation <= 10.0%
```

Reason:

```text
KAW Native Proxy recent realized annualized std ≈ 9.70%
KAW Core Revised Internal long realized annualized std ≈ 9.32%
```

Both cluster around a 10% volatility level. Therefore 10.0% is the default KAW-equivalent risk budget.

This is a **standard-deviation / volatility constraint, not an MDD constraint**. MDD remains a separate realized-risk evaluation metric.

The previously used `11.5%` annual volatility target is historical calibration only and is superseded as the default KAW benchmarking risk budget.

## Key Validation Evidence

### Revised Native vs Core bridge

Experiment:

```text
studies/kaw-target-reconstruction/experiments/020-kaw-native-vs-revised-core-backtest.yaml
```

Run:

```text
runs/20260910-0001
https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0001/report.html
```

Same recent window, KRW, monthly rebalance, fixed RF:

```text
                        Native       Core
CAGR                    9.60%       10.28%
Annualized return       9.67%       10.41%
Std dev                  9.70%       10.80%
MDD                    -13.83%      -12.80%
Sharpe                   0.600        0.608
End balance             15,575       16,046
```

Bridge fidelity:

```text
monthly correlation      0.9168
direction agreement      51/58 = 87.9%
Native-on-Core beta      0.8240
OLS R²                   0.8406
annualized tracking err  4.32%
drawdown correlation     0.9430
```

Interpretation: revised Core is acceptable as a longer-history behavioral approximation of current KAW. It is not a literal Native NAV reconstruction.

### Post-fix KAW benchmark smoke runs

Short / Native benchmark:

```text
runs/20260910-0004
https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0004/report.html
```

Long / Core benchmark:

```text
runs/20260910-0005
https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0005/report.html
```

These supersede `0002/0003` as smoke-validation references because the earlier reports were generated before the fixed-RF propagation bug was corrected. `0002/0003` remain immutable historical artifacts.

`0005` long-run KAW Core summary versus SPY candidate over 2014-07 through 2026-08:

```text
KAW Core CAGR      11.07%
KAW Core Std        9.32%
KAW Core MDD      -12.80%
KAW Core Sharpe     0.77

SPY CAGR           16.73%
SPY Std            14.07%
SPY MDD           -17.41%
SPY Sharpe          0.91
```

The KAW evaluation question is portfolio-level return/stability tradeoff versus alternatives, not whether the revised proxy perfectly reproduces every Native constituent.

## User Provided Portfolio — next comparison candidate

The user previously supplied this fixed-weight portfolio:

| Ticker | Instrument | Weight | Inception / listing |
|---|---|---:|---|
| `QQQ` | Invesco QQQ | 20% | 1999-03-10 |
| `SPMO` | Invesco S&P 500 Momentum ETF | 10% | 2015-10-09 |
| `GDX` | VanEck Gold Miners ETF | 10% | 2006-05-16 |
| `SLV` | iShares Silver Trust | 10% | 2006-04-21 |
| `AIA` | iShares Asia 50 ETF | 15% | 2007-11-13 |
| `XLE` | Energy Select Sector SPDR ETF | 15% | 1998-12-16 |
| `PTF` | Invesco Dorsey Wright Technology Momentum ETF | 10% | 2006-10-12 |
| `SHG` | Shinhan Financial Group ADR | 10% | 2003-09-16 |
| **Total** |  | **100%** |  |

History bottleneck: `SPMO`, inception 2015-10-09.

Canonical first complete Month-to-Month month for the portfolio:

```text
2015-11
```

Therefore:

- long comparison against `kaw_long` can use common period from `2015-11` onward
- recent comparison against `kaw_short` can use common period from `2021-11` onward
- for KAW-risk-matched Maximum Return experiments, use the new default `10.0%` annualized standard-deviation constraint unless an experiment explicitly states another target

## Important Constraints

- No stitched KAW Native/Core NAV.
- Do not reintroduce old `SPY`/`EEM` Core mappings.
- Do not reinterpret historical Direct v1/v2 runs as current Native results.
- Whole-portfolio fidelity is the Core acceptance criterion; avoid fitting individual sleeves to the 58-month bridge window.
- Portfolio generation != portfolio evaluation.
- USD assets are uniformly converted to KRW in internal research.
- `10.0%` is the current default KAW-equivalent **Std/volatility** budget for Maximum Return tests; it is not MDD.

## Next

The KAW baseline is ready. Resume from portfolio-level comparison rather than proxy reconstruction.

Natural next study using the user's Provided Portfolio:

1. Fixed-weight Provided Portfolio vs `kaw_long` over the common long period beginning `2015-11`.
2. Fixed-weight Provided Portfolio vs `kaw_short` over the common recent period beginning `2021-11`.
3. Compare CAGR, annualized Std, MDD, Sharpe/Sortino, drawdown shape, and benchmark-relative metrics.
4. Run opportunity-set / Maximum Return analysis at the canonical KAW-equivalent risk budget of **10.0% annualized Std**.
5. Keep fixed-weight deployed behavior separate from optimized opportunity-set evaluation.
