# Proposal — Run navigation summaries

## 목적

`runs/<run_id>/`의 숫자형 ID만으로는 사람이거나 LLM이 repository를 탐색할 때 어떤 연구 결과인지 식별하기 어렵다.

Persisted run에 canonical artifact에서 파생된 짧은 navigation summary를 제공하고, `runs/README.md`에서 전체 run을 한 번에 탐색할 수 있게 한다.

## 변경 범위

- `run-artifacts`: 각 persisted run에 구조화된 `README.md`를 생성한다.
- `run-artifacts`: `runs/README.md` aggregate catalog를 생성/갱신한다.
- summary는 `input.yaml`, `context.yaml`, `result.json`, `review/` 등 기존 artifact에서 파생한다.
- 개별 README 형식은 Metadata, Purpose, Portfolios, Key Results, Notes, Artifacts 순서를 기본 계약으로 사용한다.
- aggregate catalog는 Run, Product, Study / Experiment, Period, Benchmark, Summary를 제공한다.

## Source of truth

Run README와 aggregate catalog는 discovery/navigation projection이다. 금융 결과와 실행 조건의 canonical source of truth는 기존 `input.yaml`, `context.yaml`, `result.json` 및 raw artifact 계약을 유지한다.

## 영향

- changed shared capability: `run-artifacts`
- affected products: `portfolio-optimization`, `portfolio-backtest`
- finance calculation semantics: 변경 없음
- required regression: 두 product 형식의 run summary 생성, aggregate index 생성, canonical artifact 불변성
