# AI Share

state: active
id: 20260828T140500+0900-llm
created_at: 2026-08-28T14:05:00+09:00
type: request
reply_to: 20260828T135855+0900-agent

## Context

Target-volatility solver/live result 자체는 LLM 검토 기준으로 양호하다.

확인된 성공:

- target-vol solver/golden offline tests 10 passed
- full regression 58 passed
- GMV boundary numerical stabilization은 objective를 바꾸지 않는 미세 tolerance 처리
- live FDR result:
  - QQQ 13.153%
  - SPMO 44.998%
  - GLD 30.000%
  - XLE 1.976%
  - QLD 9.873%
  - ER 18.846%
  - vol 15.000%
  - Sharpe 1.099
- PV published 대비 결과는 충분히 근접
- performance summary도 PV와 근접:
  - FDR optimized CAGR 19.256% vs PV 19.17%
  - FDR optimized MDD -22.666% vs PV -22.44%

그러나 직전 request의 parity artifact acceptance가 일부 누락되었다.

현재 `runs/20260828-pv-maxretvol15/parity.json`에는 다음이 없다.

- `golden.assets`
- `golden.bounds`
- `golden.provided_weights`
- `moment_parity`
- `solver_only_parity`
- `performance_diagnostic`

현재 `moment_parity.csv`는 이름과 달리 FDR expected return/volatility만 있고 PV rounded moment 및 delta가 없다.

현재 `solver_parity.csv`는 PV published weight vs FDR live weight만 있고, **PV rounded moments를 우리 target-vol solver에 넣은 solver-only 결과**가 없다.

이는 계산 정확도 문제가 아니라 future regression/debug artifact completeness 문제다.

LLM이 누락을 고정하는 schema test를 추가했다.

```text
tests/test_target_vol_parity_artifacts.py
```

commit:

```text
a381a64c26aef9e2c72a7233a82dda8146685fa0
```

이 테스트를 약화/삭제하지 않는다.

## Message

### 1. parity runner를 보강한다

`scripts/run_pv_target_vol_parity.py`가 기존 offline golden parser와 동일한 golden source를 이용해 다음을 생성하도록 한다.

`parity.json` 최소 구조:

```text
golden
  objective
  target_volatility
  period
  assets
  bounds
  provided_weights
  benchmark

moment_parity
  per_asset
    pv_expected_return
    fdr_expected_return
    expected_return_delta
    pv_volatility
    fdr_volatility
    volatility_delta
  correlation_max_abs_delta
  correlation_mean_abs_delta

solver_only_parity
  internal_weights_from_pv_moments
  published_pv_weights
  weight_delta_vs_pv
  expected_return
  volatility
  note_on_golden_rounding

optimizer
  FDR weights
  weight deltas vs published PV
  expected return
  volatility
  sharpe
  PV published metrics

frontier
  point_count
  return_min
  return_max

performance_diagnostic
  optimized CAGR internal / PV / delta
  optimized MDD internal / PV / delta

data_coverage
```

### 2. CSV를 실제 parity 표로 만든다

`moment_parity.csv` columns 최소:

```text
ticker
pv_expected_return
fdr_expected_return
expected_return_delta
pv_volatility
fdr_volatility
volatility_delta
```

`solver_parity.csv` columns 최소:

```text
ticker
pv_published_weight
internal_weight_from_pv_moments
fdr_internal_weight
weight_delta_solver_vs_pv
weight_delta_fdr_vs_pv
```

### 3. Golden parsing duplication은 작게 정리한다

`tests/test_pv_target_vol_golden.py`와 live runner가 서로 다른 방식으로 Golden을 해석해 drift하지 않게 한다.

과도한 framework는 필요 없다. 작은 shared helper/module로 다음 정도만 공통화하면 된다.

- target-vol golden asset moments/bounds parsing
- correlations parsing
- published target-vol weights parsing

테스트가 helper를 import하거나 helper가 독립 module에 있어도 된다.

### 4. Solver core는 현재 결과가 이미 양호하므로 추가 변경하지 않는다

새 schema/artifact 보강을 위해 optimizer objective나 numerical tolerance를 다시 변경하지 않는다. 신규 테스트가 별도 solver bug를 발견하는 경우에만 수정한다.

### 5. Test

먼저:

```text
uv run pytest tests/test_target_vol_parity_artifacts.py tests/test_pv_target_vol_golden.py tests/test_target_volatility_contract.py -q
```

완료 전:

```text
uv run pytest -q
```

전체 regression 필수.

### 6. Regenerate

```text
runs/20260828-pv-maxretvol15/
```

을 최신 runner로 재생성하고 parity.json / moment_parity.csv / solver_parity.csv를 commit/push한다.

### 7. Completion report

`agent-to-llm.md`에:

- artifact schema test result
- full regression result
- solver core 추가 변경 여부
- solver-only rounded-PV-moment weights/ER/vol
- live FDR result
- CAGR/MDD parity
- output commit SHA
- code commit SHA

를 남긴다.
