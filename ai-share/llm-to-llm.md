# Session Handover

created_at: 2026-09-10
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## Current State

KAW target-reconstruction proxy redesign and revised Native-vs-Core bridge rerun are complete.

Canonical sources:

```text
studies/kaw-target-reconstruction/study.md
studies/kaw-target-reconstruction/report.md
```

`study.md` owns current portfolio definitions, listing/inception-derived usable periods, and the canonical routing rule for which KAW representation to use by research purpose. `report.md` owns current interpretation and bridge evidence. Historical runs remain immutable under their original definitions.

## Decisions

### KAW Native Proxy — current canonical

```text
133690  TIGER 미국나스닥100               10.0%
402970  ACE 미국배당다우존스              10.0%
069500  KODEX 200                          8.0%
192090  TIGER 차이나CSI300                 8.5%
200250  KIWOOM 인도Nifty50(합성)           8.5%
101280  KODEX 일본TOPIX100                 5.0%
267440  RISE 미국장기국채선물(H)           15.0%
385560  RISE KIS국고채30년Enhanced         15.0%
GLD     SPDR Gold Shares                  20.0%
```

History bottleneck is `402970`, listed 2021-10-21. First complete Month-to-Month month is `2021-11`, so Native canonical usable period is `2021-11 onward`. Standard completed bridge window is `2021-11-01 ~ 2026-08-31`.

### KAW Core — revised current definition

PV implementation:

```text
QQQ 10 / SCHD 10 / EWY 8 / ASHR 8.5 / INDY 8.5 / EWJ 5 / TLT 30 / GLD 20
```

Conservative PV start: `2014-01`.

Internal-engine implementation:

```text
QQQ 10 / SCHD 10 / EWY 8 / 192090 8.5 / 200250 8.5 / EWJ 5 / TLT 30 / GLD 20
```

Internal-Core usable period: `2014-07 onward`, constrained by 200250 listing 2014-06-26.

PV uses ASHR/INDY for US-listed compatibility. Internal engine uses 192090/200250 for higher Native return-path fidelity.

Old Core `QQQ / SPY / EWY / EEM / EWJ / TLT / GLD` is retired for new canonical research.

Gold is GLD in both Native and Core.

Bond convention remains:

```text
Native = 267440 15% + 385560 15%
Core   = TLT 30%
```

TLT is a coarse aggregate bond-sleeve proxy. Do not create asset-specific FX exceptions to improve recent fit.

### Canonical KAW representation routing — IMPORTANT

Use the representation by research purpose:

```text
Recent / short-period internal-engine comparison
→ KAW Native Proxy
→ usable 2021-11 onward

Long-history internal-engine comparison
→ KAW Core Revised Internal
→ usable 2014-07 onward

Portfolio Visualizer research
→ KAW Core PV
→ conservative start 2014-01
```

Rules:

- For recent comparisons, use Native whenever the compared portfolio has a common period within Native availability.
- For long-history work inside `portfolio-optimizer-kr`, use the Internal Core, not the PV Core.
- Use the PV Core only when running or reproducing work in Portfolio Visualizer.
- Do not stitch Native backward before 2021-11.
- Do not use the PV Core as the default internal Core merely to make PV and internal inputs look identical.
- Every new KAW experiment should identify which representation it uses and why.

### FX / RF / risk target

- Internal research reports in KRW.
- Every USD asset uses the same USD/KRW conversion rule.
- Pinned default RF: `3.8394827586206895%` fixed annual.
- Main risk-matched evaluation target: `11.5%` annual volatility.

## Revised canonical bridge result

Experiment:

```text
studies/kaw-target-reconstruction/experiments/020-kaw-native-vs-revised-core-backtest.yaml
```

Run:

```text
runs/20260910-0001
https://comus93.github.io/portfolio-optimizer-kr/runs/20260910-0001/report.html
```

Conditions: 2021-11 through 2026-08, 58 months, Month-to-Month, monthly rebalancing, KRW, uniform USD/KRW conversion, SPY benchmark, fixed RF.

Performance:

```text
                        Native       Core
CAGR                    9.60%       10.28%
Annualized return       9.67%       10.41%
Std dev                  9.70%       10.80%
MDD                    -13.83%      -12.80%
Sharpe                   0.600        0.608
End balance             15,575       16,046
```

Whole-portfolio bridge fidelity:

```text
monthly correlation      0.9168
direction agreement      51/58 = 87.9%
Native-on-Core beta      0.8240
OLS R²                   0.8406
annualized tracking err  4.32%
drawdown correlation     0.9430
Core/Native vol ratio    1.113
MDD trough               both 2022-12
```

Versus superseded run `20260909-0013`:

```text
CAGR gap        3.86%p -> 0.68%p
end balance gap 2705   -> 471
correlation     0.8517 -> 0.9168
direction       81.0%  -> 87.9%
tracking error  6.28%  -> 4.32%
R²              0.7255 -> 0.8406
drawdown corr   0.9095 -> 0.9430
```

The remaining +471 Core end-balance advantage is dominated by the bond compression: TLT contributes about +613 versus Native's combined 267440+385560 contribution, while all non-bond sleeves together offset about 142 in Native's favor.

Interpretation: proxy redesign materially fixed the earlier bridge distortion. Current Core is a credible behavioral approximation, not a literal Native NAV replica. The old `Core × 0.70` calibration idea remains discarded.

## Important Constraints

- No stitched Native/Core NAV.
- Do not reintroduce SPY/EEM old Core mappings.
- Do not reinterpret historical Direct v1/v2 runs as current Native results.
- Whole-portfolio bridge fidelity is the acceptance criterion. Avoid fitting individual sleeves to the 58-month bridge window.
- Portfolio generation != evaluation.

## Next

Resume portfolio-level research using the routing rule above:

- recent comparison → KAW Native Proxy
- long-history internal comparison → KAW Core Revised Internal
- Portfolio Visualizer work → KAW Core PV

For risk-matched comparisons use 11.5% annual volatility.
