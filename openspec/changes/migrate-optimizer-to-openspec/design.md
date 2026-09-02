## Context

이 change의 목적은 기존 Optimization 제품 behavior를 바꾸는 것이 아니라, 현재 여러 `docs/*.md`에 분산된 내부 contract를 capability별 OpenSpec으로 이관하는 것이다.

이관 기준은 `docs/specification.md` 하나가 아니다. 기존 내부 설계와 UI/runner/viewer contract까지 함께 parity를 확인한다.

## Legacy Contract Baseline

이관 시 다음 문서를 역할별 baseline으로 사용한다.

```text
Finance / calculation behavior   docs/specification.md
Report UI / interaction          docs/report-ui-specification.md
Input / YAML / runner / viewer   docs/input-ui-contract.md
Architecture / responsibility    docs/architecture.md
Validation procedure             docs/visual-acceptance-contract.md
```

`docs/report-visual-overrides-20260829.md` 같은 correction/history 문서는 현재 내부 contract와 일치하는 항목을 확인하는 보조자료로만 사용한다. 충돌 시 현재 canonical internal contract를 우선한다.

Portfolio Visualizer, screenshot, historical golden은 외부 reference이며 migration parity source가 아니다.

## Capability Mapping

### `portfolio-optimization`

주요 source:

- `docs/specification.md`의 optimizer input, ex-ante statistics, constraints, objectives, efficient frontier
- `docs/input-ui-contract.md`의 optimization input surface 중 product-specific field

여기에는 Optimization에서만 필요한 expected return/covariance/expected volatility/ex-ante Sharpe, min/max constraints, objective, frontier behavior를 둔다.

### `market-data`

주요 source:

- `docs/specification.md`의 FDR, FX, period, month-end return, coverage, RF semantics
- `docs/architecture.md`의 data normalization responsibility

가격 수집과 normalization 의미는 product별로 중복 정의하지 않는다.

### `portfolio-simulation`

주요 source:

- `docs/specification.md`의 target weights, monthly/yearly rebalancing, drift, historical path semantics
- `docs/architecture.md`의 portfolio layer responsibility

Optimization이 만든 weights와 사용자가 제공한 weights는 simulation 진입 이후 같은 convention을 사용한다.

### `portfolio-analytics`

주요 source:

- `docs/specification.md`의 realized performance, active analytics, rolling, correlation, decomposition
- `docs/architecture.md`의 analytics source-of-truth boundary

Browser/viewer가 동일 metric을 별도 convention으로 재계산하지 않는다.

### `run-artifacts`

주요 source:

- `docs/input-ui-contract.md`
- `docs/architecture.md` persistence architecture

보존할 핵심 contract:

- CLI/UI/Agent가 동일 YAML run contract를 사용
- UI는 별도 실행경로를 만들지 않고 canonical YAML runner로 수렴
- 실제 input YAML 보존
- `result.json` canonical source of truth
- `raw/` full precision, `review/` human/LLM orientation
- UI와 Viewer는 논리적으로 독립
- 기존 persisted run은 optimizer를 다시 실행하지 않고 열 수 있음
- Viewer는 finance metric을 재계산하지 않음

### `research-report`

주요 source:

- `docs/report-ui-specification.md`
- `docs/visual-acceptance-contract.md` 중 observable report semantic checks

보존할 핵심 contract:

- human-readable portfolio/benchmark/asset identity
- Name + Ticker identity where available
- %, ratio, currency, date unit semantics
- missing != zero, unavailable은 `N/A`
- semantic axis, meaningful tooltip, identity-preserving series
- required table columns/metrics 보존
- desktop/mobile에서 information meaning 보존
- color만으로 identity를 전달하지 않음
- optimization-only Efficient Frontier sections와 shared historical sections의 applicability 분리
- browser는 persisted canonical finance value를 재계산하지 않음

검증 절차 자체는 capability requirement와 섞지 않고 tasks/verification에서 `docs/visual-acceptance-contract.md` parity를 확인한다.

## Architecture Preservation

현재 architecture의 책임 경계를 유지한다.

```text
CLI / UI / Research Control
        -> YAML Runner
        -> canonical request model
        -> pipeline
        -> data / stats / optimize / portfolio / analytics
        -> canonical result / raw / review
        -> viewer / report
```

OpenSpec 이관은 이 구조를 새로운 parallel architecture로 교체하지 않는다.

특히 다음을 유지한다.

- core analytics는 browser DOM, GitHub message, study control을 알지 않는다.
- finance calculation은 Python runtime이 담당한다.
- browser/viewer는 presentation-only transform만 수행한다.
- persisted artifact를 viewer가 독립적으로 열 수 있다.
- optimizer-specific ex-ante layer와 realized historical analytics layer를 구분한다.

## Migration Rule

1. capability별 delta spec을 작성한다.
2. `docs/specification.md`뿐 아니라 해당 capability와 관련된 UI/interaction/input/architecture contract를 함께 parity-check한다.
3. 구현 behavior는 이 migration change에서 변경하지 않는다.
4. parity가 확인된 capability만 `openspec/specs/<capability>/`를 normative source로 전환한다.
5. 전환 후 기존 docs는 reference로 유지하되 dual normative source로 남기지 않는다.

## Known Boundary

`docs/architecture.md`의 CVXPY, OSQP, CLARABEL, renderer layering 같은 implementation detail은 observable product behavior가 아니므로 capability spec에 억지로 넣지 않는다. 유지할 가치가 있는 architecture constraint는 이 design 또는 architecture reference에서 관리한다.

반대로 `docs/report-ui-specification.md`의 identity, unit, N/A, axis, tooltip, required information 같은 사용자 관찰 가능 behavior는 `research-report` capability requirement로 이관한다.
