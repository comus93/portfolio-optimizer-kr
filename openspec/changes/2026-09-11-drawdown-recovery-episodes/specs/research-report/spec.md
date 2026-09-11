## ADDED Requirements

### Requirement: Drawdown recovery presentation uses canonical analytics
Shared Drawdowns report는 canonical drawdown episode timing과 recovery analytics를 소비해야 하며 renderer/browser에서 Recovery Rate 또는 Recovery Progress finance formula를 다시 계산해서는 안 된다(MUST NOT).

#### Scenario: Worst Drawdowns recovery fields
- GIVEN canonical drawdown episode에 recovery_months와 annualized recovery rate가 있다
- WHEN Worst Drawdowns table을 표시한다
- THEN 기존 Recovery Time/Underwater 정보를 유지하고 Recovery Rate를 사용자-facing percentage로 확인할 수 있다

### Requirement: Recovery Progress comparison
Shared Drawdowns report는 portfolio별 worst drawdown episode들의 Bottom 이후 normalized Recovery Progress를 비교할 수 있어야 한다(MUST).

기본 view는 drawdown rank 기준 worst 5 episode 이하를 표시하고, X축은 `Months Since Bottom`, Y축은 `Recovery Progress %`를 사용해야 한다(MUST). 100% recovery reference를 제공해야 한다(MUST).

#### Scenario: ongoing drawdown
- GIVEN worst episode가 아직 ongoing이다
- WHEN Recovery Progress chart를 표시한다
- THEN latest canonical observation까지만 선을 표시하고 100% 회복을 임의로 연결하지 않는다
