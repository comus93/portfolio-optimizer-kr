# Session Handover

created_at: 2026-09-11T12:35:00+09:00
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## Current State

The current working thread is no longer KAW proxy reconstruction. It is the **Provided Portfolio optimization report + frontier risk/recovery analysis** work.

Most recent user-facing Maximum Return report:

```text
runs/20260911-0002
https://comus93.github.io/portfolio-optimizer-kr/runs/20260911-0002/report.html
```

The user visually confirmed the previously broken **5Y Rolling Returns chart now works**.

Recent report/UI work already completed before this handover:

- Frontier risk dashboard title is `리스크·성과 균형 분석`.
- Maximum Return report uses the same 8 frontier metrics as Maximum Sharpe.
- Maximum Return target-vol run carries an objective marker/label.
- The risk dashboard was enlarged for desktop:
  - minimum card width roughly `360px`
  - chart height roughly `220px`
  - typically 3 columns on desktop, responsive to 1 column on mobile
- For `target_volatility` runs, a fixed **Target Volatility guideline** was added to the frontier risk charts. It is distinct from the movable selected-point line.
- Report header objective/benchmark pills were made more visible while preserving the existing background treatment.
- 5Y rolling report rendering was fixed by removing the fragile delayed/double-render timing and using the shared historical renderer as the final mount path.

Latest same-universe Maximum Return experiment remains:

```text
studies/provided-portfolio-v1-optimization/experiments/006-aia-schd-max-return-vol11_5-same-period.yaml
```

Same assets / same period as the AIA+SCHD Maximum Sharpe comparison, target volatility 11.5%.

Latest exact Maximum Return optimizer weights from the prior validated run family:

```text
QQQ      15.8052%
SPMO     27.0483%
AIA       0.0000%
GLD      47.6163%
XLE       4.2723%
144600    0.0000%
SCHD      5.2578%
```

The frontier dashboard still has **no automatic Sweet Spot rule**. This is deliberate. The user explicitly wants to inspect actual curves before defining any automatic optimum rule.

---

## Recovery Resilience Discussion — IMPORTANT

The current open work is to make **recovery resilience / rebound strength** an explicit part of drawdown episode analytics.

The user's question is not merely "how long was the portfolio underwater?" but:

> When an asset or portfolio hits a trough, how quickly and strongly does it spring back toward the previous peak?

The user specifically wants to distinguish assets/portfolios that may suffer a deep drawdown but recover sharply, from assets that fall less but remain weak for a long time.

### Existing metrics are not enough

Existing frontier metrics:

- MDD
- Time Under Water (TUW)
- Pain Index
- Max Underwater Months

are useful but do not isolate **Bottom -> Recovery** behavior.

`Max Underwater` slope on the frontier is NOT itself a recovery-resilience metric. Its X-axis is volatility, so its slope only says how worst underwater duration changes as risk changes.

### Existing Drawdown Episode structure

Canonical drawdown episode code currently lives in:

```text
src/portfolio_optimizer_kr/analytics/metrics.py
```

Current `drawdown_episodes()` fields:

```text
rank
start
bottom
recovery
maximum_drawdown
duration_months
```

Important semantic issue:

`duration_months` is currently `len(segment)`, i.e. the number of monthly observations from the first underwater observation through recovery, inclusive. It is not a clean calendar-month difference and it does not isolate recovery time.

Example from current run artifact:

```text
runs/20260911-0002/review/drawdowns.csv
```

Optimized 2020-09 -> 2021-05 episode has:

```text
start          2020-09-30
bottom         2020-10-31
recovery       2021-05-31
duration_months 9
```

Calendar difference is 8 months, but `duration_months=9` because both endpoint observations are counted.

### Existing report already shows a presentation-only Recovery Time

This was a key discovery.

Shared PV-style drawdown renderer already has a table with:

```text
Rank
Start
End
Length
Recovery By
Recovery Time
Underwater Period
Drawdown
```

Relevant shared renderer:

```text
src/portfolio_optimizer_kr/viewer/pv_visual.py
```

It currently computes presentation values from the episode dates:

```text
Length          ~= Start -> Bottom
Recovery Time   = Bottom -> Recovery
Underwater      ~= Start -> Recovery
```

using `_month_delta(...)` and `_duration_label(...)` in the renderer.

This means the visual concept already exists, but the finance semantics are **not canonical upstream values yet**.

That is exactly what the next implementation should fix: move the recovery-duration semantics into canonical analytics/artifacts instead of leaving finance calculations in the renderer.

Architecture rule to preserve:

> Browser/report presentation must not invent or recompute canonical financial metrics. Canonical drawdown/recovery values belong in shared analytics and persisted artifacts.

---

## Agreed Recovery Episode Model

The user approved extending the existing **Drawdown Episode** model rather than creating a separate parallel analytics system.

Conceptual episode:

```text
Peak
 |
 | Decline phase
 v
Bottom / Trough
 |
 | Recovery phase
 v
Recovery to prior Peak
```

Desired fields/concepts:

```text
Peak
Start
Bottom
Recovery
Decline Months
Recovery Months
Underwater Months
Maximum Drawdown
Recovery Rate
```

Not all of these need to become new columns immediately if an existing field already has an accepted meaning, but the canonical semantics must be explicit.

### Recovery Months

Primary direct recovery measure:

```text
Recovery Months = months from Bottom/Trough to Recovery
```

Interpretation:

```text
lower = faster recovery
```

This is the cleanest answer to:

> Once the portfolio hit bottom, how long did it take to regain the previous peak?

Unrecovered episode:

```text
Recovery Months = N/A
```

Never fabricate a future recovery date.

### Recovery Rate

Second metric, meant to account for how deep the trough was.

For a completed episode:

```text
Recovery Rate = (Peak / Trough)^(12 / RecoveryMonths) - 1
```

Equivalent interpretation:

> Annualized compound rate achieved from the trough back to the previous peak.

Example:

```text
Peak = 100
Trough = 80
Recovery Months = 6
Recovery Rate = (100/80)^(12/6)-1 = 56.25%
```

Interpretation:

```text
higher = stronger rebound
```

This avoids the distortion of comparing only recovery duration. A -20% drawdown recovered in 6 months can represent stronger rebound behavior than a -5% drawdown recovered in 3 months.

Edge cases/spec decisions to make explicit during implementation:

- Recovery Rate is unavailable for unrecovered episodes.
- Recovery Months <= 0 requires explicit handling; do not silently divide by zero.
- Use the actual wealth ratio at Peak/Trough, not an approximation that treats MDD percentage points as linear return.
- Preserve monthly-observation semantics and document whether month count is calendar delta vs observation-step count. The preferred direction from discussion is a clean Bottom -> Recovery month delta, not the old inclusive `len(segment)` convention.

### Recovery Progress Curve

The user also liked a possible normalized monthly recovery visualization inspired by Cumulative Active Return charts.

For each episode, align the trough at month 0 and normalize recovery progress:

```text
RecoveryProgress_t = (Value_t - Trough) / (Peak - Trough) * 100
```

So:

```text
Trough        = 0%
Half recovered = 50%
Prior peak    = 100%
```

Potential chart:

```text
X = Months Since Trough
Y = Recovery Progress %
```

This is useful for comparing "spring-like" rebound shape across assets or portfolios.

However, this chart is **not yet implemented and should not be forced into v1 before inspecting the episode-level values first**.

### Asset-level vs portfolio-level recovery

Important interpretation rule:

- Asset recovery curves explain *why* a portfolio may recover well.
- Portfolio recovery episodes are the actual realized portfolio outcome.
- Individual asset recovery curves must not be algebraically added to claim portfolio recovery, because portfolio peak/trough dates, rebalancing, and cross-asset correlations differ.

The user was interested in asset-by-asset monthly recovery curves, but the agreed first move is to make the drawdown episode recovery metrics canonical and inspect real results before defining any aggregate score or more elaborate chart.

---

## What Was Implemented vs NOT Implemented

### Already implemented before the recovery-resilience request

- 5Y Rolling Returns renderer fix, user visually confirmed working.
- Larger `리스크·성과 균형 분석` dashboard.
- Target Volatility guideline for Maximum Return risk-analysis charts.
- More visible objective/benchmark header pills.
- Existing PV-style Drawdown table already displays `Recovery Time` and `Underwater Period`, but these are currently calculated in the renderer from dates.

### Recovery-resilience implementation status

**No new canonical recovery-resilience code was completed yet.**

The previous chat was interrupted while inspecting repository governance/specs and existing drawdown implementation.

Spec/code investigation completed:

- `AGENTS.md` read.
- `openspec/config.yaml` read.
- `openspec/specs/portfolio-analytics/spec.md` inspected.
- `docs/report-ui-specification.md` inspected.
- `src/portfolio_optimizer_kr/analytics/metrics.py` inspected.
- `src/portfolio_optimizer_kr/pipeline.py` inspected.
- `src/portfolio_optimizer_kr/backtest.py` inspected.
- `src/portfolio_optimizer_kr/viewer/pv_visual.py` inspected.
- `src/portfolio_optimizer_kr/viewer/shared_historical_overlay.py` inspected.
- Relevant tests inspected, especially:
  - `tests/test_analytics.py`
  - `tests/test_backtest_report_content_contract.py`

No recovery-specific OpenSpec delta, source change, test change, run, or Pages publication has been completed yet.

Do **not** tell the user that Recovery Months/Recovery Rate is implemented until source + tests + real run have actually been completed and inspected.

---

## Relevant Canonical Specs / Existing Contracts

Current shared analytics spec already requires drawdown episode fields:

```text
openspec/specs/portfolio-analytics/spec.md
```

Current baseline requirement is roughly:

```text
Rank, Start, Bottom, Recovery, Maximum Drawdown, Duration Months
```

Unrecovered episodes must preserve unavailable recovery semantics.

Report UI baseline:

```text
docs/report-ui-specification.md
```

Drawdown episode minimum currently includes:

```text
Rank
Start
Bottom
Recovery
Maximum Drawdown
Duration
```

Shared report architecture already requires Optimization and Backtest to reuse the same historical drawdown component.

Therefore this is a **shared portfolio-analytics change affecting both portfolio-optimization and portfolio-backtest**.

Per AGENTS.md, implementation should:

1. create/update an OpenSpec change first
2. document affected products
3. add affected regressions for both Optimization and Backtest
4. keep finance calculation upstream of the viewer

The existing active change `2026-09-10-frontier-risk-tradeoff` is about frontier risk tradeoff and may not be the cleanest ownership boundary for canonical drawdown episode semantics. Evaluate whether to extend it or create a focused new change such as `2026-09-11-drawdown-recovery-resilience`. Do not create duplicate formulas in product-specific specs.

---

## Recommended Next Implementation

### 1. Create OpenSpec delta

Shared capability:

```text
portfolio-analytics
```

Affected products:

```text
portfolio-optimization
portfolio-backtest
```

Define exact formulas/units for:

```text
Recovery Months
Recovery Rate
```

Also clarify the meaning of existing `duration_months` and whether it remains backward-compatible or is supplemented by explicit decline/recovery/underwater fields.

### 2. Extend canonical `drawdown_episodes()`

File:

```text
src/portfolio_optimizer_kr/analytics/metrics.py
```

Persist at minimum:

```text
recovery_months
recovery_rate
```

Strongly consider explicit upstream values for:

```text
decline_months
underwater_months
```

if that allows the renderer to stop computing finance duration semantics itself.

### 3. Preserve legacy field carefully

Do not silently change `duration_months` semantics without migration/regression review. Existing artifacts/tests may depend on its inclusive observation-count meaning.

Safer first version:

```text
keep duration_months as-is for compatibility
add explicit recovery_months
add explicit decline_months / underwater_months if needed
add recovery_rate
```

Then the user-facing table can use the explicit fields.

### 4. Update shared renderer

File:

```text
src/portfolio_optimizer_kr/viewer/pv_visual.py
```

The renderer should consume canonical persisted values rather than recompute them from dates.

User-facing Worst Drawdowns table can remain close to:

```text
Rank | Start | End/Bottom | Length | Recovery By | Recovery Time | Underwater Period | Drawdown
```

Potential addition after inspecting real results:

```text
Recovery Rate
```

Do not redesign the whole Drawdowns section before seeing the first output.

### 5. Tests

Add synthetic analytics tests proving:

- Bottom -> Recovery month count
- unrecovered episode returns N/A for recovery fields
- Recovery Rate formula matches independent calculation
- legacy `duration_months` behavior is intentionally preserved if kept

Update shared report contract test so the renderer uses canonical recovery values.

Because this is shared analytics, run both Optimization and Backtest affected regressions.

### 6. Real research run

Regenerate the same Provided Portfolio / Maximum Return 11.5% experiment used for `20260911-0002` so the user can compare the recovery metrics without changing the investment universe/period/objective.

Then inspect actual major episodes such as COVID and 2022 rather than immediately inventing a portfolio-level aggregate score.

### 7. Only after viewing results

Discuss whether to add:

- median Recovery Months
- depth-weighted Recovery Months
- depth-weighted Recovery Rate
- Recovery Progress curve
- 1M / 3M / 6M Recovery Progress
- drawdown-depth buckets

Do **not** define a composite `Spring Score` yet.

The user explicitly wants to inspect real episode curves/data before defining any aggregation rule.

---

## Key Product Principle

The recovery-resilience work should remain interpretable:

```text
MDD              = how deep did it fall?
Underwater/TUW   = how long was capital below prior peak?
Recovery Months  = once bottomed, how long to regain the peak?
Recovery Rate    = how forcefully did it compound from trough back to peak?
```

This is the clean conceptual family the user approved.

The immediate next step is implementation + same-condition report regeneration, then review actual results together before adding any aggregate recovery score or automatic rule.
