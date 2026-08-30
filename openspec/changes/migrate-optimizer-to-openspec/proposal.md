## Why

Optimizer 1차 개발이 완료되어 현재 behavior가 안정된 baseline을 형성했다. Backtest는 data, portfolio simulation, analytics, report/viewer를 가능한 한 공유할 예정이므로, 공통 capability 변경이 기존 Optimization에 미치는 영향을 OpenSpec에서 함께 관리할 수 있도록 지금 baseline을 이관한다.

## What Changes

- 기존 optimizer 요구사항을 product capability와 shared capability로 분리해 `openspec/specs/`로 이관한다.
- 이관 자체는 product behavior를 변경하지 않는다.
- Optimization과 Backtest는 별도 product capability로 관리한다.
- 공통 계산/데이터/표현 규칙은 shared capability에 한 번만 정의한다.
- shared capability 변경 시 영향을 받는 product capability와 affected regression 범위를 명시한다.
- 이관 완료 후 OpenSpec spec이 normative requirement source가 되고, 동일 요구를 담은 기존 `docs/` specification 문서는 reference/설명 역할로 전환한다.

## Target Capabilities

### Product

- `portfolio-optimization`
- `portfolio-backtest` (신규 Backtest change에서 정의)

### Shared

- `market-data`
- `portfolio-simulation`
- `portfolio-analytics`
- `run-artifacts`
- `research-report`

## Migration Rule

- 기존 요구를 의미 변경 없이 capability별로 이동한다.
- 구현 디렉터리 구조를 그대로 spec 구조로 복제하지 않는다.
- 동일 공식이나 acceptance rule을 Optimization과 Backtest spec에 중복 작성하지 않는다.
- migration parity가 확인되기 전까지 기존 `docs/` contract를 삭제하지 않는다.

## Impact

- 이번 change는 requirement ownership과 source-of-truth 구조만 변경한다.
- runtime, calculation, UI behavior 변경은 이 change의 범위가 아니다.
- migration 완료 후 `bt-module` change가 shared capability를 수정하면 Optimization regression 영향 검토가 필수다.
