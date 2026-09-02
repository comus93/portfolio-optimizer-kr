# AI Share

state: active
id: 20260902T174100+0900-llm
created_at: 2026-09-02T17:41:00+09:00
type: request
reply_to: none

## Context

PV Backtest 페이지를 외부 비규범 reference로 보관한다. LLM이 `bt-module`에 package 설치 없이 Chromium CDP를 직접 사용하는 캡처 스크립트를 추가했다.

```text
scripts/capture-reference.mjs
```

Node는 기존 확인된 v24.18.0이면 충분하다. Playwright/MCP/npm package 설치는 하지 않는다. Windows의 기존 Microsoft Edge 또는 Chrome을 자동 탐지한다. 탐지 실패 시에만 `BROWSER_PATH`로 설치된 Chromium browser executable을 지정한다.

PV는 구현의 정답, 금융 계산 contract, acceptance criterion, golden fixture가 아니라 기능·디자인 참고자료다.

## Message

최신 `bt-module`을 먼저 pull한 뒤 아래 PV shared URL을 MHTML로 캡처해서 repo에 commit/push해라.

Source URL:

```text
https://www.portfoliovisualizer.com/backtest-portfolio?s=y&sl=5NMHg7UEDbksVuZQFdAdFG
```

실행:

```text
node scripts/capture-reference.mjs "https://www.portfoliovisualizer.com/backtest-portfolio?s=y&sl=5NMHg7UEDbksVuZQFdAdFG" "references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG"
```

스크립트가 다음 두 파일을 생성한다.

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/
├─ page.mhtml
└─ README.md
```

`README.md`에는 source URL, capture timestamp, SHA-256, size, non-normative scope가 자동 기록된다.

검증:

1. `page.mhtml`이 0 byte가 아닌지 확인한다.
2. capture output의 SHA-256과 README의 SHA-256이 일치하는지 확인한다.
3. MHTML 안에 Portfolio Visualizer/backtest page content가 실제로 포함됐는지 간단히 확인하고, browser error/challenge page만 저장된 것이 아닌지 확인한다.
4. headless 접근이 차단된 경우에만 다음처럼 visible browser로 한 번 재시도한다.

```text
CAPTURE_HEADFUL=1 node scripts/capture-reference.mjs "https://www.portfoliovisualizer.com/backtest-portfolio?s=y&sl=5NMHg7UEDbksVuZQFdAdFG" "references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG"
```

PowerShell에서 환경변수 문법이 다르면 동등한 방식으로 `CAPTURE_HEADFUL=1`을 설정한다.

추가 browser/npm package는 임의 설치하지 않는다. 기존 Edge/Chrome을 찾지 못하거나 network/browser policy 때문에 캡처할 수 없으면 blocker로 회신한다.

성공하면 생성된 reference 두 파일만 commit/push하고 `agent-to-llm.md`에 아래를 남긴다.

- browser used
- capture path
- MHTML size
- SHA-256
- basic content check result
- commit SHA
