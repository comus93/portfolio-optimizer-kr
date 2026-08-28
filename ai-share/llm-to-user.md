# LLM → User Durable Note

state: active
created_at: 2026-08-28
subject: Golden-source Portfolio Visualizer report mapping

## 목적

포트폴리오 최적화 엔진이 생성할 self-contained `report.html`의 표/차트 구성을 Golden Source JPG와 최대한 동일하게 재현하기 위한 매핑 결과를 보존한다.

Golden Source:

- `comus93/llm_share/projects/portfoliovisualizer/optimizations/260828_PTF_maxsharpe.jpg`
- 동일 결과의 텍스트 보존본: `260828_PTF_maxsharpe.md`

구현 원칙:

- 표/차트 종류, 배치, 순서, 제목, 축, 범례, 구성은 Golden Source를 기준으로 한다.
- 숫자와 데이터는 엔진 산출물(`result.json`, `review/*.csv` 등)에서 주입한다.
- Viewer/HTML은 금융 계산을 다시 하지 않고 presentation만 담당한다.
- 로컬 검증은 서버 없이 생성된 self-contained `report.html`을 브라우저에서 직접 연다.
- 추후 같은 결과물을 GitHub Pages에서 제공한다.

## 상태 표기

- ✅ 그대로 가능: 현재 엔진 output으로 직접 구현 가능
- 🟡 가공/필드 보강: 현재 데이터는 있으나 PV형 presentation 또는 일부 metric 보강 필요
- 🔴 엔진 output 추가 필요: 현재 run artifact만으로 Golden Source를 재현하기 어려움

## Golden Source ↔ Engine Output 매핑

| Golden Source 영역 | 형태 | 현재 엔진 소스 | 상태 | 구현 판단 |
|---|---|---|---|---|
| Results 기간 / Objective / 설명 | Header | `input.yaml`, `result.json`, `context.yaml` | ✅ | 그대로 표시 가능 |
| Provided Portfolio | 표 | `optimization_results.csv` + input | ✅ | 그대로 |
| Provided Allocation | Pie | `optimization_results.csv` | ✅ | 그대로 |
| Maximum Sharpe Portfolio | 표 | `optimization_results.csv` | ✅ | objective 이름에 맞춰 동적 제목 |
| Optimized Allocation | Pie | `optimization_results.csv` | ✅ | 그대로 |
| Performance Summary | 표 | `performance_summary.csv` + `benchmark_analytics.csv` | 🟡 | 주요 지표는 이미 있음. PV의 ex-ante Sharpe 등 일부 보강 필요 |
| Portfolio Growth | Line | 현재 직접 series 없음 | 🔴 | Provided / Optimized / Benchmark 누적 balance series 추가 필요 |
| Annual Returns | Bar | `annual_returns.csv` | ✅ | 그대로 |
| Trailing Returns | 표 | `trailing_returns.csv` | ✅ | 전용 output 존재 |
| Efficient Frontier Assets | 표 | `asset_statistics.csv` + input bounds | 🟡 | ER/Vol 등은 있음. ex-ante Sharpe와 min/max를 PV형 한 표로 조합 |
| Asset Correlations | 표/heatmap | `correlations.csv` | ✅ | asset subset 표시 가능 |
| Efficient Frontier | Scatter | `efficient_frontier.csv` + performance/asset stats | ✅ | Frontier + Provided + Optimized + Benchmark + 개별 asset 표시 가능 |
| Efficient Frontier Transition Map | stacked area/line | `efficient_frontier.csv` | ✅ | 각 frontier point의 Vol/weights가 있어 바로 구현 가능 |
| Efficient Frontier Portfolios | 표 | `efficient_frontier.csv` | ✅ | 전체 point 표시 가능 |
| Annualized Active Return | Line | `active_returns.csv` | ✅ | `annual_active_return_pct` 존재 |
| Active Return Contribution | Line + 표 | 현재 없음 | 🔴 | 자산별 cumulative active contribution series 필요 |
| Rolling Active Return / Tracking Error | Line | `active_returns.csv` | ✅ | rolling active return / tracking error 이미 존재 |
| Up vs Down Market Performance | 표 | 현재 없음 | 🔴 | benchmark up/down별 outperform/underperform 집계 필요 |
| Portfolio Metrics | 표 | `performance_summary.csv` + `benchmark_analytics.csv` | 🟡 | Sharpe/Sortino/MDD/Active Return/TE/IR 등은 있음. Beta, Alpha, R², Treynor, Calmar, M², Skewness, Excess Kurtosis, Historical VaR 등은 추가 필요 |
| Monthly Returns | 표 | `monthly_return_series.csv` 또는 `monthly_returns_calendar.csv` | ✅ | portfolio + benchmark + asset 월별 수익률 표시 가능 |
| Drawdown Chart | Area/Line | 현재 point-in-time series 없음 | 🔴 | Provided / Optimized / Benchmark의 월별 underwater/drawdown series 필요 |
| Historical Market Stress Periods | 표 | 현재 없음 | 🔴 | 사전 정의 stress period와 구간별 성과 output 필요 |
| Worst Drawdowns | 표 | `drawdowns.csv` | 🟡 | start/bottom/recovery/MDD는 있음. Golden Source의 Length / Recovery Time / Underwater Period 포맷으로 정리 필요 |
| Portfolio Asset Performance | 표 | `asset_statistics.csv` | ✅ | 현재 output이 충분히 풍부함 |
| Portfolio / Asset Correlations | 표 | `correlations.csv` | ✅ | optimized/provided/benchmark까지 포함 가능 |
| Return Decomposition | 표 | `return_decomposition.csv` | ✅ | 그대로 |
| Risk Decomposition | 표 | `risk_decomposition.csv` | ✅ | 그대로 |
| Annual Asset Returns | Chart | 현재 직접 output 없음 | 🔴 | 각 asset의 연도별 수익률 series 추가 필요 |
| Rolling Returns Summary | 표 | `rolling_returns_summary.csv` | ✅ | 그대로 |
| Rolling 3Y Returns | Line | `rolling_returns_3y.csv` | ✅ | 그대로 |
| Rolling 5Y Returns | Line | `rolling_returns_5y.csv` | ✅ | 그대로 |

## 현재 엔진에 이미 존재하는 주요 review artifacts

`runs/20260828-0002/review/` 기준:

- `active_returns.csv`
- `annual_returns.csv`
- `asset_statistics.csv`
- `benchmark_analytics.csv`
- `benchmark_summary.csv`
- `correlations.csv`
- `drawdowns.csv`
- `efficient_frontier.csv`
- `monthly_return_series.csv`
- `monthly_returns.csv`
- `monthly_returns_calendar.csv`
- `optimization_results.csv`
- `performance_summary.csv`
- `portfolio_performance.csv`
- `return_decomposition.csv`
- `risk_decomposition.csv`
- `rolling_returns_3y.csv`
- `rolling_returns_5y.csv`
- `rolling_returns_raw.csv`
- `rolling_returns_summary.csv`
- `trailing_returns.csv`

## 신규 엔진 output이 필요한 핵심 항목

Golden Source를 높은 충실도로 재현하려면 아래 6개가 핵심 추가 항목이다.

1. `portfolio_growth`
   - Provided / Optimized / Benchmark 누적 balance series

2. `drawdown_series`
   - Provided / Optimized / Benchmark 시점별 underwater %

3. `annual_asset_returns`
   - 각 자산의 연도별 수익률

4. `active_return_contribution`
   - benchmark 대비 자산별 cumulative active contribution

5. `up_down_market_performance`
   - Benchmark 상승/하락월별 outperform / underperform 통계

6. `stress_periods`
   - COVID 등 사전 정의 market stress period별 portfolio / benchmark 성과

추가로 `portfolio_metrics`는 현재 metric과 benchmark analytics를 기반으로 하되, Golden Source 수준을 목표로 한다면 Beta, Alpha, R², Treynor, Calmar, M², Skewness, Excess Kurtosis, Historical VaR 등의 계산/출력이 필요하다.

## Frontier 관련 판단

Golden Source의 핵심 두 시각화는 현재 `efficient_frontier.csv`만으로 구현 가능하다.

### Efficient Frontier

- X: Standard Deviation / Volatility
- Y: Expected Return
- Efficient Frontier curve/points
- Provided Portfolio marker
- Optimized / Maximum Sharpe marker
- Benchmark marker
- 개별 asset marker

### Efficient Frontier Transition Map

- X: Standard Deviation / Volatility
- Y: Allocation %
- 각 asset의 frontier weight trajectory
- Golden Source와 동일하게 위험 증가에 따른 자산 비중 변화를 시각화

이 부분은 `docs/llm-analysis-framework.md`의 핵심 분석 방식과 직접 연결된다. 사용자는 차트를 보며 LLM이 설명하는 자산의 등장/퇴출, binding constraint, 대체 관계, risk range를 동시에 확인할 수 있다.

## 구현 방향 확정 사항

- Viewer는 새로운 자체 대시보드 디자인보다 Golden Source JPG 복제를 목표로 한다.
- 로컬에서는 별도 서버를 띄우지 않는다.
- 각 run에 self-contained `report.html`을 생성한다.
- HTML은 엔진 결과를 다시 계산하지 않는다.
- 동일 report/view를 추후 GitHub Pages에서 제공한다.

## 다음 사용자 판정 필요 사항

현재 🔴 항목 6개를 Golden Source 1차 구현에 모두 포함할지, 일부를 2차로 미룰지 결정한다.

특히 Golden Source 복제 완성도에 직접적인 항목은 다음이다.

- Portfolio Growth
- Drawdown Chart
- Annual Asset Returns
- Active Return Contribution
- Up vs Down Market Performance
- Historical Market Stress Periods

사용자 판정 후 엔진 output 확장 범위와 HTML 구현 scope를 확정한다.
