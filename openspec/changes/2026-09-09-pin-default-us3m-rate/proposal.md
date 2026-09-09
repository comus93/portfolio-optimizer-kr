# Proposal

## 배경

현재 Research Frontend의 기본 RF는 U.S. 3-Month T-Bill convention이지만 `risk_free.mode: us_3m_tbill` 실행은 매 run마다 FDR/FRED `TB3MS`를 다시 조회한다. KAW 연구 중 provider 실패로 동일 조건 재실행이 중단됐고, 성공한 run `20260908-0002`에서 같은 convention의 effective annual RF가 이미 산출되어 있다.

```text
source run: runs/20260908-0002/result.json
requested mode: us_3m_tbill
effective annual RF: 0.038394827586206895
percent: 3.8394827586206895%
source period: 2021-11-01 ~ 2026-08-31
```

## 변경

사용자가 RF를 별도로 지정하지 않은 Optimization/Backtest research input은 위 값을 **pinned U.S. 3-Month T-Bill effective rate**로 materialize한다.

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

이는 새로운 경제 가정을 도입하는 것이 아니라 이미 `us_3m_tbill` 경로로 resolve한 값을 기본 research convention으로 재사용하여 반복 provider 호출을 제거하는 것이다.

사용자가 RF를 명시하면 해당 입력이 우선한다. `us_3m_tbill` dynamic provider mode 자체는 유지한다.

## 영향

Shared `research-input` default가 변경된다. 동일 canonical YAML/runner를 사용하는 Optimization과 Backtest 모두 영향받는다. 금융 계산 공식은 변경하지 않는다.
