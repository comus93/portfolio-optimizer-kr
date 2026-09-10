# Session Handover

created_at: 2026-09-10
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## Current State

KAW target-reconstruction study is being revised before rerunning the Native-vs-Core bridge.

Canonical sources:

```text
studies/kaw-target-reconstruction/study.md
studies/kaw-target-reconstruction/report.md
```

`study.md` owns the current portfolio definitions. Historical runs remain immutable evidence under their original definitions.

## Decisions

### KAW Native Proxy — current canonical

| Sleeve | Code/Ticker | Proxy | Weight | Listing/Inception |
|---|---|---|---:|---|
| Nasdaq100 | 133690 | TIGER 미국나스닥100 | 10% | 2010-10-18 |
| US dividend | 402970 | ACE 미국배당다우존스 | 10% | 2021-10-21 |
| Korea | 069500 | KODEX 200 | 8% | 2002-10-14 |
| China CSI300 | 192090 | TIGER 차이나CSI300 | 8.5% | 2014-02-17 |
| India Nifty50 | 200250 | KIWOOM 인도Nifty50(합성) | 8.5% | 2014-06-26 |
| Japan | 101280 | KODEX 일본TOPIX100 | 5% | 2008-02-20 |
| US long Treasury | 267440 | RISE 미국장기국채선물(H) | 15% | 2017-04-20 |
| KR 30Y Treasury | 385560 | RISE KIS국고채30년Enhanced | 15% | 2021-05-26 |
| Gold | GLD | SPDR Gold Shares | 20% | 2004-11-18 |

History bottleneck: `402970`, listed 2021-10-21.

Therefore:

```text
all constituents exist from: 2021-10-21
first complete Month-to-Month month: 2021-11
canonical Native usable period: 2021-11 onward
standard completed bridge window: 2021-11-01 ~ 2026-08-31
```

### KAW Core — revised economic definition

Old Core `QQQ / SPY / EWY / EEM / EWJ / TLT / GLD` is retired for new research.

PV implementation:

```text
QQQ 10
SCHD 10
EWY 8
ASHR 8.5
INDY 8.5
EWJ 5
TLT 30
GLD 20
```

PV listing/inception dates:

```text
QQQ   1999-03-10
SCHD  2011-10-20
EWY   2000-05-09
ASHR  2013-11-06
INDY  2009-11-18
EWJ   1996-03-12
TLT   2002-07-22
GLD   2004-11-18
```

Core PV default conservative start: `2014-01`.

Internal-engine implementation:

```text
QQQ 10
SCHD 10
EWY 8
192090 8.5
200250 8.5
EWJ 5
TLT 30
GLD 20
```

Internal Core bottleneck is `200250`, listed 2014-06-26. First complete calendar month is `2014-07`, so canonical Internal-Core usable period is `2014-07 onward`.

PV uses ASHR/INDY for US-listed compatibility. Internal engine uses 192090/200250 because they reproduce the intended native China/India paths better in recent comparison.

Gold is GLD in both Native and Core.

Bond definition remains:

```text
Native = 267440 15% + 385560 15%
Core   = TLT 30%
```

TLT is a coarse aggregate bond-sleeve proxy, not a literal proxy for either component.

### FX rule

Internal research reports in KRW and applies the same USD/KRW conversion rule to every USD asset. No asset-specific FX exception is allowed merely because it improves recent-period correlation. The earlier local-USD TLT experiment is diagnostic evidence only.

### Risk target / RF

Final experimental target volatility remains `11.5%`, not 9.94%.

Pinned research RF when omitted:

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

## Important Constraints

- No stitched Direct/Core NAV.
- Portfolio generation != evaluation.
- Do not reinterpret historical Direct v1/v2 runs as results for the current Native definition.
- Whole-portfolio bridge fidelity is the final acceptance criterion. Do not overfit individual sleeves to the recent bridge window.

## Next

Rerun the bridge with the revised definitions over the common Native window `2021-11-01 ~ 2026-08-31`, then evaluate correlation, direction agreement, beta, tracking error, drawdown correlation, volatility ratio, CAGR gap, and whether a scalar calibration is still necessary.
