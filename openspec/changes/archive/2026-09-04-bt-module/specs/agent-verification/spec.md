## Purpose

Backtest 및 shared capability 변경을 Agent가 실제 환경에서 반복 검증할 때 요구사항을 임의 변경하지 않고 재현 가능한 evidence를 남기는 verification behavior를 정의한다.

## ADDED Requirements

### Requirement: Verification flow
Agent verification은 변경 성격에 따라 `Test → Real Run → Result Verification → Browser Verification(if applicable) → Fix → Re-verify` 흐름을 따라야 한다(MUST).

#### Scenario: Backtest report 변경
- GIVEN Backtest 계산과 report가 함께 변경되었다
- WHEN Agent가 completion verification을 수행한다
- THEN affected tests, 실제 Backtest run, persisted result 검증, browser 검증을 순서대로 수행하고 수정이 발생하면 영향을 받은 단계부터 다시 검증한다

### Requirement: Requirements are immutable during verification
Agent는 테스트나 검증을 통과시키기 위해 OpenSpec requirement, acceptance criterion, 계산 규칙 또는 verification criterion을 임의로 변경해서는 안 된다(MUST NOT).

#### Scenario: contract test failure
- GIVEN 구현이 canonical requirement를 만족하지 못해 test가 실패한다
- WHEN Agent가 원인을 조사한다
- THEN test를 약화/삭제/skip하지 않고 구현을 수정하거나 requirement 자체가 문제라고 판단되면 blocker로 보고한다

### Requirement: Affected regression for shared changes
Shared capability behavior가 변경되면 새 Backtest뿐 아니라 해당 capability를 사용하는 기존 product의 affected regression을 포함해야 한다(MUST).

#### Scenario: total-return semantics 변경
- GIVEN `market-data` total-return behavior가 Backtest change에서 변경된다
- WHEN Agent verification scope를 구성한다
- THEN Backtest 검증과 함께 Optimization historical-path/analytics affected regression을 수행한다

### Requirement: Real-run verification
제품 실행 behavior가 변경되면 synthetic/unit test만으로 completion을 판정하지 않고 실제 canonical input을 사용한 real run을 수행해야 한다(MUST).

#### Scenario: 새로운 Backtest runner
- GIVEN Backtest YAML runner 경로가 구현되었다
- WHEN completion을 검증한다
- THEN repository의 실제 실행 환경에서 canonical Backtest input으로 run을 생성하고 persisted artifact를 확인한다

### Requirement: Result verification
Real run에서 생성된 `result.json`과 필요한 raw/review artifact가 OpenSpec invariants와 identity를 만족하는지 확인해야 한다(MUST).

#### Scenario: multi-portfolio run
- GIVEN 세 portfolio Backtest run이 완료되었다
- WHEN result verification을 수행한다
- THEN portfolio identity, weight sum, effective period, return/wealth path, applicable analytics와 benchmark semantics가 서로 혼합되지 않았는지 확인한다

### Requirement: Browser verification for report changes
Report/viewer behavior가 변경된 경우 generated report를 실제 browser served context에서 열어 machine-judgeable semantic/interaction checks를 수행해야 한다(MUST).

#### Scenario: Backtest growth chart
- GIVEN Backtest report에 여러 portfolio growth series가 있다
- WHEN browser verification을 수행한다
- THEN required section 존재, portfolio identity, semantic axis/unit, tooltip/legend identity, clipping/overflow 같은 검증 가능한 contract를 확인한다

### Requirement: Browser verification uses internal contract
Browser verification은 PV pixel parity를 요구하지 않고 OpenSpec `research-report`와 applicable internal report contract를 기준으로 판정해야 한다(MUST).

#### Scenario: PV와 layout 차이
- GIVEN 내부 report layout이 PV와 다르지만 required information과 interaction contract를 만족한다
- WHEN Agent가 browser verification을 수행한다
- THEN PV layout 차이만으로 failure를 만들지 않는다

### Requirement: Published report evidence for visual acceptance
Material report/layout 변경의 visual acceptance 대상은 로컬 screenshot만으로 끝내지 않고 repository GitHub Pages에 실제 served report를 게시해야 한다(MUST). 게시된 URL은 검증 evidence와 handoff에 남겨야 한다(MUST).

#### Scenario: Backtest report layout 변경
- GIVEN material Backtest report layout 변경이 완료되고 real-run artifact가 생성되었다
- WHEN visual acceptance 단계로 이동한다
- THEN 해당 persisted report를 GitHub Pages에서 접근할 수 있게 배포하고 exact report URL을 기록한다

### Requirement: Layered visual acceptance
Material report/layout 변경은 `LLM first-pass visual acceptance → User second-pass visual acceptance`의 두 단계 검토를 거쳐야 한다(MUST). Agent의 자동 Playwright 통과 또는 Agent 자체 관찰만으로 최종 visual acceptance를 선언해서는 안 된다(MUST NOT).

#### Scenario: LLM first-pass comparison
- GIVEN GitHub Pages에 새 Backtest report가 게시되고 PV MHTML reference가 존재한다
- WHEN 1차 visual acceptance를 수행한다
- THEN LLM은 실제 published page와 MHTML을 비교하여 정보구조, output data 성격, section grouping, chart semantics, interaction capability의 명백한 누락/불일치를 먼저 식별한다

#### Scenario: User second-pass review
- GIVEN LLM 1차 검토에서 기능적/정보구조적 P0/P1 blocker가 해소되었다
- WHEN 2차 visual acceptance를 수행한다
- THEN 사용자가 실제 GitHub Pages report에서 최종 관능적 usability/layout/polish 판단을 수행한다

### Requirement: Human visual review is conditional
Human visual review는 layout 또는 interaction이 materially 변경되어 정성적 usability/polish 판단이 필요한 경우 completion gate로 사용해야 한다(MUST). 계산-only, artifact-only, 비시각적 변경에는 human visual review를 일률적으로 요구해서는 안 된다(MUST NOT).

#### Scenario: report layout 재구성
- GIVEN Backtest report의 section layout, chart placement 또는 interaction이 materially 변경되었다
- WHEN completion을 판정한다
- THEN automated browser semantic verification과 별도로 layered visual acceptance 결과를 확인한다

#### Scenario: calculation-only 변경
- GIVEN report layout/interaction이 변경되지 않은 calculation-only change다
- WHEN completion verification을 수행한다
- THEN human visual review가 없다는 이유만으로 completion을 막지 않는다

### Requirement: Verification evidence
사용자 또는 LLM이 검토해야 하는 verification은 command/test/run/browser 결과와 blocker/deviation을 재현 가능한 형태로 남겨야 한다(MUST).

#### Scenario: completion report
- GIVEN Agent가 Backtest change 검증을 완료했다
- WHEN 결과를 회신한다
- THEN start HEAD, changed files, test/run/browser evidence, P0/P1/P2 또는 blocker, run path, published report URL, result commit을 식별할 수 있다

### Requirement: Verification remains minimal until needed
초기 verification framework는 현재 requirement를 검증하는 데 필요한 최소 구조로 시작하고 실제 반복 요구가 확인되기 전 범용 abstraction을 선제적으로 추가하지 않아야 한다(MUST NOT).

#### Scenario: browser 검증이 없는 계산-only change
- GIVEN UI/report가 영향을 받지 않는 계산-only 변경이다
- WHEN verification profile을 구성한다
- THEN 불필요한 browser test scaffolding을 completion 조건으로 강제하지 않는다
