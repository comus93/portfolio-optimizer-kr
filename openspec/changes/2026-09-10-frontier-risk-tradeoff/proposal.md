# Proposal: Frontier Risk Trade-off Analysis

## 배경

기존 Optimization Efficient Frontier는 expected return, volatility, Sharpe와 weights를 제공하지만, frontier를 따라 이동할 때 realized drawdown의 깊이와 지속시간이 어떻게 변하는지는 보여주지 않는다.

Maximum Sharpe 하나만 선택하면 Sharpe 증가의 대가로 MDD, Time Under Water(TUW), recovery burden이 얼마나 변하는지 판단하기 어렵다.

## 목표

Efficient Frontier 각 point에 동일 historical monthly path 기준의 realized risk overlay를 계산한다.

이번 change는 sweet spot을 자동 선택하지 않는다. 먼저 100-point frontier 전체의 실제 trade-off shape를 관찰할 수 있는 계산 artifact를 만든다.

## 범위

- Frontier point별 realized ex-post Sharpe
- Maximum Drawdown
- Time Under Water percentage
- Pain Area
- Pain Index
- Maximum consecutive underwater months
- 이전 frontier point 대비 delta와, Sharpe가 증가하는 구간의 descriptive marginal cost
- `review/frontier_risk_tradeoff.csv` artifact 생성
- GitHub Actions research run에서 추가 계산 비용 측정

## 비범위

- sweet spot / knee point 자동 판정
- 새로운 optimization objective
- Sharpe/MDD/TUW/Pain의 가중합 score
- 기존 Efficient Frontier solver 변경

## Shared capability impact

changed shared capability: `portfolio-analytics`

reason: drawdown path로부터 TUW와 Pain을 계산하는 canonical formula/unit 계약이 필요하다.

affected product capability: `portfolio-optimization`

required affected regression: 기존 Efficient Frontier와 Optimization 결과는 변경하지 않고, 동일 monthly return path에서 risk overlay만 추가됨을 검증한다. Backtest product behavior는 이번 change에서 변경하지 않는다.
