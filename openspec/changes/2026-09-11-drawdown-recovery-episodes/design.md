# Design: Drawdown Recovery Episodes

## Canonical episode timing

기존 `start`, `bottom`, `recovery`, `maximum_drawdown`, `duration_months`는 호환성을 위해 유지한다. 새 timing field는 calendar-month distance로 계산한다.

```text
month_delta(a,b) = (year_b-year_a)*12 + (month_b-month_a)
decline_months   = month_delta(start,bottom) + 1
recovery_months  = month_delta(bottom,recovery)
underwater_months= month_delta(start,recovery) + 1
```

`recovery`가 없는 ongoing episode는 `recovery_months`와 annualized recovery rate를 unavailable로 유지한다. `underwater_months`는 latest available observation까지 계산한다.

`duration_months`는 기존 artifact 호환을 위해 유지하며, 신규 분석에서는 의미가 명시된 `underwater_months`를 사용한다.

## Recovery Rate

Bottom drawdown을 `d < 0`, Bottom에서 이전 peak 회복까지 calendar month 수를 `m > 0`이라 하면:

```text
required_recovery_factor = 1 / (1 + d)
annualized_recovery_rate = required_recovery_factor^(12/m) - 1
```

이 값은 Bottom 이후 이전 peak까지의 복리 연환산 회복률이다. `m`이 없거나 0이면 unavailable이다.

## Recovery Progress

각 episode의 Bottom 이후 monthly drawdown path에 대해:

```text
progress_t = (drawdown_t - drawdown_bottom) / (0 - drawdown_bottom) * 100
```

- Bottom = 0%
- 이전 peak 회복 = 100%
- ongoing episode는 latest observation까지만 보존한다.
- `month_since_bottom`은 calendar-month distance다.

Canonical artifact는 최소 `portfolio`, `rank`, `date`, `month_since_bottom`, `recovery_progress_pct`, `drawdown_pct`, `recovered`를 보존한다.

## Presentation

기존 shared Drawdowns component를 재사용한다. Browser는 recovery formula를 다시 계산하지 않는다.

- drawdown path는 portfolio별 반복 chart가 아니라 한 개의 shared overlay chart로 렌더링한다.
- chart foreground selector는 line emphasis에만 사용한다. 선택 state가 summary/table visibility를 바꾸지 않는다.
- non-selected context line도 실제 비교가 가능하도록 충분한 opacity와 stroke width를 유지한다.
- Drawdown comparison에서만 색 순서는 `blue -> green -> orange`를 사용한다. Optimization에서는 `Provided -> Optimized -> Benchmark` identity 순서와 일치시킨다.
- overlay chart 바로 아래에 모든 portfolio의 `탄성회복도`를 한 table로 나열한다. 값은 canonical `Normalized Underwater Duration` summary를 그대로 소비한다.
- 그 아래 episode table은 portfolio마다 모두 렌더링하고 Optimization에서는 `Provided -> Optimized -> Benchmark` 순서로 고정한다.
- episode table은 기존 PV-style recovery columns와 `Recovery Rate`를 유지한다.
- `Recovery Progress from Bottom` chart는 user-facing report에서 표시하지 않는다.

## Validation

- synthetic episode에서 timing, recovery rate, progress path를 독립 검증한다.
- Optimization/Backtest 양쪽에서 recovery artifact가 생성되는지 확인한다.
- shared report component가 canonical episode/resilience value를 소비하는지 확인한다.
- browser contract에서 단일 overlay chart, blue/green/orange order, context-line visibility, 모든 resilience row 및 episode table 상시 노출을 확인한다.
- 대표 Optimization run을 재생성해 user-facing 결과를 검토한다.
