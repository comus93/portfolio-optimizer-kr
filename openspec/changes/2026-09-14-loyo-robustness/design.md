# Design: Leave-One-Year-Out Optimization Robustness

## Decision

LOYO는 Optimization-specific robustness layer로 구현하고 existing `solve_optimization()` shared engine을 호출한다. 별도 solver implementation을 만들지 않는다.

## Execution flow

```text
PreparedOptimizationData.monthly_returns
        + existing baseline optimization_result
        + request objective / bounds / target_volatility
        + one fixed effective annual RF
                       |
                       v
             LOYO robustness loop
                       |
          exclude calendar year y
                       |
              annualized moments
                       |
              solve_optimization()
                       |
          compare with baseline result
```

Baseline objective는 다시 solve하지 않는다. Normal Optimization이 이미 생성한 baseline result를 기준으로 사용한다.

## Scenario semantics

각 LOYO scenario는 해당 calendar year에 속하는 canonical monthly return observations를 모두 제거한다. 첫해/마지막해가 partial year여도 제거 대상이며 `removed_observations`를 함께 기록해 비교 가능성을 보존한다.

LOYO 동안 다음 설정은 baseline과 동일하게 고정한다.

- optimization objective
- min/max asset bounds
- target annual volatility
- effective annual risk-free rate

Risk-free rate를 연도별로 다시 추정하지 않는다. 제거 연도의 asset-return sample influence를 다른 설정 변화와 섞지 않기 위함이다.

## Output

Canonical result에는 `optimization_robustness.loyo`를 추가한다.

각 scenario는 최소 다음을 가진다.

- `excluded_year`
- `removed_observations`, `remaining_observations`
- feasibility/status
- optimized expected return / volatility / Sharpe
- baseline 대비 metric delta
- asset weights와 baseline 대비 weight delta
- `allocation_turnover = 0.5 * sum(abs(delta_weight))`
- largest absolute asset weight change와 해당 asset

Machine/review artifact에는 `loyo_robustness.csv`를 추가한다.

LOYO는 결과를 해석해 자동으로 `overfit=true` 같은 판정을 만들지 않는다. 사용자가 stability evidence를 inspect할 수 있는 진단 자료만 제공한다.

## Error and infeasibility handling

연도 제거 후 target-volatility가 새로운 GMV보다 낮아지거나 Maximum Sharpe가 infeasible해지는 등 canonical optimizer가 infeasible을 반환하면 해당 연도 row를 `feasible=false`로 기록한다. 이는 robustness signal이므로 전체 run failure로 승격하지 않는다.

남은 monthly observations가 covariance 계산에 부족한 경우에도 해당 scenario를 `insufficient_data`로 기록한다.

예상하지 못한 programming/runtime exception은 숨기지 않고 기존 run failure semantics를 따른다.

## Performance

연도별로 market data fetch, FX normalization, Efficient Frontier, portfolio simulation, historical analytics, benchmark analytics, HTML rendering을 반복하지 않는다.

비용은 대략 calendar-year count만큼의 annualized moment 계산과 shared objective solve로 제한한다. 현재 universe 규모에서는 별도 prefix-statistics 최적화를 도입하지 않는다.

## Affected regression

- existing Optimization objective result가 LOYO 도입 전과 동일함
- LOYO가 shared `solve_optimization()`을 사용함
- Max Sharpe / Target Volatility LOYO scenario 계산
- infeasible scenario가 전체 run을 실패시키지 않음
- raw/review artifact persistence
- Backtest result에 LOYO가 추가되지 않음
