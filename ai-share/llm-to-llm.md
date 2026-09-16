# Session Handover

<!-- latest-loyo-readability:start -->
## Latest Update — 2026-09-16 LOYO readability refinement

- LOYO section placement: Portfolio Metrics → Leave-One-Year-Out Robustness → Monthly Returns.
- Asset-Year Influence uses four-row year-group zebra banding on Year/Metric columns only; numeric conditional backgrounds remain unchanged.
- Asset-Year Influence and Allocation Changes use two-line asset headers: Name with CSS ellipsis, then full Ticker. No new hover/tooltip interaction was added.
- LOYO Summary keeps compact ticker + signed delta shift cells and adds a static wrapping `Ticker · Name` legend below the table.
- This change is presentation-only. LOYO/annual-return/optimization calculations and persisted finance artifacts are unchanged.
<!-- latest-loyo-readability:end -->


<!-- latest-loyo-asset-year:start -->
## Latest Update — 2026-09-16 LOYO Asset-Year Influence

- LOYO user-facing report hierarchy is now Asset-Year Influence → LOYO Summary → Allocation Changes.
- New `asset_year_influence` is a projection only: existing annual asset returns + full-sample optimized weights + existing LOYO weights/deltas. It does not rerun annual-return calculations, baseline optimization, or LOYO optimization.
- Raw/review artifacts are persisted as `asset_year_influence.csv`; review units are `%/%p`.
- Asset-Year Influence matrix uses year groups with four metric rows: 구성자산 해당년도 수익률, 전체기간 최적비중, 해당년도 제외 최적비중, 비중 변화. Numeric cells retain values with metric-specific conditional backgrounds.
- LOYO Summary uses `Reallocation` and top 3 signed Allocation Shifts; Removed Start/End, observation counts, Solver are not primary user-facing columns; Status/Reason is conditional on abnormal scenarios.
- Allocation Changes shows full-sample baseline then excluded-year weights as `weight (delta)`.
- Run `20260914-0003` was backfilled from persisted artifacts without reoptimization and its report regenerated/deployed.
- Targeted LOYO regression passed in GitHub Actions run `35046139206`; backfill/source-equality/report/deploy validation passed in run `35046290432`.
- Implementation commits include `f1f479b2` projection, `e59948d6` review persistence, `4b50b3ae` UI matrix renderer, `595d31d3` viewer integration, and `aec22756` run-0003 regenerated artifacts.
<!-- latest-loyo-asset-year:end -->


created_at: 2026-09-16T06:18:00+09:00
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## Current State

The active research thread is portfolio optimization robustness plus evaluation of a new defense asset candidate.

The most important completed feature is **Leave-One-Year-Out Optimization Robustness (LOYO)**. LOYO is implemented, persisted, included in the current default Optimization report renderer, and as of this handover its calculation contract has been promoted from the completed change delta into the normative baseline:

```text
openspec/specs/portfolio-optimization/spec.md
```

The completed historical change remains useful as implementation/design history:

```text
openspec/changes/2026-09-14-loyo-robustness/
```

The report presentation contract is still in the report UI migration baseline:

```text
docs/report-ui-specification.md
```

which contains `## 24. Leave-One-Year-Out Robustness` and requires the Optimization report to show the LOYO section when canonical `optimization_robustness.loyo` / persisted `loyo_robustness.csv` exists.

The latest repository research-data addition is the Solactive Global Defense Index PR history for evaluating **496770 PLUS 글로벌방산**:

```text
data/market_data/solactive/
├─ DE000SL0JKC0.raw.csv
├─ DE000SL0JKC0.csv
└─ README.md
```

Latest data-import commit before the LOYO baseline-spec sync was:

```text
7787f298350e9ecbb48ffe1b454b6fc32efa53aa
```

LOYO baseline-spec promotion commit:

```text
fb70dbd1a60e4f971435aa91e907e5acb13bbaa4
```

---

## User Research Philosophy / Working Style

The user does not want optimizer decimals treated as truth. The goal is to identify independent economic return engines and robust allocation structure, then use optimizers as evidence rather than as an oracle.

Important interpretation preferences:

- challenge corner solutions and sample dependence rather than celebrating the mathematically best point;
- distinguish a robust asset-role signal from an exact optimizer weight;
- avoid extra knobs, composite scores, or automatic labels before the underlying evidence is inspected;
- do not introduce broad experimental matrices unless they answer a concrete question;
- for ordinary research/optimization execution with no feature change, skip broad regression/Playwright overhead and run the normal GitHub Actions research flow;
- for actual finance/report behavior changes, follow AGENTS/OpenSpec affected-scope validation.

---

# LOYO — Leave-One-Year-Out Optimization Robustness

## Why LOYO exists

The user wanted a practical way to ask:

> Is an optimized allocation genuinely persistent, or is one unusually favorable calendar year making an asset look dominant?

LOYO is a **year influence diagnostic for the optimization solution**. It is not a new optimization objective and not a generic performance attribution tool.

Conceptually:

```text
Full monthly sample
  -> baseline optimization

Remove 2019
  -> recompute moments
  -> same optimization objective/constraints
  -> compare with baseline

Remove 2020
  -> recompute moments
  -> same optimization objective/constraints
  -> compare with baseline

...
```

The key output is how much the optimized allocation and ex-ante objective statistics move when one calendar year is removed.

## Exact LOYO semantics

For each calendar year present in the canonical monthly-return sample:

1. Remove all monthly observations belonging to that calendar year.
2. Recompute annualized expected returns/covariance from the remaining canonical monthly returns.
3. Re-run the **same canonical optimization objective** through the shared optimization core.
4. Keep the same:
   - asset universe
   - min/max bounds
   - objective
   - target annual volatility when applicable
   - effective annual risk-free rate
5. Compare that year-excluded optimized result with the already-existing full-sample baseline.

Important isolation rule:

```text
Baseline effective RF is held fixed across LOYO scenarios.
```

The risk-free rate is not re-estimated after removing each year. This intentionally isolates the influence of the asset-return sample rather than mixing in a second moving input.

## Baseline is NOT re-solved

Normal Optimization already produced the full-sample baseline result. LOYO reuses that result.

```text
baseline solve count added by LOYO = 0
```

Do not add another baseline call merely to make LOYO self-contained.

## Partial years

The first or last analysis year may contain fewer than 12 observations. It is still a valid LOYO scenario.

Example from the main research run:

```text
2015 -> only Nov-Dec, 2 observations removed
2026 -> Jan-Aug, 8 observations removed
```

The actual removed count must be recorded so partial-year influence is not mistaken for a full-year omission.

## Supported optimization objectives

LOYO follows the original objective exactly.

```text
Maximum Sharpe
-> omit year
-> Maximum Sharpe again

Maximum Return @ Target Volatility
-> omit year
-> Maximum Return subject to the SAME target volatility
```

Thus LOYO applies to both supported v1 objectives.

## Allocation sensitivity

For every feasible year-excluded solution, preserve per-asset weight changes and calculate:

```text
allocation_turnover
  = 0.5 * sum(abs(loyo_weight_i - baseline_weight_i))
```

Interpretation:

- `0` means identical allocation.
- `0.10` means 10% of portfolio capital would have to be reallocated to move from baseline weights to the LOYO weights.
- Larger does not automatically mean overfit. It is evidence to inspect.

Also record:

```text
max absolute asset weight change
most changed asset
per-asset LOYO weight
per-asset delta vs baseline
```

LOYO MUST NOT automatically turn this into:

```text
overfit=true
corner_solution=true
robust=false
```

The user wants evidence, not a black-box verdict.

## Objective sensitivity

For each feasible LOYO scenario preserve:

```text
optimized expected annual return
annualized volatility
ex-ante Sharpe
baseline delta for each metric
```

A particularly important interpretation pattern is:

```text
large allocation turnover
+ tiny objective-value change
```

This often means the exact optimizer weights are unstable because several allocations are nearly equivalent, not necessarily that the underlying asset-role thesis is bad.

## Infeasible / insufficient-data scenario handling

A year-excluded scenario can become infeasible, especially for target-volatility optimization if the new constrained GMV volatility exceeds the fixed target.

In that case:

```text
scenario -> feasible=false / infeasible
baseline run -> remains valid
other LOYO years -> continue
```

The whole run must not fail merely because one LOYO scenario is infeasible.

If the remaining observations are insufficient for canonical moment calculation, record an insufficient-data scenario rather than inventing a solution.

Unexpected programming/runtime exceptions still follow normal run-failure semantics and must not be silently converted to diagnostic rows.

## Performance architecture

LOYO is deliberately **not** implemented as `calendar years × full pipeline`.

Do NOT repeat per omitted year:

```text
market-data fetch
FX normalization
canonical return preparation
Efficient Frontier generation
portfolio path simulation
historical analytics
benchmark analytics
HTML report rendering
```

Instead:

```text
PreparedOptimizationData.monthly_returns
        + existing baseline optimization_result
        + objective / bounds / target vol
        + fixed effective RF
                       |
                       v
                 LOYO loop
                       |
               exclude year
                       |
             annualized moments
                       |
             solve_optimization()
                       |
              compare baseline
```

This design depends on the earlier Shared Optimization Core refactor. Normal Optimization and LOYO call the same optimization engine rather than maintaining parallel solver semantics.

Current solver architecture:

```text
OSQP
- minimum variance
- Maximum Sharpe path / parameterized frontier QP

CLARABEL
- Maximum Return @ Target Volatility SOCP
```

`MinimumVarianceForReturnSolver` uses a CVXPY `Parameter` and `warm_start=True` for repeated frontier-related QP work.

## Persistence contract

Canonical result:

```text
result.json
└─ optimization_robustness
   └─ loyo
```

Persisted tables:

```text
loyo_robustness.csv
raw/loyo_robustness.csv
review/loyo_robustness.csv
```

Each scenario includes at least:

```text
excluded_year
removed_observations
remaining_observations
removed_start
removed_end
feasible
status
solver
expected_return
volatility
sharpe
metric deltas
allocation_turnover
most_changed_asset
max_abs_weight_change
asset weights
asset weight deltas
```

## Product scope

LOYO is **Optimization-only**.

```text
Default Optimization -> LOYO yes
Backtest             -> LOYO no
Custom analyzer      -> do not silently add LOYO
```

The user asked whether Provided Portfolio also receives LOYO. Answer: **no** under the current definition.

Reason:

Provided weights are fixed by the user. Removing a year would not change its target allocation, so allocation turnover would always be zero. A separate analysis could ask how a fixed Provided portfolio's CAGR/Sharpe/volatility changes when years are removed, but that would be a **performance year influence analysis**, not this optimization-robustness LOYO.

## LOYO report behavior

Current default Optimization renderer includes a **Leave-One-Year-Out Robustness** section when the persisted LOYO artifact exists.

The report consumes existing persisted LOYO values. It must not recompute LOYO in the browser/report layer.

Historical run caveat:

```text
runs/20260914-0003
```

contains valid LOYO results in result.json/CSV, but its existing `report.html` was generated **before** the LOYO HTML panel was added. Therefore that old HTML does not show LOYO.

It could be re-rendered later from existing artifacts with the latest renderer without re-running optimization, but the user explicitly said to HOLD that action. Do not regenerate it unless asked.

## LOYO verification status

The completed LOYO change has affected-scope regression evidence:

```text
25 passed
GitHub Actions run: 34805351848
```

Coverage included:

- Maximum Sharpe LOYO
- Target-volatility LOYO
- target-volatility infeasible scenario handling
- partial-year removal
- baseline immutability / no duplicate baseline solve
- artifact persistence
- Backtest not invoking LOYO

---

# Main LOYO Research Example — run 20260914-0003

## Experiment

```text
studies/provided-portfolio-v1-optimization/experiments/
008-aia-schd-soybean-max-return-vol11_5-2015_11.yaml
```

Conditions:

```text
Objective: Maximum Return
Target annual volatility: 11.5%
Period: 2015-11-01 to 2026-08-31
Frequency: monthly
Rebalancing: monthly
Annual RF: 3.78%
Benchmark: SPY
Fees/slippage: 0
```

Provided portfolio:

```text
QQQ      20%
SPMO     20%
AIA      15%   # proxy for ACE 아시아TOP50 277540
GLD      15%
XLE      15%
SCHD      5%
144600    5%   # KODEX 은선물(H)
138920    5%   # KODEX 콩선물(H)
```

## Baseline optimized allocation

```text
QQQ       31.0628%
SPMO      19.8172%
AIA        4.5084%
GLD       39.4845%
XLE        2.7333%
144600     0.0000%
SCHD       2.3938%
138920     0.0000%
```

Baseline optimized ex-ante / realized summary used in discussion:

```text
Expected/annualized return  ~18.1864%
Volatility                  ~11.5000%
Ex-ante Sharpe              ~1.24756
Realized CAGR               ~19.0127%
Realized MDD                ~-11.6351%
```

Provided portfolio comparison:

```text
CAGR          17.6523%
Ann return    17.0776%
Volatility    11.9837%
MDD          -14.8614%
Sharpe         1.10467
```

SPY comparison:

```text
CAGR          16.7371%
Ann return    16.5778%
Volatility    14.2014%
MDD          -17.4099%
Sharpe         0.89697
```

## LOYO results by excluded year

All target-volatility LOYO solves were feasible, status optimal, solver CLARABEL.

### 2015, partial year, 2 months removed

```text
Allocation turnover: 3.69%
Most changed: SCHD
Expected return: 18.5346%
Sharpe: 1.27784

QQQ    29.7637
SPMO   20.0001
AIA     4.8821
GLD    40.8542
XLE     4.5000
SCHD    0
Soy     0
```

### 2016

```text
Turnover: 8.22%
Most changed: GLD
Expected return: 18.6056%
Sharpe: 1.28401

QQQ    27.9649
SPMO   21.8970
AIA     2.1153
GLD    43.3511
XLE     0
SCHD    4.6716
Soy     0
```

### 2017

```text
Turnover: 10.86%
Most changed: AIA
Expected return: 18.8921%
Sharpe: 1.30893

QQQ    27.1053
SPMO   20.2097
AIA     0
GLD    43.8403
XLE     6.3500
SCHD    0
Soy     2.4946
```

### 2018

```text
Turnover: 8.48%
Most changed: AIA
Expected return: 19.7773%
Sharpe: 1.38590

QQQ    29.3807
SPMO   18.5328
AIA    10.3041
GLD    34.2625
XLE     5.4194
SCHD    2.1006
Soy     0
```

### 2019

```text
Turnover: 12.38%
Most changed: QQQ
Expected return: 16.9691%
Sharpe: 1.14171

QQQ    21.0720
SPMO   25.9978
AIA     6.8101
GLD    40.6049
XLE     4.7210
SCHD    0
Soy     0.7942
```

### 2020

```text
Turnover: 32.92%
Most changed: XLE
Expected return: 18.9874%
Sharpe: 1.31721

QQQ    22.8490
SPMO   34.0601
AIA     0
GLD    21.6778
XLE    21.4131
SCHD    0
Soy     0
```

### 2021

```text
Turnover: 19.08%
Most changed: QQQ
Expected return: 17.8446%
Sharpe: 1.21784

QQQ    17.1133
SPMO   23.3113
AIA    15.4050
GLD    43.7047
XLE     0
SCHD    0
Soy     0.4657
```

### 2022

```text
Turnover: 30.34%
Most changed: QQQ
Expected return: 21.7952%
Sharpe: 1.56137

QQQ    56.9341
SPMO    0
AIA     1.2911
GLD    34.9091
XLE     0
SCHD    5.6281
Soy     1.2377
```

### 2023

```text
Turnover: 39.36%   # largest
Most changed: QQQ
Expected return: 17.8520%
Sharpe: 1.21848

QQQ     0
SPMO   42.9218
AIA    11.2877
GLD    33.5341
XLE     0.3830
SCHD   11.8734
Soy     0
```

### 2024

```text
Turnover: 27.30%
Most changed: SPMO
Expected return: 16.1219%
Sharpe: 1.06803

QQQ    49.3700
SPMO    0
AIA     1.0458
GLD    35.4665
XLE     4.6229
SCHD    4.3324
Soy     5.1624   # largest soybean LOYO weight
```

### 2025

```text
Turnover: 30.65%
Most changed: SCHD
Expected return: 17.0262%
Sharpe: 1.14667

QQQ    35.2176
SPMO    6.5850
AIA     0.4144
GLD    28.8969
XLE     0
SCHD   28.1474
Soy     0.7387
```

### 2026, partial year, 8 months removed

```text
Turnover: 13.42%
Most changed: QQQ
Expected return: 19.1182%
Sharpe: 1.32858

QQQ    44.4808
SPMO   18.6167
AIA     0
GLD    36.9025
XLE     0
SCHD    0
Soy     0
```

## Main interpretation of run 0003 LOYO

### 1. GLD signal is comparatively persistent

Baseline GLD is about 39.48%.

Across all one-year omissions GLD remains approximately:

```text
21.68% to 43.84%
```

and never disappears.

Therefore the useful conclusion is NOT:

```text
"39.4845% gold is the true optimal weight"
```

but rather:

```text
"A substantial gold allocation remains a persistent optimizer signal across single-year omissions."
```

2020 omission has the largest downward effect on GLD, taking it to about 21.68%.

### 2. QQQ and SPMO are much more sample-sensitive

Examples:

```text
Exclude 2023:
QQQ   31.06% -> 0%
SPMO  19.82% -> 42.92%

Exclude 2022:
QQQ   31.06% -> 56.93%
SPMO  19.82% -> 0%
```

This suggests the exact split between these equity engines is much less robust than the presence of the growth/momentum sleeve itself.

### 3. 2023 is a particularly useful diagnostic case

Excluding 2023 causes the largest allocation turnover:

```text
39.36%
```

but the objective statistics barely deteriorate:

```text
Expected return delta ~ -0.334%p
Sharpe delta          ~ -0.029
```

This is an important pattern for future interpretation:

> The optimizer's exact weights can be very unstable while several alternative allocations have nearly the same objective value.

So the user should read **asset roles / plausible ranges**, not decimal optimizer weights.

### 4. 2022 is not a favorable year artificially inflating the optimizer

Removing 2022 improves the optimized result substantially:

```text
Expected return +3.61%p
Sharpe          +0.314
```

Thus 2022 behaves more like a stress year that suppresses apparent portfolio efficiency.

### 5. 2024 is relatively supportive of the current optimized sample

Removing 2024 reduces:

```text
Expected return ~ -2.06%p
Sharpe          ~ -0.180
```

So 2024 contributes meaningfully to the current sample's attractive frontier.

### 6. Soybean has occasional diversification value, not a persistent optimal allocation

Baseline optimized soybean weight is 0%.

It enters only in some omitted-year scenarios:

```text
exclude 2017 -> 2.49%
exclude 2019 -> 0.79%
exclude 2021 -> 0.47%
exclude 2022 -> 1.24%
exclude 2024 -> 5.16%
exclude 2025 -> 0.74%
otherwise    -> 0%
```

Interpretation:

```text
occasional marginal diversification value
!= robust always-optimal soybean allocation
```

### 7. Overall LOYO conclusion so far

There is no obvious evidence that the whole solution is being carried by one single calendar year.

However, exact weights, especially QQQ/SPMO/SCHD, are materially sample-sensitive.

The strongest practical message from LOYO is:

```text
trust persistent asset-role signals more than exact optimizer percentages
```

---

## LOYO Runtime / Performance

Measured on run 20260914-0003:

```text
uv sync --frozen package prepare+install, cold cache: ~0.87 sec
whole portfolio-optimizer execute:                   14.206 sec
Action start -> artifact commit/report dispatch:     ~33 sec
Action start -> public Pages deployment complete:    ~56 sec
```

The `portfolio-optimizer execute` interval includes:

```text
data loading
baseline optimization
LOYO omitted-year solves
analytics
artifact generation
HTML report generation
```

This validates the lightweight architecture: twelve year-omission solves fit inside a ~14 second full execution rather than multiplying the whole pipeline by twelve.

A previous discussion estimated that a naive full-pipeline-per-year LOYO design might have taken roughly 130-170 seconds for this case, implying approximately 9-12x better repeated-analysis efficiency. That figure is an architectural estimate, not a direct benchmark of an old LOYO implementation, so do not present it as a measured before/after benchmark.

---

# Recent Report Contract Corrections

## Remove `Portfolio / Asset Correlations`

The user clarified that the old `Portfolio / Asset Correlations` requirement was itself erroneous.

Correct contract:

```text
Asset Correlations -> keep
Name + Ticker      -> keep
Portfolio / Asset Correlations -> remove
```

Do not reintroduce it.

Important implementation point: there must be no duplicate asset-only correlation calculation.

Existing canonical source is already:

```text
asset_statistics.correlation
```

from shared annualized statistics.

The old synthetic path that separately built correlations including Provided / Optimized / Benchmark was removed. `correlations.csv` for Optimization should be only a presentation view of the existing asset-only matrix.

## LOYO default HTML section

LOYO is now part of the default Optimization report whenever persisted LOYO artifacts exist. The renderer consumes persisted data rather than recalculating finance semantics.

## Cumulative Active Return legend

The chart is a stacked active-contribution visualization. Legend order was changed to follow the visual stack order at the latest point so the user can map colors/series more reliably.

## Cumulative Active Return benchmark semantics

A Portfolio Visualizer reference check confirmed that PV's `Cumulative Active Return` / `Active Return Contribution` presentation is benchmark-relative.

Current implementation concept is monthly asset active contribution:

```text
weight * (asset return - benchmark return)
```

then cumulative contribution through time.

Important interpretation discovered:

A cumulative series staying below zero does NOT mean that asset hurt active return in every year. It only means the running contribution from the analysis start remains below zero.

Examples discussed:

- AIA remained cumulatively negative through the inspected 2022-2025 period.
- GLD stayed below zero cumulatively but improved strongly in 2022 and 2025, so those years had positive active contribution.
- XLE actually crossed above zero during 2022 and had positive intervals in 2023.

### Naming cleanup is intentionally HOLD

The user decided not to change the title immediately. Later report cleanup should make benchmark-relative meaning explicit, likely one of:

```text
Cumulative Active Return vs Benchmark
Cumulative Active Contribution vs Benchmark
```

Do not change this now unless the user resumes that report-cleanup task.

---

# Known Unresolved Workflow Issue

Permanent workflow:

```text
.github/workflows/run-optimization.yml
```

still has the post-core step:

```text
Analyze frontier risk trade-off
python scripts/analyze_frontier_risk_tradeoff.py "$RUN_PATH"
```

For the first standard attempt at run 0003, the core Optimization/report generation succeeded but this later postprocessing step failed with:

```text
ValueError: target weights must be long-only and sum to one
```

Trace path:

```text
scripts/analyze_frontier_risk_tradeoff.py
-> frontier_risk_dataset
-> build_portfolio_path
-> _target_vector
```

Likely cause is a tiny numerical solver weight/sum tolerance crossing a stricter portfolio-target validation boundary, but this is only a hypothesis.

**This permanent workflow bug is NOT fixed.**

Do not claim otherwise.

If the user asks to fix it, inspect at least:

```text
scripts/analyze_frontier_risk_tradeoff.py
src/portfolio_optimizer_kr/analytics/frontier_risk.py
src/portfolio_optimizer_kr/portfolio/returns.py::_target_vector
```

A likely correct direction is an explicit numerical-tolerance normalization/clip at the correct finance-semantic boundary, not simply making the workflow step nonblocking. Because that can change calculation/postprocessing behavior, follow OpenSpec and add targeted tests.

---

# New Asset Research: 496770 PLUS 글로벌방산

The user wants to evaluate:

```text
496770 PLUS 글로벌방산
Underlying index: Solactive Global Defense Index PR
ISIN: DE000SL0JKC0
```

The ETF's live history is too short for the user's preferred portfolio research horizon, so the user extracted Solactive index history directly.

## User's extraction method

Solactive endpoint:

```text
https://www.solactive.com/_actions/getDayHistoryChartData/
```

Payload included:

```text
isin: DE000SL0JKC0
indexCreatingTimeStamp: 0
dayDate: Date.now()
```

The response uses Solactive/devalue-style references, which the user's Node script decoded into:

```text
isin
date
level
```

## Repository storage

Use repo-held market data rather than `indices/` because the user wanted to avoid ambiguity between financial index / pandas index / indicator terminology.

Chosen location:

```text
data/market_data/solactive/
```

Files:

```text
DE000SL0JKC0.raw.csv
DE000SL0JKC0.csv
README.md
```

### Raw file

```text
Exact uploaded extraction
Rows: 1,920
Date range: 2019-05-06 to 2026-09-13
Columns: date,level,isin
```

### Canonical file

```text
Rows: 1,920
Date range: 2019-05-07 to 2026-09-14
Columns: date,level,isin
```

The canonical dates are raw dates + 1 calendar day.

Reason:

- raw extraction produced a repeating Mon/Tue/Wed/Thu/Sun pattern;
- official Solactive guideline defines start date 2019-05-07 with initial level 1000;
- raw first row was 2019-05-06 with level 1000;
- shifting +1 day restores normal Monday-Friday observation dates.

No index level was modified.

Canonical checks:

```text
first: 2019-05-07, 1000.00
last:  2026-09-14, 3679.87
ISIN:  DE000SL0JKC0 for all rows
```

README records provenance and also notes:

```text
Official live date: 2024-09-06
Pre-live index history is Solactive back-tested history.
```

This caveat matters when using the index as a long-history proxy.

## Intended use

Treat the Solactive series as:

```text
long-history proxy for the underlying index
```

Do NOT treat it as realized ETF trading history.

The preferred research separation is:

```text
Solactive index history
-> long-period asset behavior / optimization proxy

496770 post-listing ETF history
-> live tracking behavior / implementation validation
```

Do not silently stitch index history and ETF history into one identity unless that methodology is explicitly designed and documented.

## Likely next implementation

The optimizer currently assumes the v1 market-data source is FinanceDataReader.

To consume `data/market_data/solactive/DE000SL0JKC0.csv` as a normal research asset, the likely next feature is a repository-held market-data provider / source option that can coexist with FDR assets in one canonical universe.

This is a **shared `market-data` capability behavior change**, not just an experiment YAML tweak. Before implementation:

1. inspect `openspec/specs/market-data/spec.md`;
2. create an OpenSpec delta for repository-held market data;
3. define identity/source/path semantics without contaminating downstream stats/optimizer with provider-specific logic;
4. ensure the same canonical monthly-return preparation path is used after loading.

Do not build a Solactive-specific optimizer path if a small general repository-market-data source can solve the actual repeated need.

---

## Important Constraints / Do Not Regress

- LOYO is an Optimization robustness diagnostic, not a new optimization objective.
- LOYO must reuse the shared optimization core.
- Baseline optimization must not be solved again just for LOYO.
- Keep the baseline effective RF fixed across omitted years.
- Partial first/last years are valid LOYO scenarios and must record removed observation count.
- Infeasible LOYO rows are evidence, not whole-run failures.
- Do not automatically label LOYO results as overfit/robust/corner-solution.
- Do not add LOYO to Backtest.
- Do not add LOYO allocation analysis to Provided Portfolio; a fixed-portfolio year-influence study would be a distinct analysis.
- Do not reintroduce `Portfolio / Asset Correlations`.
- Asset Correlations must use the existing canonical asset correlation matrix, not a duplicate calculation.
- Do not rename Cumulative Active Return yet; naming cleanup is on hold.
- Do not claim the permanent frontier-risk workflow post-step bug is fixed.
- Do not regenerate historical run 0003's HTML merely to show LOYO unless the user asks.
- Solactive index data is a proxy index series, not 496770 realized ETF history.

---

## Open Issues / Next

Most likely next user direction is one of these:

1. **496770 / Solactive research continuation**
   - add repository-held market-data provider support;
   - use `DE000SL0JKC0.csv` in a portfolio experiment;
   - compare marginal utility/correlation/frontier effect against the current portfolio;
   - separately compare live 496770 tracking after listing.

2. **LOYO report review**
   - latest renderer already supports LOYO;
   - historical run 0003 HTML does not because it predates the panel;
   - if asked, re-render from persisted artifacts rather than recomputing optimization.

3. **Workflow repair**
   - fix the frontier-risk postprocessing numerical-weight validation issue using a proper tolerance contract.

4. **Report naming cleanup**
   - later make Cumulative Active Return explicitly benchmark-relative in its title/label.

When a new ChatGPT session begins, read this handover plus the current OpenSpec baseline before asking the user to repeat any of the above context.
