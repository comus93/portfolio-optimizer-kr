# AI Share

state: active
id: 20260829T202800+0900-llm
created_at: 2026-08-29T20:28:00+09:00
type: request
reply_to: none

## Context

사용자가 구현은 LLM이 직접 하고 Agent는 실제 실행 검증만 맡기도록 결정했다.

LLM이 main에 다음을 직접 반영했다.

### RF

- `FDRLoader.load_economic_series()` 추가
- Runner가 canonical/default `us_3m_tbill` 실행 시 FDR `FRED:TB3MS`를 직접 로드
- 실제 optimization monthly-return observation months와 TB3MS month를 맞춘 뒤 monthly quoted annual percentage-point rate의 arithmetic mean을 decimal annual RF로 사용
- 필요한 observation month가 TB3MS에 없으면 명시적 `DataValidationError`
- `fixed` mode는 explicit override로 유지
- UI default를 `us_3m_tbill`로 변경
- example/config/active study experiment를 `us_3m_tbill`로 변경
- runner targeted tests 추가

### Report chart contrast

사용자 피드백: 아래 차트는 첫 번째와 두 번째 portfolio series가 모두 blue 계열로 보여 구분이 어렵다.

```text
Portfolio Growth
Annual Returns
Annualized Active Return
Drawdowns
Rolling 3Y Returns
Rolling 5Y Returns
```

LLM이 `final_renderer.py`에 final presentation corrective pass를 추가했다.

- 첫 번째 series의 기존 blue는 유지
- 두 번째 series의 기존 purple `#7c3aed`를 기존 project asset palette의 green `#22c55e`로 변경
- 해당 6개 section 안에서만 stroke / fill / legend color를 변경
- 다른 chart palette는 변경하지 않음
- `tests/test_report_series_contrast.py` 추가

Historical `runs/**`는 provenance이므로 수정하지 않았다.

Agent의 PASS/FAIL 평가는 completion 근거로 사용하지 않는다. 검증 목적은 실제 실행 artifact를 LLM/사용자가 직접 검토할 수 있게 만드는 것이다.

## Message

구현하지 말고 최신 main을 pull한 뒤 **execution/browser validation만** 수행해라.

### 1. Targeted tests

최소:

```text
uv run pytest tests/test_runner.py tests/test_report_series_contrast.py -q
```

직접 영향받는 테스트가 더 있으면 필요한 범위만 추가한다. 관련 없는 full regression은 하지 않는다.

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

### 4. Browser color evidence

생성된 `report.html`을 실제 browser에서 열고 아래 6개 section을 확인한다.

각 section에 대해:

```text
first portfolio series color = blue
second portfolio series color = #22c55e green
legend second item = same green
series가 육안으로 명확히 구분됨
```

대상:

```text
Portfolio Growth
Annual Returns
Annualized Active Return
Drawdowns
Rolling 3Y Returns
Rolling 5Y Returns
```

가능하면 browser에서 실제 element `stroke` 또는 `fill` 값을 확인하여 보고한다. screenshot 자체를 만들 필요는 없고, 실제 DOM/style evidence가 우선이다.

### 5. 결과 보고

`agent-to-llm.md`에는 평가 문구보다 raw evidence를 우선한다.

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
6개 chart 각각 second series actual stroke/fill + legend color
```

`PASS`라고 써도 LLM은 신뢰 근거로 사용하지 않는다. 숫자와 생성된 `report.html`을 직접 검토한다.

코드 수정은 하지 않는다. 실행 blocker가 있으면 증상과 로그만 회신한다.
