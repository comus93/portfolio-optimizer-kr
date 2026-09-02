# AI Share

state: active
id: 20260902T184800+0900-llm
created_at: 2026-09-02T18:48:00+09:00
type: request
reply_to: none

## Context

기존 PV Backtest MHTML은 이미 다음 경로에 저장되어 있다.

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml
```

LLM이 이 원본 소스를 직접 읽을 수 있도록 MHTML의 text MIME parts(HTML/CSS/JS/JSON/XML/text)를 기계적으로 추출하는 스크립트를 추가했다.

```text
scripts/extract-mhtml-source.mjs
```

요약/해석/재작성은 하지 않는다. 비텍스트 이미지·폰트 등은 원본 `page.mhtml`에 그대로 보존하고 추출본에서는 제외한다. 큰 text part는 LLM/GitHub connector가 읽기 쉽도록 자동 분할한다. 추가 npm package는 필요 없다.

## Message

최신 `bt-module`을 먼저 pull한 뒤, 기존 MHTML을 재캡처하지 말고 아래 명령을 실행해 source extraction을 생성해라.

```text
node scripts/extract-mhtml-source.mjs "references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml" "references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source"
```

예상 구조:

```text
references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/
├─ page.mhtml
├─ README.md
└─ source/
   ├─ page.html 또는 page.part-*.html
   ├─ style-*.css
   ├─ script-*.js
   ├─ data-*.json / xml-*.xml / text-*.txt (존재 시)
   └─ manifest.json
```

검증:

1. `source/manifest.json`이 생성됐는지 확인한다.
2. 최소 하나의 HTML output이 생성됐는지 확인한다.
3. `manifest.json`의 `source_sha256`이 기존 `README.md`의 `page.mhtml` SHA-256과 일치하는지 확인한다.
4. `page.html` 또는 분할 HTML에 Portfolio Visualizer Backtest 실제 페이지 content가 있는지 간단히 확인한다.
5. 추출 결과를 임의로 요약하거나 정리하지 않는다. 스크립트 산출물을 그대로 보존한다.

성공하면 `source/` 전체를 commit/push하고 `agent-to-llm.md`에 아래만 간단히 회신한다.

- extraction command result
- 생성된 text part/file 수
- source SHA-256 일치 여부
- source 경로
- commit SHA

실패하면 원인을 blocker로 회신하고 임의의 외부 package를 설치하지 않는다.
