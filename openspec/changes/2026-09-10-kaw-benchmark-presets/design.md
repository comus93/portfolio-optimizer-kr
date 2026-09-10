# Design — KAW benchmark presets

## 결정

1. KAW preset은 Research Frontend shortcut이다. 실행 전 실제 asset rows와 portfolio benchmark weights로 materialize한다.
2. Backtest model은 기존 single-asset `benchmark`를 유지하고 별도 `benchmark_portfolio`를 추가한다. Optimization contract는 변경하지 않는다.
3. Composite benchmark path는 기존 `build_portfolio_path()`를 재사용해 생성한다. 별도 finance 계산 로직을 만들지 않는다.
4. Benchmark portfolio constituent는 `assets` union에 포함되어 기존 FDR/FX/common-alignment 경로를 그대로 탄다.
5. `benchmark: kaw_short|kaw_native|kaw_long|kaw_core`는 controlled research와 direct YAML run 모두 동일하게 materialize한다.
6. persisted `input.yaml`에는 shortcut 문자열이 아니라 `type: portfolio`, canonical preset id/name, `weights_pct`, constituent assets가 남는다.
7. 기본 SPY semantics와 explicit no-benchmark semantics는 그대로 유지한다.

## Preset registry

### kaw_native

```text
133690 10
402970 10
069500 8
192090 8.5
200250 8.5
101280 5
267440 15
385560 15
GLD 20
```

### kaw_core

```text
QQQ 10
SCHD 10
EWY 8
192090 8.5
200250 8.5
EWJ 5
TLT 30
GLD 20
```

Aliases:

```text
kaw_short -> kaw_native
kaw_long  -> kaw_core
```

## Error / compatibility

- Composite benchmark weights must sum to 100%.
- Unknown benchmark constituent after materialization is invalid.
- Existing `{symbol, name, currency}` benchmark mapping remains unchanged.
- Optimization receives no KAW portfolio preset support in this change.
