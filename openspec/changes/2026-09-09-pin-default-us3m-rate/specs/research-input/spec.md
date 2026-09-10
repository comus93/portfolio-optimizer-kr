## ADDED Requirements

### Requirement: Default pinned U.S. 3-Month T-Bill rate
사용자가 RF를 별도로 지정하지 않은 Optimization/Backtest Research Frontend input은 `runs/20260908-0002/result.json`에서 `us_3m_tbill`로 resolve된 effective annual rate `3.8394827586206895%`를 default로 materialize해야 한다(MUST).

Canonical effective input은 다음 representation을 사용해야 한다(MUST).

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

이 값은 임의의 별도 경제가정이 아니라 이미 resolve된 U.S. 3-Month T-Bill effective rate를 반복 research run에서 재사용하는 pinned value로 설명해야 한다(MUST).

#### Scenario: Optimization에서 RF 미지정
- GIVEN 사용자가 Optimization을 요청했지만 RF를 언급하지 않았다
- WHEN Research Frontend가 effective input을 구성한다
- THEN fixed 3.8394827586206895%를 `risk_free`에 명시한다

#### Scenario: Backtest에서 RF 미지정
- GIVEN 사용자가 Backtest를 요청했지만 RF를 언급하지 않았다
- WHEN Research Frontend가 effective input을 구성한다
- THEN 동일한 fixed 3.8394827586206895%를 `risk_free`에 명시한다

#### Scenario: custom fixed RF override
- GIVEN 사용자가 다른 fixed annual RF를 명시했다
- WHEN Research Frontend가 effective input을 구성한다
- THEN pinned default 대신 사용자가 지정한 fixed rate를 보존한다

#### Scenario: dynamic us_3m_tbill override
- GIVEN 사용자가 `risk_free.mode: us_3m_tbill`을 명시했다
- WHEN Research Frontend가 effective input을 구성한다
- THEN pinned fixed default로 치환하지 않고 explicit dynamic mode를 보존한다

### Requirement: Default RF persistence
Research Frontend가 pinned RF default를 적용한 경우 completed research run의 persisted `input.yaml`에서 실제 effective fixed rate를 확인할 수 있어야 한다(MUST).

#### Scenario: RF 미지정 research run 재현
- GIVEN 사용자가 RF를 지정하지 않은 research run이 완료됐다
- WHEN `runs/<run_id>/input.yaml`을 확인한다
- THEN `mode: fixed`와 `annual_rate_pct: 3.8394827586206895`를 확인할 수 있다

### Requirement: Materialized fixed RF is effective at runtime
Research Frontend가 materialize한 fixed RF는 persistence metadata에만 남는 값이 아니라 해당 run의 shared analytics에 전달되는 effective annual RF여야 한다(MUST). 별도 caller override가 없다는 이유로 configured fixed RF를 `None` 또는 unavailable로 떨어뜨려서는 안 된다(MUST NOT).

#### Scenario: Backtest fixed RF analytics propagation
- GIVEN effective Backtest input에 `risk_free.mode: fixed`와 유효한 `annual_rate_pct`가 존재하고 별도 runtime RF override는 없다
- WHEN canonical runner가 historical analytics와 report artifacts를 생성한다
- THEN configured fixed annual RF를 ex-post Sharpe, Sortino 및 기타 applicable risk-adjusted analytics에 전달하고 RF 부재를 이유로 applicable Risk and Return Metrics 생성을 생략하지 않는다

#### Scenario: explicit runtime override priority
- GIVEN effective input에 fixed RF가 있고 canonical execution caller가 명시적인 supported RF override를 제공한다
- WHEN runner가 effective annual RF를 resolve한다
- THEN 명시적 override를 우선하되 input의 fixed RF가 존재하지 않는 것처럼 처리하지 않는다
