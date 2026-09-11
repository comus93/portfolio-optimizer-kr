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

Catalog는 repository navigation만으로 연구 흐름을 판단할 수 있도록 다음 3단계 구조를 제공해야 한다(MUST).

```text
Latest by Experiment
Recent Runs
Full Run History (collapsed)
```

`Latest by Experiment`는 Product + Study / Experiment 조합별 latest run 한 건과 run count를 제공해야 한다(MUST). `Recent Runs`는 최신 run들을 시간 역순으로 제공해야 한다(MUST). `Full Run History`는 모든 persisted run을 유지하되 기본 화면의 정보 밀도를 낮추기 위해 접힌 `<details>` 영역으로 제공할 수 있다(MAY).

각 run row는 최소 Run, Product, Study / Experiment, Period, Benchmark, Report, Summary 정보를 보존해야 한다(MUST).

#### Scenario: multiple run discovery
- GIVEN 동일 experiment의 반복 run과 여러 다른 experiment가 공존한다
- WHEN `runs/README.md`를 연다
- THEN 하위 run directory를 개별 탐색하지 않고 각 experiment의 최신 결과와 반복 횟수를 먼저 판단할 수 있다
- AND 최근 개별 실행 이력도 바로 확인할 수 있다
- AND 전체 persisted run history는 유실되지 않는다

### Requirement: Aggregate catalog Markdown remains structurally valid
Public report link enrichment 또는 navigation 재생성을 반복해도 `runs/README.md`의 Markdown table header separator는 유효해야 한다(MUST). Separator row를 일반 data row로 처리해 `N/A` 또는 report link를 삽입해서는 안 된다(MUST NOT).

#### Scenario: public link refresh on already enriched index
- GIVEN `Report` column이 이미 포함된 aggregate catalog가 있다
- WHEN public report link refresh를 다시 실행한다
- THEN separator row는 모든 cell이 Markdown separator syntax를 유지한다
- AND catalog table은 GitHub에서 정상 렌더링된다

### Requirement: Public report URL is passed through, not derived by navigation
Public report URL은 실행 또는 publication orchestration이 exact URL로 제공하고 run publication metadata에 저장해야 한다(MUST). Navigation layer는 repository owner, Pages domain, run path 규칙을 조합하여 public URL을 자체 계산해서는 안 된다(MUST NOT).

Run publication metadata는 `runs/<run_id>/links.yaml`의 `public_report_url`을 사용한다.

#### Scenario: arbitrary publication location
- GIVEN 실행기가 `https://reports.example.net/custom/result.html`을 public report URL로 등록했다
- WHEN run README와 aggregate catalog를 생성한다
- THEN 두 navigation artifact는 전달받은 URL을 그대로 링크한다
- AND GitHub Pages 고정 도메인 또는 고정 경로 규칙을 적용하지 않는다

### Requirement: Public report link survives navigation rebuild
등록된 public report URL은 일반 navigation 재생성 이후에도 run README와 aggregate catalog에 다시 적용할 수 있어야 한다(MUST).

#### Scenario: report regeneration
- GIVEN `links.yaml`에 public report URL이 등록된 completed run이 있다
- WHEN report 또는 navigation README가 재생성된다
- THEN run README의 `Artifacts`에 `Public Report` 링크가 다시 나타난다
- AND `runs/README.md`의 `Report` 열에도 동일 URL이 나타난다

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
