## Context

이번 변경은 기존 Optimization 제품에 독립적인 Portfolio Backtest 제품 capability를 추가한다.

Backtest 기능 및 화면 구조의 외부 설계 레퍼런스는 아래에 보관한 Portfolio Visualizer Backtest Portfolio snapshot이다.

- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml`
- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/`

PV snapshot에서 Settings / Portfolio Assets, 최대 3개 portfolio 비교, benchmark, initial amount, periodic rebalancing, advanced option, performance/active/drawdown/rolling/asset 분석 구조를 확인했다.

단, PV는 외부 비규범 자료다. PV의 계산값, 구현 방식, hidden field, UI 문구, pixel layout 자체는 acceptance criterion이 아니다.

## Internal Design Baseline

Backtest 설계는 PV를 그대로 복제하지 않고 기존 프로젝트 내부 contract 위에 확장한다. 적용 baseline은 다음과 같다.

```text
Finance / calculation behavior   docs/specification.md
Report UI / interaction          docs/report-ui-specification.md
Input / YAML / runner / viewer   docs/input-ui-contract.md
Architecture / responsibility    docs/architecture.md
Validation procedure             docs/visual-acceptance-contract.md
External feature reference       PV Backtest snapshot
```

따라서 새 Backtest requirement를 작성할 때 `docs/specification.md`의 계산 의미뿐 아니라 기존 UI/interaction, YAML/runner/viewer, architecture 책임 경계도 함께 보존한다.

PV는 기존 internal contract에 없는 Backtest-specific product concept과 information architecture를 채우는 레퍼런스로 사용한다. 기존 internal contract와 충돌하는 PV behavior는 자동 채택하지 않는다.

## Goals

- Optimization과 분리된 Backtest 실행 경계를 만든다.
- v1에서 최대 3개의 named portfolio를 동일 기간과 benchmark에서 비교한다.
- canonical portfolio model은 collection 기반으로 두어 향후 3개 초과 확장이 schema 재설계 없이 가능하게 한다.
- 기존 `market-data`, `portfolio-simulation`, `portfolio-analytics`, `run-artifacts`, `research-report`를 의미가 같은 범위에서 재사용한다.
- 기존 YAML runner, persistence, viewer architecture를 우회하는 별도 Backtest 실행경로를 만들지 않는다.
- PV에서 유용한 입력 및 결과 정보구조를 참고하되 내부 데이터/계산 capability와 맞지 않는 기능을 억지로 복제하지 않는다.
- shared capability 변경이 Optimization에도 영향을 주면 affected regression을 명시한다.

## Product and Shared Capability Boundary

Optimization과 Backtest의 차이는 주로 **portfolio weights가 어디에서 오고 무엇을 산출하려는가**에 있다. Portfolio weights와 historical return path가 확정된 이후의 계산은 가능한 한 같은 shared pipeline을 사용한다.

```text
Optimization
market-data
  → ex-ante estimation / constraints / objective / efficient frontier
  → optimized or provided target weights
  → portfolio-simulation
  → portfolio-analytics
  → run-artifacts / research-report

Backtest
market-data
  → user-defined target weights
  → portfolio-simulation
  → portfolio-analytics
  → run-artifacts / research-report
```

### Product-specific: `portfolio-optimization`

Optimization만 소유하는 behavior:

- expected return / covariance / expected volatility / ex-ante Sharpe
- min/max constraints, long-only fully-invested constraint
- Maximum Sharpe / Target Volatility objective
- solver result와 residual validation
- Efficient Frontier 및 frontier allocation
- Optimization 전용 입력 surface와 ex-ante result identity

분리 이유는 이 단계가 historical portfolio 평가가 아니라 시장 관측치에서 portfolio weights를 생성하는 의사결정 계산이기 때문이다. Backtest는 이 계산을 요구하지 않는다.

### Product-specific: `portfolio-backtest`

Backtest만 소유하는 behavior:

- Backtest product mode와 run identity
- 비교할 named portfolio collection
- portfolio별 user-defined target allocation
- v1 사용자-facing portfolio 비교 한도 3개
- optional benchmark 선택
- initial balance 입력
- portfolio별 rebalancing policy 선택
- Optimization objective/constraint 없이 historical comparison을 수행하는 product contract

분리 이유는 Backtest의 목적이 weights를 찾는 것이 아니라 사용자가 이미 정의한 portfolio를 동일 historical 조건에서 비교하는 것이기 때문이다.

### Shared: `market-data`

Optimization과 Backtest가 공통으로 사용한다.

- canonical market data source 및 normalization
- FX/common currency
- requested/effective period와 common coverage
- completed-month filtering 및 monthly return matrix
- canonical total-return semantics
- risk-free rate와 effective RF evidence

공유 이유는 같은 asset/period를 분석하면서 두 product가 서로 다른 historical return series를 사용하면 Optimization 결과의 historical 평가와 Backtest 결과가 직접 비교될 수 없기 때문이다.

### Shared: `portfolio-simulation`

Optimization과 Backtest가 target weights를 받은 이후 공통으로 사용한다.

- target weights + asset returns → portfolio return path
- weight drift
- rebalancing schedule의 계산 semantics
- benchmark path
- normalized/initial-balance wealth path

Backtest가 `none`, quarterly, semiannual 등 더 많은 policy를 요구하더라도 simulation engine은 shared capability에 둔다. 특정 product가 모든 policy를 UI에서 노출해야 한다는 뜻은 아니다.

공유 이유는 동일 target weights와 동일 rebalancing policy라면 그 weights가 optimizer에서 왔든 사용자가 입력했든 historical path가 동일해야 하기 때문이다.

### Shared: `portfolio-analytics`

모든 realized/historical metric을 공통으로 사용한다.

- CAGR, annualized return/volatility
- Sharpe/Sortino, MDD, drawdown episodes
- annual/monthly/trailing/rolling returns
- active return, tracking error, information ratio
- Up/Down analytics
- correlations
- return/risk decomposition

공유 이유는 동일 historical return path에 대해 product에 따라 CAGR/MDD/Sharpe 계산식이 달라지는 것을 막기 위해서다.

### Shared: `run-artifacts`

저장 방식과 재현성 contract는 공통으로 사용한다.

- YAML run contract
- CLI/UI/Agent가 같은 YAML runner 경로로 수렴하는 execution contract
- exact `input.yaml`
- canonical `result.json`
- raw/review artifacts
- validation evidence
- self-contained report artifact
- persisted run을 재실행 없이 여는 Viewer independence

단, `product mode`에 따라 Optimization-specific result domain과 Backtest-specific result domain은 분리한다.

### Shared: `research-report`

기존 `docs/report-ui-specification.md`의 표현/interaction contract를 공유한다.

- finance value를 browser에서 재계산하지 않는 boundary
- human-readable portfolio/benchmark identity
- asset Name + Ticker identity where available
- %, ratio, currency, date unit semantics
- missing != zero, unavailable은 `N/A`
- semantic axis와 meaningful tooltip
- required table/metric preservation
- series identity 보존과 color-only identity 금지
- responsive layout에서 information meaning 보존
- Performance Summary, annual/monthly/trailing/rolling, drawdown, correlations, decomposition 등 shared sections

Optimization-only Efficient Frontier와 Backtest-specific overview/allocation/growth comparison은 section applicability로 분리한다.

## Why This Boundary

핵심 원칙은 **portfolio 생성과 portfolio 평가를 분리**하는 것이다.

- Optimization은 portfolio를 생성한다.
- Backtest는 정의된 portfolio를 평가한다.
- 생성 이후의 historical simulation/analytics는 동일해야 한다.

이 구조는 중복 구현을 막고, 계산 convention divergence를 방지하며, shared capability 변경이 두 product에 미치는 regression 범위를 명확히 한다.

예를 들어 total-return semantics를 바꾸면 두 product의 historical 결과가 모두 영향을 받으므로 `market-data` shared change다. 반대로 Maximum Sharpe solver behavior를 바꿔도 Backtest에는 영향이 없으므로 `portfolio-optimization` change다.

## Input / Runner / Viewer Design

기존 `docs/input-ui-contract.md`의 execution architecture를 Backtest에도 적용한다.

```text
Input UI / CLI / Agent
        ↓
      YAML
        ↓
YAML adapter + validator
        ↓
product-specific canonical request
        ↓
shared runner / pipeline
        ↓
canonical result + raw/review
        ↓
Viewer / report
```

Backtest UI는 별도의 finance execution path를 만들지 않는다. UI에서 구성한 Backtest input도 canonical YAML contract를 거쳐 runner로 전달한다.

UI와 Viewer는 논리적으로 독립한다. 완료된 Backtest run은 `result.json`, raw/review, report artifact로 다시 simulation하지 않고 열 수 있어야 한다.

Backtest request model은 OptimizationRequest를 억지로 재사용하지 않는다. Product-specific request boundary는 분리하되 runner 이후 shared market-data/simulation/analytics를 재사용한다.

## PV Reference Mapping

### Adopt for v1 specification

- Settings / Portfolio Assets의 분리된 정보구조
- v1 최대 3개 named portfolio와 custom portfolio name
- shared asset grid에서 portfolio별 allocation 입력
- optional benchmark ticker
- initial amount
- 동일 기간에서 여러 portfolio 비교
- No / Monthly / Quarterly / Semi-annual / Annual rebalancing
- allocation, performance summary, wealth/growth, annual/monthly return, drawdown, rolling return, asset performance, benchmark-relative analytics의 비교 구조

### Reuse existing internal/shared behavior

- asset search/add/remove/edit와 YAML preview/save/execute/open-existing-run 흐름
- market data 수집, FX, common coverage
- CAGR, realized risk, Sharpe/Sortino, MDD, trailing/annual/monthly/rolling analytics
- active return, tracking error, information ratio, Up/Down, correlation, return/risk decomposition
- persisted run artifacts와 self-contained research report
- report identity/unit/N/A/semantic-axis/tooltip/responsive behavior

단순 재사용은 이 change의 shared capability delta로 만들지 않는다.

## Confirmed V1 Scope Decisions

- Cashflow: v1 제외
- Rebalance bands: v1 제외
- Leverage: v1 제외
- Portfolio count: v1 사용자-facing 최대 3개. 단 canonical schema와 internal model은 fixed `portfolio1/2/3` field가 아니라 extensible collection으로 정의
- Dividend handling: Backtest별 reinvest toggle을 두지 않고 shared market-data의 canonical total-return semantics 사용

추가로 PV에 존재하는 style analysis, factor regression, regime performance, provider 기반 exposure, imported benchmark/portfolio, lazy portfolio preset, non-calendar schedule은 v1 범위에 포함하지 않는다.

## Total-return Design

Optimization과 Backtest 모두 동일 canonical total-return series를 사용한다. 배당을 별도 Backtest option으로 처리하지 않는다.

- asset return은 price change만이 아니라 distribution reinvestment를 반영한 total return 의미여야 한다.
- total-return-capable source/derivation을 확보할 수 없는 asset을 price-only return으로 조용히 대체해서는 안 된다.
- 구체적인 data source 또는 dividend-adjustment 구현 방식은 market-data implementation design에서 결정한다.

이 변경은 Optimization historical analysis에도 영향을 주므로 implementation 시 Optimization affected regression을 포함한다.

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

v1 UI와 validation은 최대 3개 portfolio를 허용하지만 canonical configuration/result는 portfolio collection으로 표현한다. 따라서 향후 한도 증가 시 `portfolio_4` 같은 신규 schema field를 추가하는 방식이 아니라 collection limit만 확장할 수 있어야 한다.

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

Backtest input은 run/settings와 portfolio asset/allocation 편집의 의미를 구분한다. 이것은 PV의 정보구조를 참고하되 exact tab/pixel layout을 요구하지 않는다.

Backtest result에서는 최소 다음 information hierarchy를 유지한다.

1. run identity / requested-effective period / benchmark / rebalancing / portfolio identities
2. target allocation 비교
3. growth / balance path와 Performance Summary
4. annual / monthly / trailing / rolling return
5. drawdown
6. asset performance와 correlation/decomposition
7. benchmark가 있을 때 active analytics

기존 report contract를 그대로 적용한다.

- user-facing identity는 generic internal key가 아니라 이름으로 구분한다.
- unavailable value는 0으로 꾸며내지 않고 `N/A` 또는 non-applicable로 처리한다.
- chart는 실제 date/year/value semantic axis를 사용한다.
- hover는 같은 비교 시점의 portfolio/benchmark 값을 이해할 수 있는 identity와 value를 제공한다.
- desktop/mobile 모두 필수정보를 clipping이나 과도한 축소로 잃지 않는다.
- Report browser는 persisted canonical finance values를 재계산하지 않는다.

## Validation Direction

`docs/visual-acceptance-contract.md`의 역할 분리를 유지한다.

```text
Calculation contract verification
→ Report semantic verification
→ Browser acceptance
```

PV와의 pixel parity는 completion 기준이 아니다. Backtest acceptance는 OpenSpec으로 이관된 internal calculation/design behavior와 browser semantic checks를 기준으로 한다.
