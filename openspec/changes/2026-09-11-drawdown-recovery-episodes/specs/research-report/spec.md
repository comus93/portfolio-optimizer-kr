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

### Requirement: Drawdown comparison uses one shared overlay chart
Shared Drawdowns report는 Provided/Optimized/Benchmark 또는 Backtest의 configured portfolios/benchmark drawdown series를 동일한 X/Y 축의 단일 overlay chart에서 비교해야 한다(MUST). Portfolio마다 별도 drawdown chart를 반복 렌더링해서는 안 된다(MUST NOT).

각 series는 고유 색을 유지해야 하며, 사용자가 portfolio identity를 선택하면 선택 series는 foreground에서 굵고 불투명하게 강조되고 나머지 series는 동일 chart 안에서 얇고 반투명한 context line으로 남아야 한다(MUST). 선택 동작은 canonical finance 값을 재계산하지 않고 presentation state만 변경해야 한다(MUST NOT).

선택 portfolio의 `탄성회복도`와 Worst Drawdowns episode table만 상세 영역에 표시해야 하며 benchmark도 선택 가능한 identity로 취급해야 한다(MUST). 기본 선택은 첫 configured portfolio로 한다(MUST).

#### Scenario: compare three drawdown paths
- GIVEN two configured portfolios와 benchmark drawdown series가 있다
- WHEN Drawdowns section을 표시한다
- THEN 세 series가 하나의 chart에 서로 다른 색으로 겹쳐 보이고 chart는 하나만 존재한다

#### Scenario: foreground selected portfolio
- GIVEN overlay chart에서 두 번째 portfolio를 선택한다
- WHEN 선택 state가 변경된다
- THEN 두 번째 portfolio line은 foreground 굵기와 full opacity로 강조되고 다른 line들은 context opacity로 남는다
- AND 상세 영역의 탄성회복도와 Worst Drawdowns table은 두 번째 portfolio 데이터로 바뀐다

#### Scenario: shared product coverage
- GIVEN Optimization과 Backtest가 shared Drawdowns component를 사용한다
- WHEN overlay interaction을 변경한다
- THEN 두 product의 generated report regression에서 동일 presentation contract를 검증한다
