## ADDED Requirements

### Requirement: Efficient Frontier realized risk overlay
Optimization Efficient Frontier의 각 point는 기존 ex-ante statistics/weights를 보존한 채 동일 canonical monthly asset-return sample과 portfolio rebalancing convention을 사용한 realized risk overlay를 계산할 수 있어야 한다(MUST).

Overlay는 최소 다음 field를 포함해야 한다.

- ex-ante Sharpe Ratio
- realized ex-post Sharpe Ratio
- realized CAGR
- Monthly Gain-to-Pain Ratio
- Pain Ratio
- Maximum Drawdown
- MDD depth (positive magnitude)
- Time Under Water percentage
- Pain Area in percentage-point months
- Pain Index percentage
- Maximum consecutive underwater months

#### Scenario: overlay preserves solver frontier
- GIVEN 기존 100-point Efficient Frontier가 있다
- WHEN realized risk overlay를 계산한다
- THEN 기존 point identity, expected return, volatility, ex-ante Sharpe와 weights를 변경하지 않는다

### Requirement: Frontier interactive backdata
Optimization report는 모든 Efficient Frontier point에 대해 client-side 선택과 재표시에 필요한 canonical realized backdata를 compact JSON으로 보존해야 한다(MUST).

JSON은 최소 다음 데이터를 포함해야 한다.

- ordered frontier point identity
- monthly observation dates
- asset ticker와 snapshotted asset name
- point별 asset weights
- point별 realized monthly portfolio return path
- point별 canonical realized drawdown path
- point별 CAGR, ex-post Sharpe, Monthly Gain-to-Pain, Pain Ratio, MDD, TUW, Pain Index, Maximum Underwater Months

Browser presentation layer는 monthly return path에서 drawdown 같은 canonical finance metric을 다시 계산해서는 안 된다(MUST NOT). 클릭/hover 시 persisted canonical values를 선택하고 chart coordinate로 변환하는 presentation-only transform만 수행한다.

#### Scenario: static report point selection
- GIVEN GitHub Pages에 게시된 정적 `report.html`과 embedded frontier JSON이 있다
- WHEN 사용자가 frontier dashboard에서 한 point를 선택한다
- THEN 서버 호출 없이 browser-side JavaScript가 persisted canonical metrics, weights와 drawdown path를 선택하여 화면을 함께 갱신해야 한다

### Requirement: 리스크·성과 균형 분석 primary reporting metrics
리스크·성과 균형 분석 dashboard는 다음 8개 realized metric을 같은 primary reporting level에서 제공해야 한다(MUST).

- CAGR
- Sharpe Ratio
- Monthly Gain-to-Pain
- Pain Ratio
- Maximum Drawdown
- Time Under Water
- Pain Index
- Max Underwater

각 metric card는 사용자가 지표의 의미를 판단할 수 있도록 한글 설명을 제공해야 한다(MUST).

```text
CAGR
연복리 수익률 (%)

Sharpe Ratio
샤프지수

Monthly Gain-to-Pain
손실이 난 달들의 총 손실 1단위당, 최종적으로 얼마의 순수익을 남겼는가

Pain Ratio
전고점 아래에서 겪은 낙폭 부담 1단위당 최종적으로 얼마의 연환산 초과수익을 얻었는가
(낙폭 부담은 하락의 깊이와 지속기간을 함께 반영)

Maximum Drawdown
낙폭 (%)

Time Under Water
이전 최고점을 회복하지 못하는 기간(물려있는 기간)

Pain Index
평균 낙폭 (깊이와 지속시간 반영)

Max Underwater
최장 미회복 기간 (개월)
```

#### Scenario: metric meanings remain distinguishable
- GIVEN Monthly Gain-to-Pain과 Pain Ratio가 같은 dashboard에 있다
- WHEN 사용자가 설명을 읽는다
- THEN Monthly Gain-to-Pain은 losing-month return burden을, Pain Ratio는 prior-peak drawdown burden을 분모로 사용하는 서로 다른 효율지표임을 구분할 수 있어야 한다

### Requirement: 리스크·성과 균형 분석 chart axes
8개 metric chart는 모두 동일한 semantic X축을 사용해야 한다(MUST).

```text
X = Annualized Volatility %
```

Point index를 chart의 실제 X coordinate로 사용해서는 안 된다(MUST NOT). 각 chart의 Y축은 해당 realized metric의 실제 값과 단위를 사용해야 한다(MUST).

각 chart는 최소 다음 정보를 화면에서 읽을 수 있게 제공해야 한다(MUST).

- X축 title과 numeric scale
- Y축 title/unit과 numeric scale
- 선택된 point marker
- 선택/hover point의 frontier point id, annualized volatility와 해당 metric value

Y display domain은 observed frontier metric range를 사용하고 curve shape를 읽을 수 있도록 여백을 둘 수 있다(MAY). 모든 chart에서 Y축을 0부터 강제 시작해서는 안 된다(MUST NOT), 단 semantic zero baseline이 필요한 별도 metric이 향후 정의되는 경우는 예외다.

#### Scenario: same point stays synchronized
- GIVEN 사용자가 어느 metric chart에서든 한 frontier point를 클릭한다
- WHEN selected point가 변경된다
- THEN 8개 metric chart의 marker, selected-point metrics, weights와 drawdown chart는 동일 point identity로 갱신되어야 한다

### Requirement: Selected Frontier Point allocation table
선택한 Frontier Point의 자산 구성 표는 `Ticker`, `Name`, `Allocation` 3개 column으로 표시해야 한다(MUST).

- `Ticker`: canonical asset symbol
- `Name`: input에 snapshotted 된 asset name
- `Allocation`: 해당 point의 asset weight percentage

#### Scenario: selected allocation identity is readable
- GIVEN 사용자가 한 frontier point를 선택한다
- WHEN allocation table이 갱신된다
- THEN 각 행에서 ticker와 상품명을 함께 확인할 수 있고 Allocation은 해당 point의 weight와 일치해야 한다

### Requirement: Frontier dashboard objective marker
동일한 리스크·성과 균형 분석 dashboard를 `max_sharpe`와 `target_volatility` optimization에 공통으로 사용해야 한다(MUST). Objective별로 별도 dashboard나 별도 metric set을 만들지 않는다(MUST NOT).

초기 선택 point와 선택점 label은 현재 run의 optimization objective를 반영해야 한다(MUST).

- `max_sharpe`: 기존 realized Maximum Sharpe default point를 유지하고 `Maximum Sharpe`로 표시한다.
- `target_volatility`: frontier point 중 `volatility_pct <= target_volatility_pct`를 만족하는 feasible point에서 `expected_return_pct`가 가장 높은 point를 초기 선택하고 `Maximum Return · Target Vol X%`로 표시한다.

`target_volatility` dashboard에서 Maximum Sharpe point를 별도 보조 marker로 추가하지 않는다(MUST NOT). 사용자는 동일한 8개 curve를 탐색하되 이번 optimization objective가 선택한 point 하나만 강조해서 볼 수 있어야 한다.

#### Scenario: Maximum Return run reuses the same dashboard
- GIVEN `objective: target_volatility`와 유효한 `target_volatility_pct`를 가진 optimization run이 있다
- WHEN 리스크·성과 균형 분석 dashboard를 생성한다
- THEN 8개 metric chart, 축, hover/click, allocation table과 drawdown interaction은 Maximum Sharpe run과 동일하다
- AND 초기 선택점은 목표 변동성 이하 frontier 중 기대수익이 가장 높은 point다
- AND 선택점에는 Maximum Return과 목표 변동성 값이 표시된다

### Requirement: Frontier marginal diagnostics are descriptive only
Frontier point order에서 이전 point 대비 delta를 계산할 수 있어야 한다(MUST).

```text
delta_cagr_pct = cagr_pct_i - cagr_pct_(i-1)
delta_sharpe = ex_post_sharpe_i - ex_post_sharpe_(i-1)
delta_monthly_gain_to_pain_ratio = monthly_gain_to_pain_ratio_i - monthly_gain_to_pain_ratio_(i-1)
delta_pain_ratio = pain_ratio_i - pain_ratio_(i-1)
delta_mdd_depth_pct = mdd_depth_pct_i - mdd_depth_pct_(i-1)
delta_tuw_pct = tuw_pct_i - tuw_pct_(i-1)
delta_pain_index_pct = pain_index_pct_i - pain_index_pct_(i-1)
```

Sharpe가 증가하는 interval에서는 비교 편의를 위해 Sharpe +0.10당 local marginal cost를 계산할 수 있다(MAY).

```text
mdd_cost_per_0_10_sharpe = delta_mdd_depth_pct / delta_sharpe * 0.10
tuw_cost_per_0_10_sharpe = delta_tuw_pct / delta_sharpe * 0.10
pain_cost_per_0_10_sharpe = delta_pain_index_pct / delta_sharpe * 0.10
```

`delta_sharpe <= epsilon`인 interval은 cost ratio를 유효한 decision metric으로 만들어서는 안 된다(MUST NOT).

이 change는 해당 diagnostics로 sweet spot을 자동 선택해서는 안 된다(MUST NOT).

#### Scenario: post-Max-Sharpe interval
- GIVEN frontier point 순서상 ex-post Sharpe가 이전 point보다 감소한다
- WHEN marginal diagnostics를 생성한다
- THEN raw deltas는 보존하되 Sharpe +0.10 cost ratio는 unavailable로 처리한다