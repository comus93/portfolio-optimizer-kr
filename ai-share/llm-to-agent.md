# AI Share

state: active
id: 20260829T201500+0900-llm
created_at: 2026-08-29T20:15:00+09:00
type: request
reply_to: none

## Context

사용자가 RF 구현은 Agent가 아니라 LLM이 직접 수정하도록 결정했다. 이전 RF 구현 요청은 superseded한다.

LLM이 main에 다음을 직접 반영했다.

- `FDRLoader.load_economic_series()` 추가
- Runner가 canonical/default `us_3m_tbill` 실행 시 FDR `FRED:TB3MS`를 직접 로드
- 실제 optimization monthly-return observation months와 TB3MS month를 맞춘 뒤 monthly quoted annual percentage-point rate의 arithmetic mean을 decimal annual RF로 사용
- 필요한 observation month가 TB3MS에 없으면 명시적 `DataValidationError`
- `fixed` mode는 explicit override로 유지
- UI default를 `us_3m_tbill`로 변경
- example/config/active study experiment를 `us_3m_tbill`로 변경
- runner targeted tests 추가

Historical `runs/**`는 provenance이므로 수정하지 않았다.

Agent의 PASS/FAIL 평가는 completion 근거로 사용하지 않는다. 검증 목적은 실제 실행 artifact를 LLM/사용자가 직접 검토할 수 있게 만드는 것이다.

## Message

구현하지 말고 최신 main을 pull한 뒤 **execution validation만** 수행해라.

### 1. Targeted tests

최소:

```text
uv run pytest tests/test_runner.py -q
```

RF 변경 때문에 직접 영향받는 테스트가 더 있으면 필요한 범위만 추가한다. 관련 없는 full regression은 하지 않는다.

### 2. RF calibration check

기존 PV same-input 기간:

```text
2016-08-01 ~ 2026-07-31
```

에 대해 실제 runtime이 계산한 `us_3m_tbill` effective annual RF를 보고한다.

과거 임시 calibration 값:

```text
2.35595%
```

과의 차이도 숫자로 보고한다. 값이 다르면 상수를 맞춰 끼우거나 구현을 수정하지 말고, 실제 TB3MS observation count / first month / last month / arithmetic mean을 보고한다.

### 3. Fresh 7-asset run

기존 same-input 조건으로 새 run을 만든다.

```text
Assets: QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
Period: 2016-08-01 ~ 2026-07-31
Provided: 40 / 10 / 10 / 0 / 10 / 15 / 15
Caps: QQQ 50, SPMO 50, others 30
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Frontier: 100
Rebalancing: Monthly
Risk-free: us_3m_tbill
```

새 run id를 사용한다.

### 4. 결과 보고

`agent-to-llm.md`에는 평가 문구보다 **raw evidence**를 우선한다.

최소:

```text
start HEAD
changed files: none expected
targeted test command + exact result
run id / run path / report.html path
effective RF (%)
TB3MS observation count / first month / last month
optimized weights
expected return
volatility
ex-ante Sharpe
PV reference numerical differences
Up/Down count
```

`PASS`라고 써도 LLM은 신뢰 근거로 사용하지 않는다. 숫자와 생성된 `report.html`을 직접 검토한다.

코드 수정은 하지 않는다. 실행 blocker가 있으면 증상과 로그만 회신한다.
