## ADDED Requirements

### Requirement: Default pinned U.S. 3-Month T-Bill input
사용자가 RF를 별도로 지정하지 않은 Optimization/Backtest research input은 `runs/20260908-0002/result.json`에서 `us_3m_tbill`로 resolve된 effective annual rate `3.8394827586206895%`를 canonical default로 materialize해야 한다(MUST).

Canonical YAML representation은 다음과 같아야 한다(MUST).

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

이 default는 반복 provider 조회를 피하기 위한 pinned U.S. 3-Month T-Bill convention이며 임의의 별도 경제가정으로 설명해서는 안 된다(MUST NOT).

#### Scenario: Optimization에서 RF 미지정
- GIVEN 사용자가 Optimization을 요청했지만 RF를 언급하지 않았다
- WHEN Research Frontend가 canonical input을 만든다
- THEN fixed 3.8394827586206895%를 effective RF로 명시한다

#### Scenario: Backtest에서 RF 미지정
- GIVEN 사용자가 Backtest를 요청했지만 RF를 언급하지 않았다
- WHEN Research Frontend가 canonical input을 만든다
- THEN 동일한 fixed 3.8394827586206895%를 effective RF로 명시한다

#### Scenario: 사용자가 RF를 override
- GIVEN 사용자가 custom fixed rate 또는 `us_3m_tbill` provider mode를 명시했다
- WHEN canonical input을 만든다
- THEN pinned default 대신 사용자가 지정한 RF 설정을 보존한다
