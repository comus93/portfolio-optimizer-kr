# Proposal — KAW benchmark presets

## 목적

KAW Native Proxy와 KAW Core Revised Internal이 검증된 baseline이 되었으므로, 반복되는 Backtest 연구에서 기존 `SPY` 단일 benchmark 대신 KAW를 쉽게 선택할 수 있게 한다.

## 변경 범위

- `research-input`: KAW short/long benchmark preset을 사용자-facing shortcut으로 지원하고 effective input에 완전한 종목/비중 정의를 materialize한다.
- `portfolio-backtest`: 기존 단일 asset benchmark 외에 고정 target-weight portfolio benchmark를 지원한다.
- 기존 benchmark-relative analytics 계산식은 변경하지 않고 기존 `portfolio-analytics`를 재사용한다.
- 기본 benchmark는 계속 SPY다. KAW는 explicit override일 때만 사용한다.

## 비범위

- Optimization benchmark의 composite-portfolio 지원
- Native/Core NAV stitching
- 기간에 따라 benchmark를 자동 선택하는 hidden routing
- KAW 종목/비중의 재설계

## 영향

- changed capability: `research-input`, `portfolio-backtest`
- affected shared behavior: market-data universe materialization 및 existing benchmark-relative analytics input path
- affected product: `portfolio-backtest`
- required regression: 기존 SPY benchmark, no-benchmark, KAW Native preset, KAW Core preset, persisted effective input
