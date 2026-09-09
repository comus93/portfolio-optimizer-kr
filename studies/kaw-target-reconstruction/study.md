# KAW Target Reconstruction Study

Reconstruct the current Kim Seong-il K-All Weather portfolio as a reproducible benchmark for later comparison against the user's TO-BE portfolio and for long-horizon behavior analysis.

## Canonical portfolio definitions

- **KAW Direct Proxy**: recent-period proxy that preserves the current nine sleeves as directly as practical. Common usable period begins 2021-11.
  - Canonical US long-Treasury sleeve is now **267440 RISE 미국장기국채선물(H) 15%**.
  - Earlier Direct Proxy experiments that used **TLT 15%** are retained as historical **Direct Proxy v1** evidence and must not be silently relabeled as the current canonical Direct Proxy.
- **KAW Core**: compressed long-history proxy using QQQ, SPY, EWY, EEM, EWJ, TLT, and GLD. Long-horizon study period begins 2006-01.
- No STITCH portfolio is used. Direct Proxy and Core are separate experiments with different purposes.

The 267440 ETF was listed in 2017, so this revision does not shorten the Direct Proxy common test start of 2021-11.

## Canonical report

All research results, interpretation, corrections, evidence links, and follow-up findings are maintained in:

- `studies/kaw-target-reconstruction/report.md`

Future validation should update or append to that report rather than create a parallel summary unless a genuinely separate research question is introduced.

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
- Source: successful Direct Proxy v1 run `runs/20260908-0002/result.json`
- Tracking issue: GitHub Issue #1

Reason: once a research period's RF has already been resolved, repeated experiments over the same period do not need to re-fetch the same economic series. Fixed mode improves determinism, reproducibility, and run reliability.

## Current phase

The original TLT-based Direct Proxy v1 to Core bridge study established useful methodology and movement-fidelity evidence, but the canonical Direct Proxy has now been revised to use **267440 RISE 미국장기국채선물(H)** for the US long-bond sleeve.

Therefore, before treating Direct-vs-Core bridge metrics as current canonical evidence or using Direct Proxy in the next TO-BE comparison, rerun the key recent-period Direct experiments and movement-fidelity checks with 267440.

The initial native-coverage experiment remains a data-coverage probe only. Its dummy portfolio weights are not an investment allocation and its performance metrics are not used for research conclusions.
