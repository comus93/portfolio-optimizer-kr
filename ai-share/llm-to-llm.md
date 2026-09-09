# Session Handover

created_at: 2026-09-09
project: `comus93/portfolio-optimizer-kr`
branch: `main`

## 1. Current objective

KAW(Kim Seong-il K-All Weather) 재구성 연구를 기반으로 다음 단계에서 사용자가 설계한 TO-BE portfolio와 KAW의 우열을 동일 framework에서 비교할 예정이다.

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

## 3. Risk-free convention — IMPORTANT

Framework는 YAML에서 두 RF 모드를 지원한다.

Dynamic provider:

```yaml
risk_free:
  mode: us_3m_tbill
```

Deterministic fixed:

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

Pinned value provenance:

```text
source run: runs/20260908-0002/result.json
source requested_mode: us_3m_tbill
effective annual RF: 0.038394827586206895
percent: 3.8394827586206895%
source period: 2021-11-01 ~ 2026-08-31
```

목적:

- 반복 Optimization/Backtest research run에서 FDR/FRED `TB3MS` 재조회 제거
- provider 상태와 무관한 deterministic run
- 같은 비교 실험군의 RF consistency

사용자가 custom RF 또는 explicit `us_3m_tbill`을 지정하면 그 입력을 우선한다.

Tracking:

```text
GitHub Issue #1: FDR TB3MS 무위험수익률 조회 의존성 제거/캐시화
```

## 4. KAW benchmark definitions

### 4.1 KAW Direct Proxy v2 — CURRENT CANONICAL

현재 KAW 9개 sleeve를 가능한 직접적으로 보존하는 recent-period benchmark.

```text
usable period: 2021-11 onward
standard recent/bridge period: 2021-11-01 ~ 2026-08-31
```

Weights:

```text
133690  TIGER 미국나스닥100             10.0%
402970  ACE 미국배당다우존스            10.0%
069500  KODEX 200                        8.0%
168580  ACE 중국본토CSI300               8.5%
200250  KIWOOM 인도Nifty50(합성)         8.5%
101280  KODEX 일본TOPIX100               5.0%
267440  RISE 미국장기국채선물(H)         15.0%
385560  RISE KIS국고채30년Enhanced       15.0%
132030  KODEX 골드선물(H)                20.0%
```

2026-09-09 사용자 결정으로 미국 장기채 sleeve를 기존 `TLT 15%`에서 **`267440 RISE 미국장기국채선물(H) 15%`**로 변경했다.

267440은 2017년 상장이라 Direct Proxy의 2021-11 시작기간에는 제약이 없다.

### 4.2 Direct Proxy v1 — HISTORICAL ONLY

기존 Direct 실험은 미국 장기채 sleeve에 `TLT 15%`를 사용했다.

이전 run과 HTML evidence는 삭제하지 않고 **Direct Proxy v1 historical evidence**로 보존한다.

중요:

```text
기존 TLT 기반 Direct 결과를 현재 canonical Direct v2 결과라고 부르면 안 된다.
```

TO-BE와의 recent-period 비교 전에 267440 기반 Direct v2 핵심 실험을 다시 실행해야 한다.

### 4.3 KAW Core

장기 behavior proxy:

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

Core의 TLT는 유지한다. Core는 current KAW의 literal historical return replica가 아니라 장기 trend/regime/strength/weakness를 연구하는 behavior proxy다.

Direct와 Core를 하나의 stitched NAV로 연결하지 않는다.

## 5. Existing bridge evidence and version warning

기존 movement bridge는 **TLT 기반 Direct Proxy v1 vs Core**에서 계산했다.

```text
monthly return correlation   0.898
direction agreement          52/58 = 89.7%
Core beta vs Direct          1.10
annualized tracking error    5.45%
drawdown correlation         0.944
MDD trough                   both 2022-12
```

이 수치는 방법론적으로 중요한 historical evidence지만, Direct가 v2로 바뀌었으므로 현재 canonical movement-fidelity 수치로 재사용하면 안 된다.

다음에 반드시 다시 계산:

```text
Direct Proxy v2 (267440) vs KAW Core
same 2021-11-01 ~ 2026-08-31 period
```

## 6. Existing Direct Proxy v1 optimization evidence

TLT 기반 v1 결과:

```text
Provided                CAGR 8.60%   Std 9.95%   Sharpe 0.50   MDD -15.78%
Max Sharpe              CAGR 16.66%  Std 9.37%   Sharpe 1.29   MDD -8.23%
Max Return @10.5% vol   CAGR 17.79%
Max Return @11.0% vol   CAGR 18.20%
Max Return @11.5% vol   CAGR 18.57%
Max Return @13.0% vol   CAGR 19.53%
```

Evidence:

```text
runs/20260908-0002  Direct v1 Max Sharpe
runs/20260908-0004  Direct v1 Max Return @10.5
runs/20260908-0005  Direct v1 Max Return @11.0
runs/20260909-0002  Direct v1 Max Return @11.5
runs/20260908-0003  Direct v1 Max Return @13.0
```

이 숫자들은 267440 기반 v2에서 재검증 전까지 current Direct 결과로 사용하지 않는다.

## 7. Corrected KAW Core evidence

과거 all-USD Core runner는 FX config가 있어도 USD/KRW를 적용하지 않는 bug가 있었다. 수정 전 Full Core 결과는 연구 결론에 사용하지 않는다.

Corrected canonical Core runs:

```text
runs/20260909-0009  Core Max Sharpe
runs/20260909-0010  Core Max Return @ 11.5% vol
```

Corrected Core bridge-period results:

```text
Provided            CAGR 12.11%  Std 12.19%  Sharpe 0.69  MDD -16.58%
Max Sharpe          CAGR 21.69%  Std 11.10%  Sharpe 1.49  MDD -11.12%
Max Return @11.5    CAGR 22.25%  Std 11.50%  Sharpe 1.48  MDD -11.92%
```

## 8. Real Kim Seong-il direct-account reference

User supplied actual-account reference:

```text
period             2024-01-26 ~ 2026-07-31
annualized return  18.11%
annual volatility  10.52%
MDD                -9.14%
Sharpe              1.72
```

기간이 다르므로 proxy와 strict winner/loser 비교에 직접 쓰지 않는다. Risk-budget / plausibility reference다.

## 9. Immediate prerequisite before TO-BE comparison

사용자가 다음 창에서 TO-BE portfolio를 비교하려고 한다.

그 전에 current canonical recent benchmark를 만들기 위해 다음을 우선 수행한다.

```text
1. Direct Proxy v2 provided-weight run
2. Direct Proxy v2 Max Sharpe
3. Direct Proxy v2 main target-volatility comparison, primarily 10.5%~11.5%
4. Direct Proxy v2 vs Core movement fidelity
   - monthly correlation
   - direction agreement
   - beta
   - annualized tracking error
   - drawdown correlation
   - MDD trough timing
5. studies/kaw-target-reconstruction/report.md 업데이트
```

기존 run artifact는 수정/삭제하지 않는다. 새 v2 experiment/run으로 만든다.

## 10. Next research phase: TO-BE vs KAW

사용자가 TO-BE portfolio를 정의하면 두 층으로 비교한다.

```text
A. Recent
TO-BE Direct-compatible vs KAW Direct Proxy v2
2021-11 ~ 2026-08

B. Long history
TO-BE Core-compatible vs KAW Core
2006-01 ~ 2026-08
```

기존 capability로 우선 수행:

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

필요가 실제로 확인될 때만 확장:

```text
Batch experiment execution
Cross-run comparison aggregation
Start-End sensitivity matrix
Regime performance capability
Study-level cross-run report
```

프레임워크 확장은 반복되는 연구 요구가 확인된 후 shared capability 경계를 유지하며 추가한다.
