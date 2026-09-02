# Session Handover

created_at: 2026-09-03T06:33:35+09:00
project: `comus93/portfolio-optimizer-kr`
branch: `bt-module`
current_remote_head_at_handover: `2567fa31f5f6e7096523714896c5567c08e8ae0a`

## 1. Purpose of This Handover

이 handover는 새 ChatGPT/LLM 창이 `portfolio-optimizer-kr`의 Backtest module 작업을 바로 이어갈 수 있도록 현재 제품 결정, OpenSpec source of truth, 구현/검증 상태, Portfolio Visualizer(PV) reference 위치, MHTML 분할본, screenshot evidence, Agent handoff 상태를 한 번에 제공한다.

과거 토론을 재현하는 문서가 아니다. 아래 내용과 GitHub remote의 최신 파일을 기준으로 다음 작업을 이어간다.

가장 먼저 다음 파일을 읽는다.

```text
ai-share/PROTOCOL.md
ai-share/llm-to-llm.md        # 이 파일
ai-share/agent-to-llm.md      # Agent 최신 결과가 있는지 반드시 확인
ai-share/llm-to-agent.md      # 현재 Agent에게 어떤 검증을 요청했는지 확인
```

`ai-share` inbound/outbound source of truth는 로컬이 아니라 GitHub remote다.

---

## 2. Project Goal

현재 feature branch `bt-module`에는 세 가지 목표가 함께 진행 중이다.

1. Portfolio Visualizer의 Backtest Portfolio를 외부 reference로 삼아 개인 연구용 Portfolio Backtest module 구현
2. requirement/project-state 관리를 OpenSpec 방식으로 전환
3. Agent verification framework 도입

핵심 구조는 다음과 같다.

```text
Optimization
market-data
  -> ex-ante estimation / constraints / objective / efficient frontier
  -> optimized or provided target weights
  -> portfolio-simulation
  -> portfolio-analytics
  -> run-artifacts / research-report

Backtest
market-data
  -> user-defined target weights
  -> portfolio-simulation
  -> portfolio-analytics
  -> run-artifacts / research-report
```

중요 원칙:

```text
portfolio generation != portfolio evaluation
```

Backtest는 optimizer가 아니다. Historical comparison을 수행하며 optimality, efficient frontier, optimal weight를 주장하지 않는다.

---

## 3. Normative Sources and Governance

### 3.1 Existing baseline docs

기존 project-wide baseline/reference 문서:

```text
docs/specification.md
docs/report-ui-specification.md
docs/input-ui-contract.md
docs/architecture.md
docs/visual-acceptance-contract.md
docs/research-operation-pipeline.md
docs/llm-research-input-contract.md
docs/llm-analysis-framework.md
```

역할:

```text
Finance / calculation semantics   docs/specification.md
Report UI / interaction semantics docs/report-ui-specification.md
Architecture / responsibility     docs/architecture.md
Validation procedure              docs/visual-acceptance-contract.md
```

하지만 이번 Backtest 작업에서는 **기존 `docs/*.md`를 Backtest 때문에 수정하지 않는다.**

Backtest-specific 신규/변경 동작은 다음 OpenSpec change가 normative source다.

```text
openspec/changes/bt-module/
```

PV, screenshot, external service는 reference이며 자동 acceptance criterion이 아니다.

```text
internal specification > external reference
```

다만 현재 visual workflow에서는 PV와의 차이 중 단순 pixel 차이가 아니라 **information architecture, output data character, user-facing analytics semantics, interaction 기능 차이**를 defect discovery에 적극 사용한다.

---

## 4. OpenSpec Location and Read Order

### 4.1 Main Backtest change

```text
openspec/changes/bt-module/
├─ .openspec.yaml
├─ proposal.md
├─ design.md
├─ tasks.md
└─ specs/
   ├─ agent-verification/spec.md
   ├─ market-data/spec.md
   ├─ portfolio-backtest/spec.md
   ├─ portfolio-simulation/spec.md
   ├─ research-analysis/spec.md
   ├─ research-execution/spec.md
   ├─ research-input/spec.md
   ├─ research-report/spec.md
   └─ run-artifacts/spec.md
```

새 LLM은 다음 순서로 읽는 것을 권장한다.

```text
1. openspec/changes/bt-module/proposal.md
2. openspec/changes/bt-module/design.md
3. openspec/changes/bt-module/specs/portfolio-backtest/spec.md
4. openspec/changes/bt-module/specs/portfolio-simulation/spec.md
5. openspec/changes/bt-module/specs/market-data/spec.md
6. openspec/changes/bt-module/specs/research-input/spec.md
7. openspec/changes/bt-module/specs/research-execution/spec.md
8. openspec/changes/bt-module/specs/research-analysis/spec.md
9. openspec/changes/bt-module/specs/research-report/spec.md
10. openspec/changes/bt-module/specs/run-artifacts/spec.md
11. openspec/changes/bt-module/specs/agent-verification/spec.md
12. openspec/changes/bt-module/tasks.md
```

### 4.2 Optimizer OpenSpec migration dependency

별도 change가 존재한다.

```text
openspec/changes/migrate-optimizer-to-openspec/
```

이 change의 일부 기존 ADDED Requirement에는 RFC2119 `MUST/SHALL` 문제로 strict validation이 실패한 이력이 있다. **Backtest 작업을 위해 임의로 고치지 않는다.** 별도 migration issue로 분리한다.

현재 Backtest 최신 head에 대해서는 새로운 Agent가 다시 strict validation하도록 요청된 상태다. 과거 head에서 PASS한 적이 있어도 최신 head PASS를 추정하지 않는다.

---

## 5. Confirmed Backtest Product Decisions

D1-D11은 닫혀 있다.

### D1 Experiment identity

Experiment identity = 비교 portfolio들의 **union ticker set**.

- union ticker set이 동일하면 portfolio 수, 이름, membership, weight, benchmark, initial amount, period, rebalance가 달라도 같은 Experiment의 새 Run
- union ticker set이 달라지면 새 Experiment

### D2 Benchmark

Core Backtest benchmark는 optional.
Research Frontend default는 `SPY`.
사용자가 override하거나 명시적으로 none 선택 가능.

### D3 Initial balance

Research Frontend default = `10,000`.
Backtest report는 실제 입력 initial balance를 사용한다.

### D4 Period omitted

필요 asset + applicable benchmark가 모두 가능한 **full common effective period** 사용.

### D5 Time Period

지원:

```text
Month-to-Month
Year-to-Year
```

Default = `Month-to-Month`.

Month-to-Month inputs:

```text
Start Year
First Month
End Year
Last Month
```

Year-to-Year:

```text
Start Year
End Year
```

full calendar years 의미.

### D6 Portfolio names

Auto name:

```text
Portfolio 1
Portfolio 2
Portfolio 3
```

### D7 Analysis guide

기존 optimizer 전용 `docs/llm-analysis-framework.md`는 변경하지 않는다.
Backtest는 별도 `research-analysis` capability를 가진다.

### D8 Browser / visual verification

가능한 경우 browser semantic verification을 수행한다.
Material layout/interaction change가 있을 때 human visual review를 둔다.

현재 더 구체적인 workflow는 아래 Visual Acceptance 절 참고.

### D9 Calendar Aligned

Yes/No 모두 지원.

Yes:

```text
Quarterly   Jan / Apr / Jul / Oct
Semiannual  Jan / Jul
Yearly      Jan
```

No:

```text
first active month를 anchor로 사용
Quarterly   +3 months
Semiannual  +6 months
Yearly      +12 months
```

Monthly는 alignment-independent, every active month.
None은 first target 후 drift, alignment-independent.

Research Frontend default `Yes`는 기존 behavior 호환을 위해 LLM이 보완한 default다. D9에서 사용자가 직접 default를 선택한 것은 아니므로, default 자체가 다시 논점이 되면 이 점을 투명하게 설명한다.

### D10 Rebalancing

한 Run에서 모든 portfolio가 같은 run-level setting 사용.

지원:

```text
none
yearly
semiannual
quarterly
monthly
```

Default = `Monthly`.

Portfolio-specific rebalancing과 rebalance bands는 v1 제외.

### D11 Display Income

v1 제외.
Canonical total return은 유지하되 distribution income 별도 series/report는 만들지 않는다.

### Other v1 exclusions

```text
Cashflows
Rebalance bands
Leverage
Style Analysis
Factor Regression
Regime Performance
Display Income
Provider-specific exposure
Imported portfolio
Imported benchmark
Lazy preset
Dividend-reinvestment toggle
```

Dividend reinvestment toggle가 없는 이유는 canonical return 자체가 total-return semantics이기 때문이다.

---

## 6. Market Data / FDR Decision

### 6.1 Canonical principle

Optimization과 Backtest historical asset return은 동일한 canonical total-return observations를 사용한다.

```text
price-only return을 total return으로 silent fallback 금지
```

### 6.2 US assets

FDR/Yahoo에서 `Adj Close`가 존재하면 `Adj Close`를 우선 사용한다.

### 6.3 Korean FDR routing research result

FinanceDataReader의 현재 구현을 GitHub에서 확인한 결과:

- 6자리 한국 종목의 default route는 `NaverDailyReader`
- Naver reader 반환 schema는:

```text
Open
High
Low
Close
Volume
Change
```

- `Adj Close` column 자체가 없다. `Adj Close = null` 문제가 아니다.

FDR issue evidence:

- default/NAVER는 수정주가 성격
- 명시적 `KRX:` source는 수정주가가 아닌 것으로 보고됨
- 국내 ETF 중 분배금이 사전 공지되는 ETF는 default `Close`가 배당 고려 수정주가라는 FDR issue 설명이 존재

### 6.4 Current product decision

OpenSpec `market-data/spec.md`에 반영됨.

```text
Korean ETF + FDR default/NAVER:
  FDR ETF listing으로 ETF임이 확인되고 source semantics가 맞으면
  Close를 adjusted/distribution-aware canonical series로 허용

Explicit KRX: source:
  Close를 canonical total return으로 자동 승인하지 않음

Korean common stock:
  ETF 규칙을 자동 확장하지 않음
```

구현은 `FDRLoader`에서 source/instrument를 판정한 뒤 `select_total_return_price(..., close_is_total_return=True)` 같은 explicit path로만 Close 허용하도록 바뀐 상태다.

새 Agent에게 실제 `069500` 조회, attrs, KRX source failure/behavior를 다시 검증하도록 요청했다.

---

## 7. Backtest Implementation State

이미 구현된 큰 범위:

```text
Backtest request / model
YAML parsing
1~3 portfolio collection
run-level rebalancing
Calendar Aligned Yes/No
Month-to-Month / Year-to-Year
benchmark optional
initial balance
shared portfolio simulation
shared analytics
result/raw/review persistence
Research execution
Streamlit Backtest input
Backtest-specific self-contained HTML report
Playwright browser verification
GitHub Pages report publishing workflow
```

최근 report presentation 수정은 **test-first**로 진행했다.

추가/강화된 test:

```text
tests/test_backtest_report_presentation.py
tests/test_fdr_total_return.py
verification/browser/backtest-report.spec.mjs
```

최근 구현 수정의 목표:

```text
1. raw artifact schema를 user-facing report에 dump하지 않음
2. Performance Summary의 unit storage column 제거
3. Trailing Returns snake_case / _pct label 제거
4. Metrics long-format portfolio/metric/value -> metric x portfolio matrix
5. Active Returns raw monthly dump -> analysis presentation
6. canonical portfolio input order 유지
7. Growth x-axis actual-date coordinate + calendar-aware Jan/Jul cadence
8. benchmark를 configured human-readable name으로 표시
9. annual/monthly/drawdown/assets/rolling table도 user-facing label/unit으로 변환
```

이 최신 implementation은 Agent 최종 검증 결과를 아직 받기 전 상태다.

---

## 8. Visual Acceptance Philosophy and Workflow

이 프로젝트에서 visual acceptance는 단순 screenshot pixel parity가 아니다.

사용자 판단:

> 사용자가 관능 평가를 하기 전에, output data의 성격과 기능이 PV reference와 너무 다르면 LLM이 먼저 찾아야 한다.

따라서 현재 workflow:

```text
LLM writes tests + implementation
        ↓
Agent tests / real run / Playwright
        ↓
Agent commits run + validation evidence
        ↓
GitHub Pages publish
        ↓
LLM 1st Visual Acceptance
  - actual published page
  - PV captured MHTML
  - information architecture
  - output data/function character
  - section semantics
  - chart axes/ticks/tooltip/identity
        ↓
문제 있으면 LLM이 spec 확인/필요시 spec update 후 구현 수정
        ↓
Agent reverify + republish
        ↓
User 2nd Visual Acceptance
  - usability
  - layout
  - readability
  - visual polish
  - 실제 사용 관능 평가
```

Agent는 machine acceptance와 obvious defect evidence를 제공하지만 **LLM 1차 visual acceptance를 대신하지 않는다.**

사용자 2차 visual acceptance를 넘기기 전에는 LLM이 최소 P0/P1 성격 차이를 먼저 제거한다.

---

## 9. Portfolio Visualizer Backtest Reference

### 9.1 Live reference URL

현재 Backtest reference URL:

```text
https://www.portfoliovisualizer.com/backtest-portfolio?s=y&sl=5NMHg7UEDbksVuZQFdAdFG
```

이 URL은 external non-normative reference다.

### 9.2 Captured reference directory

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/
```

구성:

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/
├─ README.md
├─ page.mhtml
└─ source/
   ├─ manifest.json
   ├─ page.part-001.html
   ├─ page.part-002.html
   ├─ page.part-003.html
   ├─ page.part-004.html
   ├─ page.part-005.html
   ├─ style-001.part-001.css
   ├─ style-001.part-002.css
   ├─ style-002.css
   ├─ style-003.css
   └─ style-004.css
```

### 9.3 Capture metadata

`README.md`에 기록된 capture metadata:

```text
Captured at: 2026-09-02T09:33:31.404Z
Artifact: page.mhtml
SHA-256: 91b926501c5a8a1584c4426681ac2ecbca255d9fe5dabe40a07171975d510853
Browser: chrome.exe
```

`page.mhtml`이 원본 archive다.

### 9.4 Split source files

MHTML을 LLM/GitHub에서 쉽게 inspection하기 위해 text MIME part를 기계적으로 분할했다.

Manifest:

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/manifest.json
```

HTML 본문은 다음 5개 chunk로 이어진다.

```text
source/page.part-001.html
source/page.part-002.html
source/page.part-003.html
source/page.part-004.html
source/page.part-005.html
```

CSS:

```text
source/style-001.part-001.css
source/style-001.part-002.css
source/style-002.css
source/style-003.css
source/style-004.css
```

Extraction은 mechanical MIME extraction only이며 semantic rewrite가 아니다.

### 9.5 Capture/extraction utilities

```text
scripts/capture-reference.mjs
scripts/extract-mhtml-source.mjs
```

Capture 당시 headless Chrome은 403이 있었고 headful Chrome capture가 성공했다.

---

## 10. Current Backtest Report Evidence / Screenshots

### 10.1 Existing representative run

이전 Agent 검증 run:

```text
runs/20260902-backtest-qqq-gld-spy-renderer-v2/
```

Report:

```text
runs/20260902-backtest-qqq-gld-spy-renderer-v2/report.html
```

Input character:

```text
Assets: QQQ / GLD
Benchmark: SPY
Portfolios: Growth 70/30, Balanced 50/50
Period: 2020-2025
Mode: Month-to-Month
Rebalancing: Monthly
Calendar Aligned: Yes
Initial balance: 10,000
Observations: 72 months
```

Previous sanity values:

```text
Growth 70/30 end balance  ≈ $30,468.89
Balanced 50/50 end balance ≈ $30,181.47
```

### 10.2 Screenshot evidence paths

```text
runs/20260902-backtest-qqq-gld-spy-renderer-v2/validation/desktop.png
runs/20260902-backtest-qqq-gld-spy-renderer-v2/validation/mobile.png
runs/20260902-backtest-qqq-gld-spy-renderer-v2/validation/README.md
```

중요:

**이 screenshot은 latest presentation/FDR change 전 representative evidence다. 최종 visual acceptance용 최신 screenshot으로 간주하지 않는다.**

현재 Agent 요청에서는 최신 HEAD로 fresh unique run을 만들고 새 screenshot evidence를 생성하도록 했다.

### 10.3 Why prior machine PASS was not enough

이전 report는 Playwright semantic/responsive checks를 통과했지만 LLM 1차 review에서 다음 P1 성격 문제를 발견했다.

```text
- Active Returns가 raw artifact dump에 가까움
- Metrics가 long-format storage table
- Trailing Returns에 3m_pct 등의 storage label 노출
- Performance Summary unit column 노출
- portfolio order 불일치
- Growth x-axis가 row-index cadence라 calendar-aware하지 않음
- benchmark identity가 generic benchmark로 노출
```

이 문제들은 현재 OpenSpec `research-report/spec.md`와 최신 implementation에 반영/수정된 상태이며, Agent 재검증 대기 중이다.

---

## 11. Report Specification Changes from First Visual Review

현재 `openspec/changes/bt-module/specs/research-report/spec.md`에는 최소 다음이 명시되어 있다.

### Raw schema exposure prohibition

```text
raw/review CSV/JSON storage schema를 user-facing primary presentation으로 그대로 dump 금지
snake_case, _pct, unit=pct|balance|ratio 같은 storage metadata는 human-facing label/unit으로 변환
```

### Stable portfolio display order

```text
canonical input portfolio order를 Allocation, Performance Summary, legends,
Trailing/Annual/Monthly/Rolling comparison 전반에서 유지
benchmark는 portfolio collection 뒤의 comparison reference
```

### Growth chart semantic axes

```text
X = time/calendar
Y = Portfolio Balance + currency
multiple intermediate x/y ticks
horizontal reference grid
calendar-aware cadence (e.g. Jan/Jul, year start, quarter start 등)
row-index equal-spacing label 금지
```

### Growth interaction

```text
visible hover/focus tooltip
Date + Portfolio identity + Balance
ARIA label만 있고 visible feedback 없는 구현은 불충분
```

### Summary hierarchy

```text
Target Allocation
-> Performance Summary
-> Portfolio Growth
-> Trailing Returns
```

### Section grouping

```text
Summary
Active Returns (benchmark 있을 때)
Metrics
Annual Returns
Monthly Returns
Drawdowns
Assets
Rolling Returns
```

PV-only unsupported 기능을 외형 맞춤을 위해 fabricate하지 않는다.

---

## 12. Browser Verification

Playwright repo-level browser verification이 들어가 있다.

Main test:

```text
verification/browser/backtest-report.spec.mjs
```

Fixture generator:

```text
scripts/prepare_browser_fixture.py
```

Main verification entrypoint:

```bash
uv run python scripts/verify.py --openspec --full --browser
```

Real report:

```bash
uv run python scripts/verify.py --browser-report runs/<run-id>/report.html
```

Playwright Chromium을 canonical machine browser runner로 사용한다.
Codex full CDP access는 사용자가 이미 활성화해 두었으며, 필요 시 DOM/console/network diagnosis에 사용할 수 있다. 하지만 formal acceptance runner는 Playwright다.

---

## 13. GitHub Pages Publishing

Workflow는 persisted research reports를 GitHub Pages에 올리도록 구성돼 있다.

```text
.github/workflows/publish-reports.yml
```

이전에는 `github-pages` environment가 `bt-module` branch deployment를 허용하지 않아 workflow가 실패했다.

사용자는 **다음 Agent 실행 전에 GitHub Pages environment 설정에서 `bt-module` deployment를 허용할 예정**이라고 명시했다.

따라서 다음 Agent는 과거 blocker를 재사용하지 말고 **새 final HEAD 기준 workflow를 실제 실행/확인**해야 한다.

Agent가 반드시 반환해야 하는 것:

```text
GitHub Pages base URL
US representative exact published report URL
KRX report exact published URL (publish되면)
workflow run URL/ID
HTTP/browser로 실제 접근 성공 여부
```

URL을 추정해서 쓰면 안 된다.

GitHub Pages에 올라온 **실제 published page**가 LLM 1차 visual acceptance의 대상이다.

---

## 14. Current Agent Request Pending

현재 Agent에게 보낸 최신 요청:

```text
ai-share/llm-to-agent.md
id: 20260903T001800+0900-llm
```

이 요청은 current head의 presentation/FDR 변경을 검증하는 작업이다.

Agent 요청 핵심:

```text
1. git pull --ff-only origin bt-module
2. bt-module OpenSpec strict
3. targeted tests
4. full regression
5. deterministic Playwright
6. live FDR US Adj Close verification
7. Korean ETF 069500 default/NAVER source-aware verification
8. explicit KRX source가 total-return으로 오인되지 않는지 확인
9. fresh US QQQ/GLD/SPY run
10. fresh KRX 069500 smoke run
11. real-report Playwright
12. screenshot evidence persistence
13. commit/push
14. GitHub Pages publish
15. exact published report URL 확인
16. agent-to-llm.md 결과 commit/push
```

현재 이 handover 작성 시점에는 **이 최신 요청에 대한 Agent 결과를 아직 확인하지 않았다.**

새 LLM은 먼저 GitHub remote의 최신:

```text
ai-share/agent-to-llm.md
```

를 읽어 결과가 올라왔는지 확인해야 한다.

절대 background Agent가 자동 실행 중이라고 가정하지 않는다.

---

## 15. Previous Agent Result, for Context Only

현재 `agent-to-llm.md`에 남아 있는 이전 결과는 latest presentation/FDR 변경 이전 작업이다.

그 이전 결과에는:

```text
bt-module OpenSpec strict PASS
Backtest targeted 19 PASS
full pytest 149 PASS
deterministic Playwright PASS
real-report Playwright PASS
QQQ/GLD/SPY real run success
069500/NAVER:069500 rows/null/gap/month coverage check
Pages deployment failure due environment protection
```

가 기록돼 있다.

하지만 current head는 그 뒤에 spec + tests + implementation이 더 변경되었으므로 이 결과를 최신 PASS로 재사용하지 않는다.

---

## 16. New LLM First Action After Agent Result Arrives

Agent result가 새로 올라와 있고 Pages exact URL까지 반환됐다면 다음 순서로 진행한다.

### Step 1. Verify Agent evidence

```text
- start/final HEAD
- OpenSpec strict
- targeted/full pytest
- deterministic Playwright
- real-report Playwright
- FDR US/KRX behavior
- fresh run paths
- screenshot paths
- Pages deployment workflow
- exact published URL
```

Agent의 PASS 문구만 믿지 말고 report/evidence를 직접 inspection한다.

### Step 2. Open published GitHub Pages report

Agent가 반환한 exact URL을 실제로 확인한다.

### Step 3. LLM 1st Visual Acceptance

비교 대상:

```text
A. Published GitHub Pages Backtest report
B. PV live/reference URL
C. Captured MHTML
D. split source/page.part-001..005.html
E. current screenshot evidence
F. internal OpenSpec research-report + legacy report UI contract
```

판정 우선순위:

```text
1. internal spec violation인가?
2. canonical output data 의미가 user-facing analytics로 적절히 표현됐는가?
3. PV와 다른 점이 단순 polish인가, 기능/정보 성격 차이인가?
4. P0/P1/P2 분류
```

특히 먼저 볼 것:

```text
- Summary 정보 흐름
- portfolio identity/order
- Performance Summary metric matrix
- Trailing human labels/format
- Growth x/y ticks and grid
- Growth hover tooltip
- benchmark name
- Active Returns data character
- Metrics가 storage dump가 아닌지
- Annual/Monthly/Drawdown/Assets/Rolling 표현 성격
- benchmark=None conditional behavior
- mobile clipping/readability
```

### Step 4. If LLM finds P0/P1

1. internal specification과 비교
2. spec이 이미 요구하면 implementation defect로 수정
3. spec이 부족하고 product 판단상 변경이 맞으면 OpenSpec 먼저 update
4. test 작성/수정
5. implementation 수정
6. Agent 재검증 + Pages republish 요청

### Step 5. User 2nd Visual Acceptance

LLM 1차에서 P0/P1을 제거한 뒤에만 사용자에게 Pages URL을 넘겨 관능 평가를 요청한다.

---

## 17. Relevant Code / Test Locations

Backtest core:

```text
src/portfolio_optimizer_kr/models.py
src/portfolio_optimizer_kr/backtest.py
src/portfolio_optimizer_kr/config/yaml.py
src/portfolio_optimizer_kr/runner.py
src/portfolio_optimizer_kr/research.py
```

Market data:

```text
src/portfolio_optimizer_kr/data/fdr.py
src/portfolio_optimizer_kr/data/transform.py
src/portfolio_optimizer_kr/data/__init__.py
```

Report/persistence:

```text
src/portfolio_optimizer_kr/report/backtest.py
src/portfolio_optimizer_kr/viewer/backtest_renderer.py
```

Tests:

```text
tests/test_backtest.py
tests/test_backtest_execution.py
tests/test_backtest_input_persistence.py
tests/test_backtest_scope.py
tests/test_backtest_report_presentation.py
tests/test_data.py
tests/test_fdr_total_return.py
```

Browser verification:

```text
verification/browser/backtest-report.spec.mjs
scripts/prepare_browser_fixture.py
scripts/verify.py
```

Pages:

```text
.github/workflows/publish-reports.yml
```

---

## 18. Research Execution / Agent Verification Rules

Research execution reuses:

```text
Study / Experiment / Run
control/execute.yaml
canonical YAML runner
```

Rules:

- explicit product mode
- experiment YAML 변경만으로 실행한 것으로 간주하지 않음
- explicit execution intent 필요
- provenance에 Study/Experiment/Run/product mode 유지
- Agent/Codex는 canonical user research execution engine이 아님

Verification flow:

```text
Test
-> Real Run
-> Result Verification
-> Browser Verification
-> Fix
-> Re-verify
-> Publish
-> LLM 1st Visual Acceptance
-> User 2nd Visual Acceptance
```

Agent는 requirements/tests/acceptance를 pass시키기 위해 약화하면 안 된다.
Shared code 변경 시 affected Optimization regression도 수행한다.

---

## 19. Report Analysis Semantics

Backtest report/research analysis는 historical comparison이다.

권장 분석 순서:

```text
coverage
-> return/risk
-> drawdown/recovery
-> rolling/period consistency
-> benchmark-relative (benchmark 있을 때만)
-> contribution/diversification supporting evidence
```

Facts와 interpretation을 분리한다.

Backtest만으로 다음을 주장하지 않는다.

```text
optimal portfolio
optimal weights
efficient frontier optimality
```

---

## 20. Known Open Issues

1. 최신 Agent request 결과 확인 필요
2. current head의 OpenSpec strict PASS 여부 최신 검증 필요
3. latest report presentation이 실제 fresh run/browser에서 spec을 만족하는지 확인 필요
4. Korean ETF default/NAVER Close total-return policy의 live FDR validation 필요
5. explicit KRX source는 여전히 canonical total-return으로 승인하지 않아야 함
6. Korean common stocks total-return source는 별도 해결되지 않음
7. GitHub Pages `bt-module` publish가 새 environment 설정 후 실제 성공하는지 확인 필요
8. exact Pages URL 확보 필요
9. LLM 1차 Visual Acceptance pending
10. User 2차 Visual Acceptance pending
11. `migrate-optimizer-to-openspec` strict RFC2119 issue는 Backtest와 별도 migration cleanup 필요

---

## 21. Do Not Regress These Rules

```text
- PV가 다르다는 이유만으로 spec을 자동 변경하지 않는다.
- 반대로 machine test가 PASS했다는 이유만으로 visual/product output이 충분하다고 간주하지 않는다.
- Backtest 때문에 기존 docs/*.md를 수정하지 않는다.
- Backtest-specific change는 openspec/changes/bt-module/에 둔다.
- price-only를 total-return으로 silent fallback하지 않는다.
- raw artifact/debug schema를 user-facing report의 primary UI로 노출하지 않는다.
- portfolio identity를 color만으로 전달하지 않는다.
- browser에서 finance 계산을 다시 수행하지 않는다.
- Agent가 LLM 1차 visual acceptance를 대신하지 않는다.
- User에게 2차 관능 평가를 넘기기 전에 LLM이 output/function character를 먼저 검토한다.
```

---

## 22. Immediate Next

새 LLM 창에서 바로 다음과 같이 진행한다.

```text
1. GitHub remote의 ai-share/PROTOCOL.md 확인
2. 이 llm-to-llm.md 확인
3. 최신 ai-share/agent-to-llm.md 확인
4. 현재 branch/head 확인
5. Agent 최신 결과가 있으면 검증 evidence와 exact Pages URL 확인
6. Published Pages report vs PV captured MHTML로 LLM 1차 Visual Acceptance 수행
7. P0/P1이면 spec 확인 -> 필요시 OpenSpec update -> test-first 수정
8. Agent reverify/republish
9. LLM PASS 후 User 2차 Visual Acceptance
```

새 창에서 사용자는 간단히 다음처럼 시작하면 된다.

```text
portfolio-optimizer-kr의 ai-share/llm-to-llm.md를 읽고 현재 Backtest 작업을 이어서 진행하자.
```
