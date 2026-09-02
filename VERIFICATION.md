# Verification

이 repository의 agent verification은 `verification/profile.yaml`을 기준으로 최소 단계부터 수행한다.

```text
Test
→ Real Run
→ Result Verification
→ Browser Verification
→ Human Visual Review when applicable
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

`--browser`는 network-free synthetic price fixture를 `.playwright/backtest-browser/`에 만들고, localhost HTTP server에서 두 report를 검사한다.

- benchmark 있음
- benchmark 없음

`--browser-report`는 fixture 대신 repository 내부의 실제 `report.html`을 검사한다.

## One-time Playwright setup

Node/npm이 설치된 Codex checkout에서 한 번 실행한다.

```bash
npm install
npx playwright install chromium
```

`npm install`이 만든 `package-lock.json`은 dependency lockfile이므로 최초 setup/verification에서 정상 생성되면 repository에 commit하는 것을 권장한다.

이후 browser verification은 Chromium을 매번 다시 설치하지 않는다.

## Automated browser acceptance

`verification/browser/backtest-report.spec.mjs`가 다음을 machine-judgeable contract로 검사한다.

- Overview에 Time Period Mode, requested/effective period, Initial Amount, Benchmark, Rebalancing, Calendar Aligned, Return Semantics가 존재
- Target Allocation에 portfolio/ticker/target weight identity가 존재
- Growth chart가 portfolio/date/실제 balance 의미를 제공
- Optimization-only `Efficient Frontier` / `Optimized Portfolio`가 없음
- benchmark가 있을 때만 benchmark-relative section 표시
- Performance/Annual/Monthly/Drawdown/Rolling/Correlation/Decomposition section 존재
- 390px viewport에서 document-level horizontal clipping 없음
- 폭이 큰 table/chart는 자체 horizontal scroll로 정보 접근 가능

Playwright는 localhost에서 repository root를 static serving한다. `file://` 기반 검증은 사용하지 않는다.

## Evidence

Playwright는 다음 evidence를 생성한다.

```text
playwright-report/
test-results/playwright/
```

실패 시 trace/screenshot을 보존하고, Backtest browser test는 PASS 시에도 desktop/mobile full-page screenshot을 test output에 남긴다.

위 artifact들은 로컬 검증 산출물이므로 `.gitignore` 대상이다. 대표 validation run에 evidence를 영구 보존해야 할 경우 Agent가 필요한 screenshot/summary를 해당 `runs/<run-id>/validation/`으로 복사해 commit한다.

## Human visual review

Playwright는 semantic/interaction acceptance를 담당한다. 픽셀 완성도, 정보 밀도, 시각적 균형 같은 미적 판단은 자동 PASS로 선언하지 않는다.

material layout/interaction change에서는 Agent가 Playwright screenshot과 P0/P1/P2 관찰사항을 준비하고, **human reviewer가 최종 visual acceptance를 결정한다.**

Codex의 Full CDP Access는 켜져 있으면 추가 진단에 사용할 수 있지만 Playwright acceptance의 필수 dependency는 아니다. Playwright Chromium이 canonical automated browser runner다.

## Rules

- 실패를 통과시키기 위해 requirement, acceptance criterion, finance formula, test를 임의로 약화·삭제·skip하지 않는다.
- 구현 수정 후에는 영향을 받은 단계부터 다시 검증한다.
- shared capability 변경은 영향을 받는 기존 Optimization regression을 포함한다.
- report/viewer 변경은 실제 served browser context에서 semantic/interaction을 확인한다.
- PV pixel parity는 acceptance criterion이 아니다.
- Human visual review는 material layout/interaction change에만 completion gate로 사용한다.
