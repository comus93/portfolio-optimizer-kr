# Proposal

## 배경

현재 기본 RF mode는 `us_3m_tbill`이고, runner는 매 run마다 FDR/FRED `TB3MS`를 다시 조회해 effective annual RF를 계산한다. KAW 연구 중 provider 실패로 동일 조건 재실행이 중단됐다.

성공한 run `20260908-0002`에는 동일 `us_3m_tbill` convention으로 계산된 effective annual RF가 이미 존재한다.

```text
source run: runs/20260908-0002/result.json
requested mode: us_3m_tbill
effective annual RF: 0.038394827586206895
percent: 3.8394827586206895%
source period: 2021-11-01 ~ 2026-08-31
```

## 변경

Optimization과 Backtest의 기본 `us_3m_tbill` mode는 위 값을 **cached/pinned U.S. 3-Month T-Bill effective rate**로 재사용한다.

```text
us_3m_tbill default resolution
-> 0.038394827586206895
-> no per-run FDR/FRED TB3MS fetch
```

사용자-facing default mode 이름과 input contract는 `us_3m_tbill`로 유지한다. `fixed` mode는 사용자가 별도의 custom fixed rate를 지정할 때 그대로 사용한다.

CLI/runtime에서 annual RF를 명시적으로 공급하는 override도 유지한다.

## 의미

이 변경은 RF의 경제적 출처를 바꾸는 것이 아니다. 이미 `us_3m_tbill` 경로로 resolve한 값을 project cache처럼 재사용하여 반복 external provider dependency를 제거한다.

Pinned 값은 source run 기간의 dynamic result와 동일하다. 다른 analysis period의 period-specific TB3MS 평균과 항상 동일하다고 주장하지 않고, project default US3M convention으로 사용한다.

## 영향

Shared `market-data` / risk-free resolution behavior가 변경되므로 Optimization과 Backtest 양쪽 regression이 필요하다. Sharpe/Sortino 등 금융 계산 공식은 변경하지 않는다.
