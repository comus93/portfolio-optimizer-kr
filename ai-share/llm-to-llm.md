# Session Handover

created_at: 2026-08-29T18:55:00+09:00
project: `comus93/portfolio-optimizer-kr`

## Current State

Report review v4 implementation is complete on the LLM side and has passed targeted GitHub-side CI. Codex Agent independent real-run/browser validation has been requested through `ai-share/llm-to-agent.md` and is pending.

Implemented v4 changes:

```text
src/portfolio_optimizer_kr/analytics/metrics.py
src/portfolio_optimizer_kr/viewer/feedback_v4.py
src/portfolio_optimizer_kr/viewer/final_renderer.py
tests/test_report_user_feedback_v4.py
```

LLM-side targeted CI:

```text
GitHub Actions run: 33245129883
Result: success
Later branch validation runs after docs also passed, including 33245300194.
```

The temporary LLM validation workflow was removed after validation and must not remain in main.

Project docs were refreshed to current behavior:

```text
AGENTS.md
docs/specification.md
docs/architecture.md
docs/visual-acceptance-contract.md
docs/report-visual-overrides-20260829.md
```

## Decisions

### Current PV behavioral golden

When the user asks for the PV URL, use:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

This URL must also be preserved in future handovers unless explicitly replaced by the user.

Current same-input universe:

```text
Period: 2016-08-01 ~ 2026-07-31
Assets: QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
Provided: QQQ 40 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15
Bounds: QQQ/SPMO max 50%; others max 30%; all min 0
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Frontier: 100 points
```

### Efficient Frontier numerical status

The local optimizer itself is no longer considered suspicious. With the same 7-asset universe, PV and local frontier values are very close across the curve. Previous large mismatch was caused by comparing different PV universes that included PTF and/or QLD.

Representative parity:

```text
PV point 1  ~ ER 16.23 / SD 12.74 / Sharpe 1.089
local       ~ ER 16.22 / SD 12.75 / Sharpe 1.088

PV max-sharpe ~ ER 17.19 / SD 13.08 / Sharpe 1.134
local         ~ ER 17.16~17.21 / SD 13.07~13.10 / Sharpe ~1.133

Both high-return ends converge to ~ QQQ 50% + SPMO 50%.
```

Current Frontier remaining concern is presentation, not core optimization calculation.

v4 presentation principle:

- curve-centered viewport with nearby asset/landmark context
- do not let extreme GDX/SLV/XLE values flatten the curve
- final display-domain decides visible/outside
- current PV meaning is approximately X 12%~22.5%, Y 11%~22%
- visible expected: QQQ/SPMO/GLD/AIA
- outside expected: GDX/SLV/XLE
- chart physical height enlarged to near-PV readability

### Rolling Active Return correction

Previous implementation was semantically wrong because it used raw 36M total-return difference and produced 40~60% values.

New canonical convention:

```text
portfolio_total_36m = product(1+r_p) - 1
benchmark_total_36m = product(1+r_b) - 1
portfolio_ann = (1+portfolio_total_36m)^(12/36)-1
benchmark_ann = (1+benchmark_total_36m)^(12/36)-1
rolling_active_return = portfolio_ann - benchmark_ann
rolling_tracking_error = std(monthly active return over 36m, sample) * sqrt(12)
```

UI:

```text
Active Return = blue bars, LEFT Y-axis
Tracking Error = mint line, RIGHT Y-axis
Provided / Maximum Sharpe separate panels
Title = Rolling Active Return and Risk (36 months)
```

Tracking-error calculation itself was already likely correct. Local recent values were roughly Provided 8.2%, Max Sharpe ~6.0%, similar to PV screenshots.

### Metrics / tables fixes

v4 fixes:

- normalized Start Balance 1.0 displays as `$10,000`, not `$1`
- End Balance also uses normalized wealth x $10,000
- Benchmark Active Return / Tracking Error / Information Ratio display `N/A`, not zero
- Performance Summary restores required metrics including ex-ante Sharpe and active metrics
- Portfolio Asset Performance restores Annualized Return and 3M/YTD/1Y/3Y/5Y/10Y trailing returns
- generic `Optimized` / `Benchmark` identity is replaced where possible by objective-aware and benchmark names

### Up/Down known deviation

Local 84 up / 36 down vs PV 85 / 35 remains an intentional market-data-source deviation.

Known divergent month:

```text
2026-07 SPY
local FDR monthly return ~ -0.68027%
PV source ~ +0.03%
```

Do not hard-code counts to PV.

### Static Golden

The old static golden URL was broken and earlier screenshots also had asset-universe drift.

Current status:

```text
Static golden: PENDING USER REFRESH
```

The user explicitly said a fresh static PV screenshot can be supplied after implementation during final validation. Do not block implementation on it now. Once supplied, update the visual acceptance reference.

## Development Workflow Decision

The project no longer hard-codes LLM vs Codex roles in `AGENTS.md`.

Supported per-task modes:

```text
LLM sandbox development
  LLM = design + sandbox implementation + targeted test/CLI
  Agent = independent real-environment/E2E/browser verification

LLM implementation
  LLM = design + GitHub implementation
  Agent = execution verification

LLM design
  LLM = requirements/calculation/test/acceptance design
  Agent = implementation + execution verification
```

The current `ai-share/llm-to-agent.md` defines the Agent role for each task.

Testing is affected-scope-first. Full regression is not a universal completion ritual; expand only when requested or when common/core impact makes it appropriate.

Note: In this ChatGPT session, sandbox `git clone` failed because container DNS could not resolve github.com. The LLM therefore used a temporary GitHub branch plus targeted GitHub Actions as its first execution validation, then removed the temporary workflow.

## Important Constraints

- FDR is v1 market-data source.
- Browser viewer must not redefine finance calculations. Python analytics/canonical result remains source of truth.
- `missing != zero`.
- Same-input PV validation must first confirm identical asset universe and constraints.
- Use current 7-asset PV URL, not older `2Fh...` link.
- Do not use PTF/QLD screenshots/tables as same-input numerical evidence for the 7-asset fixture.
- Static golden is pending refresh, not a current PASS/FAIL gate.
- Do not run full pytest for small report iterations unless impact/request justifies it.

## Agent Request Pending

Latest request is in:

```text
ai-share/llm-to-agent.md
id: 20260829T183500+0900-llm
```

Agent must fresh-run the same 7-asset input and independently validate:

- Efficient Frontier size/domain/visible-outside/hover
- Rolling Active annualized convention + dual-axis bar/line UI
- `$10,000` balance semantics
- Benchmark active metrics = N/A
- complete Performance Summary
- restored Portfolio Asset Performance fields
- objective/benchmark identity consistency
- v3 regression sanity

Expected fresh run id:

```text
20260829-report-review-v4-validation
```

## Open Issues

1. Await Agent independent result in `ai-share/agent-to-llm.md`.
2. After Agent completion, LLM must independently review its evidence and preferably inspect the generated Pages report instead of accepting Agent PASS blindly.
3. User will provide a fresh same-input PV static screenshot after implementation/final validation. Then promote it to the static golden reference.
4. Renderer currently uses layered corrective renderers (`base -> ... -> v3 -> v4`). This is acceptable for current regression control but is a future consolidation candidate after UI stabilizes.

## Next

When the user says Agent finished:

1. read latest `ai-share/agent-to-llm.md` from GitHub remote
2. inspect fresh run artifacts and validation report
3. compare representative Rolling Active values and Frontier domain against current PV
4. classify any remaining P0/P1/deviation
5. fix directly if necessary, then ask Agent only for affected re-validation
6. once report is accepted, obtain the user's refreshed PV static screenshot and update the static-golden reference

Do not restart optimizer design or re-investigate the already-resolved PTF/QLD universe mismatch unless new evidence appears.
