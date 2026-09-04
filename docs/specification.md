# Portfolio Optimizer Specification — Migrated to OpenSpec

> Status: compatibility pointer. This file is no longer the canonical finance/product specification.

2026-09-04 기준으로 이 문서가 소유하던 금융 계산, Optimization, historical analytics, canonical result와 run-artifact 요구사항은 `openspec/specs/`의 capability spec으로 마이그레이션되었다.

새 requirement를 추가하거나 기존 product/calculation behavior를 변경할 때 이 파일을 직접 확장하지 않는다. Canonical requirement는 owning OpenSpec capability를 변경하고, 필요한 경우 `openspec/changes/<change>/`에서 delta를 정의한다.

## Canonical capability map

| 기존 `docs/specification.md` 영역 | Canonical OpenSpec |
| --- | --- |
| Optimization scope / canonical Optimization input / constraints / objectives / Efficient Frontier | `openspec/specs/portfolio-optimization/spec.md` |
| Market data / analysis-period observation semantics / common coverage / FX / risk-free | `openspec/specs/market-data/spec.md` |
| Historical portfolio path / monthly-yearly rebalancing / benchmark path / normalized wealth baseline | `openspec/specs/portfolio-simulation/spec.md` |
| Expected return / covariance / volatility / performance / trailing / active return / Up-Down / drawdown / correlations / return-risk decomposition / rolling returns | `openspec/specs/portfolio-analytics/spec.md` |
| Canonical `result.json` / `input.yaml` / raw-review artifacts / run immutability | `openspec/specs/run-artifacts/spec.md` |
| Canonical-result vs presentation responsibility boundary | `openspec/specs/research-report/spec.md` |

## Backtest change

Backtest는 현재 `openspec/changes/bt-module/`에서 기존 baseline에 대한 product/shared delta로 정의한다.

특히 다음은 baseline document가 아니라 bt-module change spec이 소유한다.

- independent Backtest product behavior
- named multi-portfolio collection과 v1 comparison policy
- Backtest Time Period / initial balance / Calendar Aligned / expanded rebalancing semantics
- Backtest-specific canonical/result/report applicability
- Research Frontend product-intent routing과 explicit `product_mode`
- product-mode 기반 LLM analysis branch
- Backtest constituent-only monthly correlation scope

`bt-module`이 main에 통합되고 OpenSpec change가 archive/sync될 때 해당 delta는 canonical `openspec/specs/`에 반영한다.

## Remaining migration baselines

이번 마이그레이션은 기존 `docs/specification.md`가 소유하던 영역을 대상으로 한다. 아래 문서는 자신의 capability가 OpenSpec으로 완전히 마이그레이션될 때까지 해당 영역의 migration baseline으로 유지한다.

- `docs/report-ui-specification.md` — report UI / interaction semantics
- `docs/input-ui-contract.md` — input / YAML / runner / viewer behavior
- `docs/architecture.md` — architecture / responsibility boundary
- `docs/visual-acceptance-contract.md` — validation / visual acceptance procedure
- `docs/research-operation-pipeline.md` — Study / Experiment / Run operation flow
- `docs/llm-research-input-contract.md` — LLM/User input behavior
- `docs/llm-analysis-framework.md` — LLM analysis execution guide

외부 서비스, screenshot, historical golden과 third-party output은 validation/reference 자료이며 OpenSpec requirement보다 우선하지 않는다.

## Change rule

Product 또는 finance semantics를 변경할 때:

1. owning OpenSpec capability와 현재 active change를 확인한다.
2. requirement/scenario를 먼저 변경한다.
3. canonical tests를 갱신한다.
4. implementation을 갱신한다.
5. existing run/result compatibility와 affected product regression을 확인한다.
6. external reference와 다르다는 이유만으로 canonical requirement를 자동 변경하지 않는다.

이 파일을 참조하는 기존 문서/도구는 계속 동작할 수 있지만, 구체적인 finance requirement를 찾을 때는 위 capability map의 OpenSpec을 따라가야 한다.
