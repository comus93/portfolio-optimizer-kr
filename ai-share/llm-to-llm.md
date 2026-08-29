# Session Handover

created_at: 2026-08-29T19:30:00+09:00
project: `comus93/portfolio-optimizer-kr`

## Current State

Report-review v4 implementation is complete on the LLM side and targeted GitHub-side CI passed. Codex Agent independent real-run/browser validation is pending.

A major governance change was made after v4 implementation:

> **PV/screenshots are no longer product acceptance sources. Internal specifications are the product source of truth.**

Canonical hierarchy:

```text
Finance / calculation semantics   docs/specification.md
Report UI / interaction semantics docs/report-ui-specification.md
Architecture / responsibility     docs/architecture.md
Validation procedure              docs/visual-acceptance-contract.md
External references               PV / screenshots / historical golden, non-normative
```

`AGENTS.md` and `ai-share/llm-to-agent.md` were updated to this hierarchy.

## Product Logic Baseline

`docs/specification.md` now canonically defines:

- FDR market-data pipeline and common coverage
- monthly simple returns
- arithmetic annual expected return
- sample covariance × 12
- realized volatility × sqrt(12)
- risk-free modes
- long-only fully-invested constraints
- Maximum Sharpe Ratio
- Maximum Return at Target Volatility
- 100-point Efficient Frontier
- monthly/yearly rebalancing
- CAGR / MDD / ex-post Sharpe / Sortino
- trailing returns
- active return / tracking error / information ratio
- rolling active-return annualization
- rolling tracking error
- Up/Down classification
- return/risk decomposition
- canonical result/run artifact boundary

Key Rolling Active convention:

```text
portfolio_total_W = product(1 + portfolio monthly returns) - 1
benchmark_total_W = product(1 + benchmark monthly returns) - 1
portfolio_ann_W = (1 + portfolio_total_W)^(12/W) - 1
benchmark_ann_W = (1 + benchmark_total_W)^(12/W) - 1
rolling_active_return = portfolio_ann_W - benchmark_ann_W
rolling_tracking_error = std(monthly active returns in W, sample) * sqrt(12)
```

Default W = 36 months.

## Report UI Baseline

New canonical document:

```text
docs/report-ui-specification.md
```

It defines report behavior independently from PV, including:

- identity and unit rules
- header/effective-period notes
- allocation sections
- Efficient Frontier Assets
- Efficient Frontier viewport/size/tooltip/outside-scale rules
- Frontier Transition
- Performance Summary
- trailing / annual / monthly returns
- drawdowns
- Portfolio Asset Performance
- correlations
- return/risk decomposition
- Annual Asset Returns
- Active Return Contribution
- Rolling Active Return and Risk dual-axis bar+line presentation
- Up vs. Down paired-bar view transform
- rolling 3Y/5Y returns
- responsive/readability rules
- P0/P1/P2 severity

Important rule:

```text
external service changes do not automatically change our UI
```

If an external service shows a better UX/convention, treat it as a product improvement proposal. Change the internal spec first, then implementation.

## External PV Reference

When the user asks for the useful current PV comparison URL, provide:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

Current comparison fixture:

```text
Period: 2016-08-01 ~ 2026-07-31
Assets: QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
Provided: QQQ 40 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15
Bounds: QQQ/SPMO max 50%; others max 30%; all min 0
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Frontier: 100 points
```

This URL is now **non-normative external evidence**, not the acceptance source.

The same-input numerical comparison previously established that the local 7-asset Efficient Frontier is very close to the external reference. Earlier large differences were caused by accidentally comparing universes containing PTF and/or QLD.

## v4 Implementation State

Implemented changes include:

- corrected annualized 36M Rolling Active Return
- Tracking Error remains annualized std of monthly active returns
- Rolling Active UI: bars on left Y-axis, Tracking Error line on right Y-axis, separate Provided/Optimized panels
- Efficient Frontier presentation enlarged and viewport logic improved
- normalized balance 1.0 renders as $10,000
- Benchmark Active Return / Tracking Error / Information Ratio render N/A
- Performance Summary required metrics restored
- Portfolio Asset Performance Annualized Return + trailing columns restored
- objective-aware optimized identity / human-readable benchmark identity improved
- prior v3 Annual Asset Returns and Up/Down paired-bar behavior retained

LLM-side targeted CI passed before main integration.

## Known Data-source Deviation

Up/Down classification uses canonical local benchmark returns.

Known prior difference:

```text
2026-07 SPY
local FDR monthly return ~ -0.68027%
external reference source ~ +0.03%
```

Therefore local 84 up / 36 down vs external 85 / 35 is not to be hard-coded away.

## Development Workflow Modes

Per-task modes remain:

```text
LLM sandbox development
LLM implementation
LLM design
```

Roles are not constitutionalized as one fixed split. Current `ai-share/llm-to-agent.md` defines Agent role for each task.

Testing is affected-scope-first. Expand to full regression only when impact/request justifies it.

## Agent Request Pending

Latest message:

```text
ai-share/llm-to-agent.md
id: 20260829T192500+0900-llm
```

This supersedes the older PV-centered validation wording.

Agent should validate v4 against internal specs:

```text
Calculation contract
Report semantic contract
Browser acceptance
P0/P1/P2
```

PV comparison is supplementary only.

## Open Issues

1. Await Agent independent v4 result.
2. LLM should inspect Agent evidence and generated report instead of accepting PASS blindly.
3. Static PV screenshots may still be retained as historical/external visual evidence, but they are no longer product completion gates.
4. Layered corrective renderers (`base -> ... -> v3 -> v4`) are a future consolidation candidate once UI stabilizes.

## Next

When Agent finishes:

1. read latest `ai-share/agent-to-llm.md`
2. inspect fresh run and report
3. judge against `specification.md` + `report-ui-specification.md`
4. classify P0/P1/P2
5. use external PV only to investigate unexplained differences or discover improvement ideas
6. after report stabilizes, consider consolidating layered renderer code without changing canonical behavior

Do not return to “PV looks different, therefore our implementation is wrong” as the default acceptance model.
