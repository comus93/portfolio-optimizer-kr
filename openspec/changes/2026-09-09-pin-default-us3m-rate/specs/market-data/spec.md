## MODIFIED Requirements

### Requirement: Risk-free modes
Risk-free configuration은 `us_3m_tbill`과 `fixed` mode를 지원해야 하고 기본 mode는 `us_3m_tbill`이어야 한다(MUST).

기본 `us_3m_tbill` mode는 normal research execution에서 FDR/FRED `TB3MS`를 매 run마다 다시 조회하지 않고, canonical cached effective annual rate `0.038394827586206895`를 사용해야 한다(MUST).

이 값의 provenance는 `runs/20260908-0002/result.json`이며 해당 run에서 `requested_mode: us_3m_tbill`로 resolve된 값이다.

`fixed` mode는 사용자가 입력한 annual rate를 그대로 사용해야 한다(MUST).

Runtime boundary가 명시적인 annual RF override를 공급하면 `us_3m_tbill` cached default보다 해당 supplied value를 우선할 수 있어야 한다(MUST).

#### Scenario: RF를 지정하지 않은 기본 run
- GIVEN Optimization 또는 Backtest input에서 별도 RF override가 없다
- WHEN 기본 `us_3m_tbill` risk-free rate를 resolve한다
- THEN effective annual rate `0.038394827586206895`를 사용하고 FDR/FRED economic-series provider를 호출하지 않는다

#### Scenario: explicit us_3m_tbill
- GIVEN canonical input이 `risk_free.mode: us_3m_tbill`을 명시한다
- WHEN 별도 runtime annual RF override가 없다
- THEN 동일 cached effective annual rate를 사용한다

#### Scenario: custom fixed rate
- GIVEN `risk_free.mode: fixed`와 annual rate가 입력된다
- WHEN effective RF를 resolve한다
- THEN cached US3M 값이 아니라 사용자가 입력한 fixed rate를 사용한다

#### Scenario: runtime annual RF override
- GIVEN `us_3m_tbill` mode에서 runtime이 명시적인 annual RF를 공급한다
- WHEN effective RF를 resolve한다
- THEN supplied annual RF를 사용한다

### Requirement: Persist effective risk-free metadata
Canonical run은 requested risk-free mode와 실제 effective annual rate를 구분해 기록해야 한다(MUST). User-facing 설명은 실제 effective mode/rate semantics와 충돌해서는 안 된다(MUST NOT).

#### Scenario: cached us_3m_tbill run
- GIVEN 기본 `us_3m_tbill` mode가 cached rate로 완료된다
- WHEN persisted metadata를 확인한다
- THEN `requested_mode: us_3m_tbill`과 effective annual rate `0.038394827586206895`를 함께 복원할 수 있다
