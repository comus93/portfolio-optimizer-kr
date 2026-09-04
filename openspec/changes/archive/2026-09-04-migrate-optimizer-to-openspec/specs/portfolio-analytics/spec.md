## Purpose

생성된 historical portfolio/benchmark/asset return path를 동일한 공통 규칙으로 평가하는 realized performance, benchmark-relative, decomposition 및 rolling analytics behavior를 정의한다.

## ADDED Requirements

### Requirement: Wealth convention
시스템은 historical return series의 canonical normalized wealth를 1.0에서 시작해 cumulative product로 계산해야 한다.

#### Scenario: normalized wealth
- GIVEN monthly return series가 있다
- WHEN wealth path를 생성한다
- THEN 시작값은 1.0이며 이후 값은 누적 `product(1 + return_t)`를 반영한다

### Requirement: CAGR
시스템은 `years = monthly_observations / 12`를 사용하고 `CAGR = terminal_wealth^(1 / years) - 1`로 계산해야 한다.

#### Scenario: full-period CAGR
- GIVEN 60개의 monthly observations와 terminal wealth가 있다
- WHEN CAGR을 계산한다
- THEN years=5 convention으로 annualized growth를 반환한다

### Requirement: Realized annualized return and volatility
시스템은 realized annualized return을 `mean(monthly returns) * 12`, realized standard deviation을 sample standard deviation에 `sqrt(12)`를 곱해 계산해야 한다.

#### Scenario: realized statistics
- GIVEN historical monthly returns가 있다
- WHEN annualized return과 volatility를 계산한다
- THEN arithmetic annualization과 sample-volatility annualization convention을 사용한다

### Requirement: Annual returns
Calendar year return은 해당 year에 실제로 available한 monthly observations를 복리 결합해야 한다.

#### Scenario: partial calendar year
- GIVEN 첫해에 일부 completed months만 존재한다
- WHEN annual return을 계산한다
- THEN available months의 `product(1 + monthly_return) - 1`을 사용하며 partial year를 제거하지 않는다

### Requirement: Maximum drawdown
시스템은 cumulative wealth 대비 running peak의 최저 비율로 Maximum Drawdown을 계산해야 한다.

#### Scenario: drawdown 계산
- GIVEN historical wealth path가 있다
- WHEN drawdown series를 계산한다
- THEN `drawdown_t = wealth_t / running_peak_t - 1`이며 MDD는 해당 series의 minimum이다

### Requirement: Drawdown episodes
시스템은 portfolio별 drawdown episode를 독립적으로 계산하고 Rank, Start, Bottom, Recovery, Maximum Drawdown, Duration Months를 제공해야 한다.

#### Scenario: 미회복 episode
- GIVEN 분석 종료 시점까지 회복되지 않은 drawdown이 있다
- WHEN drawdown episodes를 생성한다
- THEN recovery는 unavailable 상태로 유지한다

### Requirement: Ex-post Sharpe
시스템은 `(annualized arithmetic return - effective annual RF) / realized annualized volatility`로 ex-post Sharpe Ratio를 계산해야 한다.

#### Scenario: portfolio Sharpe
- GIVEN historical returns와 effective annual RF가 있다
- WHEN ex-post Sharpe를 계산한다
- THEN realized return/volatility와 market-data capability가 제공한 RF를 사용한다

### Requirement: Sortino Ratio
시스템은 annual RF를 monthly compound-equivalent MAR로 변환하고 downside deviation을 기준으로 Sortino Ratio를 계산해야 한다.

#### Scenario: Sortino 계산
- GIVEN historical monthly returns와 effective annual RF가 있다
- WHEN Sortino를 계산한다
- THEN `monthly_mar = (1 + annual_rf)^(1/12) - 1`과 `downside = min(return - monthly_mar, 0)` convention을 사용한다

### Requirement: Trailing returns
시스템은 3M, YTD, 1Y, 3Y annualized, 5Y annualized, 10Y annualized, Full Period CAGR 및 3Y/5Y Annualized Volatility를 계산할 수 있어야 한다.

#### Scenario: 부족한 lookback
- GIVEN 요청 trailing window보다 historical observations가 적다
- WHEN trailing metric을 계산한다
- THEN 해당 metric을 unavailable로 반환한다

#### Scenario: multi-year annualization
- GIVEN 12개월을 초과하는 trailing window가 충분하다
- WHEN trailing annualized return을 계산한다
- THEN `(1 + total_return)^(12 / months) - 1`을 사용한다

### Requirement: Asset performance analytics
시스템은 분석 asset별 CAGR, Annualized Return, Standard Deviation, Best/Worst Year, Maximum Drawdown, Sharpe, Sortino 및 canonical trailing returns를 계산할 수 있어야 한다.

#### Scenario: asset performance table source
- GIVEN common monthly return matrix가 있다
- WHEN asset-level analytics를 계산한다
- THEN 각 asset identity에 독립된 performance metrics를 제공한다

### Requirement: Monthly active return
시스템은 benchmark가 있을 때 `active_return_t = portfolio_return_t - benchmark_return_t`로 monthly active return을 계산해야 한다.

#### Scenario: monthly active series
- GIVEN portfolio와 benchmark의 동일 월 return이 있다
- WHEN active return을 계산한다
- THEN 두 monthly return의 차이를 반환한다

### Requirement: Annualized active return, tracking error, information ratio
시스템은 annualized active return을 monthly active return 평균의 12배, tracking error를 sample standard deviation의 `sqrt(12)`배, information ratio를 두 값의 비율로 계산해야 한다.

#### Scenario: benchmark-relative metrics
- GIVEN 충분한 monthly active returns가 있다
- WHEN active analytics를 계산한다
- THEN canonical annualization 규칙을 적용한다

#### Scenario: zero tracking error
- GIVEN tracking error가 0이다
- WHEN Information Ratio를 계산한다
- THEN unavailable/non-finite로 취급한다

### Requirement: Benchmark-relative N/A semantics
Benchmark 자체의 Active Return, Tracking Error, Information Ratio는 conceptually not applicable로 처리해야 한다.

#### Scenario: benchmark summary
- GIVEN benchmark summary metrics를 표시한다
- WHEN benchmark-relative rows를 구성한다
- THEN 0이 아니라 N/A 의미를 유지한다

### Requirement: Annual and cumulative active return
시스템은 annual active return을 portfolio annual total에서 benchmark annual total을 뺀 값으로, cumulative active return을 cumulative portfolio wealth와 benchmark wealth의 차이로 계산해야 한다.

#### Scenario: annual active return
- GIVEN 같은 calendar year의 portfolio와 benchmark annual totals가 있다
- WHEN annual active return을 계산한다
- THEN 두 annual total return의 차이를 사용한다

### Requirement: Rolling active return
기본 rolling active window는 36개월이며 각 window에서 portfolio와 benchmark total return을 각각 annualize한 뒤 그 차이를 rolling active return으로 계산해야 한다.

#### Scenario: 36개월 rolling active
- GIVEN 36개월 portfolio/benchmark returns가 있다
- WHEN rolling active return을 계산한다
- THEN 각각의 compound total return에 exponent `12/36`을 적용한 annualized return의 차이를 사용한다

### Requirement: Rolling tracking error
Rolling tracking error는 동일 window의 monthly active return sample standard deviation에 `sqrt(12)`를 곱해 계산해야 한다.

#### Scenario: rolling active risk
- GIVEN 36개월 monthly active return window가 있다
- WHEN rolling tracking error를 계산한다
- THEN annualized sample standard deviation을 반환한다

### Requirement: Up and Down market classification
Market type은 canonical benchmark monthly return의 sign으로 Up(>0), Down(<0), Flat(=0)을 분류해야 한다.

#### Scenario: market classification
- GIVEN benchmark monthly return이 양수다
- WHEN 해당 observation을 분류한다
- THEN Up market observation으로 처리한다

### Requirement: Up and Down conditional statistics
시스템은 portfolio별 market type에 대해 portfolio mean return, benchmark mean return, mean active return, occurrence/count statistics, benchmark 초과/미달 count와 conditional active return 통계를 계산할 수 있어야 한다.

#### Scenario: Down market statistics
- GIVEN 여러 Down market observations가 있다
- WHEN conditional statistics를 계산한다
- THEN 해당 observations만 사용한 count와 average metrics를 제공한다

### Requirement: Correlations
시스템은 canonical monthly simple returns를 사용해 asset correlation 및 portfolio/asset/benchmark correlation을 Pearson correlation으로 계산해야 한다.

#### Scenario: portfolio/asset matrix
- GIVEN asset returns와 generated portfolio/benchmark returns가 있다
- WHEN combined correlation matrix를 계산한다
- THEN 각 identity가 유지된 Pearson correlation matrix를 제공한다

### Requirement: Return decomposition
Historical return contribution은 해당 period 시작 weight에 asset return을 곱해 계산하며 cumulative monetary contribution의 합은 portfolio total gain과 일치해야 한다.

#### Scenario: cumulative contribution invariant
- GIVEN historical portfolio path와 period-start weights가 있다
- WHEN asset별 cumulative PnL contribution을 계산한다
- THEN 모든 asset contribution 합은 portfolio total gain과 일치한다

### Requirement: Risk decomposition
시스템은 supplied annual covariance matrix와 portfolio weights를 사용해 `RC_i = w_i * (Sigma @ w)_i / (w.T @ Sigma @ w)`로 component risk contribution을 계산해야 한다.

#### Scenario: risk contribution invariant
- GIVEN valid weights와 annual covariance matrix가 있다
- WHEN risk decomposition을 계산한다
- THEN 모든 component risk contribution의 합은 1이다

### Requirement: Rolling portfolio returns
시스템은 기본 36개월과 60개월 rolling portfolio return을 지원하고 12개월 초과 window는 annualized return으로 표현해야 한다.

#### Scenario: 60개월 rolling return
- GIVEN 60개월 이상의 monthly observations가 있다
- WHEN rolling 5-year return을 계산한다
- THEN 각 window의 compound total return을 `(1 + total)^(12/60) - 1`로 annualize한다

### Requirement: Advanced historical metrics contract
Alpha, Beta, R-squared, Treynor Ratio, Calmar Ratio, Modigliani-Modigliani, Historical VaR 95, Skewness, Excess Kurtosis는 calculation formula와 unit contract가 정의된 항목만 canonical metric으로 제공할 수 있다.

#### Scenario: 새 advanced metric 추가
- GIVEN 새로운 metric을 report에 노출하려 한다
- WHEN canonical analytics에 추가한다
- THEN 계산식과 unit contract가 먼저 정의되어 있어야 한다
