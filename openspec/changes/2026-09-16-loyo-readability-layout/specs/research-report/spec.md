## ADDED Requirements

### Requirement: LOYO section placement follows result-reading flow
Default Optimization report는 LOYO section을 Portfolio Metrics 뒤, Monthly Returns 앞에 배치해야 한다(MUST).

#### Scenario: LOYO section order
- GIVEN Optimization report에 Portfolio Metrics, LOYO, Monthly Returns가 모두 존재한다
- WHEN report를 렌더링한다
- THEN section order는 Portfolio Metrics → Leave-One-Year-Out Robustness → Monthly Returns다

### Requirement: Asset-Year Influence groups are visually separable without altering heatmap semantics
Asset-Year Influence는 4-row year group마다 Year와 Metric column에 alternating zebra background를 적용해야 한다(MUST). Numeric asset cells의 metric-specific conditional background는 이 banding 때문에 덮어써서는 안 된다(MUST NOT).

#### Scenario: adjacent years
- GIVEN 2022와 2023 Asset-Year Influence group이 연속 표시된다
- WHEN table을 읽는다
- THEN Year와 Metric 영역의 alternating shade로 두 year group을 구분할 수 있고 asset numeric heatmap colors는 유지된다

### Requirement: LOYO asset identity is readable without hover
Asset-Year Influence와 Allocation Changes의 asset header는 `Name + Ticker`를 두 줄로 표시해야 한다(MUST). Name은 layout width에서 single-line ellipsis로 제한할 수 있지만(MAY) Ticker는 전체를 표시해야 한다(MUST).

LOYO Summary의 Allocation Shift cell은 compact ticker + signed delta 표현을 유지하고, summary 아래에 ticker/name mapping을 한 줄에 가능한 여러 자산이 들어가는 wrapping static legend로 표시해야 한다(MUST).

Asset identity를 위해 새 hover/tooltip JavaScript를 요구해서는 안 된다(MUST NOT).

#### Scenario: numeric Korean ticker
- GIVEN `144600 / KODEX 은선물(H)`이 LOYO asset universe에 있다
- WHEN Asset-Year Influence 또는 Allocation Changes header를 본다
- THEN `KODEX 은선물(H)`과 `144600`을 같은 header에서 두 줄로 식별할 수 있다
- AND LOYO Summary에서는 shift cell이 compact ticker 중심으로 유지되고 아래 legend에서 `144600 · KODEX 은선물(H)` mapping을 확인할 수 있다
