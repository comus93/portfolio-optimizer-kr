# Proposal: Refactor Optimization execution core

## Why

The Optimization product currently couples one objective solve with expensive
full-run work such as Efficient Frontier generation and repeats canonical
return preparation inside the same execution when the default U.S. 3-Month
T-Bill risk-free rate is resolved.

That cost structure becomes unnecessarily expensive for future repeated
robustness analyses. Creating a separate lightweight optimizer for those
analyses would also introduce a second solver path that could drift from the
normal Optimization product.

## Scope

This change is intentionally semantic-neutral. It does **not** add LOYO or any
new research result.

A. Introduce one shared objective-solving boundary used by the normal
Optimization product and future repeated analyses.

B. Keep Efficient Frontier generation outside the objective-solving boundary
and reuse one parameterized minimum-variance QP across frontier target-return
points.

C. Prepare canonical Optimization monthly/benchmark returns once per default
execution and share that prepared dataset with risk-free resolution and the
analysis pipeline.

## Non-goals

- Leave-One-Year-Out robustness analysis
- start/end-period search or matrix analysis
- dependency installation or GitHub Actions environment optimization
- changing objective formulas, constraints, solver routing, frontier point
  count, market-data semantics, reporting semantics, or persisted finance
  results

## OpenSpec impact

No normative capability requirement changes. `portfolio-optimization` still
uses the same Maximum Sharpe and Maximum Return at Target Volatility semantics,
and Efficient Frontier remains required with the configured point count.

The change is recorded because it materially changes execution architecture and
establishes the shared boundary that later robustness work will reuse.
