# Design — Run navigation summaries

## 구조

```text
input.yaml / context.yaml / result.json / review/*
                     ↓
runs/<run_id>/README.md
                     ↓
runs/README.md
```

`README.md`와 `runs/README.md`는 canonical artifact를 읽어 재생성 가능한 projection으로 구현한다.

## 개별 Run README

고정 section 순서:

1. Metadata
2. Purpose
3. Portfolios
4. Key Results
5. Notes
6. Artifacts

Metadata는 가능한 범위에서 Run ID, Product, Study, Experiment, Period, Benchmark, Rebalancing, Currency를 표시한다. 값이 unavailable이면 임의 추론값을 만들지 않고 `N/A`를 사용한다.

Purpose는 명시적 title/purpose가 있으면 우선하고, 없으면 Study/Experiment identity와 portfolio/benchmark identity에서 deterministic하게 생성한다.

Key Results는 persisted review/canonical performance에서 product에 맞는 대표 metric만 표시한다. Summary용 formatting이 canonical precision을 변경하지 않는다.

## Aggregate catalog

`runs/README.md`는 `runs/` 아래 `result.json`을 가진 run directory를 스캔해 최신 run부터 정렬하고 다음 열을 만든다.

```text
Run | Product | Study / Experiment | Period | Benchmark | Summary
```

새 run 완료 시 catalog 전체를 deterministic하게 재생성한다. 따라서 기존 run도 별도 migration metadata 없이 catalog에 포함될 수 있다.

## 실행 경계

- report writer는 result가 생성된 시점에 개별 README의 최소 완성본을 만든다.
- canonical runner/research execution은 `input.yaml`, `context.yaml`, `report.html`이 준비된 뒤 README를 다시 materialize하고 aggregate catalog를 갱신한다.
- navigation projection 생성 실패는 finance result를 성공으로 위장하거나 canonical artifact를 변경하지 않는다.
