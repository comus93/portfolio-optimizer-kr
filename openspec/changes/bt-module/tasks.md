## 1. Decision Gate

- [x] D1 Backtest Experiment identity = union ticker set
- [x] D2 Research Frontend benchmark default = SPY, explicit override/none 허용
- [x] D3 initial balance default = 10,000
- [x] D4 analysis period default = full common effective period
- [x] D5 Time Period = Month-to-Month / Year-to-Year, default Month-to-Month
- [x] D6 portfolio name default = Portfolio 1..3
- [x] D7 Backtest LLM analysis = 별도 research-analysis capability/guide
- [x] D8 human visual review = material layout/interaction change에만 completion gate
- [x] D9 Calendar Aligned = Yes/No 모두 지원, No는 first-active-month anchor
- [x] D10 Rebalancing = run-level 공통, default Monthly
- [x] D11 Display Income = v1 제외
- [x] D1-D11 결과를 관련 spec/design에 반영

## 2. OpenSpec Completion

- [ ] `portfolio-backtest` requirement 최종 parity review
- [ ] `market-data` total-return delta review
- [ ] `portfolio-simulation` calendar/non-calendar rebalancing/wealth delta review
- [ ] `run-artifacts` product-mode/multi-portfolio/Time-Period/schedule-setting delta review
- [ ] `research-report` Backtest section/applicability/balance/schedule semantics review
- [ ] `research-execution` union-ticker Experiment identity review
- [ ] `research-input` confirmed defaults/decision boundary review
- [ ] `research-analysis` separate Backtest analysis boundary review
- [ ] `agent-verification` conditional human-review gate review
- [ ] OpenSpec strict validation 수행

## 3. Total-return Feasibility

- [ ] 현재 FDR 기반 asset/ETF 데이터에서 distribution-reinvested total return을 신뢰성 있게 만들 수 있는지 조사
- [ ] adjusted series 또는 distribution data availability 확인
- [ ] price-only silent fallback 없이 지원/비지원 조건 정의
- [ ] data source 보강이 필요하면 최소 변경 design 제안
- [ ] shared market-data 변경이므로 Optimization affected regression scope 확정

## 4. Product Input / Models

- [ ] explicit product mode를 canonical YAML contract에 추가
- [ ] Backtest-specific request model 추가
- [ ] portfolio collection schema 구현, v1 validation limit=3 적용
- [ ] portfolio name / target allocations / initial balance / optional benchmark 입력 구현
- [ ] `Month-to-Month` / `Year-to-Year` Time Period mode 구현
- [ ] Month-to-Month의 Start Year / First Month / End Year / Last Month 입력 구현
- [ ] Year-to-Year의 Start Year / End Year 입력 및 month non-applicable 처리
- [ ] period selector year range를 data-supported range에서 동적으로 구성
- [ ] Calendar Aligned Yes/No 입력 구현, default Yes
- [ ] run-level rebalancing input 구현, default Monthly
- [ ] cashflow / band rebalance / leverage / Display Income / style / factor / regime field는 v1에서 노출하지 않음
- [ ] dividend reinvest toggle은 만들지 않고 canonical total return 사용
- [ ] YAML round-trip과 exact `input.yaml` persistence 테스트

## 5. Shared Simulation

- [ ] `none` rebalancing path 구현 및 drift 검증
- [ ] calendar-aligned quarterly rebalancing 구현
- [ ] calendar-aligned semiannual rebalancing 구현
- [ ] calendar-aligned yearly behavior regression
- [ ] non-calendar quarterly first-active-month + 3개월 schedule 구현/검증
- [ ] non-calendar semiannual first-active-month + 6개월 schedule 구현/검증
- [ ] non-calendar yearly first-active-month + 12개월 schedule 구현/검증
- [ ] monthly가 Calendar Aligned와 무관하게 매월 rebalance되는지 검증
- [ ] none이 Calendar Aligned와 무관하게 drift하는지 검증
- [ ] mid-schedule analysis start behavior 검증
- [ ] actual initial-balance wealth path 구현
- [ ] multi-portfolio independent path identity 검증

## 6. Backtest Pipeline / Runner

- [ ] Optimization과 Backtest runner dispatch 분리
- [ ] Backtest에서 optimization objective/frontier 없이 market-data → simulation → analytics 경로 실행
- [ ] shared `portfolio-analytics` 재사용, duplicate formula 생성 금지
- [ ] run-level rebalancing / Calendar Aligned setting을 모든 portfolio에 동일 적용
- [ ] benchmark 없음/있음 양쪽 실행 검증
- [ ] common effective period / coverage evidence 보존
- [ ] Month-to-Month / Year-to-Year requested period가 canonical market-data period로 올바르게 전달되는지 검증

## 7. Artifacts

- [ ] Backtest `result.json` canonical domain 구현
- [ ] product mode와 Time Period mode/boundaries persistence 구현
- [ ] Calendar Aligned와 run-level rebalancing persistence 구현
- [ ] frontend defaults(SPY/10,000/Portfolio n/Month-to-Month/Calendar Aligned Yes/Monthly)가 effective `input.yaml`에 명시되는지 검증
- [ ] portfolio collection identity가 raw/review에서 유지되도록 구현
- [ ] `(portfolio, asset)` series identity 보존
- [ ] existing run directory silent overwrite 방지 regression
- [ ] persisted Backtest run을 재실행 없이 Viewer에서 열 수 있도록 구현

## 8. Input UI

- [ ] Optimization / Backtest product mode 선택 경계 추가
- [ ] Backtest Settings / Portfolio Assets 정보구조 구현
- [ ] Time Period selector: Month-to-Month / Year-to-Year, default Month-to-Month
- [ ] period mode에 따라 month selector show/hide 또는 applicable state 처리
- [ ] Calendar Aligned Yes/No, default Yes
- [ ] Initial Amount default 10,000
- [ ] Rebalancing: No / Annual / Semi-annual / Quarterly / Monthly, run-level, default Monthly
- [ ] asset search/add/remove/edit existing behavior 재사용
- [ ] shared asset rows + portfolio별 allocation 입력 구현
- [ ] v1 최대 3 portfolio UI/validation 적용, model은 collection 유지
- [ ] 이름 미지정 시 Portfolio 1..3 자동 생성
- [ ] Optimization objective/min-max control을 Backtest mode에서 요구하지 않음
- [ ] excluded v1 advanced setting을 노출하지 않음

## 9. Research Report

- [ ] Backtest overview 구현
- [ ] Time Period mode / requested-effective boundaries / Calendar Aligned / run-level rebalancing 표시
- [ ] target allocation comparison 구현
- [ ] actual initial-balance growth comparison 구현
- [ ] Backtest realized-only Performance Summary 적용
- [ ] shared annual/monthly/trailing/rolling/drawdown/asset/correlation/decomposition section 재사용
- [ ] benchmark-relative section conditional applicability 구현
- [ ] Optimization-only Frontier section을 Backtest에서 제외
- [ ] Display Income section을 v1에서 생성하지 않음
- [ ] identity/unit/N/A/axis/tooltip/responsive existing contract regression

## 10. Research Workflow

- [ ] union ticker set 기반 Backtest Experiment identity 구현
- [ ] union 동일 + portfolio membership/weights 변경은 same Experiment/new Run인지 검증
- [ ] union ticker 변경은 new Experiment인지 검증
- [ ] Study / Experiment / Run provenance에 product mode 보존
- [ ] `control/execute.yaml`에서 Backtest experiment 실행 가능하도록 generalize
- [ ] explicit run intent 없이 experiment 수정만으로 실행되지 않는지 확인
- [ ] 별도 Agent/opaque request execution path를 만들지 않음

## 11. LLM Research Frontend / Analysis

- [ ] product-intent-aware input flow 구현/가이드 반영
- [ ] Backtest에서 optimizer objective/min-max 질문 금지
- [ ] benchmark default SPY, explicit none/override 반영
- [ ] initial balance 10,000 default 반영
- [ ] period 미지정 시 full common period 적용
- [ ] Time Period default Month-to-Month 적용
- [ ] Calendar Aligned default Yes 적용
- [ ] run-level rebalancing default Monthly 적용
- [ ] portfolio name default 반영
- [ ] mechanical validation 후 필요한 사용자 decision만 질문
- [ ] explicit execution intent 후 redundant approval 방지
- [ ] 별도 Backtest historical-comparison analysis guide 반영

## 12. Agent Verification Framework

- [ ] 최소 `verification/profile.yaml` 구조 도입 여부를 현재 repo에 맞게 결정
- [ ] `scripts/verify.py` 또는 기존 test/run entrypoint를 재사용해 minimal verification entrypoint 구성
- [ ] calculation test → real run → result verification 흐름 구현
- [ ] report change에서 browser semantic verification 추가
- [ ] shared change의 Optimization affected regression 포함
- [ ] requirement/test/acceptance를 Agent가 임의 변경하지 않는 blocker rule 유지
- [ ] material layout/interaction change에서만 human visual review gate 적용

## 13. Completion Verification

- [ ] Backtest synthetic/contract tests PASS
- [ ] Optimization affected regression PASS
- [ ] 실제 1-portfolio Backtest run 검증
- [ ] 실제 3-portfolio Backtest run 검증
- [ ] benchmark 없음/있음 real run 검증
- [ ] Month-to-Month / Year-to-Year real run 검증
- [ ] monthly/quarterly/semiannual/yearly/none policy 검증
- [ ] Calendar Aligned Yes/No schedule 검증
- [ ] generated report browser semantic verification
- [ ] material visual change가 있으면 human visual review 완료
- [ ] P0/P1 blocker 없음
- [ ] validation evidence와 result commit 기록
