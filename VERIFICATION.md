# Verification

이 repository의 agent verification은 `verification/profile.yaml`을 기준으로 최소 단계부터 수행한다.

```text
Test
→ Real Run
→ Result Verification
→ Playwright Browser Verification
→ GitHub Pages Publish (material report change)
→ LLM 1차 Visual Acceptance
→ User 2차 Visual Acceptance
→ Fix
→ Re-verify
```

## Command entrypoint

Targeted + affected regression:

```bash
python scripts/verify.py
```

OpenSpec strict validation 포함:

```bash
python scripts/verify.py --openspec
```

Full pytest까지 포함:

```bash
python scripts/verify.py --openspec --full
```

Deterministic Playwright browser acceptance까지 포함:

```bash
python scripts/verify.py --openspec --full --browser
```

실제 생성된 Backtest report를 Playwright로 검증:

```bash
python scripts/verify.py --browser-report runs/<run-id>/report.html
```

`--browser`는 network-free synthetic price fixture를 `.playwright/backtest-browser/`에 만들고 localhost HTTP server에서 benchmark 있음/없음 두 report를 검사한다. `--browser-report`는 fixture 대신 repository 내부의 실제 `report.html`을 검사한다.

## One-time Playwright setup

Node/npm이 설치된 Codex checkout에서 한 번 실행한다.

```bash
npm install
npx playwright install chromium
```

`npm install`이 만든 `package-lock.json`은 dependency lockfile로 repository에 유지한다. 이후 browser verification은 Chromium을 매번 다시 설치하지 않는다.

## Automated browser acceptance

`verification/browser/backtest-report.spec.mjs`가 다음을 machine-judgeable contract로 검사한다.

- Summary에 requested/effective period, Initial Amount, Benchmark, Rebalancing, Calendar Aligned, Return Semantics가 존재
- Summary primary flow에 Target Allocation, Performance Summary, Portfolio Growth, Trailing Returns가 존재
- Target Allocation에 portfolio/asset/target weight identity가 존재
- Growth chart에 복수의 중간 x/y ticks와 y-grid, `Year`, `Portfolio Balance ($)` axis semantics가 존재
- Growth chart hover와 keyboard focus에서 date/portfolio/balance visible tooltip이 존재
- Summary / conditional Active Returns / Metrics / Annual Returns / Monthly Returns / Drawdowns / Assets / Rolling Returns section grouping이 존재
- Optimization-only `Efficient Frontier` / `Optimized Portfolio`가 없음
- v1에서 지원하지 않는 Style Analysis / Factor Regression을 fabricated section으로 만들지 않음
- benchmark가 있을 때만 Active Returns section 표시
- 390px viewport에서 document-level horizontal clipping 없음
- 폭이 큰 table/chart는 자체 horizontal scroll로 정보 접근 가능

Playwright는 localhost에서 repository root를 static serving한다. `file://` 기반 검증은 사용하지 않는다.

## GitHub Pages publishing

Material report/layout change의 visual acceptance는 local screenshot만으로 끝내지 않는다. 대표 real run을 `runs/<run-id>/`에 persist하고 commit/push한 뒤 `.github/workflows/publish-reports.yml`로 GitHub Pages에 게시한다.

Workflow는 `main`과 `bt-module`의 persisted run 변경을 배포하며 Pages index에 `report.html`이 존재하는 run 링크를 생성한다. Agent는 배포 성공을 확인하고 **정확한 published report URL**을 `runs/<run-id>/validation/` evidence와 `agent-to-llm.md`에 기록한다.

## Layered visual acceptance

Material layout/interaction change는 두 단계로 판정한다.

### 1차: LLM visual acceptance

LLM은 실제 GitHub Pages report와 repository의 captured Portfolio Visualizer MHTML reference를 함께 확인한다. Pixel copy를 요구하지 않지만 다음은 사람이 보기 전에 먼저 잡아낸다.

- information architecture / section grouping이 Backtest 결과의 성격과 맞는지
- canonical result에 존재하는 중요한 output이 report에서 지나치게 축약/누락되지 않았는지
- chart axis, units, ticks, legend, tooltip/interaction semantics가 충분한지
- benchmark conditional behavior와 unsupported feature exclusion이 맞는지
- PV reference와 큰 차이가 있더라도 그 차이가 내부 requirement에 따른 의도인지, 단순 기능 누락인지

LLM 1차에서 P0/P1 수준의 기능적/정보구조적 문제가 발견되면 먼저 수정하고 다시 publish/검증한다.

### 2차: User visual acceptance

1차 blocker가 해소된 published GitHub Pages report를 사용자가 직접 확인한다. 사용자는 최종 usability, 정보 밀도, 배치 균형, 가독성, 시각적 polish 같은 관능적 판단을 담당한다.

Agent 관찰이나 Playwright PASS는 이 2차 acceptance를 대신하지 않는다.

## Evidence

Playwright local evidence:

```text
playwright-report/
test-results/playwright/
```

실패 시 trace/screenshot을 보존하고 PASS 시에도 desktop/mobile screenshot을 test output에 남긴다. 대표 validation run에 영구 evidence가 필요하면 `runs/<run-id>/validation/`으로 필요한 screenshot/summary를 복사해 commit한다.

Codex의 Full CDP Access는 켜져 있으면 추가 DOM/console/network 진단에 사용할 수 있지만 Playwright acceptance의 필수 dependency는 아니다. Playwright Chromium이 canonical automated browser runner다.

## Rules

- 실패를 통과시키기 위해 requirement, acceptance criterion, finance formula, test를 임의로 약화·삭제·skip하지 않는다.
- 구현 수정 후에는 영향을 받은 단계부터 다시 검증한다.
- shared capability 변경은 영향을 받는 기존 Optimization regression을 포함한다.
- report/viewer 변경은 실제 served browser context에서 semantic/interaction을 확인한다.
- PV pixel parity는 acceptance criterion이 아니다.
- material report/layout change는 GitHub Pages publish 후 LLM 1차, User 2차 visual acceptance를 거친다.
