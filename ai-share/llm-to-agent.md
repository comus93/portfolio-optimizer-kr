# AI Share

state: active
id: 20260903T001800+0900-llm
created_at: 2026-09-03T00:18:00+09:00
type: request
reply_to: 20260902T235900+0900-agent

## Context

사용자 요청에 따라 LLM이 테스트를 먼저 추가한 뒤 다음 구현 수정까지 GitHub `bt-module`에 반영했다.

이번 변경의 normative source는 `openspec/changes/bt-module/`이며 legacy `docs/*.md`는 변경하지 않았다.

주요 변경:

1. FDR source-aware total-return 판정
   - FDR 한국 6자리 종목 default route는 NAVER이고 NAVER schema에는 별도 `Adj Close`가 없다.
   - 국내 ETF의 default/NAVER `Close`는 FDR에서 distribution-aware adjusted series로 취급하는 근거가 있으므로 ETF임이 FDR `StockListing("ETF/KR")`로 확인될 때 canonical total-return input으로 허용한다.
   - explicit `KRX:` source의 `Close`는 자동 승인하지 않는다.
   - 국내 일반주식에 ETF 정책을 확장하지 않는다.
   - `select_total_return_price(..., close_is_total_return=True)`는 provider adapter가 source/instrument semantics를 검증한 경우에만 `Close`를 허용한다.

2. Backtest report presentation
   - raw artifact schema를 사용자-facing primary presentation으로 그대로 노출하지 않도록 수정.
   - Performance Summary의 `unit` storage column 제거.
   - Trailing Returns의 snake_case/_pct storage label을 사용자 용어 및 % formatting으로 변환.
   - Metrics long-format `portfolio/metric/value`를 metric × portfolio matrix로 변환.
   - Active Returns의 월별 raw observation dump를 Benchmark Summary / Annual Active Return / latest Active Return Contribution / Up-Down summary presentation으로 변경.
   - canonical input portfolio 순서를 allocation/performance/legend/table 비교 전반에 유지.
   - Growth x-axis를 row-index 등분이 아니라 actual date coordinate + calendar-aware Jan/Jul cadence로 변경.
   - benchmark는 growth legend 및 table에서 human-readable configured name 사용.
   - 기타 annual/monthly/drawdown/assets/rolling table도 storage field suffix를 사용자-facing label/unit으로 변환.

3. Test-first additions
   - `tests/test_backtest_report_presentation.py`
   - `tests/test_fdr_total_return.py`
   - 강화된 `verification/browser/backtest-report.spec.mjs`

사용자가 Agent 실행 전에 GitHub `github-pages` environment가 `bt-module` deployment를 허용하도록 설정할 예정이다. 이전 Pages protection blocker는 이번 실행에서는 해소된 것으로 가정하고 실제 publish 성공 여부를 다시 확인한다.

## Message

### 0. Sync

반드시 GitHub remote 최신본부터 확인한다.

```bash
git pull --ff-only origin bt-module
```

임의 merge/rebase 금지. 작업 시작 HEAD를 기록한다.

### 1. OpenSpec validation

현재 Backtest delta를 strict validation한다.

```bash
npx -y @fission-ai/openspec@latest validate bt-module --strict
```

`migrate-optimizer-to-openspec`도 상태 확인은 하되, 기존 RFC2119 문제를 이번 Backtest 작업을 위해 임의 수정하지 않는다. 별도 blocker/deviation으로만 보고한다.

### 2. Targeted tests first

새 테스트와 affected data/report tests부터 실행한다.

```bash
uv run pytest -q \
  tests/test_data.py \
  tests/test_fdr_total_return.py \
  tests/test_backtest_report_presentation.py \
  tests/test_backtest_execution.py \
  tests/test_backtest.py
```

실패하면 specification/test를 약화하지 말고 구현 결함을 수정한다. 특히 확인할 것:

- `Adj Close`가 있으면 계속 우선 사용
- default/NAVER 한국 ETF + Close-only는 성공
- 일반 한국 주식 Close-only는 strict total-return 기준에서 실패
- explicit `KRX:` Close-only는 자동 승인하지 않음
- ETF listing 조회 실패 시 price-only fallback 금지
- Performance Summary에서 `unit` column 미노출
- Trailing Returns storage suffix 미노출
- Metrics raw long-format 미노출
- portfolio input order 유지
- Growth Jan/Jul calendar-aware ticks
- human-readable benchmark identity
- Active Returns monthly raw schema 미노출

### 3. Full regression + deterministic browser

Targeted PASS 후 전체 회귀와 browser verification을 실행한다.

```bash
uv run python scripts/verify.py --openspec --full --browser
```

Optimization/shared regression 포함. 테스트를 통과시키기 위한 acceptance 완화 금지.

Playwright에서 최소 확인:

- Summary flow: allocation → performance → growth → trailing
- allocation/performance portfolio order 동일
- Performance Summary `unit` header 없음
- Trailing human labels / percent formatting
- Metrics first column `Metric`, raw `Portfolio/Value` schema 없음
- Growth x ticks가 deterministic fixture에서 `Jan/Jul YYYY` cadence
- y ticks/grid/axis title 유지
- hover + keyboard visible tooltip
- configured benchmark name이 legend에 표시
- Active Returns에서 raw storage names가 화면에 노출되지 않음
- benchmark=None에서 benchmark-relative section 없음
- 390px document clipping 없음, wide table/chart scroll 가능

### 4. Real FDR validation

실제 FinanceDataReader에서 source-aware 정책을 검증한다.

#### 4.1 US adjusted path

QQQ / GLD / SPY의 `Adj Close` 사용이 기존대로 정상인지 확인.

#### 4.2 Korean ETF path

최소 `069500`에 대해:

```python
import FinanceDataReader as fdr

listing = fdr.StockListing("ETF/KR")
print(listing.columns)
print(listing[listing.astype(str).apply(lambda row: row.str.contains("069500").any(), axis=1)])

for symbol in ["069500", "NAVER:069500"]:
    df = fdr.DataReader(symbol, "2020-01-01", "2025-12-31")
    print(symbol, df.columns.tolist(), len(df), df.isna().sum().to_dict())
```

실제 `FDRLoader().load(AssetSpec("069500", currency="KRW"))`가 성공하고 attrs가 최소 다음 의미를 가지는지 확인:

```text
return_semantics = total_return
source_column = Close
provider = FinanceDataReader
provider_route = NAVER
```

`KRX:069500`은 total-return으로 자동 승인되지 않아야 한다. 실제 FDR 자체가 symbol을 지원하지 않는 경우에도 product가 이를 total-return 성공으로 오인하지 않는지만 확인한다.

### 5. Fresh real runs

기존 persisted report를 재사용하지 말고 현재 HEAD로 새 unique run을 생성한다.

#### A. US representative run

```text
QQQ / GLD
benchmark SPY
2 portfolios
2020-2025
Month-to-Month
Monthly
Calendar Aligned Yes
Initial 10,000
```

#### B. KRX ETF smoke run

```text
asset 069500
benchmark None
1 portfolio = 100% 069500
가능한 2020-2025
Month-to-Month
Monthly
Calendar Aligned Yes
Initial 10,000
```

KRX run이 실패하면 원인을 조사하고, source-aware implementation defect면 수정 후 재검증한다. FDR 자체/API/network limitation이면 명확한 blocker로 보고한다. Price-only semantics로 우회 금지.

### 6. Real-report Playwright

새 US representative report를 대상으로 반드시 실행:

```bash
uv run python scripts/verify.py --browser-report runs/<new-us-run-id>/report.html
```

가능하면 KRX report도 동일 검증.

새 renderer output에서 screenshot evidence를 저장한다. Agent의 visual 역할은 machine acceptance + obvious defect 관찰까지이며 LLM 1차 visual acceptance를 대신하지 않는다.

### 7. Commit/push and GitHub Pages publish

검증 수정, fresh run, validation evidence를 필요한 범위에서 commit/push한다.

그 후 `Publish research reports` GitHub Actions workflow가 **이번 final HEAD**에서 성공할 때까지 확인한다.

중요: 사용자가 실행 전에 Pages environment branch 설정을 수정할 예정이다. 따라서 이전 `bt-module not allowed` 실패를 그대로 재보고하지 말고 새 workflow 결과를 확인한다.

배포 성공 후 실제 published URL을 HTTP/browser로 열어 접근 가능한지 확인한다. deployment success만 보고 URL을 추정하지 않는다.

반드시 다음 두 경로를 회신:

```text
GitHub Pages base URL
US representative run exact published report URL
```

KRX run도 publish되면 exact URL 추가.

예시 형식일 뿐 실제 URL은 workflow/site 결과에서 확인할 것:

```text
https://<owner>.github.io/<repo>/
https://<owner>.github.io/<repo>/runs/<run-id>/report.html
```

그리고 workflow run URL/ID도 남긴다.

### 8. Result handoff

`ai-share/agent-to-llm.md` 전체를 새 result로 교체하고 commit/push한다. push 성공 전에는 전달 완료라고 하지 않는다.

최소 보고 항목:

- start HEAD / final HEAD
- `bt-module` OpenSpec strict 결과
- `migrate-optimizer-to-openspec` 상태(기존 문제라면 그대로 분리)
- targeted pytest 결과
- full pytest 결과
- deterministic Playwright 결과
- real-report Playwright 결과
- US QQQ/GLD/SPY adjusted-series 확인
- KRX ETF listing 확인 및 `069500` FDRLoader attrs/result
- explicit KRX source 처리 결과
- fresh US run id/path + sanity values
- fresh KRX smoke run id/path + sanity values 또는 blocker
- Pages deployment workflow run URL/ID + 성공 여부
- **GitHub Pages base URL**
- **US representative exact published report URL**
- KRX exact published report URL(있으면)
- screenshot/evidence path
- Agent가 관찰한 P0/P1/P2
- `LLM first-pass visual acceptance pending`
- result commit SHA
