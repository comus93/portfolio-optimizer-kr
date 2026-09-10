# Design

## 계산 기준

Frontier 생성 자체는 기존 `build_efficient_frontier()` 결과를 그대로 사용한다. Risk overlay는 solver를 다시 호출하지 않고 persisted frontier weights와 동일 run의 canonical monthly asset-return series를 재사용한다.

각 frontier point의 target weights로 기존 portfolio path semantics를 적용해 realized monthly portfolio return path를 만든다. 따라서 monthly 외의 rebalancing 설정도 기존 `build_portfolio_path()` convention을 재사용한다.

## Pain 정의

`Pain Area`는 drawdown curve 아래의 discrete monthly 면적이다.

```text
U_t = max(0, -DD_t)
Pain Area = sum(U_t) * 100            [%·month]
Pain Index = mean(U_t) * 100          [%]
```

Pain Index는 전체 observation을 denominator로 사용한다. 따라서 depth와 duration을 함께 반영하면서 sample length에 정규화된다.

TUW는 duration-only metric이고 Pain Index는 depth-duration combined metric이다. MDD는 peak loss depth tail metric이다. 세 metric은 서로 대체하지 않는다.

## Sharpe 기준

Efficient Frontier의 `sharpe`는 기존 ex-ante statistic으로 보존한다.

Drawdown/TUW/Pain은 realized path metric이므로 marginal trade-off의 Sharpe axis는 동일 realized path에서 계산한 ex-post Sharpe를 사용한다. Ex-ante와 ex-post Sharpe를 동일 field로 합치지 않는다.

## Prototype artifact

이번 단계에서는 UI 자동 선택을 만들지 않고 다음 artifact를 추가한다.

```text
runs/<run_id>/review/frontier_risk_tradeoff.csv
```

100 frontier points 각각에 raw risk metrics와 이전 point 대비 deltas를 저장한다.

## Performance

추가 분석은 market-data fetch와 solver를 반복하지 않는다. 이미 생성된 `efficient_frontier.csv`와 `monthly_return_series.csv`만 읽는다.

100 points × 약 100~200 monthly observations 규모에서는 portfolio-path 및 drawdown scan이 작은 O(points × months × assets) 계산이다. GitHub Actions에서 별도 step elapsed time을 출력해 실제 overhead를 관찰한다.

## 후속 단계

실제 trade-off curve를 관찰한 뒤에만 다음을 결정한다.

- local delta smoothing 필요 여부
- fixed Sharpe increment interpolation 필요 여부
- Pareto filtering
- knee-point detection
- report UI / chart layout

이번 change에서는 자동 sweet-spot rule을 정의하지 않는다.
