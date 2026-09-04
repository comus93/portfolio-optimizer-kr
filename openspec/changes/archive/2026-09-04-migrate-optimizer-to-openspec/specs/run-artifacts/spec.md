## Purpose

분석 실행의 canonical input/result와 재현 가능한 run artifact contract를 정의한다.

## ADDED Requirements

### Requirement: YAML run contract
사용자-facing 실행 configuration은 YAML로 표현되어 CLI, UI, Agent가 동일한 run contract를 공유해야 한다.

#### Scenario: UI 실행
- GIVEN 사용자가 UI에서 optimization 입력을 구성한다
- WHEN 실행을 요청한다
- THEN UI는 동일 YAML contract를 생성해 canonical runner 경로로 전달한다

### Requirement: Percentage input convention
YAML의 percentage field는 human-readable percentage-point 값을 사용해야 한다.

#### Scenario: 20 percent 입력
- GIVEN YAML field에 `20`이 입력된다
- WHEN 내부 weight/rate 값으로 변환한다
- THEN 20% 즉 0.20의 의미로 해석한다

### Requirement: Exact input persistence
Persisted run은 실제 실행에 사용된 YAML을 `runs/<run_id>/input.yaml`로 보존해야 한다.

#### Scenario: run 재현
- GIVEN 완료된 run이 있다
- WHEN 해당 run directory를 확인한다
- THEN 실행에 사용된 input YAML을 확인할 수 있다

### Requirement: Canonical structured result
금융 계산 결과의 source of truth는 structured `result.json`이어야 하며 presentation layer가 canonical finance value를 재정의해서는 안 된다.

#### Scenario: report와 canonical value 차이 조사
- GIVEN report 표시값과 persisted structured value를 비교한다
- WHEN 의미상 불일치가 발견된다
- THEN `result.json`의 canonical finance value를 기준으로 판단한다

### Requirement: Canonical result domains
Optimization run의 canonical result는 최소 configuration, data_coverage, asset_statistics, optimization_result, efficient_frontier, portfolio_performance, benchmark_analytics, correlations, return_decomposition, risk_decomposition 영역을 표현할 수 있어야 한다.

#### Scenario: optimization result inspection
- GIVEN 완료된 optimization run이 있다
- WHEN `result.json`을 읽는다
- THEN 주요 optimization과 historical analytics 결과를 structured domain별로 확인할 수 있다

### Requirement: Full-precision raw artifacts
`raw/` artifact는 machine-oriented full-precision table을 보존해야 한다.

#### Scenario: 정밀 수치 검증
- GIVEN report에 formatting된 수치가 있다
- WHEN exact calculation evidence가 필요하다
- THEN `raw/` table에서 full-precision 값을 확인할 수 있다

### Requirement: Review artifacts
`review/` artifact는 human/LLM이 읽기 쉬운 명시적 unit과 orientation을 가진 분석 table을 제공해야 한다.

#### Scenario: LLM result review
- GIVEN 완료된 run이 있다
- WHEN 사람이 주요 결과를 검토한다
- THEN `review/`에서 canonical result를 이해하기 위한 readable table을 사용할 수 있다

### Requirement: Self-contained report artifact
사용자-facing run은 필요할 때 persisted source에서 생성된 self-contained `report.html`을 제공할 수 있어야 한다.

#### Scenario: 기존 run 열기
- GIVEN 이미 persisted된 run output이 있다
- WHEN report를 연다
- THEN optimization을 다시 실행하지 않고 기존 artifact만으로 report를 볼 수 있다

### Requirement: Validation evidence location
검증 결과를 보존해야 하는 run은 `validation/` 하위에 validation evidence를 저장할 수 있어야 한다.

#### Scenario: browser validation run
- GIVEN report validation 결과를 사용자 또는 LLM이 검토해야 한다
- WHEN evidence를 보존한다
- THEN 해당 run의 `validation/`에서 확인할 수 있다

### Requirement: Run directory immutability
기존 `runs/<run_id>/` directory를 silent overwrite해서는 안 된다.

#### Scenario: 중복 run id
- GIVEN 동일한 run_id directory가 이미 존재한다
- WHEN 새 실행이 같은 run_id를 사용하려 한다
- THEN 기존 artifact를 조용히 덮어쓰지 않는다

### Requirement: Viewer finance boundary
Viewer는 persisted canonical/review/raw output을 읽어야 하며 returns, risk, attribution, optimization statistics를 별도 financial convention으로 재계산해서는 안 된다.

#### Scenario: existing run rendering
- GIVEN `result.json`과 review/raw artifacts가 존재한다
- WHEN viewer가 report를 렌더링한다
- THEN persisted finance values를 사용하고 browser/viewer 계산은 presentation-only transform에 한정한다

### Requirement: Missing artifact failure
Viewer가 요청한 필수 run artifact가 없으면 이를 명확한 failure로 사용자에게 알려야 한다.

#### Scenario: result.json 누락
- GIVEN run directory에 required canonical artifact가 없다
- WHEN viewer가 해당 run을 열려 한다
- THEN silent fallback 대신 missing-artifact error를 표시한다
