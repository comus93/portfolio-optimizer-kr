# PV Backtest Content Comparison

- created_at: 2026-09-03 13:56 KST
- repository: `comus93/portfolio-optimizer-kr`
- branch: `bt-module`
- comparison_run_id: `20260903-backtest-qqq-gld-spy-presentation-validation-v2`
- comparison_run_report: `runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html`
- public_report: https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html
- agent_result_commit: `d35eb520325ca576767d3edc73c1391409bbeb1a`

## 1. Purpose

이 문서는 Portfolio Visualizer(PV)의 Backtest 결과 페이지를 그대로 복제하기 위한 문서가 아니다.

목적은 사용자가 제공한 PV reference에서 **어떤 분석 주제와 정보 구조를 결과 리포트에 담고 있는지**를 추출하고, 해당 주제가 현재 Backtest 실행 결과 `report.html`에 어느 정도 존재하는지를 비교하는 것이다.

따라서 이 문서의 판정은 그래픽 픽셀 일치나 미적 유사성이 아니라 다음 관점에 집중한다.

1. PV reference가 다루는 분석 주제
2. 현재 Backtest report의 동일/유사 주제 존재 여부
3. 주제가 존재하더라도 정보 폭이나 구성 방식이 다른지
4. 빠진 항목이 구현 누락인지, 현재 제품 scope에서 의도적으로 제외된 것인지

이 문서는 **non-normative validation/research note**이며 OpenSpec, 제품 specification, 금융 계산 contract를 대체하지 않는다.

## 2. Comparison Sources

### 2.1 PV captured reference

Repo reference:

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/`

Primary capture:

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml`

Machine-extracted source:

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/manifest.json`

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/page.part-001.html`

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/page.part-002.html`

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/page.part-003.html`

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/page.part-004.html`

`references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/source/page.part-005.html`

Captured PV URL:

https://www.portfoliovisualizer.com/backtest-portfolio?s=y&sl=5NMHg7UEDbksVuZQFdAdFG

The repo README explicitly marks this capture as an external, non-normative reference for feature/layout/interaction research.

### 2.2 Companion Markdown reference

User-supplied File Library source:

`Backtest Portfolio Asset Allocation.md`

이 Markdown은 PV Backtest 결과 페이지의 텍스트/표 구조를 읽기 쉽게 보조하는 reference로 사용했다. Repo MHTML과 companion Markdown을 함께 보고 주제 taxonomy를 추출했다.

### 2.3 Current implementation result compared

Run:

`20260903-backtest-qqq-gld-spy-presentation-validation-v2`

Repo report:

`runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html`

Published report:

https://comus93.github.io/portfolio-optimizer-kr/runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html

Agent validation result:

`ai-share/agent-to-llm.md`

Agent result commit:

`d35eb520325ca576767d3edc73c1391409bbeb1a`

## 3. Comparison Rule

Status meanings:

- **Present**: 같은 분석 주제와 실질적인 정보가 현재 report에 존재
- **Partial**: 주제는 존재하지만 PV보다 정보 폭/표현이 일부 축소 또는 재배치
- **Missing**: 현재 report에 해당 분석 주제가 없음
- **Intentional exclusion candidate**: PV에는 있으나 현행 Backtest v1 scope에서 의도적으로 제외한 영역일 가능성이 큼
- **Internal advantage**: PV보다 현재 research report가 실험 재현성 관점에서 더 명시적인 정보

숫자 자체는 비교하지 않는다. PV reference와 현재 run의 포트폴리오 구성과 기간이 다르기 때문이다.

## 4. Topic-by-Topic Comparison

| Topic | PV MHTML + Markdown | Current Backtest report | Status / Interpretation |
| --- | --- | --- | --- |
| Result navigation / macro structure | Summary / Exposures / Active Returns / Metrics / Annual Returns / Monthly Returns / Drawdowns / Assets / Rolling Returns | Summary / Active Returns / Metrics / Annual Returns / Monthly Returns / Drawdowns / Assets / Rolling Returns | **Partial**. 거의 동일하지만 `Exposures`가 없음 |
| Portfolio composition | Portfolio별 ticker/name/allocation과 allocation 시각화 | Summary의 `Target Allocation` matrix | **Present**. PV는 portfolio-centric, 현재 report는 experiment-centric |
| Portfolio highlights / narrative summary | 각 portfolio별 annualized return, benchmark relative return, volatility, drawdown, positive months, best/worst year, Sharpe, upside/downside capture 등을 읽기 쉬운 요약으로 설명 | Performance Summary + Growth + Trailing Returns 중심 | **Partial**. 숫자 상당수는 있으나 한 포트폴리오를 설명하는 narrative summary는 약함 |
| Performance Summary | Start/End balance, CAGR, Std Dev, best/worst year, MDD, Sharpe, Sortino, active return, tracking error, information ratio, benchmark correlation | 대부분 동일한 core metric | **Present**. 핵심 성과 비교 기능은 충분 |
| Portfolio Growth | Portfolio/benchmark balance growth, inflation-adjusted balance tooltip, logarithmic scale option 등 | Portfolio/benchmark growth chart, calendar-aware ticks, tooltip | **Partial**. 핵심 growth는 있으나 log scale / inflation-adjusted 관점 없음 |
| Trailing Returns | 3M, YTD, 1Y, 3Y, 5Y, Full + 3Y/5Y annualized volatility | 동일 계열 + 10Y까지 지원 | **Present**. 현재 report 쪽 기간 범위가 일부 더 넓음 |
| Exposures / Holdings Based Style Analysis | Category, yield, expense ratio, P/E, duration, return/risk contribution, asset allocation, market cap, sector, bond credit, maturity 등 | section 자체 없음 | **Missing**, 동시에 **Intentional exclusion candidate**. 가장 큰 주제 단위 차이 |
| Annual Active Return | Benchmark 대비 annual active return | Annual Active Return chart/table | **Present** |
| Active Return Contribution | Constituent별 cumulative active contribution 및 관련 분석 | Asset별 Active Return Contribution visualization | **Present / Partial**. 핵심 주제는 구현됨. PV 쪽 기간별 요약 표현이 더 풍부할 수 있음 |
| Rolling Active Return / Tracking Error | 36-month rolling active return + tracking error | 36-month rolling active return + tracking error | **Present**. 높은 parity |
| Up / Down Market Performance | Benchmark 상승/하락장에서 상회/하회 횟수, 비율, 평균 active return, benchmark return별 비교 | 동일 계열 통계와 `Return vs. Benchmark` visualization | **Present**. 높은 parity |
| Broad Risk & Return Metrics | arithmetic/geometric mean, downside deviation, beta, alpha, R², Sharpe, Sortino, Treynor, Calmar, M², multiple VaR variants, capture, withdrawal-rate related metrics, positive periods, gain/loss 등 | Beta, Alpha, R², Treynor, Calmar, M², Skew, Kurtosis, Historical VaR 등 | **Partial**. 현재 report의 metric breadth가 PV보다 좁음 |
| Annual Returns | Portfolio / benchmark / inflation / balance / asset annual return 등 | Portfolio/benchmark annual returns, asset annual returns는 Assets로 이동 | **Partial**. 주요 return 데이터는 있으나 inflation/balance는 없음, 일부 재배치 |
| Monthly Returns | Portfolio별 Jan-Dec + YTD | Portfolio/benchmark Jan-Dec + YTD | **Present** |
| Drawdowns | Portfolio별 ranked drawdown episodes, start, bottom, recovery, duration, MDD | Drawdown chart + episode table | **Present**. 높은 parity |
| Portfolio Asset Performance | 개별 자산 CAGR, volatility, drawdown, Sharpe/Sortino, trailing return 등 | 개별 자산 historical performance table | **Present** |
| Annual Asset Returns | 자산별 연도별 return | Assets section의 annual asset return chart/table | **Present**, 위치만 다름 |
| Correlations | Portfolio/asset correlation analysis | Asset / portfolio / benchmark 통합 correlation heatmap | **Present**. research 용도상 현재 구성이 명확한 편 |
| Return Decomposition | Constituent return contribution | Return Decomposition | **Present** |
| Risk Decomposition | Constituent risk contribution | Risk Decomposition | **Present** |
| Rolling Returns | 1Y/3Y/5Y Average/High/Low summary + 3Y/5Y rolling charts | 3Y/5Y rolling charts + rolling time-series table | **Partial**. PV의 Average/High/Low 압축 summary가 없음 |
| Inflation-adjusted analysis | Inflation-adjusted balances / CAGR / inflation-related display | 없음 | **Missing** |
| Fund fundamentals / style data | Morningstar 기반 category/yield/P-E/duration/sector 등 | 없음 | **Missing**, 현재 v1 scope의 style/fundamental 제외와 연결됨 |
| Notes / definitions / disclosures | Total Return, dividend reinvestment, CAGR/TWRR/MWRR, risk metric definitions, data/provider disclosures 등 폭넓게 제공 | Metadata 및 최소한의 semantic information 중심 | **Partial by product design**. PV는 consumer-facing explanatory layer가 더 두꺼움 |
| Run provenance / reproducibility | 결과 조건 일부 노출 | Run ID, Requested/Effective period, months, rebalancing, calendar alignment, return semantics 명시 | **Internal advantage**. 현재 research report가 실험 추적성에서 더 강함 |

## 5. Main Findings

### 5.1 Core backtest analytics coverage is already high

현재 report는 PV의 백테스트 분석 뼈대를 놓친 상태가 아니다.

특히 다음 주제는 높은 수준으로 존재한다.

- Performance Summary
- Portfolio Growth
- Trailing Returns
- Active Returns
- Active Return Contribution
- Rolling Active Return / Tracking Error
- Up / Down Market Performance
- Annual / Monthly Returns
- Drawdowns
- Portfolio Asset Performance
- Correlations
- Return Decomposition
- Risk Decomposition
- Rolling Returns

따라서 현재 단계의 핵심 문제를 "PV의 분석 기능 대부분이 빠졌다"고 보는 것은 부정확하다.

### 5.2 The largest topic-level gap is Exposures

PV reference의 가장 큰 독립 분석 축 중 하나는 `Exposures`다.

이 영역은 단순 allocation table이 아니라 다음과 같은 질문에 답한다.

- 무엇을 보유하고 있는가
- 어떤 asset class / sector / market-cap exposure인가
- fund category와 valuation/fundamental 특성이 무엇인가
- 각 구성 요소가 return/risk에 어떤 경제적 노출을 만든다고 볼 수 있는가

현재 report는 "성과가 어떻게 발생했는가" 분석에는 강하지만, "포트폴리오가 무엇에 노출되어 있는가"에 대한 style/fundamental layer는 없다.

다만 이 차이는 구현 누락이라고 즉시 판정하면 안 된다. 현재 Backtest v1에서 style/factor/fundamental provider 기반 분석을 제외한 기존 scope 결정과 충돌할 수 있으므로, 향후 제품 확장 여부를 별도로 결정해야 한다.

### 5.3 Metrics breadth is narrower than PV

현재 Metrics는 연구에 유용한 핵심 risk-adjusted statistics를 제공하지만 PV reference보다 폭이 좁다.

따라서 다음 단계에서는 PV metric 전체를 그대로 복제할 것이 아니라, 현재 제품 목적에서 실제 의사결정에 유용한 metric만 선별할 필요가 있다.

중요한 것은 **metric 개수 parity가 아니라 분석 가치 parity**다.

### 5.4 Inflation is a real information gap

PV reference는 inflation-adjusted end balance와 CAGR 등 명목 수익과 실질 수익을 함께 해석할 수 있는 정보를 제공한다.

현재 report에는 inflation dimension이 없다.

이 영역은 Exposures와 달리 Backtest 자체의 성과 해석과 직접 연결되므로, 향후 필요성을 별도로 검토할 가치가 있다.

### 5.5 Summary information architecture differs materially

PV Summary는 각 portfolio를 작은 투자 리포트처럼 설명한다.

대략적인 흐름은:

`return → benchmark relative → volatility → drawdown → growth → positive months → best/worst year → risk-adjusted return → upside/downside capture`

현재 report는:

`run provenance → allocation → performance matrix → growth → trailing returns`

순서다.

현재 방식은 reproducible research artifact 관점에서 장점이 크다. 특히 Run ID, requested/effective period, calendar alignment, total-return semantics 같은 정보는 PV보다 내부 연구에 중요하다.

따라서 PV Summary를 복제하기보다 **현재 reproducibility 정보를 유지하면서, portfolio-level human-readable highlight layer를 추가할지**가 올바른 논점이다.

### 5.6 Rolling Returns needs compact summary, not more raw data

현재 report는 3Y/5Y rolling time series를 충분히 제공한다.

PV와의 핵심 차이는 PV가 1Y/3Y/5Y별 Average / High / Low를 먼저 압축해 보여준다는 점이다.

따라서 향후 개선 방향은 rolling raw data를 더 추가하는 것이 아니라, 긴 chart/table을 읽기 전에 분포의 범위를 빠르게 파악할 수 있는 compact summary를 넣는 것이다.

## 6. Priority Interpretation

현재 reference comparison 기준 정보 격차 우선순위:

### Large topic gap

1. **Exposures / holdings-style exposure analysis**
   - 다만 현재 scope상 intentional exclusion 가능성이 높으므로 바로 구현 대상으로 확정하지 않는다.

### Medium information gaps

2. **Risk & Return Metrics breadth**
3. **Inflation-adjusted performance**
4. **Portfolio-level narrative / highlights**
5. **Rolling Returns Average / High / Low compact summary**

### High parity areas

- Active Returns
- Drawdowns
- Asset Performance
- Correlation
- Return Decomposition
- Risk Decomposition
- Annual / Monthly Returns
- Portfolio Growth core behavior
- Trailing Returns

## 7. Acceptance Interpretation

이 비교만으로 현재 report를 FAIL이라고 판정하지 않는다.

판정 시 다음을 구분해야 한다.

- PV reference에 존재하지만 제품 scope에서 의도적으로 제외한 주제
- 현재 specification이 요구하는데 report가 누락한 주제
- 동일 주제는 존재하지만 정보 구성만 다른 경우
- 현재 research workflow 때문에 PV보다 더 강하게 유지해야 하는 내부 정보

특히 `Exposures`, Morningstar fundamentals, style analysis 등은 PV parity만을 이유로 자동 구현하지 않는다.

반대로 run provenance, requested/effective period, calendar alignment, return semantics 같은 현재 report의 정보는 PV에 없거나 약하더라도 제거 대상이 아니다.

## 8. Recommended Next Discussion

새 LLM 창에서는 먼저 이 문서를 읽고 다음 질문부터 이어가는 것이 좋다.

> PV 대비 차이 중 어떤 항목이 현재 Backtest 제품의 실제 연구 가치를 높이는가, 그리고 어떤 항목은 external provider/style analysis 영역이므로 의도적으로 제외할 것인가?

구현 우선순위를 정하기 전에 반드시 current OpenSpec / Backtest scope와 대조한다.

## 9. Related Files

- `ai-share/llm-to-llm.md`
- `ai-share/agent-to-llm.md`
- `docs/visual-acceptance-contract.md`
- `openspec/changes/bt-module/specs/research-report/spec.md`
- `openspec/changes/bt-module/specs/agent-verification/spec.md`
- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/README.md`
- `references/portfolio-visualizer/backtest-portfolio/20260902-5NMHg7UEDbksVuZQFdAdFG/page.mhtml`
- `runs/20260903-backtest-qqq-gld-spy-presentation-validation-v2/report.html`
