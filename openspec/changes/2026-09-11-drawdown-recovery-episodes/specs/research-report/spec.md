## ADDED Requirements

### Requirement: Drawdown recovery presentation uses canonical analytics
Shared Drawdowns report는 canonical drawdown episode timing과 recovery analytics를 소비해야 하며 renderer/browser에서 Recovery Rate 또는 Normalized Underwater Duration finance formula를 다시 계산해서는 안 된다(MUST NOT).

#### Scenario: Worst Drawdowns recovery fields
- GIVEN canonical drawdown episode에 recovery_months와 annualized recovery rate가 있다
- WHEN Worst Drawdowns table을 표시한다
- THEN 기존 Recovery Time/Underwater 정보를 유지하고 Recovery Rate를 사용자-facing percentage로 확인할 수 있다

### Requirement: Elastic recovery summary is compact
Shared Drawdowns report는 각 portfolio의 Drawdowns 제목 바로 아래에 portfolio-level `Normalized Underwater Duration`을 compact KPI로 표시해야 한다(MUST).

사용자-facing label은 `탄성회복도`를 사용하고 값은 `x.x개월 / 10% DD` 형식으로 표시하며 `낮을수록 좋음`을 함께 안내해야 한다(MUST). 값이 unavailable이면 `N/A`를 표시해야 한다(MUST).

#### Scenario: portfolio drawdown section
- GIVEN canonical drawdown resilience summary가 3.14개월/10%DD이다
- WHEN 해당 portfolio의 Drawdowns section을 표시한다
- THEN 제목 아래, Drawdown chart 위에 `탄성회복도 3.1개월 / 10% DD · 낮을수록 좋음`을 확인할 수 있다
