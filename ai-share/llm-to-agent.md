# AI Share

state: active
id: 20260829T195100+0900-llm
created_at: 2026-08-29T19:51:00+09:00
type: request
reply_to: none

## Context

사용자 결정: 앞으로 risk-free의 canonical/default 기준은 Portfolio Visualizer와 같은 **U.S. 3-Month Treasury Bill**이다.

`2.35595%` fixed RF는 최초 구현/과거 PV parity 진단 편의를 위해 넣었던 임시 상수의 잔재다. production/default semantics로 사용하지 않는다.

현재 확인된 상태:

- `docs/specification.md`: 이미 `Risk-free Mode = us_3m_tbill`을 default로 선언한다.
- `RiskFreeConfig`와 YAML parser default도 `us_3m_tbill`이다.
- 그러나 `pipeline._annual_rf()`의 US 3M mode는 실제 provider가 없고 외부 `annual_rf` 주입을 요구한다.
- CLI는 이를 위해 `--annual-rf-pct` temporary override를 갖고 있다.
- UI는 selectbox 순서 때문에 `fixed`가 실질 default이며 2.0%를 제시한다.
- `configs/example.yaml`, `docs/input-ui-contract.md` 예시는 아직 fixed RF다.
- 최근 validation run도 `fixed 2.35595%`로 실행되어 PV parity 검증의 계산 조건이 완전히 canonical하지 않았다.

Federal Reserve/FRED reference series:

`TB3MS` — 3-Month Treasury Bill Secondary Market Rate, Discount Basis, monthly, averages of business days.
https://fred.stlouisfed.org/series/TB3MS

## Message

US 3M T-Bill을 실제 canonical runtime RF로 완성해라.

### Scope

1. `docs/specification.md`의 RF contract를 먼저 구체화한다.
   - default/canonical mode = `us_3m_tbill`
   - source = Federal Reserve 3-Month Treasury Bill secondary market rate
   - monthly source convention은 `TB3MS`와 동등한 semantics를 사용
   - RF effective period는 optimization monthly return observation period와 일치
   - 실제 effective RF와 source/coverage를 run metadata에 남김
   - `fixed` mode는 explicit override/test/research 용도로 계속 지원 가능하나 default가 아니다.

2. 런타임에서 `us_3m_tbill`이 별도 `--annual-rf-pct` 없이 동작하게 구현한다.
   - production RF를 상수로 hardcode하지 않는다.
   - provider/data retrieval 책임 위치는 기존 architecture에 맞춘다.
   - provider failure/coverage 부족은 명시적 error로 처리한다.
   - cache가 필요하면 기존 project convention에 맞게 최소 구현한다.

3. 임시 override 경로 정리.
   - `--annual-rf-pct`가 더 이상 canonical US 3M 실행에 필요하지 않아야 한다.
   - 유지할 필요가 있으면 명시적 debug/test override로 의미를 축소하고 문서화한다.

4. active defaults/examples/UI를 canonical RF로 통일한다.
   - `ui/app.py`: default selection = `us_3m_tbill`
   - `configs/example.yaml`: `us_3m_tbill`
   - `docs/input-ui-contract.md` YAML example: `us_3m_tbill`
   - 아직 실행 전인 active experiment/study config에서 fixed 2.35595가 기본값처럼 남아 있으면 canonical mode로 변경
   - 이미 생성된 historical `runs/**` artifact는 provenance이므로 소급 수정하지 않는다.

5. tests를 추가/수정한다.
   - YAML에서 `risk_free` 생략 시 US 3M default
   - UI generated YAML 기본값 US 3M
   - US 3M mode가 외부 annual_rf 주입 없이 실행됨
   - fixed mode explicit input은 계속 정확히 동작
   - RF source coverage가 optimization return period와 일치
   - result metadata에 requested mode / effective annual RF / source / coverage가 보존됨

### PV calibration

2016-08-01 ~ 2026-07-31 구간의 기존 `2.35595%` 값은 **production constant가 아니라 PV parity calibration reference**로만 사용한다.

새 provider로 같은 구간을 계산했을 때 PV reference와 합리적인 tolerance 내에서 일치하는지 검증한다. 값이 다르면 상수를 맞춰 끼우지 말고 source series / observation window / annualization convention 차이를 조사해 보고한다.

### Validation priority

이 변경 후 최근 7-asset validation 조건을 `risk_free: us_3m_tbill`로 새 run하여 숫자를 다시 산출한다.

Agent의 PASS 라벨 자체는 completion 근거가 아니다. 다음을 artifact로 남긴다.

- effective RF와 source/coverage
- optimized weights / expected return / volatility / ex-ante Sharpe
- PV reference와의 숫자 차이
- 차이가 남으면 metric별 원인 후보

전체 회귀테스트가 아니라 **이번 RF 변경 영향 테스트 + 해당 E2E 숫자 재검증**을 우선 실행한다. 관련 없는 회귀는 필요 시에만 수행한다.
