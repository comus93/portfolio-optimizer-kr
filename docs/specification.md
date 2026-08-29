# Specification

## 1. Purpose

`portfolio-optimizer-kr`는 Portfolio Visualizer(PV)가 직접 지원하지 않는 국내 투자 자산까지 포함해, 국내외 자산을 동일한 mean-variance framework에서 분석하기 위한 Python 기반 portfolio research system이다.

핵심 목표는 PV를 복제하는 것이 아니라 다음을 재현 가능하게 수행하는 것이다.

- 동일 입력과 설정에서 결정적인 optimization result 생성
- Provided / Optimized / Benchmark 비교
- Efficient Frontier와 allocation transition 분석
- historical performance / risk / active-return analytics
- machine-readable canonical result와 self-contained HTML research report 생성
- PV live result와 golden reference를 이용한 의미적 parity 검증

최종 연구 질문은 단일 최적 weight보다 다음에 가깝다.

> 특정 자산이 기존 portfolio에 독립적인 수익 엔진과 diversification 효과를 제공하며, objective·기간·constraint가 바뀌어도 의미 있는 allocation range를 유지하는가?

PV는 behavioral/numerical reference지만 market-data source 차이 때문에 100% 동일한 수치를 요구하지 않는다. 차이가 발생하면 optimizer logic defect와 source-data deviation을 구분한다.

---

## 2. v1 Scope

v1은 다음을 지원한다.

- FinanceDataReader(FDR) 기반 market data
- adjusted-price normalization
- USD/KRW 혼합 portfolio의 KRW 기준 환산
- calendar month-end monthly returns
- arithmetic expected return / sample covariance / volatility / correlation
- Maximum Sharpe Ratio optimization
- Maximum Return subject to Target Annual Volatility
- long-only asset min/max constraints
- 100-point Efficient Frontier
- monthly / yearly portfolio rebalancing
- Provided / Optimized / Benchmark historical analytics
- active return / tracking error / information ratio
- rolling active return / rolling tracking error
- return / risk decomposition
- trailing / annual / monthly / rolling returns
- canonical `result.json`, raw/review CSV, self-contained `report.html`
- PV live / golden parity and browser visual acceptance

v1에서 제외한다.

- PV 전체 기능 복제
- Sortino/CVaR/MDD/Risk Parity/Omega/Kelly optimization objective
- Black-Litterman
- Monte Carlo
- factor model
- tax simulation
- forecasting
- robust/resampled optimization

Sortino, MDD, Omega 계열 값은 필요 시 performance metric으로 확장할 수 있으나 optimization objective와는 별개다.

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

Experiment의 실행 가능한 canonical format은 YAML이다. UI, CLI, research control은 모두 동일 YAML contract와 runner로 수렴한다.

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

Analysis Period는 **return observation period**다. 첫 요청 월의 return을 만들기 위해 직전 month-end price를 warm-up으로 사용할 수 있다.

종료일이 해당 월의 마지막 calendar date가 아니면 terminal incomplete month를 제외한다.

### 4.2 Common coverage

Optimization universe는 공통으로 관측 가능한 monthly return matrix를 사용한다.

Run artifact에는 최소 다음 coverage를 기록한다.

```text
optimization_monthly_returns.start
optimization_monthly_returns.end
optimization_monthly_returns.observations
benchmark_overlap
asset_prices.<ticker>.start/end/observations
```

실제 기간이 requested period보다 asset availability 때문에 줄어들면 report에 limiting asset과 effective period를 명시한다. 단순히 input start가 asset listing 이후라는 이유만으로 constraint note를 만들지 않는다.

### 4.3 Currency

혼합 KRW/USD universe에서는 USD asset price를 USD/KRW로 환산해 common base currency에서 분석한다.

지원하지 않는 currency는 명시적 validation error로 처리한다.

---

## 5. Return and Statistics Conventions

Monthly return은 simple return을 사용한다.

### Expected Return

```text
mu_monthly = arithmetic mean(monthly returns)
mu_annual  = mu_monthly * 12
```

### Annual Covariance

```text
Sigma_annual = Cov(monthly returns, sample) * 12
```

### Annual Volatility

```text
vol_annual = std(monthly returns, sample) * sqrt(12)
```

### Correlation

monthly simple return의 Pearson correlation을 사용한다.

### Portfolio Ex-ante Statistics

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

Historical U.S. 3-Month Treasury Bill mode는 analysis period와 일관된 annual RF convention을 제공해야 한다. 외부 provider boundary가 아직 필요한 환경에서는 runner가 effective annual RF를 공급할 수 있다.

Fixed mode에서는 입력 annual rate를 그대로 사용한다.

Run에는 반드시 다음을 기록한다.

```text
risk_free.requested_mode
risk_free.effective_annual_rate
```

Report note는 실제 run mode와 일치해야 한다. Fixed RF run에서 historical T-Bill wording을 표시하면 안 된다.

---

## 7. Portfolio Constraints

v1:

```text
sum(weights) = 1
weight_i >= min_weight_i
weight_i <= max_weight_i
weight_i >= 0
```

즉 long-only, fully-invested portfolio다.

Constraint가 infeasible하면 optimization을 실행하지 않고 명시적 error를 반환한다.

Solver 결과는 status뿐 아니라 다음을 재검증한다.

- finite weights/statistics
- sum(weights)
- min/max residual
- long-only
- target-volatility residual when applicable

---

## 8. Optimization Objectives

### 8.1 Maximum Sharpe Ratio

```text
maximize (Expected Return - RF) / Volatility
```

Convex variable transformation을 이용해 CVXPY에서 동등 문제를 풀며 QP 경로는 OSQP를 사용한다.

출력:

- optimized weights
- expected annual return
- annualized volatility
- ex-ante Sharpe Ratio

### 8.2 Maximum Return at Target Annual Volatility

```text
maximize Expected Return
subject to Volatility <= Target Annual Volatility
```

SOCP-compatible formulation과 CLARABEL을 사용한다.

Target volatility가 feasible minimum보다 낮으면 infeasible로 처리한다.

---

## 9. Efficient Frontier

### 9.1 Boundary portfolios

최소 다음을 계산한다.

1. Global Minimum Variance portfolio
2. Maximum Expected Return portfolio under constraints

### 9.2 Frontier points

기본 100 points.

GMV expected return부터 constrained maximum expected return까지 target return을 균등 분할하고 각 target에 대해:

```text
minimize w.T @ Sigma @ w
subject to
    w.T @ mu = target_return
    sum(w) = 1
    min_weight_i <= w_i <= max_weight_i
```

각 point 저장 항목:

```text
point
asset weights
expected annual return
annualized volatility
ex-ante Sharpe Ratio
```

### 9.3 Frontier chart

```text
X = Annualized Standard Deviation %
Y = Expected Annual Return %
```

표시 대상:

- Efficient Frontier curve
- nearby individual assets
- Provided Portfolio
- objective-aware Optimized Portfolio
- Benchmark

Viewport는 frontier curve를 중심으로 하되 주변 context를 제공한다. 극단적으로 먼 asset 때문에 curve가 지나치게 축소되지 않아야 한다.

Asset visible/outside 판정은 **최종 display domain** 기준이다. 최종 domain 밖 asset만 `Assets outside chart scale` table로 내린다.

현재 7-asset PV behavioral golden에서 의미상 기대되는 viewport는 대략 X 12%~22.5%, Y 11%~22%이며, 숫자를 hard-code하지 않고 같은 원칙을 따른다.

### 9.4 Efficient Frontier Assets table

필수:

```text
Name
Ticker
Expected Return
Standard Deviation
Sharpe Ratio
Min Weight
Max Weight
```

### 9.5 Frontier Transition

```text
X = Standard Deviation %
Y = Asset Allocation %
```

Frontier를 따라 allocation transition을 stacked-area 의미로 표시한다. 모든 point의 weight 합은 100%다.

---

## 10. Historical Portfolio Series

Provided와 Optimized는 동일 monthly asset return matrix를 사용한다.

### Monthly rebalancing

```text
portfolio_return_t = sum(target_weight_i * asset_return_i,t)
```

매월 target weights로 복귀한다.

### Yearly rebalancing

첫 active period에서 target weights를 적용하고 같은 calendar year 안에서는 weights가 drift한다. 새 calendar year 첫 available monthly period에서 target weights로 복귀한다.

Benchmark가 단일 asset이면 동일 base-currency convention의 monthly return series를 직접 사용한다.

---

## 11. Performance Metrics

### 11.1 Performance Summary minimum

Provided / Optimized / Benchmark를 비교한다.

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

Normalized wealth의 presentation convention은 `Growth of $10,000`이며:

```text
canonical start_balance = 1.0
report Start Balance    = $10,000
```

Benchmark 자체에 대한 Active Return / Tracking Error / Information Ratio는 비교 대상이 아니므로 report에서는 `N/A`로 표시한다. `missing != zero` 원칙을 따른다.

### 11.2 Advanced metrics

현재 제공 가능한 benchmark-relative/distribution metrics:

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

추가 metric은 canonical calculation과 unit contract가 정의된 후 확장한다.

---

## 12. Trailing / Annual / Monthly / Asset Performance

### Trailing Portfolio Returns

```text
3 Month
YTD
1 Year
3 Year annualized
5 Year annualized
10 Year annualized
Full Period CAGR
3 Year Annualized Volatility
5 Year Annualized Volatility
```

데이터가 부족하면 `N/A`.

### Annual Returns

Calendar year available observations를 복리 결합한다.

```text
Year
Provided Portfolio
Optimized Portfolio
Benchmark
```

### Monthly Returns

각 portfolio별:

```text
Year
Jan ... Dec
YTD
```

### Portfolio Asset Performance minimum

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

Asset performance table에 identity column을 추가하면서 기존 trailing-return 정보를 제거하면 regression이다.

---

## 13. Benchmark / Active Return Analytics

### Monthly Active Return

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

### Rolling Active Return and Risk

기본 window는 36 months.

PV-compatible rolling active-return convention:

```text
portfolio_total_36m = product(1 + portfolio_monthly_return) - 1
benchmark_total_36m = product(1 + benchmark_monthly_return) - 1

portfolio_ann_36m = (1 + portfolio_total_36m)^(12/36) - 1
benchmark_ann_36m = (1 + benchmark_total_36m)^(12/36) - 1

rolling_active_return = portfolio_ann_36m - benchmark_ann_36m
rolling_tracking_error = std(monthly active returns over 36m, sample) * sqrt(12)
```

Report presentation:

- Provided / Optimized separate panels
- Active Return = bar, left Y-axis
- Tracking Error = line, right Y-axis
- title `Rolling Active Return and Risk (36 months)`
- subtitle `<Portfolio> vs. <Benchmark>`
- hover includes both values for the same month

36M total return difference를 annualization 없이 그대로 Rolling Active Return으로 표시하면 semantic failure다.

---

## 14. Up vs. Down Market Performance

Market classification은 canonical benchmark monthly return의 sign을 사용한다.

```text
Up   = benchmark_return > 0
Down = benchmark_return < 0
Flat = benchmark_return == 0
```

각 Provided / Optimized block은:

```text
conditional statistics table
+
Return vs. Benchmark paired bar chart
```

Statistics:

- Above Benchmark count
- Below Benchmark count
- Total
- % Above Benchmark
- Average Active Return above/below/overall

Chart presentation은 benchmark monthly return을 오름차순 정렬해 약 20 equal-frequency groups로 압축하고 각 group의 mean Portfolio Return / Benchmark Return을 paired bars로 표시한다.

PV와 Up/Down count가 다르면 숫자를 hard-code하지 않는다. Exact divergent month를 찾아 source-data deviation과 logic defect를 구분한다.

현재 known deviation: local FDR SPY 2026-07 monthly return sign과 PV source가 달라 local 84/36 vs PV 85/35가 발생할 수 있다.

---

## 15. Drawdown / Correlation / Decomposition

### Drawdowns

Provided / Optimized / Benchmark별 독립 계산.

```text
Rank
Start
Bottom
Recovery
Maximum Drawdown
Duration
```

### Correlations

두 scope:

1. Optimization Assets monthly-return correlation
2. Assets + Provided + Optimized + Benchmark monthly-return correlation

UI row identity는 Name + Ticker를 제공한다.

### Return Decomposition

Historical rebalancing schedule의 period-start weight를 사용한다.

```text
asset_return_contribution_i,t = weight_i,t * asset_return_i,t
asset_pnl_i,t = portfolio_value_(t-1) * weight_i,t * asset_return_i,t
```

Asset cumulative PnL 합은 total portfolio gain과 일치해야 한다.

### Risk Decomposition

Ex-ante covariance 기준:

```text
RC_i = w_i * (Sigma @ w)_i / (w.T @ Sigma @ w)
```

전체 risk contribution 합은 1이다.

---

## 16. Canonical Result and Run Artifacts

Canonical source of truth는 UI가 아니라 structured result다.

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

`raw/`는 full precision, `review/`는 human/LLM-readable units와 tables를 제공한다.

`report.html`은 self-contained static artifact다. 브라우저는 금융 수식을 재계산하지 않고 persisted presentation data를 시각화한다.

---

## 17. Interactive Report Contract

상세 visual/behavioral acceptance는 `docs/visual-acceptance-contract.md`가 담당한다.

원칙:

- automated contract와 browser visual acceptance는 서로 대체하지 않는다.
- semantic X/Y 값을 사용한다.
- missing/null을 0으로 coercion하지 않는다.
- objective-aware optimized label과 human-readable benchmark identity를 report 전체에서 일관되게 사용한다.
- same ticker는 report 전체에서 일관된 color identity를 갖는다.
- user-facing tables에서 internal snake_case field를 그대로 노출하지 않는다.

현재 behavioral golden:

```text
https://www.portfoliovisualizer.com/optimize-portfolio?s=y&sl=3n4DZ247sp7s5oMf4Umzc5
```

현재 golden universe:

```text
QQQ / SPMO / GDX / GLD / SLV / AIA / XLE
Period: 2016-08-01 ~ 2026-07-31
Provided: 40 / 10 / 10 / 0 / 10 / 15 / 15
Max: QQQ 50%, SPMO 50%, others 30%
Benchmark: SPY
Objective: Maximum Sharpe Ratio
Frontier: 100 points
```

Static Golden은 최신 UI 수정 완료 후 사용자 제공 PV screenshot으로 다시 고정한다. 이전 깨진/다른-universe image는 completion gate로 사용하지 않는다.

---

## 18. Testing and Acceptance

### Calculation tests

- synthetic fixture로 핵심 수식 독립 검증
- solver constraint residual 검증
- deterministic same-input result
- rolling active-return annualization convention 검증

### Report tests

문자열 존재 여부만으로 완료를 판정하지 않는다. 가능한 경우 rendered semantic value를 잠근다.

최소 regression examples:

```text
Start Balance renders as $10,000
Benchmark Active Return / Tracking Error / IR render N/A
Asset Performance retains annualized + trailing columns
Rolling Active uses annualized 36M return difference
Rolling Active UI uses dual axes
```

### Test scope

개발 반복 중에는 changed/affected scope 테스트를 우선한다.

Full regression은 다음 경우에 수행한다.

- 사용자/LLM 요청
- 공통/core 변경으로 영향 범위가 넓음
- release/completion gate에서 필요하다고 판단됨
- targeted test가 cross-module regression 가능성을 드러냄

작은 presentation 수정마다 관성적으로 전체 suite를 돌리지 않는다.

### Visual acceptance

Interactive Report는 실제 generated report를 localhost HTTP에서 browser로 열고 현재 PV live behavioral golden과 section-by-section 비교한다.

P0 semantic mismatch가 남으면 완료가 아니다. Data-source 차이는 evidence와 함께 intentional deviation으로 기록한다.
