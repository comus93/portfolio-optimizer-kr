## 1. Decision Gate

- [x] D1 Backtest Experiment identity = union ticker set
- [x] D2 Research Frontend benchmark default = SPY, explicit override/none 허용
- [x] D3 initial balance default = 10,000
- [x] D4 analysis period default = full common effective period
- [x] D5 Time Period = Month-to-Month / Year-to-Year, default Month-to-Month
- [x] D6 portfolio name default = Portfolio 1..3
- [x] D7 LLM analysis = 단일 `docs/llm-analysis-framework.md`에서 explicit `product_mode` 기반 Optimization / Backtest branch
- [x] D8 human visual review = material layout/interaction change에만 completion gate
- [x] D9 Calendar Aligned = Yes/No 모두 지원, No는 first-active-month anchor
- [x] D10 Rebalancing = run-level 공통, default Monthly
- [x] D11 Display Income = v1 제외
- [x] D1-D11 결과를 관련 spec/design에 반영

## 2. OpenSpec Completion

- [x] `portfolio-backtest` requirement 최종 parity review
- [x] `market-data` total-return delta review
- [x] `portfolio-simulation` calendar/non-calendar rebalancing/wealth delta review
- [x] `run-artifacts` product-mode/multi-portfolio/Time-Period/schedule-setting delta review
- [x] `research-report` Backtest section/applicability/balance/schedule semantics review
- [x] `research-execution` union-ticker Experiment identity review
- [x] `research-input` confirmed defaults/decision boundary review
- [x] `research-analysis` product-mode branch boundary review
- [x] `agent-verification` conditional human-review gate review
- [x] OpenSpec strict validation 수행

## 3. Total-return Feasibility

- [x] FDR 기반 asset/ETF canonical total-return 지원 범위 조사
- [x] adjusted/distribution-adjusted series availability 및 source-aware 선택 규칙 확인
- [x] price-only silent fallback 금지, unsupported route는 명시적 validation error로 처리
- [x] 현재 지원 범위에서는 추가 data-source 보강이 release blocker가 아님을 확인하고 coverage expansion은 `openspec/TODO.md`로 이관
- [x] shared market-data 변경에 Optimization affected regression 포함

## 4. Product Input / Models

- [x] explicit `product_mode`를 Optimization / Backtest 모두 canonical YAML contract에서 mandatory로 강제하고 silent Optimization fallback 제거
- [x] Backtest-specific request model 추가
- [x] portfolio collection schema 구현, v1 validation limit=3 적용
- [x] portfolio name / target allocations / initial balance / optional benchmark 입력 구현
- [x] `Month-to-Month` / `Year-to-Year` Time Period mode 구현
- [x] Month-to-Month의 Start Year / First Month / End Year / Last Month 입력 구현
- [x] Year-to-Year의 Start Year / End Year 입력 및 month non-applicable 처리
- [x] standalone Input UI의 dynamic period selector는 post-release 범위로 `openspec/TODO.md`에 이관
- [x] Calendar Aligned Yes/No 입력 구현, default Yes
- [x] run-level rebalancing input 구현, default Monthly
- [x] canonical v1 YAML/LLM surface에서 cashflow / band rebalance / leverage / Display Income / style / factor / regime field 비활성/비지원 계약 유지, standalone UI 검증은 TODO로 이관
- [x] dividend reinvest toggle은 만들지 않고 canonical total return 사용
- [x] YAML round-trip과 exact `input.yaml` persistence 테스트

## 5. Shared Simulation

- [x] `none` rebalancing path 구현 및 drift 검증
- [x] calendar-aligned quarterly rebalancing 구현
- [x] calendar-aligned semiannual rebalancing 구현
- [x] calendar-aligned yearly behavior regression
- [x] non-calendar quarterly first-active-month + 3개월 schedule 구현/검증
- [x] non-calendar semiannual first-active-month + 6개월 schedule 구현/검증
- [x] non-calendar yearly first-active-month + 12개월 schedule 구현/검증
- [x] monthly가 Calendar Aligned와 무관하게 매월 rebalance되는지 검증
- [x] none이 Calendar Aligned와 무관하게 drift하는지 검증
- [x] mid-schedule analysis start behavior 검증
- [x] actual initial-balance wealth path 구현
- [x] multi-portfolio independent path identity 검증

## 6. Backtest Pipeline / Runner

- [x] Optimization과 Backtest runner dispatch 분리
- [x] Backtest에서 optimization objective/frontier 없이 market-data → simulation → analytics 경로 실행
- [x] shared `portfolio-analytics` 재사용, duplicate formula 생성 금지
- [x] run-level rebalancing / Calendar Aligned setting을 모든 portfolio에 동일 적용
- [x] benchmark 없음/있음 양쪽 real-data 실행 검증
- [x] common effective period / coverage evidence 보존
- [x] Month-to-Month / Year-to-Year requested period가 canonical market-data period로 올바르게 전달되는지 검증

## 7. Artifacts

- [x] Backtest `result.json` canonical domain 구현
- [x] product mode와 Time Period mode/boundaries persistence 구현
- [x] Calendar Aligned와 run-level rebalancing persistence 구현
- [x] frontend defaults(SPY/10,000/Portfolio n/Month-to-Month/Calendar Aligned Yes/Monthly)가 effective `input.yaml`에 명시되는지 검증
- [x] portfolio collection identity가 raw/review에서 유지되도록 구현
- [x] `(portfolio, asset)` series identity 보존
- [x] existing run directory silent overwrite 방지 regression
- [x] persisted Backtest run을 재실행 없이 Viewer에서 열 수 있도록 구현

## 8. Standalone Input UI Scope

- [x] current canonical Research Frontend를 LLM + Experiment YAML로 유지하고 standalone interactive Input UI는 post-release 범위로 `openspec/TODO.md`에 이관
- [x] 향후 UI에서 구현해야 할 product selector, Backtest settings, period controls, allocation editor, 3-portfolio validation, optimization-only control 비노출 요구를 TODO에 보존

## 9. Research Report

- [x] Backtest overview 구현
- [x] Time Period mode / requested-effective boundaries / Calendar Aligned / run-level rebalancing 표시
- [x] target allocation comparison 구현
- [x] actual initial-balance growth comparison 구현
- [x] Backtest realized-only Performance Summary 적용
- [x] shared annual/monthly/trailing/rolling/drawdown/asset/correlation/decomposition section 재사용
- [x] benchmark-relative section conditional applicability 구현
- [x] Optimization-only Frontier section을 Backtest에서 제외
- [x] Display Income section을 v1에서 생성하지 않음
- [x] identity/unit/N/A/axis/tooltip/responsive existing contract regression
- [x] combined asset identity를 `Name` + 줄바꿈 + `(Ticker)`로 통일하고 Annual/Monthly detail header 및 asset legend regression 반영
- [x] Backtest Monthly Correlations를 constituent asset-only canonical/report scope로 제한하고 portfolio/별도 benchmark series 제외

## 10. Research Workflow

- [x] union ticker set 기반 Backtest Experiment identity를 canonical Research Frontend/OpenSpec 운영 계약으로 확정
- [x] union 동일 + portfolio membership/weights 변경은 same Experiment/new Run, union ticker 변경은 new Experiment 규칙 확정
- [x] automated Experiment lifecycle enforcement/regression은 post-release 자동화로 `openspec/TODO.md`에 이관
- [x] Study / Experiment / Run provenance에 product mode 보존
- [x] `control/execute.yaml`에서 Backtest experiment 실행 가능하도록 generalize
- [x] explicit run intent 없이 experiment 수정만으로 실행되지 않는지 확인
- [x] 별도 Agent/opaque request execution path를 만들지 않음

## 11. LLM Research Frontend / Analysis

- [x] product-intent-aware input guide 반영: 명확하면 진행, Optimization/Backtest가 모두 가능하면 최소 질문으로 확인
- [x] 고정 비중 존재 여부를 product 결정 heuristic으로 사용하지 않도록 명시
- [x] Optimization / Backtest 모두 Experiment YAML에 explicit `product_mode` 기록
- [x] Backtest에서 optimizer objective/min-max 질문 금지
- [x] benchmark default SPY, explicit none/override 반영
- [x] initial balance 10,000 default 반영
- [x] period 미지정 시 full common period 적용
- [x] Time Period default Month-to-Month 적용
- [x] Calendar Aligned default Yes 적용
- [x] run-level rebalancing default Monthly 적용
- [x] portfolio name default 반영
- [x] mechanical validation 후 필요한 사용자 decision만 질문
- [x] explicit execution intent 후 redundant approval 방지
- [x] 단일 `docs/llm-analysis-framework.md`에 Optimization / Backtest branch 반영
- [x] Backtest branch에 Correlation Structure를 독립 단계로 반영하고 correlation-only diversifier 판정 금지
- [x] Run 분석 시 `product_mode` 기반 deterministic branch routing, 누락 시 결과 내용으로 추론 금지

## 12. Agent Verification Framework

- [x] 최소 `verification/profile.yaml` 구조 도입 여부를 현재 repo에 맞게 결정
- [x] `scripts/verify.py` 또는 기존 test/run entrypoint를 재사용해 minimal verification entrypoint 구성
- [x] calculation test → real run → result verification 흐름 구현
- [x] report change에서 browser semantic verification 추가
- [x] shared change의 Optimization affected regression 포함
- [x] requirement/test/acceptance를 Agent가 임의 변경하지 않는 blocker rule 유지
- [x] material layout/interaction change에서만 human visual review gate 적용

## 13. Completion Verification

- [x] Backtest synthetic/contract tests PASS
- [x] Optimization affected regression PASS
- [x] full Python regression PASS: 201 tests
- [x] 실제 1-portfolio Backtest run 검증
- [x] 실제 3-portfolio Backtest run 검증
- [x] benchmark 없음/있음 real-data run 검증
- [x] Month-to-Month / Year-to-Year real-data run 검증
- [x] monthly/quarterly/semiannual/yearly/none policy real-data 검증
- [x] Calendar Aligned Yes/No schedule real-data 검증
- [x] generated report browser semantic verification
- [x] material visual review는 사용자 직접 review를 completion gate로 사용하고 후속 Name/Ticker 및 correlation 수정 regression 반영
- [x] 최종 release gate 기준 P0/P1 blocker 없음
- [x] validation evidence와 result commit 기록
