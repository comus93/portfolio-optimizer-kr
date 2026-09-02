## 1. Decision Gate

- [ ] D1 Backtest Experiment identity 확정
- [ ] D2 Research Frontend benchmark default 확정
- [ ] D3 initial balance default 확정
- [ ] D4 analysis period default 확정
- [ ] D5 rebalancing default 확정
- [ ] D6 portfolio name default 확정
- [ ] D7 Backtest LLM analysis framework 문서/Capability 경계 확정
- [ ] D8 human visual review completion gate 확정
- [ ] 확정 결과를 `proposal.md`, `design.md`, 관련 draft spec에 반영

## 2. OpenSpec Completion

- [ ] `portfolio-backtest` requirement 최종 parity review
- [ ] `market-data` total-return delta review
- [ ] `portfolio-simulation` rebalancing/wealth delta review
- [ ] `run-artifacts` product-mode/multi-portfolio delta review
- [ ] `research-report` Backtest section/applicability/balance semantics review
- [ ] `research-execution` decision-gated requirement 확정
- [ ] `research-input` default/decision boundary 확정
- [ ] `research-analysis` mode boundary 확정
- [ ] `agent-verification` human-review gate 확정
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
- [ ] portfolio name / target allocations / initial balance / optional benchmark / rebalancing 입력 구현
- [ ] cashflow / band rebalance / leverage field는 v1에서 노출하지 않음
- [ ] YAML round-trip과 exact `input.yaml` persistence 테스트

## 5. Shared Simulation

- [ ] `none` rebalancing path 구현 및 drift 검증
- [ ] quarterly calendar-aligned rebalancing 구현
- [ ] semiannual calendar-aligned rebalancing 구현
- [ ] monthly/yearly existing behavior regression
- [ ] mid-schedule analysis start behavior 검증
- [ ] actual initial-balance wealth path 구현
- [ ] multi-portfolio independent path identity 검증

## 6. Backtest Pipeline / Runner

- [ ] Optimization과 Backtest runner dispatch 분리
- [ ] Backtest에서 optimization objective/frontier 없이 market-data → simulation → analytics 경로 실행
- [ ] shared `portfolio-analytics` 재사용, duplicate formula 생성 금지
- [ ] benchmark 없음/있음 양쪽 실행 검증
- [ ] common effective period / coverage evidence 보존

## 7. Artifacts

- [ ] Backtest `result.json` canonical domain 구현
- [ ] portfolio collection identity가 raw/review에서 유지되도록 구현
- [ ] `(portfolio, asset)` series identity 보존
- [ ] existing run directory silent overwrite 방지 regression
- [ ] persisted Backtest run을 재실행 없이 Viewer에서 열 수 있도록 구현

## 8. Input UI

- [ ] Optimization / Backtest product mode 선택 경계 추가
- [ ] Backtest Settings / Portfolio Assets 정보구조 구현
- [ ] asset search/add/remove/edit existing behavior 재사용
- [ ] shared asset rows + portfolio별 allocation 입력 구현
- [ ] v1 최대 3 portfolio UI/validation 적용, model은 collection 유지
- [ ] Optimization objective/min-max control을 Backtest mode에서 요구하지 않음
- [ ] 결정된 frontend defaults 반영

## 9. Research Report

- [ ] Backtest overview 구현
- [ ] target allocation comparison 구현
- [ ] actual initial-balance growth comparison 구현
- [ ] Backtest realized-only Performance Summary 적용
- [ ] shared annual/monthly/trailing/rolling/drawdown/asset/correlation/decomposition section 재사용
- [ ] benchmark-relative section conditional applicability 구현
- [ ] Optimization-only Frontier section을 Backtest에서 제외
- [ ] identity/unit/N/A/axis/tooltip/responsive existing contract regression

## 10. Research Workflow

- [ ] 확정된 D1에 따라 Backtest Experiment identity 구현
- [ ] Study / Experiment / Run provenance에 product mode 보존
- [ ] `control/execute.yaml`에서 Backtest experiment 실행 가능하도록 generalize
- [ ] explicit run intent 없이 experiment 수정만으로 실행되지 않는지 확인
- [ ] 별도 Agent/opaque request execution path를 만들지 않음

## 11. LLM Research Frontend / Analysis

- [ ] product-intent-aware input flow 구현/가이드 반영
- [ ] Backtest에서 optimizer objective/min-max 질문 금지
- [ ] 결정된 benchmark/initial-balance/period/rebalancing/name defaults 반영
- [ ] mechanical validation 후 필요한 사용자 decision만 질문
- [ ] explicit execution intent 후 redundant approval 방지
- [ ] 확정된 D7 방식으로 Backtest historical-comparison analysis guide 반영

## 12. Agent Verification Framework

- [ ] 최소 `verification/profile.yaml` 구조 도입 여부를 현재 repo에 맞게 결정
- [ ] `scripts/verify.py` 또는 기존 test/run entrypoint를 재사용해 minimal verification entrypoint 구성
- [ ] calculation test → real run → result verification 흐름 구현
- [ ] report change에서 browser semantic verification 추가
- [ ] shared change의 Optimization affected regression 포함
- [ ] requirement/test/acceptance를 Agent가 임의 변경하지 않는 blocker rule 유지
- [ ] 결정된 D8 human visual review gate 적용

## 13. Completion Verification

- [ ] Backtest synthetic/contract tests PASS
- [ ] Optimization affected regression PASS
- [ ] 실제 1-portfolio Backtest run 검증
- [ ] 실제 3-portfolio Backtest run 검증
- [ ] benchmark 없음/있음 real run 검증
- [ ] monthly/quarterly/semiannual/yearly/none policy 검증
- [ ] generated report browser semantic verification
- [ ] P0/P1 blocker 없음
- [ ] validation evidence와 result commit 기록
