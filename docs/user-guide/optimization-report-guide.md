---
title: Optimization Report User Guide
description: portfolio-optimizer-kr의 Optimization 결과 리포트를 읽고 해석하는 방법
tags:
  - portfolio-optimizer
  - optimization
  - report
  - user-guide
  - portfolio-analysis
  - robustness
aliases:
  - Optimization 리포트 해석 가이드
  - 최적화 결과 사용자 매뉴얼
---

# Optimization Report User Guide

이 문서는 `portfolio-optimizer-kr`의 **Optimization 결과 리포트를 읽는 방법**을 설명한다.

목적은 포트폴리오 이론을 가르치거나 투자 결론을 대신 내리는 것이 아니다. 리포트에 표시되는 각 숫자와 차트가 **무엇을 의미하고, 화면에서 어떻게 읽어야 하는지**를 빠르게 이해할 수 있도록 돕는 사용자 매뉴얼이다.

구현 및 계산 규약의 source of truth는 다음 문서다.

- Report UI: [`../report-ui-specification.md`](../report-ui-specification.md)
- Calculation / reporting conventions: [`../specification.md`](../specification.md)
- OpenSpec: `openspec/specs/`

---

## 1. 처음 볼 때의 추천 읽기 순서

리포트의 모든 항목을 처음부터 끝까지 같은 비중으로 읽을 필요는 없다. 처음에는 아래 순서로 보는 것이 가장 빠르다.

1. **Provided Portfolio / Optimized Portfolio**  
   optimizer가 기존 비중을 어떻게 바꿨는지 확인한다.
2. **Performance Summary**  
   기존 포트폴리오, 최적화 포트폴리오, Benchmark의 핵심 수익과 위험을 비교한다.
3. **Efficient Frontier**  
   Optimization 입력 기준으로 각 포트폴리오가 기대수익과 변동성 공간에서 어디에 있는지 본다.
4. **Portfolio Metrics**  
   Beta, Alpha, Calmar, VaR 등 추가 성과·위험 특성을 확인한다.
5. **Leave-One-Year-Out Robustness**  
   특정 연도를 제외했을 때 최적비중과 목적함수가 얼마나 바뀌는지 확인한다.
6. **Drawdowns / Stress Periods**  
   과거 손실 구간에서 실제 경로가 어땠는지 확인한다.
7. **Return / Risk Decomposition**  
   어떤 자산이 수익과 위험을 얼마나 구성했는지 확인한다.
8. **Rolling Returns**  
   시작 시점과 종료 시점이 달라졌을 때 장기 성과가 얼마나 달라졌는지 확인한다.

---

## 2. 리포트를 읽기 전에

리포트에는 성격이 다른 숫자가 함께 나온다. 아래 구분만 기억하면 대부분의 혼동을 줄일 수 있다.

### Historical / realized

실제 분석기간의 월간 수익률 경로에서 계산한 값이다.

예: `CAGR`, `Annualized Return`, `Maximum Drawdown`, `Sharpe Ratio (ex-post)`.

### Expected / ex-ante

Optimization에 사용된 기대수익률과 공분산 추정치에서 계산한 값이다.

예: Efficient Frontier의 `Expected Return`, `Standard Deviation`, `Sharpe Ratio`.

### Absolute

Portfolio 자체의 수익과 위험을 나타낸다.

예: CAGR, Standard Deviation, Maximum Drawdown.

### Benchmark-relative

Portfolio와 Benchmark의 차이를 나타낸다.

예: Active Return, Tracking Error, Information Ratio.

### `%`와 `%p`

`31.06%`는 비중이나 수익률 자체다.

`+25.87%p`는 두 비율 사이의 **percentage point 차이**다. 예를 들어 31.06%에서 56.93%로 바뀌면 변화는 `+25.87%p`다.

### `N/A`

계산에 필요한 관측치가 부족하거나 해당 항목이 개념적으로 적용되지 않는 경우다. `0`과 다르다.

---

## 3. Provided Portfolio / Optimized Portfolio

### 무엇인가

- **Provided Portfolio**: 사용자가 입력한 기준 포트폴리오다.
- **Optimized Portfolio**: 선택한 objective와 제약조건으로 optimizer가 계산한 결과다.

각 자산에는 보통 다음 정보가 표시된다.

| 항목 | 의미 |
|---|---|
| Allocation | 해당 포트폴리오의 자산 비중 |
| Min Weight | optimizer가 허용하는 최소 비중 |
| Max Weight | optimizer가 허용하는 최대 비중 |
| Name / Ticker | 자산 식별자 |

### 읽는 법

먼저 Provided와 Optimized의 비중 차이를 본다. 어떤 자산이 증가했고 어떤 자산이 감소했는지 확인한다.

`0%`는 optimizer 결과에서 해당 자산이 선택되지 않았다는 뜻이다. 그 자체로 자산의 절대적인 우열을 의미하지 않는다.

---

## 4. Performance Summary

Provided Portfolio, Optimized Portfolio, Benchmark를 가장 빠르게 비교하는 핵심 표다.

### 주요 항목

| Metric | 정확한 의미 | 읽는 법 |
|---|---|---|
| Start Balance | 분석 시작 시점의 기준 자산가치 | Optimization report에서는 canonical `1.0`을 화면에서 `$10,000`으로 표시한다. |
| End Balance | 월간 수익률을 복리 누적한 종료 자산가치 | 같은 Start Balance에서 어느 경로가 더 크게 성장했는지 비교한다. |
| CAGR | 전체 기간 복리 성장률을 연환산한 값 | 매년 동일한 복리 성장률로 환산하면 몇 %였는지를 뜻한다. |
| Annualized Return | 월간 수익률의 산술평균 × 12 | CAGR과 계산 방식이 다르므로 값이 같지 않을 수 있다. |
| Expected Return | Optimization 통계로 계산된 기대수익률 | Provided / Optimized는 optimization expected-return vector를 사용한다. Benchmark는 관측 월수익 평균을 연환산한다. |
| Standard Deviation | 월간 수익률 표준편차 × √12 | 연환산 변동성이다. |
| Best Year | calendar year별 복리수익률 중 최대값 | 가장 좋았던 연도의 수익률이다. |
| Worst Year | calendar year별 복리수익률 중 최소값 | 가장 나빴던 연도의 수익률이다. |
| Maximum Drawdown | 누적 자산가치가 이전 고점에서 가장 크게 하락한 비율 | `-12%`라면 분석기간 중 고점 대비 최대 약 12% 하락했다는 뜻이다. |
| Sharpe Ratio (ex-ante) | Expected Return과 Expected Volatility로 계산한 Sharpe | optimizer 입력 통계 기준 위험조정 값이다. |
| Sharpe Ratio (ex-post) | `(Annualized Return - Risk Free Rate) / Standard Deviation` | 실제 historical 월수익 경로 기준 Sharpe다. |
| Sortino Ratio | 초과수익을 downside deviation으로 나눈 값 | 전체 변동성이 아니라 기준수익률 아래의 변동만 분모에 사용한다. |
| Active Return | Portfolio 월수익률 - Benchmark 월수익률의 평균을 연환산 | Benchmark 대비 평균 초과수익이다. |
| Tracking Error | 월간 active return의 표준편차 × √12 | Benchmark와의 수익률 차이가 얼마나 흔들렸는지 나타낸다. |
| Information Ratio | `Active Return / Tracking Error` | Benchmark 대비 초과수익을 active risk로 나눈 값이다. |

### CAGR와 Annualized Return

둘 다 연 단위 숫자지만 계산 방식이 다르다.

- CAGR: 전체 누적 복리 성장률을 연환산
- Annualized Return: 월수익률 산술평균을 12배

따라서 변동성이 클수록 두 값의 차이가 커질 수 있다.

### ex-ante와 ex-post Sharpe

- `ex-ante`: optimizer가 사용한 기대수익률과 공분산 기반
- `ex-post`: 실제 분석기간에 발생한 월간 수익률 경로 기반

같은 이름의 Sharpe라도 기준 데이터가 다르므로 구분해서 읽는다.

---

## 5. Portfolio Growth

### 무엇인가

월간 수익률을 복리 누적한 자산가치 경로다.

Optimization report에서는 canonical wealth `1.0`을 `$10,000`으로 표시한다.

### 읽는 법

Provided, Optimized, Benchmark의 장기 누적 경로를 같은 시작값에서 비교한다. 특정 시점의 최종값만 보는 것이 아니라 중간에 어떤 경로로 성장하거나 하락했는지도 함께 본다.

---

## 6. Annual Returns

### 무엇인가

각 calendar year에 포함된 월간 수익률을 복리로 합산한 연도별 수익률이다.

### 읽는 법

같은 연도에서 Provided, Optimized, Benchmark가 각각 얼마의 수익률을 기록했는지 비교한다.

첫해나 마지막해가 완전한 12개월이 아니면 **실제로 포함된 월만 사용한 partial-year return**이다.

---

## 7. Trailing Returns

리포트 종료 시점을 기준으로 최근 구간의 성과를 보여준다.

| 항목 | 의미 |
|---|---|
| 3M | 최근 3개월 누적수익률 |
| YTD | 마지막 관측연도의 연초 이후 누적수익률 |
| 1Y | 최근 12개월 누적수익률 |
| 3Y annualized | 최근 36개월 누적수익률을 연환산 |
| 5Y annualized | 최근 60개월 누적수익률을 연환산 |
| 10Y annualized | 최근 120개월 누적수익률을 연환산 |
| Full Period CAGR | 전체 분석기간 CAGR |
| 3Y Annualized Volatility | 최근 36개월 월수익률 변동성을 연환산 |
| 5Y Annualized Volatility | 최근 60개월 월수익률 변동성을 연환산 |

필요한 관측치가 부족한 항목은 `N/A`다.

---

## 8. Efficient Frontier Assets

### 무엇인가

Optimization universe의 각 자산이 optimizer 통계에서 어떤 기대수익률과 변동성을 가지는지 보여준다.

| 항목 | 의미 |
|---|---|
| Expected Return | optimization에 사용하는 연환산 기대수익률 |
| Standard Deviation | optimization에 사용하는 연환산 변동성 |
| Sharpe Ratio | Expected Return과 Risk Free Rate, Standard Deviation으로 계산한 ex-ante Sharpe |
| Min Weight | 허용 최소 비중 |
| Max Weight | 허용 최대 비중 |

이 표의 값은 해당 자산의 historical CAGR 표가 아니라 **optimization statistics**다.

---

## 9. Asset Correlations

### 무엇인가

Optimization 자산들의 canonical 월간 수익률로 계산한 Pearson correlation matrix다.

### 읽는 법

- `+1`에 가까움: 두 자산의 월간 수익률이 같은 방향으로 움직이는 경향이 강했다.
- `0`에 가까움: 월간 수익률의 선형 동행관계가 약했다.
- `-1`에 가까움: 반대 방향으로 움직이는 경향이 강했다.

예를 들어 `0.15`는 해당 분석기간의 월간 수익률 기준 선형 상관계수가 0.15였다는 뜻이다.

### 주의

이 값은 현재 분석기간의 관측값이다. 미래 correlation을 의미하지 않는다.

---

## 10. Efficient Frontier

### 무엇인가

현재 자산 universe와 weight constraint 안에서 계산된 기대수익률과 변동성의 조합을 보여준다.

축은 다음과 같다.

- X축: `Annualized Standard Deviation %`
- Y축: `Expected Annual Return %`

### 화면에 표시되는 것

- Efficient Frontier curve
- 개별 자산
- Provided Portfolio
- Optimized Portfolio
- Benchmark

### 읽는 법

한 점의 위치는 해당 포트폴리오의 **ex-ante Expected Return / Standard Deviation 조합**이다.

Portfolio Growth나 CAGR처럼 실제 historical wealth path를 보여주는 차트가 아니다.

---

## 11. Efficient Frontier Transition Map

### 무엇인가

Efficient Frontier를 따라 목표 변동성이 달라질 때 자산 비중이 어떻게 변하는지 보여준다.

- X축: Annualized Standard Deviation
- Y축: Asset Allocation

각 frontier point에서 자산 비중 합은 100%다.

### 읽는 법

왼쪽에서 오른쪽으로 이동하면서 frontier volatility가 높아질 때 어떤 자산 비중이 늘고 줄어드는지 본다.

---

## 12. Efficient Frontier Portfolios

Frontier의 각 point를 숫자로 확인하는 표다.

보통 다음 정보를 포함한다.

- Point
- 자산별 Allocation
- Expected Return
- Standard Deviation
- Sharpe Ratio

Transition Map의 특정 지점을 정확한 숫자로 확인할 때 사용한다.

---

## 13. Benchmark-relative / Active Return 분석

### Active Return

월별 `Portfolio Return - Benchmark Return`의 평균을 연환산한 값이다.

양수면 분석기간 평균 기준 Benchmark보다 높은 수익률, 음수면 낮은 수익률을 의미한다.

### Tracking Error

월간 Active Return의 표준편차를 연환산한 값이다.

Portfolio와 Benchmark의 수익률 차이가 얼마나 변동했는지를 나타낸다.

### Information Ratio

`Annualized Active Return / Tracking Error`다.

### Annualized Active Return

Benchmark 대비 active return을 기간별로 비교하는 chart다. Provided와 Optimized의 benchmark-relative 성과를 구분해서 읽는다.

### Active Return Contribution

각 자산이 Portfolio와 Benchmark 사이의 수익률 차이에 얼마나 기여했는지를 누적으로 보여준다.

현재 contribution의 기본 형태는 자산 비중과 `asset return - benchmark return`의 곱을 월별로 계산해 누적한 값이다.

따라서 이 차트는 **자산 자체의 누적수익률 차트가 아니다.**

### Rolling Active Return / Tracking Error

기본 36개월 rolling window에서 다음 두 값을 함께 보여준다.

- Active Return: rolling window의 benchmark-relative return
- Tracking Error: 같은 rolling window의 active-return 변동성

두 지표는 단위는 모두 %지만 의미가 달라 별도의 Y축을 사용한다.

---

## 14. Up vs. Down Market Performance

### 무엇인가

Benchmark 상황별로 Portfolio가 Benchmark보다 위에 있었는지 아래에 있었는지를 요약한다.

표에는 다음과 같은 통계가 표시된다.

- Above Benchmark count
- Below Benchmark count
- Total
- % Above Benchmark
- Average Active Return Above
- Average Active Return Below
- Average Active Return Total

차트는 월간 관측치를 Benchmark Return 기준으로 정렬한 뒤 비슷한 구간끼리 묶어 Portfolio Return과 Benchmark Return을 비교한다.

### 읽는 법

표는 관측 횟수와 평균 active return을 보고, 차트는 Benchmark가 낮거나 높은 월 구간에서 Portfolio가 상대적으로 어떻게 움직였는지를 확인한다.

---

## 15. Portfolio Metrics

Performance Summary보다 추가적인 benchmark-relative / distribution metric을 모아 놓은 표다.

현재 주요 metric은 다음과 같다.

| Metric | 정확한 의미 | 읽는 법 |
|---|---|---|
| Alpha | 월간 초과수익과 Beta를 이용해 계산한 benchmark-relative alpha를 연환산 | `%` 단위다. Benchmark 자체는 이론상 0 부근이다. |
| Beta | `Cov(Portfolio, Benchmark) / Var(Benchmark)` | Benchmark가 1 움직일 때 Portfolio가 통계적으로 얼마나 같이 움직였는지를 나타내는 비율이다. |
| R-Squared | Portfolio와 Benchmark 월수익률 correlation의 제곱 | `0~1` 범위. Benchmark 움직임과의 선형 관계가 표본에서 어느 정도였는지 나타낸다. |
| Treynor Ratio | `(Annualized Return - Risk Free Rate) / Beta` | Beta를 분모로 사용한 위험조정 수익 지표다. |
| Calmar Ratio | **최근 36개월** CAGR / 최근 36개월 최대낙폭의 절대값 | 현재 구현은 full-period가 아니라 마지막 36개월 window를 사용한다. |
| Modigliani-Modigliani | `Risk Free Rate + Sharpe × Benchmark Volatility` | Portfolio Sharpe를 Benchmark 변동성 수준으로 환산한 연환산 수익률 표현이다. `%` 단위다. |
| Skewness | 월간 수익률 분포의 비대칭도 | 0은 대칭에 가깝고, 부호는 어느 방향 꼬리가 더 긴지를 나타낸다. |
| Excess Kurtosis | 월간 수익률 분포의 excess kurtosis | 정규분포를 0 기준으로 하는 꼬리·집중도 통계다. |
| Historical VaR 95% | 월간 수익률의 5% quantile 손실을 양수 loss 형태로 표시 | 예: `3.8%`라면 표본 월수익 분포의 하위 5% 경계가 약 `-3.8%`였다는 뜻이다. |

Portfolio Metrics는 각 metric의 정의를 읽는 표다. 하나의 숫자로 전체 포트폴리오의 우열을 결정하는 표가 아니다.

---

## 16. Leave-One-Year-Out Robustness

LOYO는 full-sample optimizer 결과가 특정 calendar year에 얼마나 민감한지 확인하는 robustness diagnostic이다.

각 excluded year마다 그 연도의 **모든 자산 월수익률을 제거**한 뒤 같은 objective, constraints, target volatility, risk-free 설정으로 다시 최적화한다.

Full-sample baseline optimization은 다시 계산하지 않고 기존 결과를 기준으로 비교한다.

### 16.1 Asset-Year Influence

각 year를 4개 metric row로 보여준다.

| Metric | 의미 |
|---|---|
| 구성자산 해당년도 수익률 | 해당 자산의 그 calendar year 수익률 |
| 전체기간 최적비중 | full-sample optimization weight |
| 해당년도 제외 최적비중 | 해당 calendar year 전체를 제외하고 다시 계산한 weight |
| 비중 변화 | `해당년도 제외 최적비중 - 전체기간 최적비중` |

예:

```text
2022 / QQQ
구성자산 해당년도 수익률   -27.82%
전체기간 최적비중           31.06%
해당년도 제외 최적비중      56.93%
비중 변화                  +25.87%p
```

이 예시는 2022년 전체를 데이터에서 제외했을 때 QQQ의 최적비중이 31.06%에서 56.93%로 바뀌었다는 뜻이다.

`+25.87%p`를 QQQ 단독의 인과효과로 해석하지 않는다. 해당 연도는 모든 자산에서 동시에 제거된다.

### 16.2 LOYO Summary

| 항목 | 의미 |
|---|---|
| Excluded Year | 제거한 calendar year |
| Δ Return | LOYO expected return - full-sample expected return |
| Δ Sharpe | LOYO Sharpe - full-sample Sharpe |
| Reallocation | `0.5 × Σ|LOYO weight - baseline weight|` |
| 1st / 2nd / 3rd Allocation Shift | 절대 비중 변화가 큰 자산 3개와 signed delta |

`Reallocation 30%`는 full-sample allocation에서 해당 LOYO allocation으로 이동하려면 전체 자본의 약 30%가 재배치되어야 한다는 뜻이다.

### 16.3 Allocation Changes

첫 row는 `Full Sample` baseline이고, 이후 각 row는 excluded year별 LOYO weight다.

예:

```text
Full Sample   31.06%
2022          56.93% (+25.87%p)
```

괄호 안 값은 baseline 대비 signed weight change다.

---

## 17. Monthly Returns

Portfolio별 calendar table이다.

- Row: Year
- Column: Jan ~ Dec, YTD

각 월 셀은 해당 월의 Portfolio return이다. `YTD`는 그 calendar year에 포함된 월수익률을 복리 누적한 값이다.

관측치가 없는 월은 `0%`가 아니라 `N/A` 또는 빈 값으로 표시된다.

---

## 18. Drawdowns

### Drawdown Chart

누적 자산가치가 직전 고점보다 얼마나 낮은지를 시간축으로 보여준다.

- `0%`: 이전 고점 수준
- `-10%`: 이전 고점 대비 10% 아래

### Worst Drawdowns

각 drawdown episode를 손실 깊이 순으로 보여준다.

| 항목 | 의미 |
|---|---|
| Rank | 최대낙폭이 큰 순서 |
| Start | 이전 고점을 이탈해 drawdown이 시작된 시점 |
| Bottom | 해당 episode에서 가장 낮은 시점 |
| Recovery | 이전 고점을 회복한 시점. 아직 회복하지 못했으면 N/A |
| Maximum Drawdown | 해당 episode의 최대 손실률 |
| Duration | episode에 포함된 기간 |
| Decline Months | Start에서 Bottom까지의 기간 |
| Recovery Months | Bottom에서 Recovery까지의 기간 |
| Underwater Months | Start 이후 이전 고점을 회복하기까지의 기간 |
| Annualized Recovery Rate | Bottom에서 이전 고점으로 복귀하기 위해 실제 회복기간 동안 필요했던 연환산 회복속도 |

### Historical Market Stress Periods

미리 정의된 historical stress 구간에서 Provided / Optimized / Benchmark의 누적수익률을 비교한다.

각 row의 의미는 해당 stress period 안의 실제 portfolio return 비교다.

---

## 19. Portfolio Asset Performance

Portfolio에 사용된 개별 자산의 historical statistics를 한 표에서 비교한다.

주요 항목은 Portfolio Performance Summary와 같은 의미를 가지지만 **portfolio가 아니라 asset 단위**다.

- CAGR
- Annualized Return
- Standard Deviation
- Best Year
- Worst Year
- Maximum Drawdown
- Sharpe Ratio
- Sortino Ratio
- 3M / YTD / 1Y
- 3Y / 5Y / 10Y annualized return

추가로 `Expected Return`과 `Volatility`가 표시되는 경우 이는 optimization statistics다.

---

## 20. Return Decomposition

### 무엇인가

Provided / Optimized Portfolio의 realized return을 자산별 contribution으로 분해한다.

### 읽는 법

각 자산의 contribution 값은 Portfolio의 historical return 결과에서 해당 자산이 차지한 누적 기여를 보여준다.

`자산 비중`과 `return contribution`은 같은 숫자가 아니다.

---

## 21. Risk Decomposition

### 무엇인가

Optimization covariance와 Portfolio weight를 이용해 자산별 component risk contribution을 계산한 결과다.

각 Portfolio의 자산별 risk contribution 합은 100%다.

### 읽는 법

예를 들어 어떤 자산의 weight가 20%인데 risk contribution이 35%라면, 현재 covariance와 weight 조합에서 그 자산이 Portfolio 위험의 35%를 구성한다는 뜻이다.

`Weight 20% = Risk Contribution 20%`를 의미하지 않는다.

---

## 22. Annual Asset Returns

각 asset의 calendar-year return을 비교한다.

Portfolio-level Annual Returns와 달리 개별 자산이 각 연도에 어떤 수익률을 기록했는지 보여준다.

첫해와 마지막해가 partial year라면 해당 기간에 실제 포함된 월만 사용한다.

---

## 23. Rolling Returns

### Rolling Return의 의미

고정된 길이의 window를 한 달씩 이동시키면서 각 구간의 return을 반복 계산한다.

예를 들어 Rolling 3Y는:

```text
2016-01 ~ 2018-12
2016-02 ~ 2019-01
2016-03 ~ 2019-02
...
```

처럼 36개월 window를 계속 이동시키며 연환산 수익률을 계산한다.

### Rolling Returns Summary

각 rolling window series의 다음 값을 요약한다.

- Average
- High
- Low

### Rolling 3Y Returns / Rolling 5Y Returns

- X축: window 종료 Month / Year
- Y축: 해당 3년 또는 5년 window의 annualized return

Provided, Optimized, Benchmark를 같은 기간 기준으로 비교한다.

---

## 24. Metric Quick Reference

| Metric | Unit | 핵심 의미 |
|---|---:|---|
| Allocation | % | Portfolio 자산 비중 |
| CAGR | %/year | 전체기간 복리 성장률의 연환산 |
| Annualized Return | %/year | 월수익률 산술평균 × 12 |
| Expected Return | %/year | Optimization expected-return estimate |
| Standard Deviation | %/year | 월수익률 변동성 × √12 |
| Maximum Drawdown | % | 이전 고점 대비 최대 하락률 |
| Sharpe ex-ante | ratio | Expected excess return / Expected volatility |
| Sharpe ex-post | ratio | Historical annualized excess return / Historical volatility |
| Sortino | ratio | Historical excess return / Downside deviation |
| Active Return | %/year | Benchmark 대비 평균 초과수익 |
| Tracking Error | %/year | Active return의 변동성 |
| Information Ratio | ratio | Active Return / Tracking Error |
| Alpha | %/year | Beta를 반영한 benchmark-relative 초과수익 통계 |
| Beta | ratio | Benchmark return에 대한 민감도 통계 |
| R-Squared | ratio | Benchmark와의 월수익률 correlation² |
| Treynor Ratio | ratio | Excess return / Beta |
| Calmar Ratio | ratio | 최근 36개월 CAGR / 최근 36개월 |MDD| |
| M² | %/year | Sharpe를 Benchmark 변동성 수준으로 환산한 수익률 |
| Skewness | ratio | 월수익률 분포 비대칭도 |
| Excess Kurtosis | ratio | 월수익률 분포의 excess kurtosis |
| Historical VaR 95% | %/month | 월수익률 표본의 하위 5% 손실 경계 |
| Correlation | -1 ~ +1 | 두 asset 월수익률의 Pearson correlation |
| Reallocation | % | Baseline과 LOYO allocation 사이의 총 재배치 규모 |
| Weight Change | %p | 두 allocation weight의 percentage-point 차이 |
| Risk Contribution | % | Portfolio ex-ante component risk에서 자산이 차지하는 비중 |

---

## 25. 표기법과 해석 시 주의

### 같은 이름이라도 기준 데이터가 다를 수 있다

특히 `Return`, `Volatility`, `Sharpe`는 historical section과 optimization section에서 계산 기준이 다를 수 있다. section 제목과 `ex-ante / ex-post` 표기를 함께 확인한다.

### Partial year

분석 시작 또는 종료 연도가 12개월 미만이면 Annual Return과 Annual Asset Return은 실제 포함된 월만 사용한다.

### Benchmark-relative metric

Active Return, Tracking Error, Information Ratio는 Benchmark가 있을 때만 의미가 있다. Benchmark 자체에 대해서는 일반적으로 `N/A`다.

### Missing value

필요한 window가 부족하거나 계산이 적용되지 않는 경우 `N/A`다. 이를 0으로 해석하지 않는다.

### 이 매뉴얼의 범위

이 문서는 숫자의 의미와 report 사용법을 설명한다. 특정 metric이 높거나 낮다는 이유만으로 Portfolio 또는 자산의 투자 적합성을 판정하지 않는다.
