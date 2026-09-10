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

Pain Index는 전체 observation을 denominator로 사용한다. 따라서 사람이 읽는 의미는 "전체 투자기간 동안 전고점보다 평균적으로 얼마나 아래에 있었는가"이다. TUW는 duration-only metric이고 Pain Index는 depth-duration combined metric이다. MDD는 peak loss depth tail metric이다. 세 metric은 서로 대체하지 않는다.

## Pain Ratio

Pain Ratio는 CAGR 축의 drawdown-efficiency 보조지표로 사용한다.

```text
Pain Ratio = (CAGR - annual risk-free rate) / Pain Index(decimal)
```

사람이 읽는 설명은 다음으로 고정한다.

```text
전고점 아래에서 겪은 낙폭 부담 1단위당 최종적으로 얼마의 연환산 초과수익을 얻었는가
(낙폭 부담은 하락의 깊이와 지속기간을 함께 반영)
```

Pain Index와 CAGR을 다시 하나의 목적함수로 합치기 위한 점수가 아니라, 동일 frontier point의 realized return/drawdown 효율을 설명하는 지표다.

## Monthly Gain-to-Pain Ratio

Schwager-style monthly definition을 사용한다.

```text
Monthly GPR = sum(all monthly returns)
            / abs(sum(losing-month returns))
```

분자는 positive months만의 합이 아니라 전체 monthly return의 arithmetic sum이다. frequency 의존성이 있으므로 report label은 항상 `Monthly Gain-to-Pain`으로 표현한다.

사람이 읽는 설명은 다음으로 고정한다.

```text
손실이 난 달들의 총 손실 1단위당, 최종적으로 얼마의 순수익을 남겼는가
```

이 지표는 손실월 총량에 대한 순수익 효율을 보여주며 Pain Index와 같은 primary reporting level에서 제공한다. Pain Index가 equity-path burden을 본다면 Monthly GPR은 losing-month return burden을 본다.

## Sharpe 기준

Efficient Frontier의 `sharpe`는 기존 ex-ante statistic으로 보존한다.

Drawdown/TUW/Pain은 realized path metric이므로 marginal trade-off의 Sharpe axis는 동일 realized path에서 계산한 ex-post Sharpe를 사용한다. Ex-ante와 ex-post Sharpe를 동일 field로 합치지 않는다.

## Artifacts

다음 artifact를 생성한다.

```text
runs/<run_id>/review/frontier_risk_tradeoff.csv
runs/<run_id>/review/frontier_interactive.json
```

CSV는 100 frontier points 각각의 raw metrics와 이전 point 대비 deltas를 저장한다.

JSON은 정적 report에서 point를 즉시 전환하기 위한 compact columnar backdata다. 다음을 저장한다.

```text
dates[T]
points[P]
symbols[N]
weights_pct[P][N]
monthly_returns_pct[P][T]
drawdown_pct[P][T]
metrics[key][P]
```

Browser는 finance metric을 다시 계산하지 않는다. canonical drawdown path까지 Python analyzer에서 생성해 저장하고, browser는 selected point의 persisted series를 선택하여 좌표 변환과 표시만 수행한다.

## Static interactive report

`report.html`은 이미 client-side JavaScript와 embedded JSON을 사용하는 정적 문서다. Frontier analyzer가 report 생성 후 interactive payload와 dashboard section을 주입한다.

Dashboard는 다음 8개 primary metric의 frontier shape를 small-multiple chart로 보여준다.

- CAGR
- Sharpe Ratio
- Monthly Gain-to-Pain
- Pain Ratio
- Maximum Drawdown
- Time Under Water
- Pain Index
- Max Underwater

사용자가 어떤 chart에서 point를 클릭해도 하나의 selected point state를 공유하며 8개 chart marker, selected point metrics, asset weights와 drawdown path가 함께 갱신된다.

초기 selected point는 realized Maximum Sharpe point로 두되 이를 sweet spot 추천으로 표현하지 않는다.

### Metric card 설명

```text
CAGR
연복리 수익률 (%)

Sharpe Ratio
샤프지수

Monthly Gain-to-Pain
손실이 난 달들의 총 손실 1단위당, 최종적으로 얼마의 순수익을 남겼는가

Pain Ratio
전고점 아래에서 겪은 낙폭 부담 1단위당 최종적으로 얼마의 연환산 초과수익을 얻었는가
(낙폭 부담은 하락의 깊이와 지속기간을 함께 반영)

Maximum Drawdown
낙폭 (%)

Time Under Water
이전 최고점을 회복하지 못하는 기간(물려있는 기간)

Pain Index
평균 낙폭 (깊이와 지속시간 반영)

Max Underwater
최장 미회복 기간 (개월)
```

### Chart axis

8개 metric chart는 같은 semantic X축을 사용한다.

```text
X = Annualized Volatility %
```

각 point의 실제 `volatility_pct`를 X coordinate로 사용하며 point index를 균등 간격 X coordinate로 사용하지 않는다. Y축은 각 metric의 실제 값/단위다.

각 chart는 X/Y numeric tick, axis title, selected point line+dot를 표시한다. Hover/tap tooltip은 최소 `Frontier Point`, `연환산 변동성`, 해당 metric value를 보여준다. Y domain은 실제 frontier range에 작은 여백을 더해 curve shape를 읽기 쉽게 하고 0 시작을 강제하지 않는다.

Selected Point Drawdown chart도 X축 기간, Y축 낙폭(%) scale과 title을 제공한다.

## Performance

추가 분석은 market-data fetch와 solver를 반복하지 않는다. 이미 생성된 `efficient_frontier.csv`와 `monthly_return_series.csv`만 읽는다.

100 points × 약 100~200 monthly observations 규모에서는 portfolio-path 및 drawdown scan이 작은 O(points × months × assets) 계산이다. JSON에 canonical drawdown matrix를 추가해도 현재 100×108 monthly 규모는 정적 GitHub Pages report에서 수백 KB 추가 수준으로 예상하며 actual run에서 확인한다.

GitHub Actions에서 analyzer elapsed time, generated JSON size, final report size를 실제 run으로 확인한다.

## 후속 단계

실제 interactive trade-off curves를 관찰한 뒤에만 다음을 결정한다.

- local delta smoothing 필요 여부
- fixed Sharpe/CAGR increment interpolation 필요 여부
- Pareto filtering
- knee-point detection
- Ulcer Index / CDaR 같은 추가 downside metrics

이번 change에서는 자동 sweet-spot rule을 정의하지 않는다.
