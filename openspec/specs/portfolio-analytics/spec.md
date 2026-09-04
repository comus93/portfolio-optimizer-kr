## Purpose

Optimization과 shared historical research가 사용하는 canonical ex-ante statistics, realized performance, benchmark-relative analytics, drawdown, correlation, decomposition과 rolling-return 의미론을 정의한다.

## Requirements

### Requirement: Expected return convention
Canonical monthly expected return은 monthly simple return의 arithmetic mean이며 annual expected return은 12배 annualization을 사용해야 한다(MUST).

```text
mu_monthly = arithmetic mean(monthly returns)
mu_annual  = mu_monthly * 12
```

#### Scenario: expected-return annualization
- GIVEN canonical monthly return observations가 있다
- WHEN annual expected return을 계산한다
- THEN monthly arithmetic mean에 12를 곱한다

### Requirement: Annual covariance and volatility convention
Canonical annual covariance와 annual volatility는 sample monthly statistics를 사용해야 한다(MUST).

```text
Sigma_annual = Cov(monthly returns, sample) * 12
vol_annual   = std(monthly returns, sample) * sqrt(12)
```

#### Scenario: annualized risk
- GIVEN monthly return matrix가 있다
- WHEN covariance와 volatility를 annualize한다
- THEN sample covariance/std 기반의 12 및 sqrt(12) convention을 사용한다

### Requirement: Pearson monthly correlation
Canonical correlation은 monthly simple returns의 Pearson correlation이어야 한다(MUST).

#### Scenario: asset correlation
- GIVEN 두 asset의 aligned monthly simple-return series가 있다
- WHEN correlation을 계산한다
- THEN Pearson correlation coefficient를 사용한다

### Requirement: Portfolio ex-ante statistics
Weights `w`, annual expected-return vector `mu`, annual covariance `Sigma`, annual risk-free rate를 사용할 때 ex-ante portfolio statistics는 다음 의미를 가져야 한다(MUST).

```text
Expected Return = w.T @ mu
Variance        = w.T @ Sigma @ w
Volatility      = sqrt(Variance)
Sharpe          = (Expected Return - annual RF) / Volatility
```

#### Scenario: ex-ante portfolio evaluation
- GIVEN valid weights와 annual statistics가 있다
- WHEN ex-ante portfolio statistics를 계산한다
- THEN 동일 weights와 canonical mu/Sigma/RF로 return, volatility, Sharpe를 계산한다

### Requirement: CAGR
Canonical CAGR은 terminal wealth와 monthly observation count를 사용해야 한다(MUST).

```text
CAGR = terminal_wealth^(1 / years) - 1
years = monthly_observations / 12
```

#### Scenario: full-period CAGR
- GIVEN terminal wealth와 120 monthly observations가 있다
- WHEN CAGR을 계산한다
- THEN 10년 convention을 사용한다

### Requirement: Realized annualized arithmetic return
Realized annualized return은 monthly portfolio returns의 arithmetic mean에 12를 곱해야 한다(MUST). CAGR과 동일 metric으로 취급해서는 안 된다(MUST NOT).

```text
annualized_return = mean(monthly returns) * 12
```

#### Scenario: CAGR and arithmetic return differ
- GIVEN volatile monthly path에서 CAGR과 arithmetic annualized return이 다르다
- WHEN canonical result를 생성한다
- THEN 두 값을 별도 metric으로 보존한다

### Requirement: Realized annualized standard deviation
Realized annualized standard deviation은 monthly portfolio return sample standard deviation에 `sqrt(12)`를 곱해야 한다(MUST).

#### Scenario: realized volatility
- GIVEN monthly portfolio returns가 있다
- WHEN annualized realized volatility를 계산한다
- THEN sample standard deviation annualization을 사용한다

### Requirement: Calendar annual returns
Calendar-year return은 해당 연도의 available monthly observations를 복리 결합해야 한다(MUST).

```text
annual_return_y = product(1 + monthly_return_t) - 1
```

Best/Worst Year는 이 annual-return series의 max/min이어야 한다(MUST).

#### Scenario: partial calendar year
- GIVEN 첫 또는 마지막 calendar year에 일부 completed months만 존재한다
- WHEN annual return을 계산한다
- THEN available canonical monthly observations만 복리 결합한다

### Requirement: Maximum drawdown
Canonical drawdown과 MDD는 cumulative wealth의 running peak를 기준으로 계산해야 한다(MUST).

```text
wealth_t = cumulative product(1 + return_t)
running_peak_t = cumulative max(wealth_t)
drawdown_t = wealth_t / running_peak_t - 1
MDD = min(drawdown_t)
```

#### Scenario: drawdown episode
- GIVEN wealth path가 이전 peak 아래로 내려갔다가 회복한다
- WHEN drawdown을 계산한다
- THEN peak 대비 underwater path와 minimum drawdown을 보존한다

### Requirement: Ex-post Sharpe Ratio
Ex-post Sharpe는 realized annualized arithmetic return과 realized annualized volatility를 사용해야 한다(MUST).

```text
Sharpe_ex_post = (annualized arithmetic return - annual RF) / realized annualized volatility
```

#### Scenario: historical Sharpe
- GIVEN historical portfolio returns와 annual RF가 있다
- WHEN ex-post Sharpe를 계산한다
- THEN ex-ante expected return을 numerator로 사용하지 않는다

### Requirement: Sortino Ratio
Sortino의 monthly minimum acceptable return은 annual RF의 monthly compound-equivalent여야 한다(MUST).

```text
monthly_mar = (1 + annual_rf)^(1/12) - 1
downside = min(monthly_return - monthly_mar, 0)
downside_deviation = sqrt(mean(downside^2)) * sqrt(12)
Sortino = (annualized arithmetic return - annual_rf) / downside_deviation
```

#### Scenario: downside deviation
- GIVEN monthly returns와 annual RF가 있다
- WHEN Sortino를 계산한다
- THEN monthly MAR 아래 downside만 downside-deviation 계산에 사용한다

### Requirement: Historical performance summary
Applicable Provided/Optimized/Benchmark historical comparison은 최소 Start Balance, End Balance, CAGR, realized Annualized Return, realized Standard Deviation, Best Year, Worst Year, Maximum Drawdown, applicable ex-ante Sharpe, ex-post Sharpe, Sortino와 benchmark-relative metrics를 계산할 수 있어야 한다(MUST).

Benchmark 자체의 Active Return, Tracking Error, Information Ratio는 non-applicable이어야 하며 0으로 의미를 바꾸어서는 안 된다(MUST NOT).

#### Scenario: benchmark summary
- GIVEN benchmark series가 있다
- WHEN historical summary를 생성한다
- THEN benchmark-relative metric은 portfolio에 대해 계산하고 benchmark 자체에는 N/A semantics를 유지한다

### Requirement: Trailing return windows
Canonical trailing analytics는 3M, YTD, 1Y, 3Y annualized, 5Y annualized, 10Y annualized, Full Period CAGR, 3Y/5Y Annualized Volatility를 지원할 수 있어야 한다(MUST).

12개월 이하 total-return window는 복리 total return을 사용하고 12개월 초과 annualized return은 다음 convention을 사용해야 한다(MUST).

```text
total_return = product(1 + monthly returns) - 1
annualized = (1 + total_return)^(12 / months) - 1
```

데이터가 부족하면 N/A semantics를 유지해야 한다(MUST).

#### Scenario: insufficient 5Y history
- GIVEN 60개월보다 짧은 history가 있다
- WHEN 5Y annualized trailing return을 요청한다
- THEN 0 또는 짧은 기간 return으로 대체하지 않고 N/A로 처리한다

### Requirement: Asset performance analytics
각 Optimization asset에 대해 최소 Ticker, Name, CAGR, Annualized Return, Standard Deviation, Best Year, Worst Year, Maximum Drawdown, Sharpe, Sortino, 3M, YTD, 1Y, 3Y, 5Y, 10Y trailing analytics를 제공할 수 있어야 한다(MUST).

#### Scenario: asset-level review
- GIVEN completed Optimization run이 있다
- WHEN asset performance를 inspect한다
- THEN identity와 standalone historical return/risk/trailing evidence를 함께 확인할 수 있다

### Requirement: Monthly active return
Monthly active return은 portfolio return에서 benchmark return을 뺀 값이어야 한다(MUST).

```text
active_return_t = portfolio_return_t - benchmark_return_t
```

#### Scenario: monthly benchmark comparison
- GIVEN portfolio monthly return 2%와 benchmark 1%가 있다
- WHEN active return을 계산한다
- THEN 1%를 반환한다

### Requirement: Annualized active return
Annualized Active Return은 monthly active return arithmetic mean의 12배여야 한다(MUST). CAGR difference로 재정의해서는 안 된다(MUST NOT).

```text
annualized_active_return = mean(monthly active return) * 12
```

#### Scenario: active return vs CAGR difference
- GIVEN portfolio/benchmark CAGR difference와 arithmetic active return이 다르다
- WHEN benchmark analytics를 저장한다
- THEN 두 개념을 혼용하지 않는다

### Requirement: Tracking Error and Information Ratio
Tracking Error와 Information Ratio는 다음 convention을 사용해야 한다(MUST).

```text
tracking_error = std(monthly active return, sample) * sqrt(12)
information_ratio = annualized_active_return / tracking_error
```

Tracking Error가 0이면 Information Ratio는 unavailable/non-finite로 처리해야 한다(MUST).

#### Scenario: zero tracking error
- GIVEN portfolio와 benchmark monthly returns가 동일하다
- WHEN Information Ratio를 계산한다
- THEN divide-by-zero 값을 유효한 ratio로 저장하지 않는다

### Requirement: Annual and cumulative active return
Annual Active Return은 해당 calendar year의 portfolio annual total return과 benchmark annual total return의 차이여야 한다(MUST).

Cumulative Active Return은 cumulative portfolio wealth와 cumulative benchmark wealth의 차이여야 한다(MUST).

#### Scenario: annual active return
- GIVEN 같은 calendar year portfolio total return 12%와 benchmark 10%가 있다
- WHEN annual active return을 계산한다
- THEN 2 percentage points를 반환한다

### Requirement: Rolling active return and rolling tracking error
기본 rolling active-return window는 36 months를 지원해야 한다(MUST). 각 window에서 portfolio/benchmark total returns를 각각 annualize한 뒤 차이를 계산해야 한다(MUST).

```text
portfolio_total_W = product(1 + portfolio_monthly_return) - 1
benchmark_total_W = product(1 + benchmark_monthly_return) - 1
portfolio_ann_W = (1 + portfolio_total_W)^(12/W) - 1
benchmark_ann_W = (1 + benchmark_total_W)^(12/W) - 1
rolling_active_return = portfolio_ann_W - benchmark_ann_W
rolling_tracking_error = std(monthly active returns in window, sample) * sqrt(12)
```

#### Scenario: 36-month rolling window
- GIVEN 36 monthly observations가 있는 rolling window가 있다
- WHEN rolling active return을 계산한다
- THEN 각 side의 compounded 36-month return에 `12/36` exponent를 적용한 annualized difference를 사용한다

### Requirement: Up/Down market classification
Market classification은 canonical benchmark monthly return sign을 사용해야 한다(MUST).

```text
Up   = benchmark_return > 0
Down = benchmark_return < 0
Flat = benchmark_return == 0
```

Portfolio별 market type에 대해 portfolio mean return, benchmark mean return, mean active return, occurrences, above/below counts와 percentages, above/below일 때 mean active return을 계산할 수 있어야 한다(MUST).

#### Scenario: flat benchmark month
- GIVEN benchmark monthly return이 정확히 0이다
- WHEN market type을 분류한다
- THEN Up 또는 Down으로 임의 편입하지 않고 Flat으로 분류한다

### Requirement: Drawdown episode fields
Portfolio별 drawdown episode는 최소 Rank, Start, Bottom, Recovery, Maximum Drawdown, Duration Months를 식별할 수 있어야 한다(MUST). Recovery가 아직 발생하지 않은 episode는 unavailable 상태를 유지해야 한다(MUST).

#### Scenario: unrecovered drawdown
- GIVEN latest observation까지 이전 peak를 회복하지 못했다
- WHEN episode를 저장한다
- THEN recovery date를 fabricated future date로 채우지 않는다

### Requirement: Optimization correlation scopes
기존 Optimization analytics는 두 correlation scope를 지원한다(MUST).

1. Optimization asset monthly-return Pearson correlation matrix
2. Optimization Assets + Provided Portfolio + Optimized Portfolio + Benchmark를 포함하는 monthly-return correlation matrix

#### Scenario: portfolio/asset correlation matrix
- GIVEN Optimization assets와 Provided/Optimized/Benchmark monthly return series가 있다
- WHEN portfolio/asset correlation artifact를 생성한다
- THEN 각 series identity를 구분해 동일 aligned monthly basis에서 correlation을 계산한다

### Requirement: Return decomposition
Historical rebalancing schedule의 period-start weights를 사용해 asset return contribution과 terminal-wealth monetary contribution을 계산해야 한다(MUST).

```text
asset_return_contribution_i,t = weight_i,t * asset_return_i,t
asset_pnl_i,t = portfolio_value_(t-1) * weight_i,t * asset_return_i,t
cumulative_asset_pnl_i = sum(asset_pnl_i,t)
```

모든 asset cumulative contribution 합은 portfolio total gain과 일치해야 한다(MUST).

#### Scenario: decomposition invariant
- GIVEN completed portfolio wealth path가 있다
- WHEN asset cumulative PnL을 합산한다
- THEN portfolio terminal gain과 numerical tolerance 안에서 일치한다

### Requirement: Risk decomposition
Ex-ante annual covariance matrix 기준 component risk contribution은 다음 convention을 사용해야 한다(MUST).

```text
portfolio_variance = w.T @ Sigma @ w
RC_i = w_i * (Sigma @ w)_i / portfolio_variance
```

전체 component risk contribution 합은 1이어야 한다(MUST).

#### Scenario: risk contribution invariant
- GIVEN valid portfolio weights와 annual covariance가 있다
- WHEN component risk contributions를 계산한다
- THEN 합은 numerical tolerance 안에서 100%이다

### Requirement: Rolling portfolio returns
기본 rolling portfolio return window는 36 months와 60 months를 지원해야 한다(MUST). 12개월보다 긴 rolling total return은 다음 annualized-return convention으로 표현해야 한다(MUST).

```text
rolling_ann_return = (1 + rolling_total_return)^(12 / window_months) - 1
```

#### Scenario: five-year rolling return
- GIVEN 60-month rolling total return이 있다
- WHEN annualized rolling return을 계산한다
- THEN exponent `12/60`을 사용한다

### Requirement: Advanced metric extension requires formula and unit contract
Alpha, Beta, R-squared, Treynor Ratio, Calmar Ratio, Modigliani-Modigliani, Historical VaR 95, Skewness, Excess Kurtosis 등 advanced metric은 명시된 formula와 unit contract 없이 새 canonical metric으로 추가해서는 안 된다(MUST NOT).

#### Scenario: new advanced metric proposal
- GIVEN 새로운 metric을 report에 추가하려 한다
- WHEN canonical analytics에 포함한다
- THEN 먼저 계산 의미와 unit contract를 spec/test에서 정의한다
