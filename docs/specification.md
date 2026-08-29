# Portfolio Optimizer Specification

## 1. Purpose and Authority

`portfolio-optimizer-kr`는 국내외 투자 자산을 동일한 mean-variance framework에서 분석하고, 재현 가능한 optimization/result artifact를 생성하기 위한 portfolio research system이다.

이 문서는 **금융 계산, 데이터 의미, optimization, analytics, canonical result의 최상위 product specification**이다.

Normative hierarchy:

```text
Finance / calculation semantics   docs/specification.md
Report UI / interaction semantics docs/report-ui-specification.md
Architecture / responsibility     docs/architecture.md
Validation procedure              docs/visual-acceptance-contract.md
External reference material       non-normative
```

외부 서비스, screenshot, historical golden, third-party output은 validation과 defect discovery에 사용할 수 있지만 이 문서보다 우선하지 않는다.

Product behavior를 바꾸려면 먼저 이 specification을 변경하고, 구현과 tests를 그 변경에 맞춘다.

핵심 연구 질문은 단일 최적 weight보다 다음에 가깝다.

> 특정 자산이 기존 portfolio에 독립적인 수익 엔진과 diversification 효과를 제공하며, objective·기간·constraint가 바뀌어도 의미 있는 allocation range를 유지하는가?

---

## 2. v1 Scope

v1은 다음을 지원한다.

- FinanceDataReader(FDR) 기반 market data
- adjusted-price normalization
- USD/KRW 혼합 portfolio의 KRW 기준 환산
- calendar month-end monthly returns
- arithmetic expected return
- sample covariance / volatility / correlation
- Maximum Sharpe Ratio optimization
- Maximum Return subject to Target Annual Volatility
- long-only asset min/max constraints
- Efficient Frontier
- monthly / yearly portfolio rebalancing
- Provided / Optimized / Benchmark historical analytics
- active return / tracking error / information ratio
- rolling active return / rolling tracking error
- return / risk decomposition
- trailing / annual / monthly / rolling returns
- canonical `result.json`
- full-precision raw CSV
- human/LLM-readable review CSV
- self-contained `report.html`

v1에서 제외한다.

- Sortino/CVaR/MDD/Risk Parity/Omega/Kelly optimization objective
- Black-Litterman
- Monte Carlo
- factor model
- tax simulation
- forecasting
- robust/resampled optimization

Sortino, MDD 등은 performance metric으로 사용할 수 있지만 optimization objective와는 별개다.

---

## 3. Canonical Inputs

최소 입력:

```text
Assets
Analysis Period
Portfolio Rebalancing Period       # monthly | yearly
Provided Portfolio Weights         # optional
Asset Min Weight
Asset Max Weight
Benchmark                          # optional
Optimization Objective
Target Annual Volatility           # target-vol objective only
Risk-free Configuration
Frontier Points
```

기본값:

```text
Market Data Source = FinanceDataReader
Return Frequency = Monthly
Portfolio Rebalancing Period = Monthly
Frontier Points = 100
Risk-free Mode = us_3m_tbill
Optimization Modeling = CVXPY
QP Solver = OSQP
SOCP Solver = CLARABEL
```

Asset 기본 constraint:

```text
min_weight = 0
max_weight = 1
```

실행 가능한 canonical configuration format은 YAML이다.

```text
CLI / UI / Research Control
          ↓
         YAML
          ↓
        Runner
          ↓
OptimizationRequest
```

Interface가 달라도 계산 의미론은 동일해야 한다.

---

## 4. Data and Coverage

### 4.1 Price pipeline

```text
FDR price series
-> optional FX conversion
-> common price alignment
-> calendar month-end prices
-> monthly simple returns
-> completed-month filtering
-> requested analysis period
```

`Analysis Period`는 **return observation period**다.

첫 요청 월의 return을 만들기 위해 직전 month-end price를 warm-up data로 사용할 수 있다.

종료일이 해당 월의 마지막 calendar date가 아니면 terminal incomplete month를 제외한다.

### 4.2 Common coverage

Optimization universe는 모든 optimization asset이 공통으로 관측 가능한 monthly return matrix를 사용한다.

Run artifact에는 최소 다음 coverage를 기록한다.

```text
optimization_monthly_returns.start
optimization_monthly_returns.end
optimization_monthly_returns.observations
benchmark_overlap
asset_prices.<ticker>.start
asset_prices.<ticker>.end
asset_prices.<ticker>.observations
```

실제 usable period가 requested period보다 asset availability 때문에 줄어들면 limiting asset과 effective period를 식별할 수 있어야 한다.

단순히 requested start가 어떤 asset의 listing 이후라는 이유만으로 data constraint가 발생했다고 판단하지 않는다.

### 4.3 Currency

혼합 KRW/USD universe에서는 USD asset price를 USD/KRW로 환산해 common base currency에서 분석한다.

지원하지 않는 currency는 명시적 validation error로 처리한다.

---

## 5. Return and Statistics Conventions

Monthly return은 simple return을 사용한다.

### 5.1 Expected Return

```text
mu_monthly = arithmetic mean(monthly returns)
mu_annual  = mu_monthly * 12
```

### 5.2 Annual Covariance

```text
Sigma_annual = Cov(monthly returns, sample) * 12
```

### 5.3 Annual Volatility

```text
vol_annual = std(monthly returns, sample) * sqrt(12)
```

### 5.4 Correlation

Monthly simple return의 Pearson correlation을 사용한다.

### 5.5 Portfolio Ex-ante Statistics

```text
Expected Return = w.T @ mu
Variance        = w.T @ Sigma @ w
Volatility      = sqrt(Variance)
Sharpe          = (Expected Return - annual RF) / Volatility
```

Optimization statistics와 realized historical performance는 별개의 개념으로 유지한다.

---

## 6. Risk-free Rate

지원 mode:

```text
risk_free_mode = us_3m_tbill   # default
risk_free_mode = fixed
```

### 6.1 us_3m_tbill

Analysis period와 일관된 annual risk-free convention을 제공한다.

External provider가 runtime boundary에 있는 경우 runner가 effective annual RF를 공급할 수 있다.

### 6.2 fixed

입력 annual rate를 그대로 사용한다.

### 6.3 Persisted metadata

Run에는 반드시 다음을 기록한다.

```text
risk_free.requested_mode
risk_free.effective_annual_rate
```

User-facing note는 실제 run mode와 일치해야 한다.

---

## 7. Portfolio Constraints

v1은 long-only, fully-invested portfolio다.

```text
sum(weights) = 1
weight_i >= min_weight_i
weight_i <= max_weight_i
weight_i >= 0
```

Constraint가 infeasible하면 optimization을 실행하지 않고 명시적 error를 반환한다.

Solver result는 status뿐 아니라 다음 residual을 재검증한다.

- finite weights/statistics
- sum(weights)
- min/max constraints
- long-only
- target-volatility constraint when applicable

---

## 8. Optimization Objectives

### 8.1 Maximum Sharpe Ratio

```text
maximize (Expected Return - RF) / Volatility
```

Convex variable transformation으로 동등 문제를 구성한다.

Primary QP solver:

```text
OSQP
```

Output:

```text
optimized weights
expected annual return
annualized volatility
ex-ante Sharpe Ratio
solver/status
```

### 8.2 Maximum Return at Target Annual Volatility

```text
maximize Expected Return
subject to Volatility <= Target Annual Volatility
```

SOCP-compatible formulation을 사용한다.

Primary solver:

```text
CLARABEL
```

Target volatility가 feasible minimum보다 낮으면 infeasible로 처리한다.

---

## 9. Efficient Frontier

### 9.1 Boundary Portfolios

최소 다음을 계산한다.

1. Global Minimum Variance portfolio
2. Maximum Expected Return portfolio under constraints

### 9.2 Frontier Points

기본값은 100 points다.

GMV expected return부터 constrained maximum expected return까지 target return을 균등 분할한다.

각 target return에 대해:

```text
minimize w.T @ Sigma @ w
subject to
    w.T @ mu = target_return
    sum(w) = 1
    min_weight_i <= w_i <= max_weight_i
```

각 point의 canonical fields:

```text
point number
asset weights
expected annual return
annualized volatility
ex-ante Sharpe Ratio
```

Frontier는 asset allocation transition과 stable allocation range 분석의 canonical raw data다.

### 9.3 Efficient Frontier Asset Statistics

각 optimization asset에 대해 최소:

```text
Ticker
Name
Expected Return
Standard Deviation
Sharpe Ratio
Min Weight
Max Weight
```

를 제공할 수 있어야 한다.

Chart/table presentation 규칙은 `docs/report-ui-specification.md`가 담당한다.

---

## 10. Historical Portfolio Return Series

Provided Portfolio와 Optimized Portfolio는 동일 monthly asset return matrix를 사용한다.

### 10.1 Monthly Rebalancing

매월 period 시작 시 target weights로 rebalance한 것으로 계산한다.

```text
portfolio_return_t = sum(target_weight_i * asset_return_i,t)
```

### 10.2 Yearly Rebalancing

첫 active period에서 target weights를 적용한다.

같은 calendar year 안에서는 weights가 drift한다.

```text
portfolio_return_t = sum(weight_i,t * asset_return_i,t)

weight_i,t+1 = weight_i,t * (1 + asset_return_i,t)
               / (1 + portfolio_return_t)
```

새 calendar year의 첫 available monthly period에서 target weights로 복귀한다.

Analysis period가 연도 중간에 시작하면 첫 active period에서 target weights를 적용하고 다음 calendar year부터 정상 annual schedule을 따른다.

### 10.3 Benchmark

Benchmark가 단일 asset이면 동일 base-currency convention의 monthly return series를 직접 사용한다.

Optimization statistics와 historical portfolio path는 별도 저장/계산한다.

---

## 11. Performance Metrics

### 11.1 Wealth Convention

Canonical normalized wealth:

```text
start_balance = 1.0
```

Presentation convention:

```text
1.0 = $10,000
```

### 11.2 CAGR

```text
CAGR = terminal_wealth^(1 / years) - 1
```

`years = monthly_observations / 12` convention을 사용한다.

### 11.3 Annualized Return

```text
mean(monthly returns) * 12
```

### 11.4 Realized Standard Deviation

```text
std(monthly returns, sample) * sqrt(12)
```

### 11.5 Annual Returns

Calendar year의 available monthly observations를 복리 결합한다.

```text
annual_return_y = product(1 + monthly_return_t) - 1
```

Best/Worst Year는 annual return series의 max/min이다.

### 11.6 Maximum Drawdown

```text
wealth_t = cumulative product(1 + return_t)
running_peak_t = cumulative max(wealth_t)
drawdown_t = wealth_t / running_peak_t - 1
MDD = min(drawdown_t)
```

### 11.7 Sharpe Ratio, Ex-post

```text
(annualized arithmetic return - annual RF)
/ realized annualized volatility
```

### 11.8 Sortino Ratio

Monthly minimum acceptable return은 annual RF를 monthly compound-equivalent로 변환한다.

```text
monthly_mar = (1 + annual_rf)^(1/12) - 1
downside = min(monthly_return - monthly_mar, 0)
downside_deviation = sqrt(mean(downside^2)) * sqrt(12)
Sortino = (annualized arithmetic return - annual_rf) / downside_deviation
```

### 11.9 Required Summary Fields

Provided / Optimized / Benchmark 비교에 최소 다음 값을 계산할 수 있어야 한다.

```text
Start Balance
End Balance
CAGR
Expected Return
Realized Standard Deviation
Best Year
Worst Year
Maximum Drawdown
Sharpe Ratio (ex-ante)
Sharpe Ratio (ex-post)
Sortino Ratio
Active Return
Tracking Error
Information Ratio
```

Benchmark 자체에 대한 benchmark-relative metric은 conceptually not applicable이다.

```text
Benchmark Active Return       = N/A
Benchmark Tracking Error      = N/A
Benchmark Information Ratio   = N/A
```

### 11.10 Advanced Metrics

현재 지원 가능한 benchmark-relative/distribution metrics:

```text
Alpha
Beta
R-squared
Treynor Ratio
Calmar Ratio
Modigliani-Modigliani
Historical VaR 95
Skewness
Excess Kurtosis
```

새 metric은 calculation formula와 unit contract가 정의된 후 추가한다.

---

## 12. Trailing Returns

지원 구간:

```text
3M
YTD
1Y
3Y annualized
5Y annualized
10Y annualized
Full Period CAGR
3Y Annualized Volatility
5Y Annualized Volatility
```

### 12.1 Total-return window

12개월 이하:

```text
product(1 + monthly returns) - 1
```

### 12.2 Multi-year annualization

12개월 초과:

```text
annualized = (1 + total_return)^(12 / months) - 1
```

데이터가 부족하면 `N/A`.

---

## 13. Portfolio Asset Performance

각 optimization asset에 최소 다음 metric을 계산한다.

```text
Ticker
Name
CAGR
Annualized Return
Standard Deviation
Best Year
Worst Year
Maximum Drawdown
Sharpe Ratio
Sortino Ratio
3M
YTD
1Y
3Y annualized
5Y annualized
10Y annualized
```

Presentation layer가 identity를 추가하거나 table 구조를 변경해도 이 required information을 제거하면 안 된다.

---

## 14. Benchmark / Active Return Analytics

### 14.1 Monthly Active Return

```text
active_return_t = portfolio_return_t - benchmark_return_t
```

### 14.2 Annualized Active Return

```text
mean(monthly active return) * 12
```

### 14.3 Tracking Error

```text
std(monthly active return, sample) * sqrt(12)
```

### 14.4 Information Ratio

```text
Annualized Active Return / Tracking Error
```

Tracking Error가 0이면 Information Ratio는 unavailable/non-finite로 취급한다.

### 14.5 Annual Active Return

각 calendar year에서:

```text
portfolio_annual_total - benchmark_annual_total
```

### 14.6 Cumulative Active Return

```text
cumulative portfolio wealth - cumulative benchmark wealth
```

### 14.7 Rolling Active Return

기본 window:

```text
36 months
```

각 rolling window에서 먼저 portfolio와 benchmark의 compound total return을 구한 뒤 각각 annualize한다.

```text
portfolio_total_W = product(1 + portfolio_monthly_return) - 1
benchmark_total_W = product(1 + benchmark_monthly_return) - 1

portfolio_ann_W = (1 + portfolio_total_W)^(12/W) - 1
benchmark_ann_W = (1 + benchmark_total_W)^(12/W) - 1

rolling_active_return = portfolio_ann_W - benchmark_ann_W
```

36개월 window에서 annualization exponent는 `12/36`이다.

### 14.8 Rolling Tracking Error

동일 rolling window의 monthly active returns를 사용한다.

```text
rolling_tracking_error
= std(monthly active returns in window, sample) * sqrt(12)
```

Rolling Active Return과 Rolling Tracking Error는 서로 다른 의미와 scale을 갖는 별도 metric이다.

---

## 15. Up vs. Down Market Analytics

Market classification은 canonical benchmark monthly return의 sign을 사용한다.

```text
Up   = benchmark_return > 0
Down = benchmark_return < 0
Flat = benchmark_return == 0
```

Portfolio별, market type별 최소 statistics:

```text
portfolio mean return
benchmark mean return
mean active return
occurrences
above benchmark count
below benchmark count
total count
% above benchmark
mean active return when above
mean active return when below
```

외부 source의 Up/Down count에 맞추기 위해 sign 또는 count를 hard-code하지 않는다.

Presentation에서 monthly observations를 압축하는 view transform은 canonical statistics를 변경하지 않아야 한다.

현재 UI용 paired-bar transform은 `docs/report-ui-specification.md`에 정의한다.

---

## 16. Drawdowns

Portfolio별 독립적으로 drawdown episode를 계산한다.

Minimum fields:

```text
Rank
Start
Bottom
Recovery
Maximum Drawdown
Duration Months
```

Recovery가 아직 발생하지 않은 episode는 recovery unavailable 상태로 유지한다.

---

## 17. Correlations

두 canonical scope를 지원한다.

### 17.1 Asset Correlations

Optimization universe monthly returns의 Pearson correlation matrix.

### 17.2 Portfolio / Asset Correlations

다음을 함께 포함한 monthly-return correlation matrix.

```text
Optimization Assets
Provided Portfolio
Optimized Portfolio
Benchmark
```

---

## 18. Return Decomposition

Historical rebalancing schedule의 period-start weight를 사용한다.

Period contribution:

```text
asset_return_contribution_i,t = weight_i,t * asset_return_i,t
```

Terminal wealth 기준 monetary contribution:

```text
asset_pnl_i,t
= portfolio_value_(t-1) * weight_i,t * asset_return_i,t

cumulative_asset_pnl_i
= sum(asset_pnl_i,t)
```

모든 asset cumulative contribution 합은 portfolio total gain과 일치해야 한다.

Provided와 Optimized를 별도 계산한다.

---

## 19. Risk Decomposition

Ex-ante annual covariance matrix를 기준으로 component risk contribution을 계산한다.

```text
portfolio_variance = w.T @ Sigma @ w

RC_i = w_i * (Sigma @ w)_i / portfolio_variance
```

전체 `RC_i` 합은 1이다.

Provided와 Optimized를 별도 계산한다.

---

## 20. Rolling Portfolio Returns

기본 지원 window:

```text
36 months
60 months
```

12개월보다 긴 rolling total return은 annualized return으로 표시한다.

```text
rolling_ann_return
= (1 + rolling_total_return)^(12 / window_months) - 1
```

---

## 21. Canonical Result

계산 결과의 source of truth는 UI가 아니라 structured data다.

`result.json` 최소 영역:

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

Canonical result는 calculation semantics를 표현한다. UI-specific coordinate나 DOM state를 canonical result에 넣지 않는다.

---

## 22. Run Artifacts

```text
runs/<run_id>/
├─ input.yaml
├─ result.json
├─ context.yaml        # research execution only
├─ raw/
├─ review/
├─ report.html
└─ validation/         # validation run when applicable
```

역할:

```text
input.yaml     exact/effective execution input
result.json    canonical calculated result
raw/           full precision tables
review/        human/LLM-readable tables
report.html    self-contained presentation artifact
validation/    validation evidence when applicable
```

기존 run directory를 silent overwrite하지 않는다.

---

## 23. Presentation Boundary

Report UI의 canonical specification은:

```text
docs/report-ui-specification.md
```

이다.

Presentation layer는 canonical result를 다시 정의하지 않는다.

Browser에서 허용되는 transformation은 formatting, coordinate mapping, grouping/binning 등 **view-only operation**에 한정한다.

Finance formula를 browser에서 별도 재구현해 canonical result와 다른 값을 만드는 것은 금지한다.

---

## 24. Testing

### 24.1 Calculation Contract Tests

최소:

- return/statistics synthetic fixture
- risk-free handling
- constraint residual
- maximum Sharpe result sanity
- target-volatility feasibility/residual
- frontier point weights sum 1
- historical rebalancing convention
- CAGR / MDD / Sharpe / Sortino
- active return / tracking error / information ratio
- rolling active-return annualization
- return/risk decomposition invariants

### 24.2 Report Semantic Tests

UI test는 `docs/report-ui-specification.md`를 기준으로 한다.

Rendered-value regression을 가능한 경우 사용한다.

예:

```text
canonical balance 1.0 -> $10,000
benchmark relative metrics -> N/A
required asset performance columns retained
rolling active return value uses annualized-window convention
```

문자열 marker 존재만으로 semantic correctness를 대신하지 않는다.

### 24.3 Test Scope

개발 반복 중에는 changed/affected scope를 우선한다.

Full regression은 다음과 같은 경우 확대한다.

- core/common calculation change
- 영향 범위가 넓거나 불명확
- release/completion gate에 필요
- targeted failure가 cross-module regression을 암시
- 사용자/LLM이 명시적으로 요청

---

## 25. Change Governance

운영 단계에서 calculation behavior를 변경할 때:

1. 변경할 product semantic을 이 문서에 먼저 정의한다.
2. canonical tests를 갱신한다.
3. implementation을 갱신한다.
4. existing run/result compatibility 영향을 확인한다.
5. external reference와 차이가 있다는 이유만으로 이 문서를 자동 변경하지 않는다.

외부 service 결과는 다음 용도에 사용할 수 있다.

- sanity check
- alternative convention 발견
- data-source deviation 조사
- UX/metric 개선 아이디어 발굴

하지만 외부 service의 현재 동작 자체가 acceptance criterion은 아니다.
