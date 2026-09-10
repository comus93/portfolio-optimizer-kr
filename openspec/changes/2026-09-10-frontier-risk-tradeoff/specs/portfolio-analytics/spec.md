## ADDED Requirements

### Requirement: Canonical underwater depth
Monthly realized return path의 cumulative wealth와 running peak를 사용할 때 underwater depth는 canonical drawdown의 절대 손실 깊이여야 한다(MUST).

```text
wealth_t = product_{s<=t}(1 + return_s)
peak_t = max_{s<=t}(wealth_s)
drawdown_t = wealth_t / peak_t - 1
underwater_depth_t = max(0, -drawdown_t)
```

#### Scenario: new peak month
- GIVEN monthly wealth가 새로운 running peak를 기록한다
- WHEN underwater depth를 계산한다
- THEN 해당 month의 underwater depth는 0이다

### Requirement: Time Under Water percentage
Time Under Water(TUW)는 전체 monthly observations 중 canonical drawdown이 0보다 작은 observation의 비율이어야 한다(MUST).

```text
tuw_pct = count(drawdown_t < -epsilon) / T * 100
```

기본 numerical epsilon은 `1e-12`를 사용한다.

#### Scenario: half-period underwater
- GIVEN 12 observations 중 6 observations가 이전 peak 아래에 있다
- WHEN TUW를 계산한다
- THEN TUW는 50%이다

### Requirement: Pain Area and Pain Index
Pain Area는 monthly underwater depth의 합을 percentage-point month 단위로 표현해야 한다(MUST).

```text
pain_area_pct_months = sum(underwater_depth_t) * 100
```

Pain Index는 Pain Area를 전체 monthly observation count로 정규화한 평균 underwater depth여야 한다(MUST).

```text
pain_index_pct = pain_area_pct_months / T
               = mean(underwater_depth_t) * 100
```

Pain Index 계산에는 new-peak observation의 0 underwater depth도 포함해야 한다(MUST). Underwater observations만 조건부 평균해서는 안 된다(MUST NOT).

#### Scenario: duration affects Pain Index
- GIVEN 동일한 5% underwater depth가 더 많은 months에 지속되는 두 path가 있다
- WHEN 동일한 전체 observation length에서 Pain Index를 계산한다
- THEN 더 오래 underwater인 path의 Pain Index가 더 크다

#### Scenario: sample-length normalization
- GIVEN 동일한 underwater burden pattern을 동일 비율로 반복한 두 monthly paths가 있다
- WHEN Pain Area와 Pain Index를 계산한다
- THEN 더 긴 path의 Pain Area는 커질 수 있지만 Pain Index는 동일해야 한다

### Requirement: Maximum consecutive underwater months
Maximum Underwater Months는 `drawdown_t < -epsilon`인 consecutive monthly observations의 최장 길이여야 한다(MUST).

현재 sample 끝까지 회복하지 않은 episode도 observed underwater run으로 포함해야 한다(MUST).

#### Scenario: unrecovered tail
- GIVEN 마지막 4개 observations가 연속 underwater이고 sample 종료 시 회복되지 않았다
- WHEN Maximum Underwater Months를 계산한다
- THEN 최소 4개월의 observed underwater duration을 반영한다
