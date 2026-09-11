## ADDED Requirements

### Requirement: Drawdown recovery presentation uses canonical analytics
Shared Drawdowns report는 canonical drawdown episode timing과 recovery analytics를 소비해야 하며 renderer/browser에서 Recovery Rate finance formula를 다시 계산해서는 안 된다(MUST NOT).

#### Scenario: Worst Drawdowns recovery fields
- GIVEN canonical drawdown episode에 recovery_months와 annualized recovery rate가 있다
- WHEN Worst Drawdowns table을 표시한다
- THEN 기존 Recovery Time/Underwater 정보를 유지하고 Recovery Rate를 사용자-facing percentage로 확인할 수 있다
