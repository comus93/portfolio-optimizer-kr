## ADDED Requirements

### Requirement: Per-run navigation summary
Persisted run은 canonical run artifact에서 파생된 `README.md` navigation summary를 제공해야 한다(MUST).

Summary는 최소 다음 section 순서를 유지해야 한다(MUST).

```text
Metadata
Purpose
Portfolios
Key Results
Notes
Artifacts
```

#### Scenario: run directory inspection
- GIVEN 완료된 Optimization 또는 Backtest run이 있다
- WHEN 사용자가 `runs/<run_id>/`를 연다
- THEN run ID만 보지 않고 product, 연구 맥락, 기간, benchmark, portfolio와 대표 결과를 README에서 파악할 수 있다

### Requirement: Run navigation summary is non-canonical
Run README는 discovery/navigation projection이며 `input.yaml`, `context.yaml`, `result.json` 또는 canonical raw artifact의 의미를 재정의해서는 안 된다(MUST NOT).

#### Scenario: README formatting differs from result precision
- GIVEN README의 Key Results가 사람이 읽기 쉬운 단위로 반올림되어 있다
- WHEN canonical 값을 확인한다
- THEN README 표시값을 `result.json` 또는 raw precision보다 우선하지 않는다

### Requirement: Aggregate run catalog
Repository의 `runs/README.md`는 persisted run을 탐색할 수 있는 aggregate catalog를 제공해야 한다(MUST).

Catalog는 최소 다음 열을 유지해야 한다(MUST).

```text
Run | Product | Study / Experiment | Period | Benchmark | Summary
```

#### Scenario: multiple run discovery
- GIVEN `runs/` 아래 여러 persisted run이 있다
- WHEN aggregate catalog를 생성한다
- THEN 각 run directory를 개별 탐색하지 않고 run identity와 대략적인 실험 목적을 비교할 수 있다

### Requirement: Aggregate catalog is derived and rebuildable
Aggregate catalog는 각 run의 persisted artifact를 기준으로 deterministic하게 재생성할 수 있어야 한다(MUST). 과거 run이 별도 hand-written catalog metadata를 요구해서는 안 된다(MUST NOT).

#### Scenario: new run added
- GIVEN 기존 run들과 새 completed run이 있다
- WHEN run navigation을 갱신한다
- THEN 전체 catalog가 다시 생성되고 새 run과 기존 run이 함께 탐색 가능하다

### Requirement: Navigation generation does not mutate canonical results
Run README와 aggregate catalog 생성은 canonical finance result, effective input, raw/review artifact를 변경해서는 안 된다(MUST NOT).

#### Scenario: navigation refresh
- GIVEN completed run artifact가 존재한다
- WHEN README와 aggregate catalog를 재생성한다
- THEN 기존 `input.yaml`, `context.yaml`, `result.json`, `raw/`, `review/` 내용은 그대로 유지된다
