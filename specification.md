# Specification

## 1. Purpose

`portfolio-optimizer-kr`는 국내 ETF와 해외 ETF를 동일한 framework에서 비교하고 optimization할 수 있는 연구 도구다.

목표는 Portfolio Visualizer(PV)를 복제하는 것이 아니라, 실제 portfolio research에 필요한 핵심 optimization과 analytics를 자체적으로 일관되게 수행하는 것이다.

최종 연구 질문은 단일한 최적 weight가 아니라 다음에 가깝다.

> 특정 자산이 기존 portfolio에 독립적인 수익 엔진과 diversification 효과를 제공하며, objective·기간·constraint가 바뀌어도 의미 있는 allocation range를 유지하는가?

PV 결과는 기능 및 수치 검증을 위한 golden reference로 사용하지만 100% 동일한 계산 결과를 요구하지 않는다.

## 2. v1 Scope

v1은 다음을 구현한다.

- FinanceDataReader(FDR) 기반 market data 취득
- adjusted-price normalization
- mixed-currency portfolio의 KRW 기준 환산
- calendar month-end 기반 monthly return 생성
- expected return / covariance / volatility / correlation 계산
- Maximum Sharpe Ratio optimization
- Maximum Return subject to Target Annual Volatility optimization
- asset min/max weight constraints
- Efficient Frontier 생성
- Provided / Optimized / Benchmark historical performance 비교
- 핵심 performance / risk / benchmark analytics
- machine-readable result와 표 형태 output
- PV golden reference 기반 sanity/parity test

v1에서 제외한다.

- PV 전체 기능 복제
- Sortino/CVaR/MDD/Risk Parity/Omega/Kelly optimization
- Black-Litterman
- Monte Carlo
- factor model
- tax simulation
- forecasting
- advanced robust/resampled optimization
- 복잡한 UI

Sortino, MDD 등은 optimization objective가 아니라 performance metric으로 계산할 수 있다.

## 3. Core Inputs

최소 입력은 다음과 같다.

```text
Assets
Analysis Period
Provided Portfolio Weights
Asset Min Weight
Asset Max Weight
Benchmark                # optional
Optimization Objective
Target Annual Volatility # target-vol objective일 때
Risk-free Configuration
Frontier Points
```

기본값:

```text
Market Data Source = FDR
Return Frequency = Monthly
Frontier Points = 100
Risk-free Source = U.S. 3-Month Treasury Bill Rate
Long Only = true
Fully Invested = true
```

Provided Portfolio weights가 주어지면 합계는 1이어야 한다.

## 4. Market Data

### 4.1 Source

v1의 market data source는 **FinanceDataReader(FDR)** 로 고정한다.

FDR을 통해 한국 ETF/주식과 지원되는 미국 ticker를 조회한다.

다른 data source는 v1 core requirement가 아니다.

### 4.2 Canonical Price

각 자산은 하나의 canonical adjusted-price series로 정규화한다.

규칙:

1. `Adj Close`가 존재하면 `Adj Close`를 사용한다.
2. 별도 `Adj Close`가 없으면 FDR이 제공하는 `Close`를 canonical price로 사용한다.
3. 이후 통계/optimization 계층은 source column 이름을 알 필요가 없다.

### 4.3 Analysis Period

사용자가 요청한 기간과 실제 데이터 coverage의 교집합을 사용한다.

여러 자산이 있을 경우 모든 자산이 동시에 존재하는 공통 구간을 사용한다.

```text
common_start = max(asset_start_dates)
common_end   = min(asset_end_dates)
```

Benchmark가 historical comparison에 포함되는 경우 benchmark도 해당 비교 계산의 공통 coverage에 포함한다.

임의 backfill로 상장 이전 데이터를 만들지 않는다.

## 5. Currency Normalization

모든 자산이 같은 통화이면 native currency return을 그대로 사용한다.

KRW와 외화 자산이 하나의 optimization universe에 섞이면 **base currency는 KRW**로 한다.

USD 자산의 KRW price는 다음과 같이 만든다.

```text
price_krw = adjusted_price_usd * USDKRW
```

여기서 `USDKRW`는 1 USD당 KRW 환율이다.

환율과 자산의 거래일이 다르면 자산 관측일 기준으로 같은 날 또는 그 이전의 가장 최근 환율을 사용한다. 미래 환율을 사용하지 않는다.

통화 환산은 monthly sampling 이전에 수행한다.

Benchmark 역시 portfolio와 같은 base currency 기준으로 비교한다.

## 6. Monthly Return Series

### 6.1 Month-end Price

각 calendar month의 마지막 available trading observation을 month-end price로 사용한다.

즉 calendar month의 실제 마지막 날짜가 휴일이어도 해당 월의 마지막 유효 관측값을 사용한다.

### 6.2 Monthly Return

simple return을 사용한다.

```text
r_t = P_t / P_(t-1) - 1
```

첫 month-end price는 return 계산을 위한 기준점이며 첫 return은 다음 month부터 생성된다.

모든 optimization statistics는 동일한 aligned monthly-return matrix를 사용한다.

## 7. Optimization Statistics

월별 return matrix를 기준으로 계산한다.

### Expected Annual Return

```text
mu_monthly = arithmetic mean(monthly returns)
mu_annual  = mu_monthly * 12
```

### Annual Covariance

sample covariance를 사용한다.

```text
Sigma_annual = Cov(monthly returns) * 12
```

### Annual Volatility

```text
vol_annual = std(monthly returns, sample) * sqrt(12)
```

### Correlation

monthly simple return의 Pearson correlation을 사용한다.

### Portfolio Statistics

```text
Expected Return = w.T @ mu
Variance        = w.T @ Sigma @ w
Volatility      = sqrt(Variance)
```

Optimization statistics와 historical realized performance는 별개의 개념으로 유지한다.

## 8. Risk-free Rate

Risk-free 설정은 교체 가능하게 만든다.

기본 source는 **U.S. 3-Month Treasury Bill Rate**다.

추가로 fixed annual risk-free rate를 직접 지정할 수 있어야 한다.

```text
risk_free_mode = us_3m_tbill # default
risk_free_mode = fixed
```

고정값이 지정되면 해당 값을 사용한다.

Historical T-Bill rate를 사용할 경우 analysis period에 맞는 risk-free series를 monthly 수준으로 정규화한다.

연율 rate `y_t`를 monthly equivalent return으로 바꿀 때 기본식은 다음과 같다.

```text
rf_monthly_t = (1 + y_t)^(1/12) - 1
```

Ex-ante optimization에 사용하는 annual risk-free rate는 aligned monthly risk-free return의 arithmetic mean을 annualize한다.

```text
rf_annual = mean(rf_monthly) * 12
```

정확한 PV 내부 구현과 다를 수 있으며, PV golden test에서는 그 차이를 별도로 기록한다.

## 9. Portfolio Constraints

v1 기본 constraint:

```text
sum(weights) = 1
weight_i >= min_weight_i
weight_i <= max_weight_i
weight_i >= 0
```

즉 long-only, fully-invested portfolio다.

사용자가 asset별 min/max를 지정하지 않으면 기본값은 다음과 같다.

```text
min_weight = 0
max_weight = 1
```

Constraint 자체가 infeasible하면 optimization을 실행하지 않고 명시적인 error를 반환한다.

## 10. Optimization Objectives

### 10.1 Maximum Sharpe Ratio

다음을 최대화한다.

```text
Sharpe = (Expected Return - Risk-free Rate) / Volatility
```

출력:

- optimized weights
- expected annual return
- annualized volatility
- ex-ante Sharpe Ratio

### 10.2 Maximum Return subject to Target Annual Volatility

다음을 최대화한다.

```text
maximize Expected Return
subject to Volatility <= Target Annual Volatility
```

출력:

- optimized weights
- expected annual return
- optimized annual volatility
- ex-ante Sharpe Ratio

Target volatility가 feasible minimum volatility보다 낮으면 infeasible로 처리한다.

### 10.3 Solver Requirements

구현 solver는 표준 numerical optimization library를 사용할 수 있다.

Solver 성공 flag만 신뢰하지 않고 결과에 대해 다음을 재검증한다.

- weight sum
- min/max bounds
- long-only constraint
- target volatility constraint
- finite objective/statistics

동일 입력에서 deterministic한 결과를 만들어야 한다.

## 11. Efficient Frontier

### 11.1 Boundary Portfolios

다음을 먼저 계산한다.

1. Global Minimum Variance Portfolio
2. Maximum Expected Return Portfolio under constraints

별도로 전체 feasible expected-return minimum/maximum도 계산할 수 있다.

### 11.2 Frontier Points

기본 100 points를 생성한다.

Global Minimum Variance Portfolio의 expected return부터 Maximum Expected Return Portfolio의 expected return까지 target return을 균등하게 나눈다.

각 target return `R_k`에 대해 다음 문제를 푼다.

```text
minimize w.T @ Sigma @ w
subject to
    w.T @ mu = R_k
    sum(w) = 1
    min_weight_i <= w_i <= max_weight_i
```

각 frontier point에 최소한 다음을 저장한다.

- point number
- asset weights
- expected annual return
- annualized volatility
- ex-ante Sharpe Ratio

이 결과는 asset allocation transition과 stable allocation range 분석의 canonical raw data다.

## 12. Historical Portfolio Return Series

Provided Portfolio와 Optimized Portfolio는 동일한 monthly asset return matrix를 이용한다.

각 portfolio는 target weights로 **monthly rebalanced**된 것으로 계산한다.

```text
portfolio_return_t = sum(weight_i * asset_return_i,t)
```

Optimization에 사용한 expected statistics와 historical realized portfolio series는 별도 저장한다.

Benchmark가 단일 자산이면 해당 base-currency-adjusted monthly return series를 직접 사용한다.

## 13. Required Results

### 13.1 Portfolio Optimization Results

Provided Portfolio와 Optimized Portfolio에 대해 다음을 표시한다.

```text
Ticker
Name
Allocation
```

Optimized Portfolio 명칭은 objective를 반영한다.

예:

```text
Maximum Sharpe Ratio
Maximum Return at 13% Target Volatility
```

### 13.2 Performance Summary

Provided / Optimized / Benchmark를 비교한다.

최소 metric:

- Start Balance
- End Balance
- CAGR
- Expected Return
- Realized Standard Deviation
- Best Year
- Worst Year
- Maximum Drawdown
- Sharpe Ratio (ex-ante)
- Sharpe Ratio (ex-post)
- Sortino Ratio
- Active Return
- Tracking Error
- Information Ratio

`Expected Return`, optimization volatility, ex-ante Sharpe는 optimization statistics 기반이다.

`CAGR`, realized volatility, MDD, ex-post Sharpe는 historical return series 기반이다.

### 13.3 Trailing Returns

지원 구간:

- 3 Month
- YTD
- 1 Year
- 3 Year
- 5 Year
- 10 Year
- Full Period
- 3 Year Annualized Volatility
- 5 Year Annualized Volatility

필요 데이터가 부족하면 `N/A`다.

### 13.4 Efficient Frontier Assets

자산별 다음을 제공한다.

```text
Ticker
Name
Expected Return
Standard Deviation
Sharpe Ratio
Min Weight
Max Weight
```

### 13.5 Asset Correlations

Optimization universe 자산들의 monthly-return correlation matrix를 제공한다.

### 13.6 Efficient Frontier Portfolios

모든 frontier point의 asset weights와 expected statistics를 table로 제공한다.

이 table은 필수 결과다.

### 13.7 Annual Returns

```text
Year
Provided Portfolio
Optimized Portfolio
Benchmark
```

각 calendar year의 available observations를 복리 결합한다.

### 13.8 Monthly Returns

각 portfolio별로 월 수익률 table을 제공한다.

```text
Year
Jan ... Dec
YTD
```

### 13.9 Drawdowns

Provided / Optimized / Benchmark별로 독립 계산한다.

최소 필드:

- Rank
- Start
- Bottom
- Recovery
- Maximum Drawdown
- Duration

### 13.10 Portfolio Asset Performance

개별 자산별 최소 metric:

- CAGR
- Annualized Return
- Standard Deviation
- Sharpe
- Sortino
- Maximum Drawdown
- Best Year
- Worst Year
- Trailing Returns

### 13.11 Monthly Correlations

다음을 모두 포함한 return-series correlation matrix를 제공한다.

```text
Optimization Assets
Provided Portfolio
Optimized Portfolio
Benchmark
```

## 14. Benchmark / Active Return Analytics

Benchmark가 있는 경우 다음을 계산한다.

### Active Return Series

```text
active_return_t = portfolio_return_t - benchmark_return_t
```

### Annualized Active Return

```text
mean(monthly active return) * 12
```

### Tracking Error

```text
std(monthly active return, sample) * sqrt(12)
```

### Information Ratio

```text
Annualized Active Return / Tracking Error
```

추가 table:

- annual active return
- cumulative active return
- rolling active return
- rolling tracking error

기본 rolling window는 36 months다.

## 15. Return Decomposition

monthly rebalanced portfolio의 각 period에서 asset contribution은 다음과 같다.

```text
asset_return_contribution_i,t = weight_i * asset_return_i,t
```

Terminal wealth에 대한 누적 monetary contribution은 다음 방식으로 계산한다.

```text
asset_pnl_i,t = portfolio_value_(t-1) * weight_i * asset_return_i,t
cumulative_asset_pnl_i = sum(asset_pnl_i,t)
```

모든 asset의 cumulative contribution 합은 portfolio의 total gain과 일치해야 한다.

Provided Portfolio와 Optimized Portfolio를 각각 계산한다.

## 16. Risk Decomposition

Ex-ante covariance matrix를 기준으로 component risk contribution을 계산한다.

Portfolio variance:

```text
sigma_p^2 = w.T @ Sigma @ w
```

Asset percentage risk contribution:

```text
RC_i = w_i * (Sigma @ w)_i / (w.T @ Sigma @ w)
```

전체 `RC_i` 합은 1이어야 한다.

Provided Portfolio와 Optimized Portfolio를 각각 계산한다.

## 17. Rolling Returns

기본 지원 window:

```text
36 months
60 months
```

내부 구현은 parameterized window를 사용한다.

12개월보다 긴 rolling total return은 annualized return으로 표시한다.

## 18. Charts

계산과 table이 검증된 뒤 구현한다.

우선순위:

1. Efficient Frontier Chart
2. Efficient Frontier Transition Map

### Efficient Frontier Chart

```text
X = Annualized Standard Deviation
Y = Expected Annual Return
```

표시 대상:

- Efficient Frontier
- Individual Assets
- Provided Portfolio
- Optimized Portfolio
- Benchmark

### Efficient Frontier Transition Map

```text
X = Annualized Standard Deviation
Y = Asset Allocation
```

Frontier를 따라 각 asset weight가 어떻게 바뀌는지 표시한다.

## 19. Canonical Result

계산 결과의 source of truth는 UI가 아니라 structured data다.

최소한 machine-readable result를 제공하고, table/차트는 해당 result에서 생성한다.

권장 출력 형태:

```text
result.json
```

필요한 큰 matrix/table은 CSV로 분리할 수 있다.

Canonical result에는 최소한 다음 영역이 있어야 한다.

```text
configuration
data_coverage
asset_statistics
optimization_result
efficient_frontier
portfolio_performance
benchmark_analytics
correlations
return_decomposition
risk_decomposition
```

## 20. Golden Reference

PV golden reference는 다음 경로에 둔다.

```text
tests/golden/pv/
```

현재 기준:

```text
260828_PTF_maxsharpe.md
260828_PTF_maxsharpe.jpg
```

Golden reference의 역할은 다음과 같다.

- monthly-return/statistics 계산 sanity check
- optimization 결과 방향성 확인
- Maximum Sharpe allocation 비교
- expected return / volatility 비교
- Efficient Frontier shape 비교
- frontier weight transition 비교
- 주요 performance metric 비교

PV와 exact equality를 요구하지 않는다.

FDR과 PV의 source data 차이로 발생하는 차이와 optimizer 계산 로직에서 발생하는 차이를 가능한 한 분리해서 진단한다.

Golden parity tolerance는 첫 구현 결과를 관찰한 뒤 실제 data-source 차이를 반영해 확정한다.

## 21. Acceptance Checks

v1 core는 최소한 다음을 자동 테스트한다.

1. `Adj Close`가 있으면 canonical adjusted price로 선택된다.
2. 여러 asset의 분석기간이 가장 짧은 공통 coverage로 정렬된다.
3. calendar month-end에서 마지막 available observation이 선택된다.
4. monthly simple return 계산이 hand-calculated fixture와 일치한다.
5. mixed KRW/USD universe는 USD asset을 KRW price로 환산한 뒤 return을 계산한다.
6. FX alignment에서 미래 환율을 사용하지 않는다.
7. expected annual return이 monthly arithmetic mean × 12와 일치한다.
8. annual covariance와 volatility가 정의된 annualization과 일치한다.
9. portfolio expected return과 volatility가 matrix formula와 일치한다.
10. optimization 결과 weights 합이 1이다.
11. asset min/max constraints가 지켜진다.
12. Maximum Sharpe solver가 synthetic fixture에서 알려진 optimum과 허용오차 내 일치한다.
13. Target Volatility optimization 결과가 target volatility를 초과하지 않는다.
14. infeasible target volatility는 명시적으로 실패한다.
15. Efficient Frontier의 target expected return이 순차 증가한다.
16. 각 frontier point가 모든 weight constraints를 만족한다.
17. 동일 입력과 설정으로 반복 실행하면 동일 결과가 나온다.
18. return decomposition 합이 total portfolio gain과 일치한다.
19. risk contribution 합이 100%와 일치한다.
20. benchmark가 있을 때 active return / tracking error / information ratio가 독립 계산 fixture와 일치한다.
21. PV golden run과 비교 report를 생성할 수 있다.

## 22. Implementation Order

### P0 - Data / Statistics

- FDR loader
- canonical adjusted price
- currency normalization
- common coverage
- monthly returns
- expected return
- covariance
- volatility
- correlation

### P1 - Optimizer

- constraints
- Maximum Sharpe
- Target Volatility

### P2 - Frontier

- Global Minimum Variance
- Maximum Return
- Efficient Frontier Assets
- Asset Correlations
- Efficient Frontier Portfolios

### P3 - Portfolio Performance

- Provided Portfolio series
- Optimized Portfolio series
- Benchmark series

### P4 - Basic Analytics

- Performance Summary
- Trailing Returns
- Annual Returns
- Monthly Returns
- Drawdowns

### P5 - Benchmark Analytics

- Active Return
- Tracking Error
- Information Ratio
- cumulative / rolling active return

### P6 - Deep Analytics

- Portfolio Asset Performance
- Monthly Correlations
- Return Decomposition
- Risk Decomposition
- Rolling Returns

### P7 - Charts

- Efficient Frontier
- Efficient Frontier Transition Map

## 23. Quality Requirements

- **Consistent:** 같은 계산 convention을 모든 run에 동일하게 적용한다.
- **Deterministic:** 동일 입력과 설정은 동일 결과를 만든다.
- **Testable:** 핵심 수식은 외부 data 없이 synthetic fixture로 검증 가능해야 한다.
- **Traceable:** market data → monthly returns → statistics → optimization 결과를 추적할 수 있어야 한다.
- **Minimal:** 실제 연구에 필요한 기능부터 구현하고 범용 금융 플랫폼으로 확장하지 않는다.
- **Robust:** solver 결과와 constraints를 사후 검증하고 silent failure를 허용하지 않는다.
