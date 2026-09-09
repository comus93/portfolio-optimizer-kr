# KAW Target Reconstruction Study

Reconstruct the current Kim Seong-il K-All Weather portfolio as a reproducible benchmark for later comparison against the user's TO-BE portfolio and for long-horizon behavior analysis.

## Canonical portfolio definitions

- **KAW Direct Proxy**: recent-period proxy that preserves the current nine sleeves as directly as practical. Common usable period begins 2021-11.
- **KAW Core**: compressed long-history proxy using QQQ, SPY, EWY, EEM, EWJ, TLT, and GLD. Long-horizon study period begins 2006-01.
- No STITCH portfolio is used. Direct Proxy and Core are separate experiments with different purposes.

## Canonical report

All research results, interpretation, corrections, evidence links, and follow-up findings are maintained in:

- `studies/kaw-target-reconstruction/report.md`

Future validation should update or append to that report rather than create a parallel summary unless a genuinely separate research question is introduced.

## Study-wide risk-free-rate convention

Until the FinanceDataReader/FRED `TB3MS` dependency issue is fixed, all KAW-related follow-up experiments should use the same fixed annual risk-free rate unless explicitly overridden:

- **Annual RF: 3.8394827586206895%**
- Decimal: `0.038394827586206895`
- Source: successful Direct Proxy run `runs/20260908-0002/result.json`
- Tracking issue: GitHub Issue #1

This rule is specific to the KAW research series and exists to keep repeated experiments deterministic and comparable.

## Current phase

Bridge validation between Direct Proxy and Core is complete enough to proceed to long-horizon Core testing. Core does not reproduce Direct absolute performance exactly, but its monthly and drawdown behavior is sufficiently similar to use as a long-history behavior proxy, subject to the interpretation rules in `report.md`.

The initial native-coverage experiment remains a data-coverage probe only. Its dummy portfolio weights are not an investment allocation and its performance metrics are not used for research conclusions.
