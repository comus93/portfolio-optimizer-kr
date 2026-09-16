# Change: Fit Asset-Year Influence to report width

## Why

현재 Asset-Year Influence는 generic LOYO matrix의 `max-content` / minimum-column-width 규칙을 상속해 8개 자산에서도 desktop report section 폭을 초과하고 horizontal scrollbar가 생긴다. 이 표는 각 asset cell이 단일 짧은 숫자이므로 자연폭을 우선할 필요가 없고, 사용자는 한 화면에서 연도별 패턴을 가로로 비교할 수 있어야 한다.

## What Changes

- Asset-Year Influence에만 `width: 100%` + fixed table layout을 적용한다.
- Year column은 compact fixed width, Metric column은 읽을 수 있는 fixed width로 유지한다.
- Metric label은 한 줄을 유지하고 wrap하지 않는다.
- 나머지 가로 폭은 asset columns가 균등하게 나눠 가진다.
- 기존 Name/Ticker 2-line header와 Name ellipsis, numeric heatmap, year zebra banding은 유지한다.
- LOYO Summary와 Allocation Changes의 기존 overflow 정책은 변경하지 않는다.
- finance calculation, persisted artifact, LOYO semantics는 변경하지 않는다.

## Validation

- 기존 LOYO regression을 통과해야 한다.
- regenerated `20260914-0003/report.html`에 Asset-Year Influence 전용 fixed-layout CSS가 포함되어야 한다.
- generic `loyo-matrix` / Allocation Changes의 width semantics는 그대로 유지되어야 한다.
