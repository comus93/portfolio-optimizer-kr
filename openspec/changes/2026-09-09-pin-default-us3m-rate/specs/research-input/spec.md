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
