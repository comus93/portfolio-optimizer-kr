## Purpose

기존 Study / Experiment / Run 연구 운영 흐름 안에서 Backtest를 별도 제품 모드로 실행하는 사용자 연구 execution behavior를 정의한다. Backtest 때문에 별도 opaque orchestration이나 별도 finance execution path를 만들지 않는다.

## Requirements

### Requirement: Shared research execution boundary
Optimization과 Backtest의 일반 사용자 연구 실행은 기존 Study / Experiment / Run / `control/execute.yaml` 경계를 공유해야 한다(MUST).

#### Scenario: Backtest 실행 요청
- GIVEN 사용자가 유효한 Backtest 연구 실행을 요청한다
- WHEN 실행 조건이 확정된다
- THEN 별도 Backtest 전용 실행 시스템이 아니라 canonical research execution boundary를 통해 실행한다

### Requirement: Explicit product mode
Experiment 또는 effective run input은 실행 제품이 Optimization인지 Backtest인지 명시적으로 식별할 수 있어야 한다(MUST).

#### Scenario: Backtest experiment 실행
- GIVEN Backtest용 experiment input이 있다
- WHEN runner가 해당 input을 resolve한다
- THEN Optimization objective 존재 여부를 추론해서 mode를 결정하지 않고 명시적 product mode로 Backtest 경계를 선택한다

### Requirement: Canonical YAML runner reuse
Research execution은 UI/CLI/Agent와 동일한 canonical YAML runner를 사용해야 하며 Backtest 전용 계산 진입점을 우회해서는 안 된다(MUST).

#### Scenario: GitHub Actions 실행
- GIVEN `control/execute.yaml`이 Backtest experiment를 가리킨다
- WHEN 일반 research execution이 수행된다
- THEN experiment를 canonical Backtest YAML input으로 resolve한 뒤 동일 runner/persistence 경로를 사용한다

### Requirement: Backtest Experiment identity uses union asset set
Backtest Experiment identity는 한 run에서 비교하는 모든 portfolio의 asset ticker union set으로 정의해야 한다(MUST). Portfolio weights, portfolio count/name, asset의 portfolio별 membership, rebalancing, benchmark, initial balance, analysis period 같은 조건이 바뀌더라도 union ticker set이 같으면 같은 Experiment의 새 Run으로 관리해야 한다(MUST).

#### Scenario: portfolio membership만 변경
- GIVEN Run A와 Run B의 전체 union ticker set은 `SPY/GLD/QQQ/TLT`로 같지만 portfolio별 asset membership이 다르다
- WHEN Experiment identity를 판정한다
- THEN 같은 Experiment의 서로 다른 Run으로 관리한다

#### Scenario: union ticker 변경
- GIVEN 기존 union ticker set에 `XLE`가 추가된다
- WHEN 새 Backtest 조건을 저장한다
- THEN 기존 Experiment가 아니라 새 Experiment로 관리한다

### Requirement: Explicit execution intent
Experiment 파일의 저장 또는 수정만으로 실행을 시작해서는 안 되며 기존 execution control의 명시적 run intent를 사용해야 한다(MUST).

#### Scenario: Backtest 조건만 수정
- GIVEN Backtest experiment YAML이 수정되었지만 execution control이 run 요청 상태가 아니다
- WHEN repository 변경이 반영된다
- THEN Backtest를 자동 실행하지 않는다

### Requirement: Run provenance
완료된 Backtest research run은 Study, Experiment, Run 관계와 product mode를 provenance에서 식별할 수 있어야 한다(MUST).

#### Scenario: 과거 Backtest run 추적
- GIVEN 완료된 Backtest run이 있다
- WHEN run context와 input을 확인한다
- THEN 어떤 Study/Experiment에서 어떤 Backtest configuration이 실행되었는지 복원할 수 있다

### Requirement: Agent is not the canonical research execution engine
Agent/Codex는 개발 및 real-environment/E2E/browser 검증에 사용할 수 있지만 일반 사용자 Backtest 연구 실행의 canonical engine으로 요구해서는 안 된다(MUST NOT).

#### Scenario: 사용자 Backtest run
- GIVEN 사용자가 일반 연구 목적으로 Backtest 실행을 요청한다
- WHEN 정상 production research path를 선택한다
- THEN Agent 세션 존재 여부와 무관하게 canonical execution path로 실행할 수 있어야 한다
