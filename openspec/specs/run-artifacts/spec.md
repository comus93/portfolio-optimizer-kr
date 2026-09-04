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

### Requirement: Product mode in run contract
Canonical YAML run contract은 Optimization과 Backtest를 명확히 구분할 수 있는 product mode를 표현해야 한다(MUST).

#### Scenario: backtest YAML
- GIVEN 사용자-facing Backtest configuration이 있다
- WHEN YAML contract로 serialize한다
- THEN runner가 Optimization이 아니라 Backtest 실행 경계를 선택할 수 있는 명시적 mode가 존재한다

### Requirement: Backtest portfolio collection in YAML
Backtest YAML은 identity를 가진 portfolio collection과 각 portfolio의 target allocation을 loss 없이 표현해야 한다(MUST). v1 사용자-facing validation은 1~3개 portfolio를 허용하지만 YAML schema를 fixed `portfolio1`, `portfolio2`, `portfolio3` field로 설계해서는 안 된다(MUST NOT).

#### Scenario: 세 portfolio 입력 보존
- GIVEN 서로 다른 이름과 weights를 가진 세 portfolio가 있다
- WHEN input YAML을 저장하고 다시 읽는다
- THEN portfolio identity와 target weights가 동일하게 복원된다

#### Scenario: 향후 limit 확장
- GIVEN 향후 product policy가 4개 이상의 portfolio를 허용한다
- WHEN YAML contract를 확장한다
- THEN 기존 portfolio representation을 재설계하지 않고 collection cardinality만 확장할 수 있다

### Requirement: Backtest Time Period persistence
Backtest YAML은 `Month-to-Month` 또는 `Year-to-Year` Time Period mode와 해당 requested boundary를 loss 없이 표현해야 한다(MUST).

#### Scenario: Month-to-Month round trip
- GIVEN Start Year, First Month, End Year, Last Month가 있는 Month-to-Month input이 있다
- WHEN YAML로 저장하고 다시 읽는다
- THEN mode와 모든 period boundary가 동일하게 복원된다

#### Scenario: Year-to-Year round trip
- GIVEN Start Year와 End Year가 있는 Year-to-Year input이 있다
- WHEN YAML로 저장하고 다시 읽는다
- THEN mode와 year boundaries가 동일하게 복원되고 First/Last Month를 필수값으로 요구하지 않는다

### Requirement: Backtest schedule settings persistence
Backtest YAML은 run-level rebalancing policy와 `Calendar Aligned` setting을 loss 없이 표현해야 한다(MUST).

#### Scenario: non-calendar quarterly round trip
- GIVEN rebalancing=quarterly, Calendar Aligned=No인 Backtest input이 있다
- WHEN YAML로 저장하고 다시 읽는다
- THEN 두 setting이 동일하게 복원되고 first-active-month anchored schedule을 선택할 수 있다

### Requirement: Backtest configuration persistence
Persisted Backtest `input.yaml`은 실제 실행에 사용된 Time Period mode와 requested period, initial balance, portfolio definitions, benchmark configuration, run-level rebalancing policy, Calendar Aligned와 shared market-data settings를 보존해야 한다(MUST).

#### Scenario: run 재현
- GIVEN 완료된 Backtest run이 있다
- WHEN `runs/<run_id>/input.yaml`을 확인한다
- THEN backtest를 다시 구성하는 데 필요한 canonical user input과 자동 적용된 default를 확인할 수 있다

### Requirement: Backtest defaults are explicit in persisted input
Research Frontend가 SPY benchmark, initial balance 10,000, Month-to-Month mode, Calendar Aligned=Yes, rebalancing=Monthly, generated portfolio name 같은 default를 적용한 경우에도 persisted input에서 실제 effective 값을 생략해서는 안 된다(MUST NOT).

#### Scenario: frontend defaults 사용
- GIVEN 사용자가 benchmark, initial balance, calendar alignment와 rebalancing을 별도로 지정하지 않았다
- WHEN run이 persist된다
- THEN effective SPY benchmark, initial balance 10,000, Calendar Aligned=Yes, rebalancing=Monthly를 `input.yaml`에서 확인할 수 있다

### Requirement: Backtest canonical result domains
Backtest run의 `result.json`은 최소 configuration, data_coverage, portfolio_definitions, portfolio_paths, portfolio_performance, optional benchmark_analytics, correlations, return_decomposition, risk_decomposition을 structured domain으로 표현할 수 있어야 한다(MUST).

#### Scenario: backtest result inspection
- GIVEN 완료된 Backtest run이 있다
- WHEN `result.json`을 읽는다
- THEN 각 portfolio의 identity와 historical path/analytics를 optimization result 없이 structured하게 확인할 수 있다

### Requirement: Multi-portfolio raw and review identity
Backtest raw/review artifact는 여러 portfolio의 series와 table을 저장할 때 portfolio identity를 loss 없이 유지해야 한다(MUST).

#### Scenario: 같은 ticker가 여러 portfolio에 존재
- GIVEN SPY가 Portfolio A와 Portfolio B에 모두 포함되어 있다
- WHEN contribution 또는 weight artifact를 저장한다
- THEN `(portfolio, asset)` identity가 보존되어 서로 다른 series가 혼합되지 않는다
