## Purpose

Optimization과 Backtest가 동일한 시장 입력 의미를 공유할 수 있도록 가격, 통화, 관측기간, 수익률 입력 및 risk-free rate의 canonical behavior를 정의한다.

## ADDED Requirements

### Requirement: Canonical market data source
시스템은 v1 시장 가격 데이터의 기본 source로 FinanceDataReader(FDR)를 사용해야 한다.

#### Scenario: 기본 가격 조회
- GIVEN 지원되는 asset symbol
- WHEN 분석용 가격 데이터를 준비한다
- THEN FDR 기반 가격 series를 canonical source로 사용한다

### Requirement: Price normalization pipeline
시스템은 가격 series를 optional FX conversion, common alignment, calendar month-end price, monthly simple return, completed-month filtering 순서의 의미로 정규화해야 한다.

#### Scenario: 월별 수익률 생성
- GIVEN 일별 또는 비정기 가격 관측치가 존재한다
- WHEN monthly return matrix를 만든다
- THEN calendar month-end 가격을 기준으로 simple monthly return을 계산한다

### Requirement: Analysis period semantics
Analysis Period는 return observation period를 의미해야 하며 첫 요청 월의 return 생성에 필요한 직전 month-end 가격을 warm-up data로 사용할 수 있어야 한다.

#### Scenario: 시작월 warm-up
- GIVEN 요청 시작월의 첫 monthly return에 직전 month-end 가격이 필요하다
- WHEN 분석 데이터를 준비한다
- THEN 직전 month-end 가격을 warm-up으로 사용하되 requested return period에는 포함하지 않는다

### Requirement: Incomplete terminal month exclusion
종료일이 해당 월의 마지막 calendar date가 아니면 terminal incomplete month를 canonical monthly return series에서 제외해야 한다.

#### Scenario: 월 중간 종료일
- GIVEN analysis end가 월말 이전이다
- WHEN monthly return series를 확정한다
- THEN 해당 terminal month의 미완료 return을 제외한다

### Requirement: Common coverage
동일 분석 universe에 속한 asset들은 공통으로 관측 가능한 monthly return matrix를 사용해야 한다.

#### Scenario: listing date가 다른 asset
- GIVEN asset별 usable history 시작일이 다르다
- WHEN 공통 분석 matrix를 만든다
- THEN 모든 required asset이 동시에 관측 가능한 effective period만 사용한다

### Requirement: Coverage evidence
시스템은 requested period와 effective usable period의 차이 및 이를 제한한 asset을 식별할 수 있는 coverage 정보를 제공해야 한다.

#### Scenario: effective period 축소
- GIVEN 특정 asset의 availability로 requested start보다 실제 시작이 늦어진다
- WHEN run coverage를 기록한다
- THEN effective start/end, observation count와 limiting asset을 확인할 수 있다

### Requirement: Common currency conversion
KRW/USD 혼합 universe는 USD asset price를 USD/KRW로 환산하여 common base currency 기준에서 분석해야 한다.

#### Scenario: KRW/USD 혼합 portfolio
- GIVEN KRW asset과 USD asset이 함께 존재한다
- WHEN canonical prices를 준비한다
- THEN USD asset은 지정된 USD/KRW series를 적용한 common-base price로 변환된다

### Requirement: Unsupported currency rejection
지원하지 않는 currency는 명시적 validation error로 처리해야 한다.

#### Scenario: 지원되지 않는 통화
- GIVEN 지원 범위 밖 currency가 입력된다
- WHEN market data configuration을 검증한다
- THEN silent conversion 없이 명시적 validation error를 반환한다

### Requirement: Canonical risk-free modes
시스템은 risk-free rate에 `us_3m_tbill`과 `fixed` mode를 지원하고 기본 mode를 `us_3m_tbill`로 사용해야 한다.

#### Scenario: 기본 risk-free mode
- GIVEN 사용자가 별도 fixed rate를 요청하지 않았다
- WHEN analysis configuration을 확정한다
- THEN `us_3m_tbill` mode가 적용된다

#### Scenario: 명시적 fixed rate
- GIVEN 사용자가 fixed annual rate를 명시했다
- WHEN risk-free configuration을 확정한다
- THEN 입력 annual rate를 effective annual risk-free rate로 사용한다

### Requirement: Effective risk-free evidence
시스템은 각 run에서 requested risk-free mode와 실제 사용한 effective annual rate를 확인할 수 있어야 한다.

#### Scenario: T-Bill run
- GIVEN `us_3m_tbill` mode로 run을 수행한다
- WHEN 결과 artifact를 확인한다
- THEN requested mode와 effective annual rate가 함께 기록되어 있다
