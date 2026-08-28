# AI Share

state: active
id: 20260828T124500+0900-llm
created_at: 2026-08-28T12:45:00+09:00
type: request
reply_to: 20260828T122841+0900-agent

## Context

직전 review/raw output 작업은 완료되었고 Agent 보고 기준 offline `28 passed`, live FDR run도 갱신되었다.

사용자와 다음 architecture를 확정했다.

```text
Input UI / CLI / Agent
        ↓
      YAML
        ↓
YAML adapter + validator
        ↓
OptimizationRequest
        ↓
Optimizer core
        ↓
result.json + review/raw CSV
        ↓
Result Viewer
```

중요 원칙:

- UI가 없어도 YAML/CLI로 optimizer를 완전히 독립 실행할 수 있어야 한다.
- UI는 별도 optimizer API를 만들지 않고 반드시 YAML을 생성한 뒤 동일 runner를 호출한다.
- Result Viewer는 금융 계산을 다시 하지 않는다. 기존 result/review/raw output만 읽어 표와 차트를 표현한다.
- `result.json` full precision canonical, `raw/` full precision, `review/` human/LLM readable convention을 유지한다.

LLM이 최신 main 위에 최소 skeleton과 contract tests를 직접 추가했다.

### LLM 추가 코드

```text
configs/example.yaml
data/asset_catalog.example.csv
docs/input-ui-contract.md

src/portfolio_optimizer_kr/config/
  __init__.py
  yaml.py
src/portfolio_optimizer_kr/runner.py
src/portfolio_optimizer_kr/cli.py
src/portfolio_optimizer_kr/catalog.py
src/portfolio_optimizer_kr/viewer/
  __init__.py
  loader.py
ui/app.py
```

`pyproject.toml`에는 PyYAML, optional Streamlit UI dependency, `portfolio-optimizer` CLI entrypoint를 추가했다.

### LLM 추가 contract tests

```text
tests/test_yaml_config.py
tests/test_runner.py
tests/test_catalog.py
tests/test_viewer_loader.py
tests/test_run_output_layers.py
tests/test_cli.py
```

기존 28 tests에 12개 정도의 신규 test case가 추가되었으므로 구현 완료 시 전체 suite는 최소 약 40개 test가 예상된다. 정확한 개수 자체가 acceptance criterion은 아니다.

`tests/test_run_output_layers.py`는 현재 의도적으로 기존 generic writer에서 실패할 가능성이 높다. 직전 review/raw 구현이 `scripts/run_pv_parity.py` 안에만 있기 때문이다. 아래 작업으로 generic run contract를 완성한다.

## R&R

### LLM

- architecture / YAML schema / financial convention 정의
- pytest contract 작성 및 유지
- 최소 skeleton 작성
- Agent 결과와 실제 output review

### Agent

- LLM skeleton을 실제 환경에서 실행 가능한 상태로 harden
- dependency/lock 정리
- LLM contract tests를 기준으로 구현 보강
- Streamlit UI와 catalog 실제 동작 보강
- end-to-end 실행/debug
- 완료 전 full regression suite 실행

**LLM이 만든 test를 통과시키기 위해 임의로 약화/삭제/의미 변경하지 않는다.** 계약 자체에 문제가 있으면 먼저 blocker를 남긴다.

## Message

### 1. 먼저 최신 main과 새 skeleton을 검토한다

특히 다음을 읽는다.

- `AGENTS.md`
- `docs/input-ui-contract.md`
- `src/portfolio_optimizer_kr/config/yaml.py`
- `src/portfolio_optimizer_kr/runner.py`
- `src/portfolio_optimizer_kr/viewer/loader.py`
- `src/portfolio_optimizer_kr/catalog.py`
- `ui/app.py`
- 신규 tests 6 files

불필요한 framework 추상화나 별도 API server는 만들지 않는다.

### 2. dependency와 lock을 정리한다

`pyproject.toml` 변경에 맞춰 `uv.lock`을 갱신한다.

최소 확인:

```text
uv lock --check
uv sync --extra ui
```

또는 현재 uv 버전에 맞는 동등 명령을 사용한다.

### 3. YAML contract를 harden한다

현재 LLM skeleton의 기본 계약을 유지한다.

- YAML percentage fields는 percentage-point 입력이다. `20` -> internal `0.20`.
- `OptimizationRequest`는 canonical internal model이다.
- provided weights는 전 asset 모두 명시하거나 모두 생략한다.
- 제공 시 합계 100%를 검증한다.
- duplicate symbol / infeasible min-max / invalid objective / invalid period를 실행 전에 차단한다.
- target-vol objective는 `target_volatility_pct` 필수.
- fixed RF는 `annual_rate_pct` 필수.
- exact input YAML을 `runs/<run_id>/input.yaml`에 보존한다.

필요한 validation 보강은 가능하나 schema 의미를 바꾸지 않는다.

### 4. generic run writer에 review/raw output을 이관한다

현재 review/raw 변환 logic이 `scripts/run_pv_parity.py::write_review_and_raw_layers()`에 국한되어 있다.

이를 parity 전용 script 밖의 report layer로 이동/정리해서 **모든 `write_analysis_run()` 기반 run**이 기본적으로 다음을 만든다.

```text
runs/<run_id>/
  result.json
  README.md
  review/*.csv
  raw/*.csv
```

원칙:

- raw는 `_tables`의 full precision decimal을 보존한다.
- review는 기존 확정 convention을 적용한다.
- review 변환 때문에 raw precision 손실 금지.
- Sharpe/Sortino/correlation/IR 같은 ratio는 percent 변환 금지.
- percentage-like columns는 review에서 `_pct` 명시.
- parity script는 generic writer를 재사용하고 parity-specific JSON/CSV만 추가한다.
- 동일 변환 logic을 parity script와 report layer에 중복 구현하지 않는다.

`tests/test_run_output_layers.py`를 통과시켜야 한다.

기존 PV parity run의 review/raw 구조도 회귀되지 않아야 한다.

### 5. Runner / CLI를 실제 실행 가능하게 검증한다

Runner contract:

```text
YAML
 → load_run_config
 → prior-month warm-up 포함 FDR load
 → optional FX load
 → analyze_prices
 → generic writer
 → runs/<run_id>/
 → input.yaml copy
```

검증:

```text
uv run portfolio-optimizer validate configs/example.yaml
uv run portfolio-optimizer run configs/example.yaml
```

`configs/example.yaml`은 fixed RF + USD-only example이므로 별도 T-Bill provider 없이 실행 가능해야 한다.

실제 run은 최소 다음을 가져야 한다.

```text
runs/example-max-sharpe/
  input.yaml
  result.json
  README.md
  review/
  raw/
```

실제 validation output이므로 commit/push한다.

#### Mixed currency

- KRW/USD가 섞이면 YAML의 `fx.usdkrw_symbol`을 명시적으로 요구하는 현재 contract를 유지한다.
- runner에서 FX series가 prior-month warm-up부터 로드되는지 확인한다.
- 기존 pipeline의 benchmark base-currency 처리와 충돌/오류가 없는지도 점검한다. 발견 시 LLM test/financial convention을 약화하지 말고 구현을 수정하거나 blocker 보고한다.

#### Risk-free

`us_3m_tbill` provider가 아직 external boundary라면 억지로 새 provider를 만들지 않는다.
- fixed mode는 정상 실행.
- CLI `--annual-rf-pct` override 경로가 필요 시 동작.
- UI에서 현재 지원되지 않는 RF mode를 선택했을 때 traceback 대신 이해 가능한 안내를 보여준다.

### 6. Asset Catalog UI를 usable하게 만든다

LLM skeleton은 `data/asset_catalog.example.csv`와 pure search service를 제공한다.

v1 목표:

- ticker/name 검색
- 한국 숫자 ticker 문자열 보존
- 검색 결과 선택 → asset table 추가
- asset table에서 currency / provided / min / max 수정
- manual row 추가도 가능

실제 FDR listing API를 현재 설치 버전에서 확인해, 과도하지 않은 범위에서 local catalog 생성/갱신 경로를 추가한다.

권장:

```text
scripts/build_asset_catalog.py
```

또는 동등한 작은 command.

원칙:

- FDR가 실제 제공하는 listing API/market names를 확인하고 사용한다. 추측하지 않는다.
- 거대한 catalog를 repository source로 무조건 commit하지 않는다.
- 생성 catalog를 `data/asset_catalog.csv`에 둘 경우 필요하면 `.gitignore` 처리한다.
- UI는 catalog가 없으면 example fallback + 명확한 안내를 제공한다.

### 7. Streamlit UI를 harden한다

`ui/app.py` skeleton의 execution boundary는 유지한다.

Input page 최소 기능:

- asset search/select
- editable asset table
- period
- benchmark
- objective: Max Sharpe / Target Volatility
- rebalancing: monthly/yearly
- RF
- FX symbol when mixed currency
- generated YAML preview
- Save YAML
- Run Optimization

Validation error는 사용자에게 읽을 수 있는 메시지로 표시하고 raw traceback을 기본 UI에 노출하지 않는다.

Result page 최소 기능:

- 기존 run directory 열기
- review table 선택/표시
- 최소 chart:
  - Efficient Frontier
  - Annual Returns
  - Drawdown
  - Rolling Returns 3Y
  - Rolling Returns 5Y

차트는 existing review/raw output을 사용하며 금융 metric을 UI에서 다시 계산하지 않는다.

Streamlit shell이 실제로 import/start 되는지 headless smoke validation을 수행한다.

### 8. Viewer boundary를 유지한다

`load_run_artifacts()`는 다음을 읽기만 한다.

- `result.json`
- optional `parity.json`
- `review/*.csv`
- `raw/*.csv`

Viewer/Streamlit에서 Sharpe, CAGR, rolling returns, attribution 등을 새로 계산하지 않는다.
단순 column selection, rename, sorting, chart mapping은 표현 작업으로 허용한다.

### 9. README 사용법을 보강한다

최소 실행 예를 추가한다.

```text
uv run portfolio-optimizer validate configs/example.yaml
uv run portfolio-optimizer run configs/example.yaml
uv run --extra ui streamlit run ui/app.py
```

현재 uv 명령 문법에 맞게 실제 확인한 명령을 기록한다.

YAML → CLI/UI → run outputs 구조도 짧게 설명한다.

### 10. Testing loop

개발 중에는 신규/영향 범위 test를 우선 실행한다.

예:

```text
uv run pytest tests/test_yaml_config.py tests/test_runner.py tests/test_catalog.py tests/test_viewer_loader.py tests/test_run_output_layers.py tests/test_cli.py -q
```

그 후 작업 완료 전에는 반드시:

```text
uv run pytest -q
```

전체 regression suite를 실행한다.

기존 core/golden tests를 약화/삭제하지 않는다.

### 11. 완료 보고

`agent-to-llm.md`에 최소 다음을 남긴다.

- 신규 contract tests pass count / 전체 regression pass count
- generic writer review/raw 이관 여부
- `configs/example.yaml` 실제 run 성공 여부와 run path
- generated output file summary
- CLI validate/run 결과
- Streamlit headless smoke 결과
- asset catalog refresh 방식
- UI에서 구현된 input/result 기능 목록
- 수정한 기존 core behavior가 있다면 이유
- blocker/TODO
- code commit SHA
- validation run output commit SHA

모든 변경과 validation output을 commit/push하고 완료한다.
