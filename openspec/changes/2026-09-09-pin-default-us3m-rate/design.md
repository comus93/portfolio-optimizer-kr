# Design

## Decision

Pinned RF default는 shared finance formula나 raw YAML parser default가 아니라 **Research Frontend default materialization**에서 적용한다.

기존 `research.py::_apply_research_defaults()`는 benchmark, initial balance, time period, rebalancing, portfolio name 등 사용자가 생략한 research default를 effective input에 명시하는 boundary다. RF도 같은 boundary에서 처리한다.

사용자가 RF를 언급하지 않으면 다음 값을 effective Experiment/Run input에 삽입한다.

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

Provenance:

```text
runs/20260908-0002/result.json
source requested_mode = us_3m_tbill
effective annual rate = 0.038394827586206895
source period = 2021-11-01 ~ 2026-08-31
```

## Why `fixed` representation

이 값은 임의 fixed-rate assumption이 아니라 이전 `us_3m_tbill` resolution의 persisted result다. 이미 resolve된 숫자를 다시 provider에서 가져오지 않기 위해 executable input에는 `fixed`로 저장한다.

이렇게 하면:

- `input.yaml` 자체가 effective RF를 완전히 보존한다.
- 반복 research run이 deterministic하다.
- FDR/FRED TB3MS 상태에 영향을 받지 않는다.
- explicit `us_3m_tbill`의 기존 period-specific dynamic semantics를 깨지 않는다.

## Resolution order

```text
사용자 RF 미지정
-> fixed 3.8394827586206895%

사용자 custom fixed 지정
-> 사용자 값

사용자 us_3m_tbill 명시
-> 기존 dynamic provider behavior
```

## Affected capabilities

- `research-input`: default RF materialization 추가.
- `research-execution`: effective input persistence로 동일 값 보존.
- `portfolio-optimization`: 생성된 fixed RF를 기존 계산 경로로 소비.
- `portfolio-backtest`: 생성된 fixed RF를 기존 계산 경로로 소비.
- `market-data`: mode semantics와 provider code는 변경하지 않는다.

## Verification

- RF 미지정 Optimization research run의 persisted `input.yaml`에 fixed 3.8394827586206895%가 존재한다.
- RF 미지정 Backtest research run도 동일하다.
- 두 default run은 TB3MS economic-series provider 없이 실행된다.
- explicit custom fixed RF는 보존된다.
- explicit `us_3m_tbill`은 변경 없이 보존된다.
- existing fixed-mode execution regression과 신규 research-default tests를 통과한다.
