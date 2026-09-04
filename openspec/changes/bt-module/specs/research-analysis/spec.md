## Purpose

LLM이 Optimization과 Backtest 결과를 혼동하지 않고 `product_mode`에 따라 올바른 해석 branch를 선택하는 연구 분석 behavior를 정의한다.

Canonical LLM analysis guide는 별도 product 문서로 분리하지 않고 `docs/llm-analysis-framework.md` 하나로 유지한다. 해당 문서 안에서 Optimization과 Backtest branch를 명시적으로 분기한다.

## ADDED Requirements

### Requirement: Product-mode analysis routing
LLM은 canonical Run artifact의 explicit `product_mode`를 확인한 뒤 Optimization 또는 Backtest analysis branch를 선택해야 한다(MUST).

`product_mode`가 없거나 지원되지 않는 값이면 결과 내용만 보고 LLM이 임의로 product를 추론해서는 안 된다(MUST NOT).

#### Scenario: Optimization 결과 분석
- GIVEN `product_mode: optimization`인 Run이 존재한다
- WHEN LLM이 결과를 분석한다
- THEN `docs/llm-analysis-framework.md`의 Optimization Analysis Branch를 사용한다

#### Scenario: Backtest 결과 분석
- GIVEN `product_mode: backtest`인 Run이 존재한다
- WHEN LLM이 결과를 분석한다
- THEN 같은 `docs/llm-analysis-framework.md`의 Backtest Analysis Branch를 사용하고 Efficient Frontier/optimizer structure 단계는 적용하지 않는다

### Requirement: Backtest analysis is historical comparison
Backtest 분석은 이미 정의된 portfolio들의 historical realized behavior를 비교해야 하며 결과를 Optimization 또는 optimal allocation의 증거로 표현해서는 안 된다(MUST NOT).

#### Scenario: 한 portfolio가 더 높은 Sharpe를 보임
- GIVEN Backtest에서 Portfolio A의 realized Sharpe가 Portfolio B보다 높다
- WHEN 결과를 해석한다
- THEN 해당 역사 표본에서의 risk-adjusted performance 차이로 설명하고 A가 최적 portfolio라고 단정하지 않는다

### Requirement: Data coverage first
LLM은 서로 다른 portfolio를 비교하기 전에 requested/effective period와 limiting asset로 인한 coverage 차이가 비교 의미를 훼손하지 않는지 확인해야 한다(MUST).

#### Scenario: 짧은 history asset
- GIVEN 한 portfolio의 asset 때문에 effective period가 크게 줄었다
- WHEN 결과를 설명한다
- THEN 성과 차이보다 먼저 실제 공통 비교기간이 제한되었음을 밝힌다

### Requirement: Performance and risk comparison
LLM은 사용자 질문에 필요한 범위에서 CAGR/realized return, volatility, Sharpe/Sortino, MDD, Best/Worst period 등 canonical historical metrics를 이용해 portfolio 차이를 설명해야 한다(MUST).

CAGR, arithmetic annualized return, active return은 계산 의미가 다르면 동일한 수익률 개념으로 혼용해서는 안 된다(MUST NOT).

#### Scenario: 수익과 위험 trade-off
- GIVEN Portfolio A는 CAGR이 높고 Portfolio B는 MDD와 volatility가 낮다
- WHEN 어느 쪽이 더 나았는지 설명한다
- THEN 한 지표만으로 승자를 정하지 않고 관측된 return/risk trade-off를 함께 설명한다

### Requirement: Drawdown and recovery emphasis
Backtest 분석은 평균 성과뿐 아니라 주요 drawdown의 깊이, duration, recovery 특성을 portfolio별로 비교할 수 있어야 한다(MUST).

#### Scenario: CAGR이 비슷한 두 portfolio
- GIVEN 두 portfolio의 CAGR은 유사하지만 drawdown 구조가 다르다
- WHEN 사용자에게 차이를 설명한다
- THEN drawdown depth/duration/recovery 차이를 핵심 비교 근거로 사용할 수 있다

### Requirement: Rolling and period consistency
Full-period 성과만으로 안정성을 단정하지 않고 available rolling/annual/monthly 결과를 사용해 성과의 시간 분산과 특정 구간 의존성을 확인해야 한다(MUST).

#### Scenario: full-period 우수하지만 rolling 열세가 빈번함
- GIVEN Portfolio A가 full-period CAGR은 높지만 rolling 3Y 결과가 여러 구간에서 열세다
- WHEN robustness를 설명한다
- THEN full-period 숫자만으로 일관된 우위라고 표현하지 않는다

### Requirement: Benchmark-relative analysis is conditional
Benchmark가 존재하는 경우에만 active return, tracking error, information ratio, rolling active, Up/Down 분석을 사용해야 한다(MUST).

#### Scenario: benchmark 없음
- GIVEN Backtest run에 benchmark가 없다
- WHEN 결과를 분석한다
- THEN benchmark-relative metric을 0으로 간주하거나 가상의 benchmark를 추가하지 않는다

### Requirement: Correlation structure is an explicit analysis step
Backtest analysis는 correlation을 독립적인 구조 evidence로 다루고 asset redundancy, independent movement, benchmark relationship을 확인해야 한다(MUST).

Correlation matrix를 단순 나열하거나 낮은 correlation 하나만으로 diversification utility를 확정해서는 안 된다(MUST NOT).

#### Scenario: 낮은 correlation asset
- GIVEN 특정 asset이 다른 asset과 낮은 correlation을 보인다
- WHEN portfolio utility를 설명한다
- THEN 실제 allocation/contribution/drawdown evidence 없이 낮은 correlation만으로 필수 diversifier라고 단정하지 않는다

#### Scenario: stress diversification evidence 부족
- GIVEN full-period correlation은 낮지만 stress conditional correlation artifact가 없다
- WHEN crisis diversification을 설명한다
- THEN stress에서도 독립적이었다고 단정하지 않고 evidence gap으로 남긴다

### Requirement: Contribution and diversification interpretation
Return/risk decomposition과 allocation, correlation, drawdown evidence를 함께 사용해 portfolio 차이를 설명해야 한다(MUST).

#### Scenario: 작은 return contribution의 diversifier
- GIVEN 특정 asset의 return contribution은 작지만 allocation과 drawdown/risk evidence가 존재한다
- WHEN 해당 asset의 역할을 설명한다
- THEN standalone return만으로 불필요하다고 판단하지 않고 실제 portfolio-level risk/diversification evidence를 함께 본다

### Requirement: Fact and interpretation separation
LLM은 canonical result에서 직접 관측된 사실과 그 사실에 대한 해석 또는 가설을 구분해야 한다(MUST).

#### Scenario: 특정 기간 성과 원인 추정
- GIVEN report에는 특정 asset의 return contribution만 있고 경제적 원인 데이터는 없다
- WHEN 원인을 설명한다
- THEN contribution은 관측 사실로, 경제적 원인은 추가 evidence가 필요한 해석으로 구분한다

### Requirement: Next research follows evidence gaps
현재 Backtest만으로 결론이 부족하면 기간 변경, rebalancing 비교, portfolio 구성 변경 등 구체적인 후속 실험을 제안할 수 있어야 한다(MUST).

#### Scenario: 특정 한 기간에만 우위
- GIVEN portfolio 우위가 특정 historical 구간에 집중되어 있다
- WHEN robustness 결론이 부족하다
- THEN 다른 기간 또는 조건의 follow-up Backtest를 다음 연구로 제안한다
