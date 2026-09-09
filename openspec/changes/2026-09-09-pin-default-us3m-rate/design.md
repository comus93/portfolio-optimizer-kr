# Design

## Decision

기존 default mode `us_3m_tbill`을 유지하되 normal research execution에서는 FDR/FRED `TB3MS`를 매 run마다 다시 조회하지 않는다.

Runner는 별도 annual RF override가 없으면 다음 pinned effective value를 사용한다.

```text
PINNED_US_3M_TBILL_ANNUAL_RATE = 0.038394827586206895
```

Provenance:

```text
runs/20260908-0002/result.json
requested_mode = us_3m_tbill
source period = 2021-11-01 ~ 2026-08-31
```

## Resolution order

```text
risk_free.mode == fixed
-> existing fixed-rate behavior

risk_free.mode == us_3m_tbill + explicit runtime annual_rf override
-> supplied override

risk_free.mode == us_3m_tbill + no override
-> pinned cached value 0.038394827586206895
```

Default `us_3m_tbill` path에서는 economic-series provider를 호출하지 않는다.

## Why keep the mode name

Pinned 값은 임의 fixed-rate assumption이 아니라 실제 `us_3m_tbill` resolution의 persisted result다. 따라서 사용자-facing default와 result metadata에서 `requested_mode: us_3m_tbill`을 유지하고, effective annual rate를 별도로 기록하는 기존 contract가 가장 정확하다.

`fixed`는 사용자가 custom rate를 의도적으로 지정하는 경우와 구분한다.

## Refresh boundary

이번 change는 매 run마다 provider를 다시 조회하는 refresh behavior를 제공하지 않는다. 향후 pinned US3M 값을 갱신할 필요가 생기면 별도 maintenance/refresh workflow로 다룬다.

Pinned 값은 source period에서 dynamic result와 동일하다. 다른 analysis period의 period-specific TB3MS 평균과 동일하다는 의미는 아니다.

## Affected capabilities

- `market-data`: `us_3m_tbill` default resolution이 cached value로 변경된다.
- `portfolio-optimization`: 동일 effective RF를 소비한다.
- `portfolio-backtest`: 동일 effective RF를 소비한다.
- `run-artifacts`: requested mode와 effective annual rate를 구분하는 기존 metadata contract를 유지한다.

## Verification

- RF 미지정 Optimization run은 `us_3m_tbill` mode를 유지하고 annual RF 0.038394827586206895를 analyzer에 공급한다.
- RF 미지정 Backtest도 동일하다.
- explicit `us_3m_tbill`도 같은 cached value를 사용한다.
- default/cached path에서 `load_economic_series()`가 호출되지 않는다.
- explicit custom `fixed` behavior는 변경되지 않는다.
- Optimization과 Backtest affected regression을 확인한다.
