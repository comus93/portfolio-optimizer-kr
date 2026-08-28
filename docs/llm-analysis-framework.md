# LLM Analysis Framework for Portfolio Optimization Results

## Purpose

This document defines how an LLM should analyze a portfolio optimization result page or equivalent optimizer output.

The goal is not to copy the mathematically optimal historical allocation. The goal is to determine:

> **What marginal utility does each asset add to the portfolio, where on the efficient frontier does that utility appear, and is that role robust enough to matter?**

The analysis should focus on portfolio-level usefulness rather than standalone asset performance.

---

## 1. Confirm the experiment before interpreting the result

Read the configuration first.

Check:

- analysis period
- optimization objective
- benchmark
- risk-free rate
- rebalancing frequency
- asset universe
- minimum and maximum weight constraints
- whether the analysis period is shortened by the history of one asset

### Constraint rule

A weight that is exactly on a minimum or maximum constraint is not an unconstrained optimum.

Example:

- GLD maximum weight = 30%
- optimized GLD weight = 30%

Interpretation:

> The optimizer wants at least as much as the allowed 30%. The true unconstrained optimum may lie outside the permitted range.

Do not interpret the constraint boundary itself as the preferred economic allocation.

---

## 2. Use the optimization objective as an anchor, not as the final answer

For a Maximum Sharpe run, first inspect the Maximum Sharpe portfolio.

Record:

- selected assets
- zero-weight assets
- weights
- expected return
- standard deviation
- Sharpe ratio
- CAGR when available
- maximum drawdown when available

The first question for a candidate asset is:

> **Does the asset enter the objective portfolio at all?**

This is only a first-pass signal. A zero weight at the Maximum Sharpe point does not by itself justify rejection because the asset may still have value elsewhere on the efficient frontier.

---

## 3. Inspect the entire efficient frontier

The efficient-frontier portfolio table is one of the highest-value outputs.

Read it from low risk to high return and track how each asset's weight changes.

For each asset, classify its frontier behavior.

### A. Zero across nearly the entire frontier

The asset is dominated by combinations of other available assets.

Initial interpretation: **low marginal utility**.

### B. Appears only on the low-risk edge

The asset provides some diversification but loses usefulness when more return is required.

Initial interpretation: **weak or defensive diversifier**.

### C. Persists around the Maximum Sharpe region

This is a strong signal.

If an asset maintains a meaningful weight across several neighboring frontier portfolios, its role is less likely to be an artifact of one exact optimum.

Initial interpretation: **structural portfolio contributor**.

### D. Appears mainly on the high-return side

The asset is not primarily improving the maximum risk-adjusted point but is useful for raising expected return.

Initial interpretation: **return engine**.

### Prefer regions over exact points

Do not over-focus on a precise allocation such as 17.3% or 24.6%.

Look for a stable region or plateau where nearby portfolios retain similar quality.

A broad useful region is more important than a single numerically optimal point.

---

## 4. Evaluate return gained per unit of Sharpe sacrificed

After locating the Maximum Sharpe point, move toward higher-return frontier portfolios.

Compare:

- increase in expected return
- increase in volatility
- decline in Sharpe ratio
- change in asset composition

The key question is:

> **How much additional expected return is obtained for the loss in risk-adjusted efficiency?**

A small decline in Sharpe combined with a meaningful increase in expected return may define a more attractive practical region than the exact Maximum Sharpe point.

Conversely, a large increase in volatility or a sharp Sharpe decline for little additional return indicates an unattractive region.

The LLM should identify useful **Sharpe-return plateaus**, not merely report the numerical maximum.

---

## 5. Track substitution: who enters and who leaves?

When an asset's weight increases along the frontier, identify which assets decrease.

This reveals the economic role of the candidate.

Examples of interpretation:

- QQQ decreases while a higher-beta Nasdaq asset increases: higher-return replacement of the same growth engine.
- One regional equity asset replaces another: potentially redundant regional exposure.
- A candidate remains at zero while two existing assets retain large weights: existing assets may already provide the candidate's useful characteristics more efficiently.

Always ask:

> **What existing asset does this candidate replace, and what genuinely new behavior does it add?**

An asset can be attractive in isolation yet still be redundant in the portfolio.

---

## 6. Read correlation together with return and volatility

Correlation is diagnostic evidence, not a standalone selection rule.

Do not conclude:

> low correlation = good portfolio asset

Instead evaluate jointly:

- correlation with major portfolio assets
- expected return
- standard deviation
- standalone Sharpe / Sortino
- observed frontier inclusion

A low-correlation asset may still be rejected if its volatility is too high or expected return is too weak.

A higher-correlation asset can still be useful if its return efficiency is sufficiently strong.

The core question is:

> **Is the diversification benefit cheap enough in terms of sacrificed return and added volatility?**

---

## 7. Use standalone asset metrics to explain, not decide

Review the component statistics:

- expected return
- CAGR
- standard deviation
- Sharpe ratio
- Sortino ratio
- maximum drawdown

These metrics help explain why the optimizer selected or rejected an asset.

They should not override portfolio-level evidence.

An asset with a mediocre standalone Sharpe can still improve a portfolio because of correlation structure.

An asset with an excellent standalone Sharpe can still be redundant if another asset already supplies the same return pattern.

Priority:

> **Portfolio marginal utility > standalone performance**

---

## 8. Identify economic or regime behavior

Use annual returns, monthly returns, stress periods, and up/down-market statistics to understand when an asset earns or loses money.

Ask:

- Did it protect during equity selloffs?
- Did it work mainly during inflation, commodity, growth, value, or other identifiable regimes?
- Did its benefit come from one exceptional year?
- Does its behavior have an understandable economic role?

This step checks whether optimizer results have a plausible economic explanation rather than being a statistical accident.

Do not require every asset to perform well in every regime. A diversifier may be valuable precisely because it performs differently.

---

## 9. Examine drawdown depth and recovery

For optimized portfolios and important candidate configurations, inspect:

- maximum drawdown
- worst drawdowns
- recovery time
- underwater period
- stress-period losses

Do not treat equal MDD values as equivalent if recovery behavior is different.

A portfolio that loses 20% and recovers in six months is materially different from one that loses 20% and remains underwater for three years.

The analysis should therefore distinguish:

> **drawdown depth** and **drawdown duration**

---

## 10. Check rolling-return robustness

Full-period averages can hide strong dependence on the selected start and end dates.

Inspect rolling returns when available, especially:

- rolling 1-year
- rolling 3-year
- rolling 5-year
- average / high / low values

Give particular attention to rolling 3-year and 5-year lows.

Questions:

- Does the optimized portfolio remain acceptable across different subperiods?
- Is the strong full-period result driven mainly by one recent regime?
- Does the candidate contribute consistently or only in a narrow time window?

A strong full-period result with poor rolling lows deserves a robustness warning.

---

## 11. Use active-return and decomposition tables to detect hidden costs

When available, inspect:

### Active Return Contribution

Compare recent and full-period contribution.

If an asset has strong 1-year or 3-year active contribution but weak full-period contribution, flag possible recency dependence.

### Return Decomposition

Measure how much portfolio gain came from each asset.

### Risk Decomposition

Measure how much portfolio volatility each asset contributed.

Compare allocation weight, return contribution, and risk contribution.

Examples:

- small weight + large risk contribution + weak return contribution: inefficient
- small weight + modest risk contribution + meaningful return contribution: efficient

The purpose is to answer:

> **How much return did the asset provide relative to the amount of portfolio risk it consumed?**

---

## 12. Final asset-role classification

Do not force every asset into a binary keep/drop decision.

Use role-based classifications.

| Classification | Interpretation |
|---|---|
| **KEEP / Strong** | Meaningful weight persists around the objective region and across neighboring frontier portfolios. |
| **KEEP / Return Engine** | Mainly useful on the higher-return side of the frontier. |
| **KEEP / Diversifier** | Materially improves lower- or medium-risk portfolios through distinct behavior. |
| **WATCH** | Some portfolio utility exists, but it is small, unstable, or limited to a narrow frontier/regime. |
| **REDUNDANT** | Asset may be good individually, but existing assets provide the same role more efficiently. |
| **DROP** | Little or no marginal utility across the relevant frontier. |

A final classification should state the reason in one or two sentences.

---

## Analysis order

Use this sequence for every optimization review:

1. **Experiment configuration and constraints**
2. **Objective portfolio as anchor**
3. **Efficient-frontier weight trajectory**
4. **Sharpe sacrifice versus expected-return gain**
5. **Asset substitution and portfolio role**
6. **Correlation together with return and volatility**
7. **Standalone metrics as supporting evidence**
8. **Regime and annual-return behavior**
9. **Drawdown and recovery behavior**
10. **Rolling-return robustness**
11. **Active-return / return-risk decomposition**
12. **Role-based final classification**

---

## Interpretation guardrails

### Do not treat Maximum Sharpe weights as recommended live weights

Historical optimization identifies useful structure. It does not establish the future optimal allocation.

### Do not equate a boundary weight with an unconstrained optimum

Always note binding min/max constraints.

### Do not reject an asset solely because its standalone Sharpe is low

Portfolio interaction can create value.

### Do not select an asset solely because correlation is low

Diversification has a cost in return and volatility.

### Do not overvalue one exact frontier point

Prefer stable neighboring regions and composition patterns.

### Watch for recent-period dominance

Strong recent performance can distort full-period interpretation, especially when the analysis window is short.

### Distinguish statistical inclusion from economic role

Whenever possible, explain why the asset behaves differently and what portfolio function it performs.

---

## Recommended LLM output format

A result review should be concise but decision-oriented.

### 1. Executive conclusion

State the main portfolio finding in 2-4 sentences.

### 2. Objective portfolio

Report the optimized composition and key metrics.

### 3. Frontier interpretation

Describe:

- candidate weight trajectory
- Sharpe-return plateau
- assets entering and leaving

### 4. Diversification and redundancy

Explain correlation evidence together with return/volatility and substitution behavior.

### 5. Robustness

Summarize drawdowns, recovery, rolling returns, and regime dependence.

### 6. Final classification

Assign each important candidate one of:

`KEEP / Strong`, `KEEP / Return Engine`, `KEEP / Diversifier`, `WATCH`, `REDUNDANT`, `DROP`.

Include the evidence that drove the classification.

---

## Guiding principle

> **The optimizer is not used to discover a historical weight to copy. It is used to discover whether an asset adds independent and meaningful marginal utility to the portfolio, what role it plays, and how robust that role is across the efficient frontier and time.**
