## MODIFIED Requirements

### Requirement: Optional benchmark
Backtest run은 optional benchmark를 지정할 수 있어야 하며 benchmark는 단일 asset 또는 고정 target-weight portfolio일 수 있어야 한다(MUST).

#### Scenario: benchmark 없음
- GIVEN benchmark를 지정하지 않았다
- WHEN backtest를 실행한다
- THEN absolute performance analytics는 제공하고 benchmark-relative analytics는 N/A 또는 non-applicable로 처리한다

#### Scenario: 단일 asset benchmark 있음
- GIVEN benchmark ticker가 지정되어 있다
- WHEN backtest를 실행한다
- THEN 기존 shared benchmark path와 benchmark-relative analytics를 모든 applicable portfolio에 대해 생성한다

#### Scenario: 고정비중 portfolio benchmark 있음
- GIVEN benchmark가 shared asset universe의 constituent와 합계 100% target weights로 정의되어 있다
- WHEN backtest를 실행한다
- THEN run-level rebalancing/calendar-alignment 규칙으로 benchmark portfolio path를 생성하고 기존 benchmark-relative analytics의 benchmark series로 사용한다

### Requirement: Common analysis period
동일 Backtest run의 모든 portfolio와 benchmark constituent는 동일 requested analysis period와 shared common effective period를 사용해야 한다(MUST).

#### Scenario: composite benchmark constituent가 더 늦게 시작
- GIVEN 비교 portfolio보다 늦게 상장된 asset이 portfolio benchmark에 포함된다
- WHEN backtest를 실행한다
- THEN benchmark constituent를 포함한 shared asset universe의 common availability에 따라 effective period가 결정된다
