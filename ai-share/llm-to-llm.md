# Session Handover

created_at: 2026-09-09
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## 1. Purpose of this handover

이 문서는 다음 ChatGPT/LLM 창이 `portfolio-optimizer-kr`에서 진행한 KAW(Kim Seong-il K-All Weather) 재구성/검증 연구를 이어받아, **사용자가 새로 설계한 포트폴리오와 KAW의 우열을 비교하는 다음 study**를 바로 시작할 수 있도록 만든 handover다.

과거 대화를 재현하려 하지 말고 GitHub remote의 최신 파일을 source of truth로 사용한다.

새 LLM은 먼저 다음을 읽는다.

```text
studies/kaw-target-reconstruction/study.md
studies/kaw-target-reconstruction/report.md
ai-share/llm-to-llm.md
```

KAW 상세 실험 결과와 해석은 `report.md`가 canonical living report다. 후속 KAW 검증은 새 병렬 보고서를 만들기보다 기존 report를 update/append하는 것이 원칙이다.

---

## 2. portfolio-optimizer-kr 개요

Repository:

```text
https://github.com/comus93/portfolio-optimizer-kr
```

이 프로젝트는 한국 투자자 관점에서 포트폴리오 연구를 재현 가능하게 수행하기 위한 Python 기반 research framework다.

큰 흐름은 다음과 같다.

```text
Market Data
  ↓
Portfolio definition / Optimization objective
  ↓
Portfolio simulation
  ↓
Portfolio analytics
  ↓
Canonical run artifacts
  ↓
HTML research report / GitHub Pages
```

주요 product mode:

```text
optimization
backtest
```

Optimization은 주어진 자산 universe와 min/max constraints 안에서 Max Sharpe 또는 target volatility 등의 objective를 계산한다.

Backtest는 사용자가 정의한 고정 target weights를 역사적으로 평가한다. Backtest 자체는 optimality를 주장하지 않는다.

공유되는 핵심 원칙:

```text
portfolio generation != portfolio evaluation
```

### Research layer

연구는 대체로 다음 구조를 사용한다.

```text
studies/<study-name>/study.md
studies/<study-name>/experiments/*.yaml
```

실행 switch:

```text
control/execute.yaml
```

`run: true`와 experiment target을 push하면 GitHub Actions의 `run-optimization.yml`이 선택된 experiment를 실행하고 canonical run artifacts와 HTML report를 생성/커밋한다.

사용자가 명시적으로 `돌리자`, `진행해`, `실행해` 등 실행을 승인했을 때만 run trigger를 넣는다.

Run output은 보통 다음과 같은 파일을 포함한다.

```text
runs/<run-id>/
  context.yaml
  input.yaml
  result.json
  report.html
  review/performance_summary.csv
  review/optimization_results.csv
  review/efficient_frontier.csv
  review/risk_decomposition.csv
  review/return_decomposition.csv
  monthly_returns.csv
  monthly_return_series.csv
  drawdowns.csv
  ...
```

GitHub Pages report 형식:

```text
https://comus93.github.io/portfolio-optimizer-kr/runs/<run-id>/report.html
```

---

## 3. Risk-free rate: 매우 중요

Framework는 YAML에서 두 가지 risk-free 방식이 이미 지원된다. Optimization과 Backtest 모두 같은 config parser를 사용한다.

### Dynamic provider mode

```yaml
risk_free:
  mode: us_3m_tbill
```

이 방식은 FDR/FRED에서 US 3M T-bill (`TB3MS`) 데이터를 조회한다.

### Fixed deterministic mode

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

`annual_rate_pct`는 percent 단위다. 즉 `3.839...`를 넣으며 `0.03839...`를 넣지 않는다.

Fixed mode에서는 경제지표 series를 조회하지 않는다. Backtest execution test에서도 fixed mode가 economic-series loader를 호출하지 않는 것이 보장되어 있다.

### KAW study-wide convention

현재 FDR/FRED `TB3MS` provider 의존 문제가 있어 **KAW 관련 연구에서는 별도 지시가 없는 한 아래 값을 고정 사용한다.**

```text
Annual RF = 3.8394827586206895%
Decimal   = 0.038394827586206895
```

Source:

```text
runs/20260908-0002/result.json
```

Reason:
- 동일 연구기간에서 이미 산출한 RF를 매 experiment마다 다시 provider에서 받을 필요가 없음
- provider 일시 실패로 연구 run이 깨지는 문제 방지
- 동일기간 실험의 determinism/reproducibility 강화

Tracking issue:

```text
GitHub Issue #1
FDR TB3MS 무위험수익률 조회 의존성 제거/캐시화
https://github.com/comus93/portfolio-optimizer-kr/issues/1
```

Generic backtest example에도 두 모드가 주석으로 노출되어 있다.

```text
configs/backtest-example.yaml
```

이 값은 KAW research convention이지 framework 전체의 영구 경제가정은 아니다.

---

## 4. Currency / FX 주의사항

KAW bridge study 도중 중요한 bug가 발견되어 수정됐다.

과거 runner는 KRW와 USD 자산이 섞인 경우에만 USD/KRW를 적용했다. 그래서 모든 자산이 USD인 KAW Core가 `fx.usdkrw_symbol: USD/KRW`를 명시해도 USD 기준으로 계산되는 문제가 있었다.

현재 수정된 동작:

```text
All USD + fx 설정 없음
→ USD 기준 유지

All USD + fx.usdkrw_symbol 명시
→ KRW 기준으로 환산

KRW + USD 혼합
→ USD/KRW 환산 필요
```

Regression tests가 추가됐고, real-data 검증에서 Core와 Direct의 SPY benchmark가 동일 기간에 사실상 동일한 성과로 일치해 수정이 확인됐다.

따라서 **FX 수정 이전의 Full Core 결과는 연구 결론에 사용하면 안 된다.**

Canonical corrected Core runs는 아래 0009/0010이다.

---

## 5. KAW 연구 목적

현재 김성일 K-All Weather를 두 개의 proxy로 재구성했다.

목적은:

1. 현재 KAW에 가까운 recent-period representation 확보
2. 훨씬 긴 역사 검증이 가능한 long-history behavior proxy 확보
3. 이후 사용자가 설계한 TO-BE portfolio와 동일한 framework에서 비교

두 proxy를 하나의 stitched NAV로 연결하지 않는다.

```text
KAW Direct Proxy
KAW Core
```

은 서로 별도 experiment다.

상세 내용은 반드시 아래를 우선 참조한다.

```text
studies/kaw-target-reconstruction/study.md
studies/kaw-target-reconstruction/report.md
```

---

## 6. Current KAW target allocation

현재 KAW target weights:

| Sleeve | Weight |
|---|---:|
| Gold | 20.0% |
| US long Treasury | 15.0% |
| KR 30Y Treasury | 15.0% |
| Nasdaq 100 | 10.0% |
| China | 8.5% |
| Korea | 8.0% |
| US dividend | 10.0% |
| India | 8.5% |
| Japan | 5.0% |
| Total | 100.0% |

Strategic cash = 0%.

---

## 7. KAW Direct Proxy

목적:
현재 KAW의 9개 sleeve를 가능한 직접적으로 보존한 recent-history proxy.

Universe / provided weights:

```text
133690 TIGER 미국나스닥100             10.0%
402970 ACE 미국배당다우존스            10.0%
069500 KODEX 200                         8.0%
168580 ACE 중국본토CSI300                8.5%
200250 KIWOOM 인도Nifty50(합성)          8.5%
101280 KODEX 일본TOPIX100                5.0%
TLT iShares 20+ Year Treasury Bond ETF   15.0%
385560 RISE KIS국고채30년Enhanced        15.0%
132030 KODEX 골드선물(H)                 20.0%
```

Common valid period:

```text
2021-11 onward
```

Bridge/optimization period used so far:

```text
2021-11-01 ~ 2026-08-31
```

Common optimization constraints:

```text
monthly rebalancing
0% <= each asset <= 60%
KRW reporting
SPY benchmark
fixed RF 3.8394827586206895%
```

### Direct Proxy key optimization results

| Objective | CAGR | Std Dev | Sharpe | MDD |
|---|---:|---:|---:|---:|
| Provided | 8.60% | 9.95% | 0.50 | -15.78% |
| Max Sharpe | 16.66% | 9.37% | 1.29 | -8.23% |
| Max Return @10.5% vol | 17.79% | 10.50% | 1.26 | -10.28% |
| Max Return @11.0% vol | 18.20% | 11.00% | 1.24 | -10.86% |
| Max Return @11.5% vol | 18.57% | 11.50% | 1.21 | -11.40% |
| Max Return @13.0% vol | 19.53% | 13.00% | 1.15 | -12.83% |

Main evidence links are maintained in `report.md`.

13% is an aggressive reference. The 10.5% to 11.5% region was used as the main fair-risk comparison region because the actual direct-investment account reported 10.52% annual volatility over its shorter observed period.

---

## 8. Real Kim Seong-il direct-account reference

User supplied the actual direct-investment account summary:

```text
Operation period      2024-01-26 ~ 2026-07-31
Total return          51.89%
Annualized return     18.11%
Annual volatility     10.52%
Maximum drawdown      -9.14%
Longest loss period   3 months
Sharpe ratio          1.72
```

이 기간은 Proxy bridge period보다 짧기 때문에 엄격한 성과 winner/loser 비교에는 사용하지 않는다.

주요 역할:

```text
risk-budget calibration
plausibility reference
```

---

## 9. KAW Core

목적:
현재 KAW의 경제적 return engine을 압축해 2006년부터 장기 behavior를 연구할 수 있도록 한 proxy.

Universe / provided weights:

```text
QQQ  10%
SPY  10%
EWY   8%
EEM  17%
EWJ   5%
TLT  30%
GLD  20%
```

Mapping concept:

```text
Nasdaq                 → QQQ
US dividend predecessor→ SPY
Korea                  → EWY
China + India          → EEM
Japan                  → EWJ
US long bond + KR 30Y  → TLT
Gold                   → GLD
```

Long-history valid period:

```text
2006-01 onward
```

All Core assets existed before 2006, so 2006-01 is the conservative study start.

### Corrected bridge-period Core results

Same 2021-11 to 2026-08 KRW period:

| Objective | CAGR | Std Dev | Sharpe | MDD |
|---|---:|---:|---:|---:|
| Provided Core | 12.11% | 12.19% | 0.69 | -16.58% |
| Max Sharpe | 21.69% | 11.10% | 1.49 | -11.12% |
| Max Return @11.5% | 22.25% | 11.50% | 1.48 | -11.92% |

Canonical corrected runs:

```text
Core Max Sharpe        runs/20260909-0009
Core Max Return 11.5   runs/20260909-0010
```

Pages:

```text
https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0009/report.html
https://comus93.github.io/portfolio-optimizer-kr/runs/20260909-0010/report.html
```

Core가 Direct의 absolute performance나 efficient frontier를 정확히 재현하지는 않는다.

---

## 10. Direct Proxy vs Core movement fidelity

이 결과가 Core를 long-history proxy로 사용할 근거의 핵심이다.

Provided-weight portfolio끼리 같은 58개월을 비교한 결과:

| Comparison | Result |
|---|---:|
| Monthly return correlation | **0.898** |
| Up/down direction match | **52 / 58 months = 89.7%** |
| Core beta vs Direct | **1.10** |
| Annualized tracking error | **5.45%** |
| Drawdown-series correlation | **0.944** |
| Maximum-drawdown trough | **Both 2022-12** |

Interpretation:

- Core와 Direct는 월별 방향성이 상당히 유사하다.
- Drawdown timing은 특히 유사하다.
- Core는 Direct보다 amplitude가 조금 큰 behavior를 보이며 beta가 약 1.10이다.
- 따라서 Core는 **절대 성과 복제품이 아니라 장기 behavior proxy**로 취급한다.
- 2006년 이후 장기 trend, regime response, structural strength/weakness 검증에는 유효할 가능성이 높다.

이 interpretation rule을 무시하고 Core 장기 CAGR을 현재 KAW의 literal historical CAGR처럼 사용하면 안 된다.

---

## 11. Sleeve decomposition result

Direct에서 Core mapping을 한 sleeve씩 교체한 one-at-a-time experiment도 수행했다.

| Single replacement | Provided Std Dev | Change vs Direct | Max Sharpe Std Dev | Max Sharpe |
|---|---:|---:|---:|---:|
| Direct baseline | 9.95% | baseline | 9.37% | 1.291 |
| Gold → GLD | 10.11% | +0.16%p | 10.80% | 1.485 |
| Bond → TLT 30% | 9.95% | ~0.00%p | 9.37% | 1.291 |
| China + India → EEM 17% | 11.01% | +1.06%p | 9.37% | 1.291 |
| US dividend → SPY | 10.45% | +0.50%p | 9.89% | 1.287 |
| Korea → EWY | 10.00% | +0.05%p | 9.37% | 1.291 |
| Japan → EWJ | 9.97% | +0.02%p | 9.35% | 1.285 |

대부분 단일 교체 영향은 작았고, China + India를 EEM으로 압축할 때 provided volatility 증가가 가장 컸다.

Full Core와 Direct의 더 큰 차이는 단일 broken sleeve라기보다 여러 mapping interaction의 합으로 보는 것이 현재 working interpretation이다.

---

## 12. Canonical KAW report and study

반드시 최신 내용은 아래 두 파일을 읽는다.

```text
studies/kaw-target-reconstruction/study.md
studies/kaw-target-reconstruction/report.md
```

`report.md`에는:

```text
proxy definitions
experiment conditions
actual-account reference
Direct optimization results
Core corrected results
movement fidelity
sleeve decomposition
FX bug correction
TB3MS issue
HTML evidence links
interim conclusion
next experiments
```

가 정리돼 있다.

후속 KAW 연구 결과는 이 report에 append/update한다.

---

## 13. Next study: user's portfolio vs KAW

다음 창의 주 연구 주제는 **사용자가 설계한 포트폴리오와 KAW의 우열 비교**다.

새 LLM은 사용자가 새 포트 구성/비중/후보를 주면 먼저 비교 질문을 명확한 실험 구조로 번역해야 한다.

우선 비교 benchmark는 목적에 따라 다음 두 KAW 표현을 구분한다.

```text
Recent-period fidelity comparison
→ KAW Direct Proxy

Long-horizon structural / regime comparison
→ KAW Core
```

둘을 섞어서 하나의 KAW history로 stitch하지 않는다.

사용자 포트가 2021-11 이후 데이터가 모두 있으면 먼저 Direct Proxy와 같은 common period에서 공정 비교할 수 있다.

더 긴 역사 검증이 가능하면 Core와 2006-01 이후 long-horizon comparison을 추가한다.

### Recommended comparison layers

단순 CAGR 승패 하나로 판단하지 않는다. 최소 다음을 본다.

```text
CAGR / annualized return
Std Dev
Sharpe / Sortino
MDD
rolling returns
start/end sensitivity
correlation / behavior differences
risk and return decomposition
regime strength / weakness when useful
```

Optimization comparison에서는 동일 자산 constraints와 동일 RF/FX/period를 맞춘다.

Backtest comparison에서는 동일 기간, 동일 rebalancing convention, 동일 reporting currency를 사용한다.

사용자의 연구 철학상 핵심 질문은 단순히 가장 높은 CAGR이 아니라:

```text
새 포트가 KAW 대비 독립적인 경제적 수익 엔진을 제공하는가?
위험예산 대비 효율이 실제로 개선되는가?
특정 최근 regime에만 유리한 hindsight allocation은 아닌가?
장기적으로 strength/weakness profile이 어떻게 달라지는가?
```

이다.

---

## 14. Important cautions for next LLM

1. **KAW Core old FX-bug runs를 사용하지 않는다.** Corrected runs 0009/0010과 current report만 사용한다.
2. KAW 관련 후속 실험은 특별한 이유가 없으면 `risk_free.mode: fixed`, `annual_rate_pct: 3.8394827586206895`를 사용한다.
3. `annual_rate_pct`는 percent 단위다.
4. Core는 absolute-performance replica가 아니라 behavior proxy다.
5. Direct와 Core를 하나의 stitched NAV로 연결하지 않는다.
6. 실제 김성일 계좌의 18.11% annual return / 10.52% vol은 기간이 짧으므로 장기 proxy와 직접 winner/loser 판정하지 않는다.
7. 사용자가 실행을 승인하기 전에는 `control/execute.yaml`의 `run: true`를 넣지 않는다.
8. 새 결과가 KAW 연구에 직접 관련되면 `studies/kaw-target-reconstruction/report.md`를 갱신한다.
9. 사용자가 만든 포트 자체가 별도 장기 연구 주제가 되면 별도 study를 만들되, KAW comparison evidence는 canonical KAW report를 참조한다.

---

## 15. Current stopping point

KAW Direct Proxy와 Core 사이의 bridge validation은 완료됐다.

현재 working conclusion:

```text
Direct Proxy
= 현재 KAW의 recent-period 비교 기준

Core
= 2006년 이후 long-history behavior proxy
```

Core의 absolute optimized performance는 Direct와 다르지만 movement fidelity는 충분히 높다.

다음 창에서는 사용자가 설계한 portfolio를 입력받아 **동일 조건에서 KAW와 비교하는 실험 계획을 수립하고 실행**하는 단계부터 이어가면 된다.
