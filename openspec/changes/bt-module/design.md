## Context

이번 변경은 기존 Optimization 제품에 독립적인 Portfolio Backtest 제품 capability를 추가한다. 기능 및 화면 구조의 1차 설계 레퍼런스는 아래에 보관한 Portfolio Visualizer Backtest Portfolio snapshot이다.

- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml`
- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/`

레퍼런스는 외부 비규범 자료다. PV의 계산값, 구현 방식, hidden field, UI 문구 자체는 acceptance criterion이 아니다. 내부 OpenSpec requirement가 최종 source of truth다.

PV snapshot에서 확인한 핵심 구조는 Settings와 Portfolio Assets 입력, 최대 3개 portfolio 비교, benchmark, initial amount, 다양한 rebalancing 선택, cashflow/leverage 등 advanced option, 그리고 performance/active return/drawdown/rolling return/asset 분석 결과다.

## Goals

- Optimization과 분리된 Backtest 실행 경계를 만든다.
- 최대 3개의 named portfolio를 동일 기간과 benchmark에서 비교한다.
- 기존 `market-data`, `portfolio-simulation`, `portfolio-analytics`, `run-artifacts`, `research-report`를 의미가 같은 범위에서 재사용한다.
- PV에서 유용한 입력 및 결과 정보구조를 참고하되 내부 데이터/계산 capability와 맞지 않는 기능을 억지로 복제하지 않는다.
- shared capability 변경이 Optimization에도 영향을 주면 affected regression을 명시한다.

## Product Boundary

`portfolio-backtest`는 다음을 소유한다.

- Backtest run의 product identity
- 비교할 portfolio 정의와 이름
- portfolio별 target allocation
- optional benchmark 선택
- analysis period와 initial balance 입력
- Backtest에 적용할 rebalancing policy 선택
- Backtest 결과에서 어떤 portfolio들을 비교하는지에 대한 product-level contract

공통 계산 공식과 presentation contract는 shared capability가 소유한다.

## PV Reference Mapping

### Adopt for initial specification

- Settings / Portfolio Assets의 분리된 입력 개념
- 최대 3개 portfolio와 custom portfolio name
- shared asset grid에서 portfolio별 allocation 입력
- optional benchmark ticker
- initial amount
- 동일 기간에서 여러 portfolio 비교
- No / Monthly / Quarterly / Semi-annual / Annual rebalancing
- allocation, performance summary, wealth/growth, annual/monthly return, drawdown, rolling return, asset performance, benchmark-relative analytics의 비교 구조

### Reuse existing shared behavior

- market data 수집, FX, common coverage, monthly canonical returns
- CAGR, realized risk, Sharpe/Sortino, MDD, trailing/annual/monthly/rolling analytics
- active return, tracking error, information ratio, Up/Down, correlation, return/risk decomposition
- persisted run artifacts와 self-contained research report

단순 재사용은 이 change의 shared capability delta로 만들지 않는다.

### Not copied into initial normative requirements

아래 PV 기능은 snapshot에서 존재를 확인했지만 현재 internal semantics 또는 data ownership이 충분히 정의되지 않아 initial normative requirement에 넣지 않는다.

- fixed contribution / withdrawal / percentage withdrawal와 inflation adjustment
- rebalance bands의 absolute / relative deviation
- leverage, debt interest, maintenance margin, leveraged benchmark
- dividend reinvestment toggle과 income display
- style analysis, factor regression, regime performance
- PV provider 기반 equity size/sector/style exposure
- imported benchmark / imported portfolio / lazy portfolio preset
- `calendarAligned = false` 같은 non-calendar periodic schedule

이 항목들은 제외 확정이 아니라 user decision 또는 후속 capability proposal 대상이다.

## Rebalancing Design

현재 canonical simulation은 monthly return matrix를 사용한다. Backtest v1의 periodic rebalancing은 calendar-aligned monthly observations 위에서 정의한다.

- `none`: 최초 active period에 target weights를 적용한 뒤 계속 drift
- `monthly`: 매 active month 시작에 target weights 적용
- `quarterly`: 최초 active period와 1/4/7/10월의 첫 available active month에 target weights 적용
- `semiannual`: 최초 active period와 1/7월의 첫 available active month에 target weights 적용
- `yearly`: 최초 active period와 각 calendar year의 첫 available active month에 target weights 적용

Analysis가 schedule 중간에서 시작하면 첫 active period에는 target weights를 적용한다. 이후 calendar schedule을 따른다.

## Portfolio Comparison Model

PV의 allocation grid처럼 asset universe는 비교 portfolio의 union으로 표현할 수 있다. 각 portfolio는 같은 asset row set을 공유하되 사용하지 않는 asset의 weight는 0으로 둘 수 있다.

각 portfolio의 target weight 합은 100%여야 한다. 서로 다른 portfolio는 같은 market return matrix를 사용하더라도 독립적인 drift/rebalancing/wealth path를 가진다.

## Result Model

Backtest는 optimization-specific ex-ante statistic이나 Efficient Frontier를 생성하지 않는다. 결과는 historical/realized shared analytics를 중심으로 구성한다.

Backtest-specific result identity는 최소 다음을 구분해야 한다.

- run configuration
- portfolio definitions and target allocations
- effective data coverage
- portfolio return/wealth/weight paths
- optional benchmark path
- shared historical analytics
- shared comparison/report data

## UI / Report Direction

PV처럼 입력과 결과를 같은 기능 흐름 안에서 이해하기 쉽게 배치하되 PV pixel layout을 복제하지 않는다.

Backtest result에서는 최소 다음 information hierarchy를 유지한다.

1. run period / benchmark / rebalancing / portfolio identities
2. target allocation 비교
3. growth / balance path와 performance summary
4. annual / monthly / trailing / rolling return
5. drawdown
6. asset performance와 correlation/decomposition
7. benchmark가 있을 때 active analytics

Report browser는 persisted canonical finance values를 재계산하지 않는다.

## Open Decisions

아래는 PV snapshot만으로 내부 semantics를 확정할 수 없거나 initial scope 비용이 큰 항목이다.

1. Cashflow를 v1에 포함할지, 포함한다면 contribution/withdrawal의 적용 시점과 performance metric convention을 무엇으로 할지
2. Rebalance bands를 v1에 포함할지
3. Leverage를 v1에 포함할지
4. Backtest portfolio 최대 개수를 PV와 동일하게 3개로 고정할지, internal limit을 더 크게 둘지
5. Dividend reinvestment/income을 별도 option으로 모델링할지, canonical market-data total-return semantics에 맡길지

이 결정 전에는 해당 기능을 normative acceptance requirement로 만들지 않는다.
