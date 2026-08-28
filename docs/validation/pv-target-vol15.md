# PV Golden Validation — Maximum Return at 15% Volatility

## Purpose

`tests/golden/pv/260828_PTF_maxRetVol15.md` is the primary Portfolio Visualizer golden reference for the v1 `target_volatility` objective.

The objective is:

```text
maximize expected annual return
subject to annual portfolio volatility <= target_volatility
```

The target is a volatility **cap**, not an equality requirement. When the cap is above the volatility of the unconstrained maximum-return portfolio, the maximum-return portfolio itself is valid. For an interior efficient-frontier target the cap will normally bind within solver tolerance.

## Golden configuration

Reference period: Aug 2016 - Jul 2026

Benchmark: SPY

Assets and upper bounds:

| Ticker | Max weight |
| --- | ---: |
| QQQ | 50% |
| SPMO | 50% |
| GDX | 30% |
| GLD | 30% |
| SLV | 30% |
| AIA | 30% |
| XLE | 30% |
| PTF | 30% |
| QLD | 30% |

All minimum weights are 0% and the portfolio is long-only with weights summing to 100%.

Provided portfolio weights:

```text
QQQ 20%
SPMO 10%
GDX 10%
GLD 0%
SLV 10%
AIA 15%
XLE 15%
PTF 10%
QLD 10%
```

Target annual volatility: 15.00%

Risk-free reference: PV U.S. 3-Month Treasury Bill convention. The optimization weights for this objective do not depend on the risk-free rate; RF affects reported Sharpe only.

Important: this golden does **not** use the same upper bounds as `260828_PTF_maxsharpe.md`. In particular PTF and QLD are capped at 30% here. Do not reuse the Max-Sharpe bounds blindly.

## Published PV reference

Maximum Return at 15.00% Volatility:

```text
QQQ   14.19%
SPMO  44.30%
GDX    0.00%
GLD   30.00%
SLV    0.00%
AIA    0.00%
XLE    2.20%
PTF    0.00%
QLD    9.31%
```

Published summary:

```text
Expected Return      18.76%
Standard Deviation   14.89%
Sharpe Ratio          1.10
CAGR                  19.17%
Maximum Drawdown     -22.44%
Feasible ER range     16.23% - 26.24%
```

## Why PV shows 14.89% for a 15.00% target

PV optimizes using internal full-precision moments. The golden page exposes rounded expected returns, standard deviations, correlations, and weights.

Using the displayed rounded PV moments with the displayed PV weights gives approximately:

```text
Expected Return  18.755%
Volatility       14.899%
```

Solving the 15% cap again from the displayed rounded moments gives a nearby solution around:

```text
QQQ   ~13.99%
SPMO  ~44.27%
GLD    30.00%
XLE    ~1.97%
QLD    ~9.77%
ER     ~18.84%
Vol    ~15.00%
```

Therefore the validation must not force the **published rounded PV weights** to evaluate to exactly 15.00% under the **published rounded PV moments**. That would be a false requirement.

## Validation layers

### A. Synthetic solver contract — pytest

Network-free tests must verify:

1. `target < GMV volatility` -> explicit infeasible error.
2. `target == GMV volatility` -> solution is near the GMV portfolio.
3. Interior target -> volatility respects the cap and the portfolio maximizes expected return under that cap.
4. Interior target normally binds within numerical tolerance for a simple known fixture.
5. `target >= maximum-return portfolio volatility` -> maximum-return portfolio is returned/approached.
6. Weight min/max constraints and sum-to-one are respected.
7. Deterministic repeated solve for the same inputs.

The important contract is not merely `vol <= target`; the result must also be the maximum-return feasible portfolio.

### B. PV rounded-moment solver-only parity — pytest/offline

Parse from `260828_PTF_maxRetVol15.md`:

- 9 asset expected returns
- 9 asset volatilities
- 9x9 correlation matrix
- min/max bounds
- published optimized allocation

Reconstruct:

```text
covariance = diag(volatility) @ correlation @ diag(volatility)
```

Run `target_volatility(..., target_vol=0.15)` without FDR/network.

Because PV public moments are rounded and the rounded correlation matrix can be slightly non-PSD, exact equality is not expected. The test should use a diagnostic tolerance appropriate to published rounding, not silently alter the financial objective.

Initial expected neighborhood from the displayed moments:

```text
QQQ   ~14.0%
SPMO  ~44.3%
GLD    30.0%
XLE    ~2.0%
QLD    ~9.8%
others ~0%
ER     ~18.84%
Vol    ~15.00%
```

The published PV allocation itself is:

```text
QQQ 14.19 / SPMO 44.30 / GLD 30.00 / XLE 2.20 / QLD 9.31
```

### C. Live FDR parity — diagnostic run, not hard pytest

Use the same universe, bounds, provided weights, period, benchmark and target-volatility objective.

Canonical run directory:

```text
runs/20260828-pv-maxretvol15/
```

The live run should produce the normal generic artifacts:

```text
input.yaml
result.json
README.md
review/
raw/
```

and target-volatility parity diagnostics, preferably:

```text
parity.json
moment_parity.csv
solver_parity.csv
```

Compare at minimum:

- optimized weights vs PV published weights
- expected return
- ex-ante volatility
- Sharpe
- feasible frontier return range
- data coverage
- performance CAGR / MDD
- asset moments/correlation deltas

FDR-vs-PV data-source differences are diagnostic, not an exact-equality test.

### D. Cross-objective consistency

After both goldens are available, validate that:

- Max Sharpe and Target Volatility use the same financial moment definitions.
- Their frontier points lie on the same internally generated efficient frontier when run with the same bounds.
- Do not compare the two published PV runs as if only the objective changed when their asset bounds differ.

## Acceptance philosophy

- Synthetic financial invariants: hard pass/fail, tight tolerances.
- Offline PV rounded-moment solver parity: bounded neighborhood / sanity tolerance.
- Live FDR parity: machine-readable deltas plus human review; no arbitrary exact PV threshold unless later evidence supports one.
- `result.json` and `raw/` remain full precision. `review/` is display-oriented only.
