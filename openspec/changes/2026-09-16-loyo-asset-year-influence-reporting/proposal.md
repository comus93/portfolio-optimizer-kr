# Change: LOYO Asset-Year Influence reporting

## Why

기존 LOYO 계산은 특정 calendar year 제거가 optimized allocation과 objective metric을 얼마나 흔드는지 보존하지만, 기본 report가 raw artifact schema에 가까운 wide table을 그대로 노출해 원래 연구 질문인 "특정 연도의 어떤 구성자산이 optimizer allocation에 강하게 연결되어 있는가"를 읽기 어렵게 만든다.

또한 user-facing report에 removed date/observation, solver, 빈 message 같은 내부 진단 필드가 노출되고, asset weight와 delta가 별도 column으로 반복되어 인지 부하가 크다.

## What changes

- 기존 `annual_asset_returns`, baseline optimized weights, LOYO scenario weights/deltas를 재사용해 `asset_year_influence` derived artifact를 생성한다.
- 이 projection을 위해 annual return 계산, baseline optimization 또는 LOYO optimization을 다시 실행하지 않는다.
- Optimization LOYO report의 정보 계층을 다음 순서로 재구성한다.
  1. Asset-Year Influence
  2. LOYO Summary
  3. Allocation Changes
- Asset-Year Influence는 year group × asset matrix로 구성하고 각 year에 구성자산 해당년도 수익률, 전체기간 최적비중, 해당년도 제외 최적비중, 비중 변화를 표시한다.
- 숫자 cell은 metric별 conditional background/heatmap을 사용하되 숫자 자체를 항상 읽을 수 있어야 한다.
- LOYO Summary는 `Allocation Turnover`를 user-facing `Reallocation`로 표현하고, 상위 3개 allocation shift를 방향과 크기와 함께 표시한다.
- Allocation Changes는 baseline row와 excluded-year rows를 asset별로 비교하며 각 cell에서 LOYO weight와 baseline 대비 delta를 함께 표시한다.
- Removed Start/End, Removed/Remaining Observations, Solver는 user-facing LOYO primary tables에서 제거한다. Message는 정상 행에서 노출하지 않고 실패/insufficient-data 시 Status/Reason으로 조건부 표시한다.
- user-facing numeric display는 percentage/ratio 모두 원칙적으로 소수점 2자리로 통일한다. canonical/raw precision은 변경하지 않는다.

## Capability impact

- `portfolio-optimization`: LOYO derived artifact 계약 추가. 기존 optimization objective/solver semantics는 변경하지 않는다.
- `research-report`: LOYO presentation hierarchy와 conditional-formatting semantics 변경.
- `run-artifacts`: 기존 raw/review persistence mechanism을 재사용하며 별도 shared formula 변경은 없다.
- `portfolio-backtest`: 영향 없음. Optimization-only LOYO section을 계속 자동 적용하지 않는다.

## Affected regression

- LOYO baseline 재실행 금지와 기존 objective/result semantics 회귀
- `asset_year_influence` raw/review artifact 값과 단위
- default Optimization HTML의 Asset-Year Influence / Summary / Allocation Changes 의미 검증
- Backtest에 Optimization-only LOYO section이 추가되지 않는지 확인
