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

사람이 읽는 의미는 "전체 투자기간 동안 전고점보다 평균적으로 얼마나 아래에 있었는가"이다. Pain Index 계산에는 new-peak observation의 0 underwater depth도 포함해야 한다(MUST). Underwater observations만 조건부 평균해서는 안 된다(MUST NOT).

#### Scenario: duration affects Pain Index
- GIVEN 동일한 5% underwater depth가 더 많은 months에 지속되는 두 path가 있다
- WHEN 동일한 전체 observation length에서 Pain Index를 계산한다
- THEN 더 오래 underwater인 path의 Pain Index가 더 크다

#### Scenario: sample-length normalization
- GIVEN 동일한 underwater burden pattern을 동일 비율로 반복한 두 monthly paths가 있다
- WHEN Pain Area와 Pain Index를 계산한다
- THEN 더 긴 path의 Pain Area는 커질 수 있지만 Pain Index는 동일해야 한다

### Requirement: Pain Ratio
Pain Ratio는 동일 realized monthly return path의 CAGR에서 annual risk-free rate를 차감한 excess CAGR을 Pain Index의 decimal value로 나눈 값이어야 한다(MUST).

```text
pain_ratio = (CAGR - annual_risk_free_rate) / (pain_index_pct / 100)
```

Pain Index가 numerical epsilon 이하이면 finite Pain Ratio를 만들어서는 안 된다(MUST NOT).

#### Scenario: excess CAGR per drawdown burden
- GIVEN CAGR 20%, annual risk-free rate 4%, Pain Index 2%인 path가 있다
- WHEN Pain Ratio를 계산한다
- THEN Pain Ratio는 8.0이다

### Requirement: Monthly Gain-to-Pain Ratio
Monthly Gain-to-Pain Ratio는 Schwager-style monthly statistic을 사용해야 한다(MUST).

```text
monthly_gain_to_pain_ratio = sum(all monthly returns)
                           / abs(sum(monthly returns where return < 0))
```

분자는 winning months의 합이 아니라 모든 monthly returns의 arithmetic sum이어야 한다(MUST). 분모는 losing-month returns의 arithmetic sum의 절댓값이어야 한다(MUST).

Monthly Gain-to-Pain Ratio는 monthly-frequency statistic으로 명시해야 하며 daily-frequency Gain-to-Pain Ratio와 직접 비교 가능한 값으로 표현해서는 안 된다(MUST NOT).

#### Scenario: Schwager monthly definition
- GIVEN monthly returns가 +5%, -3%, +2%, -1%, +4%이다
- WHEN Monthly Gain-to-Pain Ratio를 계산한다
- THEN numerator는 +7%, denominator는 4%, ratio는 1.75이다

### Requirement: Maximum consecutive underwater months
Maximum Underwater Months는 `drawdown_t < -epsilon`인 consecutive monthly observations의 최장 길이여야 한다(MUST).

현재 sample 끝까지 회복하지 않은 episode도 observed underwater run으로 포함해야 한다(MUST).

#### Scenario: unrecovered tail
- GIVEN 마지막 4개 observations가 연속 underwater이고 sample 종료 시 회복되지 않았다
- WHEN Maximum Underwater Months를 계산한다
- THEN 최소 4개월의 observed underwater duration을 반영한다
