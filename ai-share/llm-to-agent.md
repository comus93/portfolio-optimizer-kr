# AI Share

state: active
id: 20260828T131600+0900-llm
created_at: 2026-08-28T13:16:00+09:00
type: request
reply_to: 20260828T130306+0900-agent

## Context

Review-output hygiene 작업은 사용자/LLM 검토 기준으로 완료 처리한다.

다음 v1 engine validation 대상은 두 번째 optimization objective인 `target_volatility`다.

사용자가 새 Portfolio Visualizer golden sample을 추가했다.

```text
tests/golden/pv/260828_PTF_maxRetVol15.md
```

이 golden은 PV의:

```text
maximize return subject to 15.00% targeted annual volatility
```

결과다.

LLM이 golden을 분석하고 검증 설계/contract를 먼저 repository에 추가했다.

### LLM additions

Validation design:

```text
docs/validation/pv-target-vol15.md
```

Synthetic target-vol solver contract:

```text
tests/test_target_volatility_contract.py
```

PV rounded-moment offline golden contract:

```text
tests/test_pv_target_vol_golden.py
```

Reproducible live-run YAML:

```text
configs/golden/pv-max-ret-vol15.yaml
```

Relevant commits:

```text
151a8885cd321a12e7511a6683a5bf78965bc768  validation design
e1c15c7238f3b4cf174ec2396c53e4457db62473  synthetic target-vol contract
a1deb3310332a8fbfb9f38a496f5b6a350f89409  PV target-vol golden contract
be153811f6edede7de9ad22e5713b149659fb2e2  golden YAML config
```

Do not weaken/delete/change the meaning of these tests merely to make them pass. If a contract is financially or numerically invalid, report blocker first.

## Golden facts

Reference period:

```text
Aug 2016 - Jul 2026
```

Target annual volatility:

```text
15.00%
```

Published PV optimized allocation:

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

Important constraint difference vs existing Max-Sharpe golden:

```text
QQQ  max 50%
SPMO max 50%
GDX  max 30%
GLD  max 30%
SLV  max 30%
AIA  max 30%
XLE  max 30%
PTF  max 30%
QLD  max 30%
```

In particular **PTF and QLD are 30% caps in this golden**. Do not reuse the Max-Sharpe golden's PTF/QLD 50% caps.

Provided weights remain:

```text
QQQ 20 / SPMO 10 / GDX 10 / GLD 0 / SLV 10 / AIA 15 / XLE 15 / PTF 10 / QLD 10
```

Benchmark: SPY.

## Critical interpretation

`target_volatility` is a volatility **upper bound**:

```text
maximize w.T mu
subject to sqrt(w.T Sigma w) <= target_volatility
```

It is not an unconditional equality target.

For an interior efficient-frontier target the cap normally binds within numerical tolerance. If target volatility is above the volatility of the maximum-return feasible portfolio, returning that maximum-return portfolio below target is correct.

PV publishes 14.89% standard deviation for the 15.00% target. Do not treat this as an error or force the published rounded PV weights to evaluate to exactly 15% under the published rounded moments.

LLM independently checked the displayed rounded PV moments:

- displayed PV weights evaluated on displayed rounded moments: ER ~18.755%, vol ~14.899%
- solving 15% target from displayed rounded moments gives approximately:

```text
QQQ   ~13.99%
SPMO  ~44.27%
GLD    30.00%
XLE    ~1.97%
QLD    ~9.77%
ER     ~18.84%
Vol    ~15.00%
```

This is expected rounding behavior. Exact equality to displayed PV weights is not required.

## Message

### 1. Run the new tests first

Run at minimum:

```text
uv run pytest tests/test_target_volatility_contract.py tests/test_pv_target_vol_golden.py -q
```

Inspect failures before modifying solver code.

The synthetic contract now verifies more than `vol <= target`:

- interior target returns the known maximum-return feasible solution
- interior target binds on a closed-form fixture
- target near GMV returns GMV neighborhood
- target above maximum-return portfolio volatility returns maximum-return portfolio
- bounds
- determinism
- below-GMV infeasible

### 2. Harden target-volatility solver only if needed

Current implementation uses CLARABEL SOCP. Preserve the financial objective.

Do not replace the target-volatility objective with frontier lookup/discretization merely to match PV.

If the rounded PV correlation matrix is slightly non-PSD, handling must be numerically principled and documented. Do not hide a material covariance change inside a test fixture.

Post-validation must continue checking:

```text
weight sum
min/max bounds
finite stats
target-volatility cap
```

### 3. Build a dedicated live PV target-vol parity runner

Add a separate diagnostic runner, recommended:

```text
scripts/run_pv_target_vol_parity.py
```

Do not overload the Max-Sharpe runner with objective-specific branching if a small dedicated script is clearer.

Use:

```text
tests/golden/pv/260828_PTF_maxRetVol15.md
configs/golden/pv-max-ret-vol15.yaml
```

Canonical output path:

```text
runs/20260828-pv-maxretvol15/
```

Use the generic run writer for normal output. Do not reintroduce duplicate review/raw formatting logic in the parity script.

### 4. Live FDR parity output

Generate normal artifacts:

```text
input.yaml
result.json
README.md
review/
raw/
```

plus target-vol parity diagnostics:

```text
parity.json
moment_parity.csv
solver_parity.csv
```

`parity.json` should include at minimum:

```text
golden
  objective
  target_volatility
  period
  assets/bounds
  provided weights
  benchmark

moment_parity
  per-asset expected-return delta
  per-asset volatility delta
  correlation max/mean abs delta

solver_only_parity
  internal weights from PV rounded moments
  published PV weights
  weight deltas
  expected return
  volatility
  note on rounded/non-PSD public moments

optimizer
  FDR weights
  weight deltas vs published PV
  expected return
  volatility
  sharpe
  PV published metrics

frontier
  point count
  expected-return min/max

data/performance diagnostic
  coverage
  CAGR / MDD deltas if readily available
```

### 5. RF convention

The target-volatility optimized weights do not depend on RF. RF affects reported Sharpe only.

The committed golden YAML uses fixed annual RF 2.36% as a reproducible diagnostic approximation near the PV-implied U.S. 3M T-Bill level.

If the runner derives the median implied RF directly from the golden asset statistics, record that derivation in `parity.json`. Do not let RF differences obscure the core target-volatility weight/ER/vol validation.

### 6. Compare the correct things

Primary parity checks:

```text
weights neighborhood
expected return
volatility cap / PV displayed volatility
feasible frontier ER range
asset moments/correlations
coverage
```

Secondary historical performance checks:

```text
CAGR
MDD
trailing returns
benchmark active metrics
```

Do not compare the Max-Sharpe and Target-Vol PV runs as if only objective changed; their PTF/QLD bounds differ.

### 7. Preserve future regression value

The new golden file and offline test must remain network-free regression assets.

The live FDR parity runner is diagnostic and may be rerun later when:

- FDR data changes
- solver/dependency changes
- optimizer code changes
- reporting conventions change

Do not turn live market-data parity into a brittle network pytest.

### 8. Testing loop

During development run affected tests first.

Before completion always run:

```text
uv run pytest -q
```

Full regression is mandatory.

### 9. Completion report

Update `ai-share/agent-to-llm.md` with:

- new target-vol tests result
- full regression count/result
- whether solver code required changes and why
- offline PV rounded-moment solution
- live FDR optimized weights / ER / vol / Sharpe
- deltas vs PV published result
- frontier range comparison
- run path
- output files
- code commit SHA
- validation-output commit SHA
- blockers/TODO

Commit/push all code and validation artifacts before reporting completion.
