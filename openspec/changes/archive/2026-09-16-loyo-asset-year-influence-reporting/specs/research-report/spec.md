## ADDED Requirements

### Requirement: Optimization LOYO report prioritizes Asset-Year Influence
Persisted Asset-Year Influence와 LOYO evidence가 존재하면 default Optimization report는 다음 정보 계층으로 LOYO 결과를 표시해야 한다(MUST).

1. Asset-Year Influence
2. LOYO Summary
3. Allocation Changes

Browser는 persisted values를 presentation-only pivot/group/order/formatting에 사용할 수 있지만 optimizer 또는 annual asset return을 다시 계산해서는 안 된다(MUST NOT).

#### Scenario: first-pass LOYO inspection
- GIVEN 여러 year와 여러 asset의 LOYO evidence가 있다
- WHEN 사용자가 LOYO section을 처음 본다
- THEN 어떤 `year × asset` 조합이 큰 allocation sensitivity를 보였는지 먼저 확인하고, 그 다음 year-level summary와 전체 allocation 변화 상세를 확인할 수 있다

### Requirement: Asset-Year Influence grouped matrix
Asset-Year Influence는 year를 group row로, asset을 column으로 사용하고 각 year에 다음 4개 metric row를 표시해야 한다(MUST).

```text
구성자산 해당년도 수익률
전체기간 최적비중
해당년도 제외 최적비중
비중 변화
```

Metric별 numeric cell은 값의 방향/크기를 보조하는 conditional background를 사용할 수 있으며(MAY), color만으로 값을 전달해서는 안 되고 numeric value를 함께 표시해야 한다(MUST).

#### Scenario: one year group
- GIVEN 2022 QQQ의 annual return, baseline weight, excluded-year weight와 delta가 있다
- WHEN matrix를 렌더링한다
- THEN 2022 group의 QQQ column에서 네 값을 서로 다른 metric row로 읽을 수 있고 하나의 cell을 4개 sub-cell로 분할하지 않는다

### Requirement: LOYO Summary uses decision-facing fields
LOYO Summary는 정상 feasible scenario에서 최소 Excluded Year, Δ Return, Δ Sharpe, Reallocation과 signed Top 3 Allocation Shifts를 표시해야 한다(MUST).

기존 `allocation_turnover`는 user-facing label에서 `Reallocation`로 표현해야 한다(MUST).

Removed Start/End, Removed/Remaining Observations와 Solver를 primary user-facing summary column으로 표시해서는 안 된다(MUST NOT). Message는 정상 scenario의 빈 column으로 표시하지 않고 failure/insufficient-data가 있을 때만 Status/Reason 형태로 조건부 표시해야 한다(MUST).

#### Scenario: top allocation shifts
- GIVEN 한 LOYO scenario에 여러 asset weight delta가 있다
- WHEN summary를 표시한다
- THEN absolute delta 기준 상위 3개 asset을 signed percentage-point 값과 함께 표시한다

### Requirement: LOYO Allocation Changes matrix
Allocation Changes는 full-sample baseline optimized allocation과 각 excluded-year optimized allocation을 asset column matrix로 비교해야 한다(MUST).

각 excluded-year asset cell은 LOYO optimized weight와 baseline 대비 signed percentage-point delta를 함께 표시해야 한다(MUST).

#### Scenario: QQQ allocation change
- GIVEN baseline QQQ weight가 31.06%이고 2022-excluded QQQ weight가 56.93%이다
- WHEN Allocation Changes를 표시한다
- THEN baseline row에는 31.06%를, 2022 row에는 `56.93% (+25.87%p)` 의미를 확인할 수 있다

### Requirement: LOYO display precision
LOYO user-facing percentage, percentage-point와 ratio metric은 원칙적으로 소수점 2자리로 표시해야 한다(MUST). Presentation rounding은 canonical/raw stored precision을 변경해서는 안 된다(MUST NOT).
