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

## Ownership Decisions

- `market-data`는 FDR, FX, coverage/alignment, return observation 생성과 risk-free rate 입력/정규화를 소유한다.
- Risk-free rate의 `us_3m_tbill`, `fixed`, effective annual rate 규칙은 `market-data`에 한 번만 정의하고 Optimization과 Analytics가 이를 사용한다.
- `portfolio-simulation`은 target weights, rebalance schedule, weight drift, historical portfolio return path를 소유한다.
- `portfolio-analytics`는 realized/historical analytics 전부를 공통으로 소유한다. CAGR, realized volatility, MDD, ex-post Sharpe/Sortino, trailing/rolling returns, benchmark-relative analytics, drawdown, correlation, return/risk decomposition 등이 포함된다.
- Optimization의 현재 ex-ante 계산인 expected return, covariance, expected portfolio volatility, ex-ante Sharpe는 당장은 `portfolio-optimization`에 둔다. Backtest 구현 중 동일 의미의 로직이 필요해지면 중복 구현하지 않고 공통 capability로 분리한다.
- `research-report`는 하나의 shared capability로 관리하고 section별로 optimization-only, shared, backtest-only 적용 대상을 구분한다.
- `run-artifacts`는 canonical result와 run artifact 의미 및 저장 계약을 소유한다.

## Migration Rule

- 기존 요구를 의미 변경 없이 capability별로 이동한다.
- 구현 디렉터리 구조를 그대로 spec 구조로 복제하지 않는다.
- 동일 공식이나 acceptance rule을 Optimization과 Backtest spec에 중복 작성하지 않는다.
- migration parity가 확인되기 전까지 기존 `docs/` contract를 삭제하지 않는다.
- migration 완료 후 기존 specification 문서는 reference로 유지하고 normative requirement는 `openspec/specs/`가 소유한다.

## Impact

- 이번 change는 requirement ownership과 source-of-truth 구조만 변경한다.
- runtime, calculation, UI behavior 변경은 이 change의 범위가 아니다.
- migration 완료 후 `bt-module` change가 shared capability를 수정하면 Optimization regression 영향 검토가 필수다.
