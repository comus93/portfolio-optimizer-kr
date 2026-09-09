# Proposal

## 배경

Research Frontend의 기본 RF convention은 U.S. 3-Month T-Bill이지만, 사용자가 RF를 지정하지 않은 상태에서 `risk_free.mode: us_3m_tbill`로 실행하면 runner가 매 run마다 FDR/FRED `TB3MS`를 다시 조회한다. KAW 연구 중 provider 실패로 동일 조건 재실행이 중단됐다.

성공한 run `20260908-0002`에는 동일 convention으로 계산된 effective annual RF가 이미 존재한다.

```text
source run: runs/20260908-0002/result.json
source requested_mode: us_3m_tbill
effective annual RF: 0.038394827586206895
percent: 3.8394827586206895%
source period: 2021-11-01 ~ 2026-08-31
```

## 변경

사용자가 RF를 별도로 언급하지 않은 Optimization/Backtest **Research Frontend** input은 위 값을 pinned U.S. 3-Month T-Bill effective rate로 materialize한다.

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

따라서 canonical research execution에서는 FDR/FRED `TB3MS`를 매 run마다 다시 조회하지 않는다.

## 유지되는 behavior

- 사용자가 custom fixed RF를 지정하면 해당 값을 그대로 사용한다.
- 사용자가 `risk_free.mode: us_3m_tbill`을 명시하면 기존 dynamic provider behavior를 그대로 사용한다.
- Core runner/YAML parser의 explicit mode semantics는 변경하지 않는다.

## 의미

`fixed` representation은 새로운 임의 경제가정이라는 뜻이 아니다. 이미 `us_3m_tbill` 경로로 resolve된 값을 deterministic research default로 저장하는 실행 표현이다.

Pinned 값은 source run 기간의 dynamic result와 동일하다. 다른 analysis period의 period-specific TB3MS 평균과 항상 동일하다고 주장하지 않고 project default convention으로 사용한다.

## 영향

`research-input` / `research-execution` default materialization이 변경된다. Optimization과 Backtest 양쪽 사용자 연구 경로에 적용된다. 금융 계산 공식과 explicit `us_3m_tbill` semantics는 변경하지 않는다.
