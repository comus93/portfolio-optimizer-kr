# LLM Analysis Framework for Portfolio Optimization Results

## Purpose

This is a standalone handover/reference document for an LLM that receives a Portfolio Visualizer optimization result page or an equivalent optimizer result.

The LLM should not treat the historical optimum as a live allocation recommendation. The purpose of the analysis is to answer:

> **What marginal utility does each asset add to the portfolio, where on the efficient frontier does that utility appear, and is that role meaningful and robust?**

The analysis is portfolio-centric. Standalone asset performance is supporting evidence, not the primary decision rule.

## Expected input

The input may be a Portfolio Visualizer result page, pasted result text, exported tables, screenshots, or equivalent optimizer output containing some or all of the following:

- optimization configuration
- objective portfolio
- efficient frontier assets
- efficient frontier portfolios
- expected return / volatility / Sharpe
- correlations
- annual and rolling returns
- drawdowns
- active-return contribution
- return and risk decomposition

The framework should still be applied when some sections are missing. State which conclusions are weaker because evidence is unavailable.

---

## 1. Confirm the experiment before interpreting results

Read the configuration first.

Check:

- analysis period
- optimization objective
- benchmark
- risk-free rate
- rebalancing frequency
- asset universe
- minimum and maximum weight constraints
- whether one asset shortened the common analysis period

### Constraint rule

A weight exactly on a minimum or maximum constraint is not an unconstrained optimum.

Example:

- GLD maximum weight = 30%
- optimized GLD weight = 30%

Interpretation:

> The optimizer wanted at least the permitted 30%. The unconstrained optimum may lie beyond the boundary.

Do not interpret a binding constraint as the economically preferred allocation.

---

## 2. Use the objective portfolio as an anchor, not the answer

For a Maximum Sharpe run, first inspect the Maximum Sharpe portfolio.

Record:

- selected assets
- zero-weight assets
- weights
- expected return
- standard deviation
- Sharpe ratio
- CAGR, when available
- maximum drawdown, when available

First-pass question for each candidate:

> **Does this asset enter the objective portfolio?**

This is only an anchor. A zero weight at the exact optimum does not by itself justify rejection because the asset may still be useful elsewhere on the efficient frontier.

---

## 3. Inspect the entire efficient frontier

The efficient-frontier portfolio table is one of the highest-value outputs.

Read from the low-risk end through the objective region and toward the high-return end. Track each asset's weight trajectory.

### Frontier behavior classes

**A. Zero across nearly the entire frontier**

The asset is dominated by combinations of other available assets.

Initial interpretation: **low marginal utility**.

**B. Appears only on the low-risk edge**

The asset offers some diversification but loses usefulness when higher return is required.

Initial interpretation: **weak or defensive diversifier**.

**C. Persists around the objective region**

This is a strong signal. A meaningful weight across several neighboring frontier portfolios is more credible than one exact optimum.

Initial interpretation: **structural portfolio contributor**.

**D. Appears mainly on the high-return side**

The asset is not primarily a risk-adjusted-return optimizer but helps raise expected return.

Initial interpretation: **return engine**.

### Prefer regions over exact points

Do not over-focus on a weight such as 17.3% or 24.6%.

Look for stable regions or plateaus where neighboring portfolios retain similar quality and composition.

A broad useful region is more important than one mathematically optimal point.

---

## 4. Compare Sharpe sacrificed with return gained

Starting at the Maximum Sharpe point, move toward higher-return frontier portfolios.

Compare:

- expected-return increase
- volatility increase
- Sharpe decline
- composition changes

Core question:

> **How much additional expected return is gained for the reduction in risk-adjusted efficiency?**

A small Sharpe decline accompanied by a meaningful return increase can define a more attractive practical region than the exact Maximum Sharpe point.

A large volatility increase or sharp Sharpe decline for little extra return is unattractive.

Identify **Sharpe-return plateaus**, not only the numerical maximum.

---

## 5. Track substitution: who enters and who leaves?

When a candidate asset's weight rises, identify which existing asset weights fall.

This often reveals the candidate's true portfolio role.

Examples:

- a higher-beta growth asset replaces QQQ: higher-return version of an existing growth engine
- one regional equity replaces another: potentially redundant regional exposure
- a candidate remains at zero while two existing assets dominate: those assets may already provide the same useful characteristics more efficiently

Always ask:

> **What existing asset does this candidate replace, and what genuinely new behavior does it add?**

An asset can be attractive in isolation yet redundant in the portfolio.

---

## 6. Read correlation together with return and volatility

Correlation is diagnostic evidence, not a standalone selection rule.

Do not conclude:

> low correlation = good portfolio asset

Evaluate together:

- correlation with major portfolio assets
- expected return
- standard deviation
- standalone Sharpe / Sortino
- frontier inclusion

A low-correlation asset may still be rejected if its volatility is too high or expected return is too weak.

A higher-correlation asset may still be useful if its return efficiency is strong enough.

Core question:

> **Is the diversification benefit cheap enough in terms of sacrificed return and added volatility?**

---

## 7. Use standalone metrics to explain, not decide

Review component statistics:

- expected return
- CAGR
- standard deviation
- Sharpe ratio
- Sortino ratio
- maximum drawdown

These metrics help explain optimizer behavior.

They should not override portfolio-level evidence.

An asset with mediocre standalone Sharpe can still improve a portfolio through correlation structure. An asset with excellent standalone Sharpe can still be redundant.

Priority:

> **Portfolio marginal utility > standalone performance**

---

## 8. Identify regime behavior

Use annual returns, monthly returns, stress periods, and up/down-market statistics to understand when an asset earns or loses money.

Ask:

- Did it protect during equity selloffs?
- Did it work mainly during inflation, commodity, growth, value, or another identifiable regime?
- Did most of its benefit come from one exceptional year?
- Does its behavior have a plausible economic role?

This step checks whether the optimizer result has an understandable economic explanation rather than looking like a statistical accident.

A diversifier does not need to perform well in every regime. Its value may come from performing differently.

---

## 9. Examine drawdown depth and recovery

Inspect:

- maximum drawdown
- worst drawdowns
- recovery time
- underwater period
- stress-period losses

Do not treat equal MDD values as equivalent when recovery behavior differs.

A portfolio that loses 20% and recovers in six months is materially different from one that loses 20% and remains underwater for three years.

Always distinguish:

> **drawdown depth** and **drawdown duration**

---

## 10. Check rolling-return robustness

Full-period averages can hide dependence on the selected start and end dates.

Inspect when available:

- rolling 1-year returns
- rolling 3-year returns
- rolling 5-year returns
- average / high / low values

Give particular attention to rolling 3-year and 5-year lows.

Ask:

- Does the optimized portfolio remain acceptable across different subperiods?
- Is the strong full-period result driven mainly by a recent regime?
- Does the candidate contribute consistently or only in a narrow window?

A strong full-period result with weak rolling lows deserves a robustness warning.

---

## 11. Use contribution and decomposition tables to detect hidden costs

When available, inspect:

### Active Return Contribution

Compare recent contribution with full-period contribution.

Strong 1-year or 3-year contribution but weak long-period contribution may indicate recency dependence.

### Return Decomposition

Measure how much portfolio gain came from each asset.

### Risk Decomposition

Measure how much portfolio volatility each asset consumed.

Compare allocation weight, return contribution, and risk contribution.

Examples:

- small allocation + large risk contribution + weak return contribution: inefficient
- small allocation + modest risk contribution + meaningful return contribution: efficient

Core question:

> **How much return did the asset provide relative to the portfolio risk it consumed?**

---

## 12. Final asset-role classification

Do not force every asset into a binary keep/drop decision.

| Classification | Interpretation |
|---|---|
| **KEEP / Strong** | Meaningful weight persists around the objective region and neighboring frontier portfolios. |
| **KEEP / Return Engine** | Mainly useful on the higher-return side of the frontier. |
| **KEEP / Diversifier** | Materially improves lower- or medium-risk portfolios through distinct behavior. |
| **WATCH** | Some utility exists, but it is small, unstable, or limited to a narrow frontier or regime. |
| **REDUNDANT** | Asset may be good individually, but existing assets provide the same role more efficiently. |
| **DROP** | Little or no marginal utility across the relevant frontier. |

Each classification should include a short reason based on frontier behavior and supporting evidence.

---

## Standard analysis sequence

Use this order for every review:

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

- Do not treat historical Maximum Sharpe weights as recommended live weights.
- Do not interpret a binding min/max weight as an unconstrained optimum.
- Do not reject an asset solely because its standalone Sharpe is low.
- Do not select an asset solely because correlation is low.
- Do not overvalue one exact frontier point; prefer stable neighboring regions.
- Flag results dominated by recent performance or a short common history.
- Distinguish statistical inclusion from an understandable portfolio role.

---

## Recommended LLM response format

### 1. Executive conclusion

State the main portfolio finding in 2-4 sentences.

### 2. Objective portfolio

Report composition and key metrics.

### 3. Frontier interpretation

Describe:

- candidate weight trajectory
- Sharpe-return plateau
- assets entering and leaving

### 4. Diversification and redundancy

Explain correlation together with return/volatility and substitution behavior.

### 5. Robustness

Summarize drawdowns, recovery, rolling returns, and regime dependence.

### 6. Final classification

Assign important candidates one of:

`KEEP / Strong`, `KEEP / Return Engine`, `KEEP / Diversifier`, `WATCH`, `REDUNDANT`, `DROP`.

Include the evidence driving the classification.

---

## Guiding principle

> **Use optimization to discover portfolio structure, not a historical weight to copy. The central question is whether an asset adds independent and meaningful marginal utility, what role it plays, and whether that role survives across the efficient frontier and time.**
