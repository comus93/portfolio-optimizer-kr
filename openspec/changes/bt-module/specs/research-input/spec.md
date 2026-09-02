## Purpose

LLM/User Research Frontend가 Optimization과 Backtest를 구분해 필요한 사용자 결정을 수집하고 canonical Backtest input을 생성하는 behavior를 정의한다.

## ADDED Requirements

### Requirement: Product-intent-aware input flow
Research Frontend는 사용자의 연구 의도가 Optimization인지 Backtest인지 구분해 해당 product에 필요한 질문만 해야 한다.

#### Scenario: 명시적 Backtest 요청
- GIVEN 사용자가 이미 정의한 두 portfolio를 과거 데이터로 비교해 달라고 요청한다
- WHEN research input을 구성한다
- THEN Optimization objective나 min/max constraint를 요구하지 않고 Backtest input flow를 사용한다

#### Scenario: 제품 의도가 모호함
- GIVEN 사용자가 "이 포트폴리오 분석해"처럼 Optimization과 Backtest 중 어느 쪽인지 결과 의미가 달라지는 요청을 한다
- WHEN 현재 대화만으로 product mode를 확정할 수 없다
- THEN 임의로 선택하지 않고 필요한 최소 질문으로 의도를 확인한다

### Requirement: Reuse already-provided information
사용자가 대화에서 이미 제공한 Backtest 입력은 다시 질문하지 않아야 한다.

#### Scenario: weights와 기간이 이미 있음
- GIVEN 사용자가 portfolio weights와 analysis period를 이미 명시했다
- WHEN 남은 input을 확인한다
- THEN 해당 값을 다시 묻지 않고 기계적 validation만 수행한다

### Requirement: Mechanical validation before user questions
Ticker 중복, portfolio weight 합, v1 portfolio count, positive initial balance 등 기계적으로 검증할 수 있는 항목은 사용자에게 판단을 떠넘기기 전에 시스템이 검증해야 한다.

#### Scenario: weight 합 90%
- GIVEN 한 Backtest portfolio의 입력 weights 합이 90%이다
- WHEN research input을 검증한다
- THEN 정상 입력으로 가정하지 않고 명시적으로 오류를 알려 수정이 필요한 값을 식별한다

### Requirement: Backtest-specific user decision surface
Backtest 입력에서 사용자가 결정해야 하는 핵심 값은 portfolio 구성과 target allocation이며, 필요할 때 period, benchmark, rebalancing을 사용자 의도에 따라 결정할 수 있어야 한다.

#### Scenario: portfolio 정의 부족
- GIVEN 사용자가 Backtest를 요청했지만 비교할 portfolio의 구성 또는 weights가 빠져 있다
- WHEN canonical input을 만들 수 없다
- THEN 빠진 portfolio 구성만 질문하고 Optimization 관련 질문을 추가하지 않는다

### Requirement: V1 comparison limit communication
Research Frontend는 v1에서 동시에 비교 가능한 portfolio가 최대 3개임을 적용하고 초과 요청을 조용히 잘라내지 않아야 한다.

#### Scenario: 네 portfolio 비교 요청
- GIVEN 사용자가 네 portfolio를 한 run에서 비교하려 한다
- WHEN v1 input을 구성한다
- THEN 일부 portfolio를 임의 제거하지 않고 v1 한도를 명시한다

### Requirement: No redundant approval after explicit execution intent
사용자가 이미 실행 의도를 명시했고 필요한 Backtest 입력과 사용자 결정이 모두 해소되면 다시 불필요한 승인 질문을 만들어서는 안 된다.

#### Scenario: "이 조건으로 백테스트해줘"
- GIVEN 유효한 Backtest input이 모두 확정되었다
- WHEN 사용자가 실행을 명시적으로 요청했다
- THEN 조건을 짧게 확인할 수는 있지만 `진행할까?` 같은 중복 승인으로 실행을 막지 않는다

### Requirement: Canonical input persistence
Research Frontend가 default를 자동 적용한 경우에도 실제 effective 값은 canonical YAML과 persisted `input.yaml`에 명시적으로 남겨야 한다.

#### Scenario: default 적용
- GIVEN 사용자가 어떤 Backtest setting을 지정하지 않아 canonical default가 적용된다
- WHEN run input을 persist한다
- THEN 실행에 실제 사용된 effective 값을 생략하지 않고 기록한다

## Decision Pending

Backtest Research Frontend의 benchmark, initial balance, analysis period, rebalancing, portfolio name default는 `design.md`의 Open Decisions에서 사용자 확정 후 구체 requirement로 추가한다.