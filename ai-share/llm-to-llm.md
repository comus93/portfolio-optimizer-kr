# Session Handover

created_at: 2026-09-09
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## 1. Current objective

KAW(Kim Seong-il K-All Weather) 재구성/bridge validation은 완료 수준이다. 다음 연구 단계는 사용자가 새로 설계하는 TO-BE portfolio를 KAW와 동일 framework에서 비교하는 것이다.

Canonical KAW sources:

```text
studies/kaw-target-reconstruction/study.md
studies/kaw-target-reconstruction/report.md
```

KAW 상세 결과는 `report.md`가 canonical living report다.

## 2. Project architecture / source of truth

개발 또는 capability 확장 전 다음 순서를 따른다.

```text
AGENTS.md
openspec/config.yaml
openspec/changes/<active-change>/
openspec/specs/
관련 docs/
```

Core product:

```text
Optimization
Backtest
```

Shared capability:

```text
market-data
portfolio-simulation
portfolio-analytics
run-artifacts
research-report
```

핵심 원칙:

```text
portfolio generation != portfolio evaluation
```

Optimization과 Backtest 모두 target weights 이후 shared simulation / analytics / persistence를 사용한다.

## 3. Global Research Frontend default risk-free convention — IMPORTANT

2026-09-09 사용자 결정으로 KAW 한정 우회가 아니라 **Optimization과 Backtest canonical research run의 기본 RF convention**으로 승격한다.

사용자가 RF를 별도로 언급하지 않으면 `research.py::_apply_research_defaults()`가 다음 effective input을 materialize하고 completed run의 `input.yaml`에 그대로 보존한다.

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

Provenance:

```text
source run: runs/20260908-0002/result.json
source requested_mode: us_3m_tbill
effective annual RF: 0.038394827586206895
percent: 3.8394827586206895%
source period: 2021-11-01 ~ 2026-08-31
```

이 값은 임의의 별도 fixed-rate 경제가정이 아니다. 기존 `us_3m_tbill` 경로로 실제 resolve한 effective rate를 **pinned U.S. 3-Month T-Bill value**로 재사용하는 것이다. Executable input에는 이미 resolve된 숫자를 provider 재조회 없이 보존하기 위해 `fixed` representation을 사용한다.

목적:

- 반복 Optimization/Backtest research run에서 FDR/FRED `TB3MS` 재조회 제거
- provider 상태와 무관한 deterministic research run
- 동일 연구 간 RF consistency

Important semantics:

- 사용자가 custom fixed RF를 명시하면 그 입력이 우선한다.
- 사용자가 explicit `risk_free.mode: us_3m_tbill`을 명시하면 기존 dynamic provider behavior를 그대로 사용한다.
- raw YAML parser / runner의 explicit RF mode semantics는 변경하지 않는다.
- pinned 값이 source period의 dynamic result와 동일하다는 뜻이며, 다른 analysis period의 period-specific TB3MS 평균과 항상 동일하다고 주장하지 않는다.

Implementation/change tracking:

```text
openspec/changes/2026-09-09-pin-default-us3m-rate/
GitHub Issue #1: FDR TB3MS 무위험수익률 조회 의존성 제거/캐시화
```

## 4. KAW benchmark definitions

### KAW Direct Proxy

현재 KAW 9개 sleeve를 가능한 직접적으로 보존하는 recent-period benchmark.

```text
usable period: 2021-11 onward
bridge period: 2021-11-01 ~ 2026-08-31
```

Weights:

```text
133690  TIGER 미국나스닥100             10.0%
402970  ACE 미국배당다우존스            10.0%
069500  KODEX 200                        8.0%
168580  ACE 중국본토CSI300               8.5%
200250  KIWOOM 인도Nifty50(합성)         8.5%
101280  KODEX 일본TOPIX100               5.0%
TLT     iShares 20+ Year Treasury       15.0%
385560  RISE KIS국고채30년Enhanced       15.0%
132030  KODEX 골드선물(H)                20.0%
```

### KAW Core

장기 behavior proxy.

```text
QQQ 10
SPY 10
EWY 8
EEM 17
EWJ 5
TLT 30
GLD 20
```

```text
long-history period: 2006-01 onward
```

Core는 current KAW의 literal historical return replica가 아니다.

## 5. Direct vs Core bridge result

Provided-weight portfolios, same 58 months:

```text
monthly return correlation   0.898
direction agreement          52/58 = 89.7%
Core beta vs Direct          1.10
annualized tracking error    5.45%
drawdown correlation         0.944
MDD trough                   both 2022-12
```

따라서:

```text
Direct = recent faithful benchmark
Core   = long-history behavior proxy
```

두 proxy를 하나의 stitched NAV로 연결하지 않는다.

## 6. Critical correction

과거 all-USD Core runner는 FX config가 있어도 USD/KRW를 적용하지 않는 bug가 있었다. 수정 전 Full Core 결과는 연구 결론에 사용하지 않는다.

Corrected canonical Core runs:

```text
runs/20260909-0009  Core Max Sharpe
runs/20260909-0010  Core Max Return @ 11.5% vol
```

## 7. Next research phase

사용자가 TO-BE portfolio를 정의하면 우선 기존 framework로 비교한다.

Recommended layers:

```text
A. Recent
TO-BE Direct-compatible vs KAW Direct Proxy
2021-11 ~ 2026-08

B. Long history
TO-BE Core-compatible vs KAW Core
2006-01 ~ 2026-08
```

기존 capability로 먼저 수행:

```text
Provided-weight Backtest
Return / Volatility / Sharpe / Sortino
Drawdown / Recovery
Rolling 3Y / 5Y
Correlation
Return / Risk decomposition
Benchmark-relative analytics
Optimization Max Sharpe
Target-volatility comparison
```

필요가 실제로 확인될 때 확장 후보:

```text
Batch experiment execution
Cross-run comparison aggregation
Start-End sensitivity matrix
Regime performance capability
Study-level cross-run report
```

프레임워크 확장은 반복되는 연구 요구가 확인된 후 shared capability 경계를 유지하며 추가한다.
