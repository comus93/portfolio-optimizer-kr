## Purpose

Canonical calculated result와 persisted run directory의 source-of-truth, precision, reproducibility와 overwrite behavior를 정의한다.

## Requirements

### Requirement: Structured canonical result is the source of truth
계산 결과의 source of truth는 UI가 아니라 structured canonical result여야 한다(MUST). UI-specific coordinate, DOM state 또는 presentation-only state를 canonical result에 저장해서 finance semantics로 취급해서는 안 된다(MUST NOT).

#### Scenario: report rendering
- GIVEN completed run의 `result.json`과 report renderer가 있다
- WHEN report를 생성한다
- THEN report의 finance values는 canonical structured result/artifact에서 유도하고 DOM state를 역으로 canonical result로 사용하지 않는다

### Requirement: Canonical Optimization result domains
기존 Optimization `result.json`은 최소 configuration, data_coverage, asset_statistics, optimization_result, efficient_frontier, portfolio_performance, benchmark_analytics, correlations, return_decomposition, risk_decomposition domain을 표현할 수 있어야 한다(MUST).

#### Scenario: completed Optimization run
- GIVEN Optimization이 정상 완료되었다
- WHEN canonical result를 inspect한다
- THEN optimized solution뿐 아니라 coverage와 applicable historical analytics domain을 복원할 수 있다

### Requirement: Run directory contract
Persisted run은 다음 artifact 역할을 유지해야 한다(MUST).

```text
runs/<run_id>/
├─ input.yaml
├─ result.json
├─ context.yaml        # research execution only
├─ raw/
├─ review/
├─ report.html
└─ validation/         # validation run when applicable
```

`input.yaml`은 exact/effective execution input, `result.json`은 canonical calculated result, `raw/`는 full-precision tables, `review/`는 human/LLM-readable tables, `report.html`은 self-contained presentation artifact, `validation/`은 applicable validation evidence를 담당해야 한다(MUST).

#### Scenario: research execution run
- GIVEN research control을 통해 run이 완료된다
- WHEN run directory를 inspect한다
- THEN execution input, canonical result, machine precision data와 human-readable review를 역할별로 구분할 수 있다

### Requirement: Full precision and review artifacts remain distinct
`raw/`는 canonical 계산값의 machine-oriented precision을 보존하고 `review/`는 사람이 읽기 쉬운 formatting/summary를 제공할 수 있어야 한다(MUST). Review formatting 때문에 canonical precision을 재정의해서는 안 된다(MUST NOT).

#### Scenario: rounded review value
- GIVEN raw metric이 소수점 이하 많은 precision을 가진다
- WHEN review CSV에서 반올림 표시한다
- THEN canonical/raw value가 review 표시값으로 덮어써지지 않는다

### Requirement: Existing run directories are immutable by default
동일 `run_id`의 기존 run directory를 새 실행이 silent overwrite해서는 안 된다(MUST NOT).

#### Scenario: duplicate run id
- GIVEN `runs/20260904-0001`이 이미 존재한다
- WHEN 같은 run id로 새 persisted execution을 시도한다
- THEN 기존 artifact를 교체하지 않고 명시적 failure 또는 새 run identity를 요구한다

### Requirement: Effective input persistence
Persisted `input.yaml`은 실제 실행에 사용된 effective canonical input을 복원할 수 있어야 한다(MUST). Runtime default가 finance/product behavior에 영향을 주는 경우 persisted input에서 그 effective value를 확인할 수 있어야 한다(MUST).

#### Scenario: runtime default applied
- GIVEN optional input이 runtime default로 확정되어 실행된다
- WHEN `input.yaml`을 inspect한다
- THEN 재실행에 필요한 effective setting을 식별할 수 있다

### Requirement: Risk-free metadata persistence
Run artifact는 requested risk-free mode와 effective annual risk-free rate를 구분해 보존해야 한다(MUST).

#### Scenario: external T-Bill resolution
- GIVEN `us_3m_tbill` mode가 external series로 effective rate를 resolve한다
- WHEN run artifact를 저장한다
- THEN requested mode와 실제 effective annual rate를 모두 추적할 수 있다
