# Session Handover

created_at: 2026-09-10
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## Current State

KAW 재구성의 current canonical 정의를 개정했다. 현재 정의의 source of truth는:

```text
studies/kaw-target-reconstruction/study.md
```

`studies/kaw-target-reconstruction/report.md`의 SPY/EEM/132030 기반 표와 기존 run은 historical evidence이며 current 정의로 재해석하면 안 된다.

## Decisions

### KAW Native Proxy

```text
133690  TIGER 미국나스닥100             10.0%
402970  ACE 미국배당다우존스            10.0%
069500  KODEX 200                        8.0%
192090  TIGER 차이나CSI300               8.5%
200250  KIWOOM 인도Nifty50(합성)         8.5%
101280  KODEX 일본TOPIX100               5.0%
267440  RISE 미국장기국채선물(H)         15.0%
385560  RISE KIS국고채30년Enhanced       15.0%
GLD     SPDR Gold Shares                 20.0%
```

Standard recent period: 2021-11 onward.

Changes: China `168580 -> 192090`; Gold `132030 -> GLD`; India stays `200250`.

### KAW Core: Portfolio Visualizer

```text
QQQ   10.0%
SCHD  10.0%
EWY    8.0%
ASHR   8.5%
INDY   8.5%
EWJ    5.0%
TLT   30.0%
GLD   20.0%
```

Conservative full-month start: 2014-01 onward.

### KAW Core: internal engine

```text
QQQ     10.0%
SCHD    10.0%
EWY      8.0%
192090   8.5%
200250   8.5%
EWJ      5.0%
TLT     30.0%
GLD     20.0%
```

Conservative full-month start: 2014-07 onward.

PV uses ASHR/INDY for platform compatibility. Internal engine uses 192090/200250 because recent native return-path fidelity is materially better. These are two implementations of the same economic Core.

Old `SPY 10 + EEM 17` Core is retired as current canonical because SPY is a weak US-dividend proxy and EEM introduces unintended Taiwan/Korea/other-EM exposure.

### Bond

Keep:

```text
Native bond = 267440 15% + 385560 15%
Core bond   = TLT 30%
```

TLT is a coarse aggregate long-duration proxy, not a literal replica of either native component. In consistent KRW comparison it does not perfectly match monthly movement, but risk magnitude is closer than EDV/ZROZ. Final acceptance is at whole-portfolio level because bond is 30% of KAW.

### FX

```text
Internal reporting currency = KRW
All USD assets -> same USD/KRW conversion rule
No asset-specific FX exception
```

Do not remove FX from TLT merely because local-USD correlation improves. That is ex-post tuning / overfitting. Local-USD bond runs are diagnostic only.

### Risk target / RF

Final target-vol evaluation target remains **11.5% annual volatility**.

Default repeated-study RF unless explicitly overridden:

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

GitHub Issue #1 remains open for dynamic TB3MS robustness.

## Next

Run a fresh whole-portfolio bridge with revised Native Proxy vs revised Core Internal under one KRW FX rule. Evaluate monthly correlation, direction agreement, beta, tracking error, volatility ratio, drawdown correlation, MDD timing/depth, and secondary CAGR gap. Do not tune proxies after seeing the result merely to maximize recent fit.
