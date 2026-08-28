# 포트폴리오 최적화 결과 LLM 분석 프레임워크

## 목적

이 문서는 Portfolio Visualizer 또는 이에 준하는 포트폴리오 최적화 결과를 LLM이 일관되게 해석하기 위한 참조 문서다.

핵심 목적은 과거 최적 비중을 복사하는 것이 아니라 다음을 판단하는 것이다.

> **현재 포트폴리오가 얼마나 비효율적인가, 각 자산이 어떤 한계 효용을 추가하는가, 그 효용이 어느 위험 수준에서 나타나는가, 그리고 그 역할이 견고한가?**

개별 자산 성과보다 포트폴리오 수준의 효용을 우선한다. 모든 metric을 나열하지 말고 현재 Study의 질문에 직접 답하는 evidence에 집중한다.

---

## 0. Study 질문을 먼저 정의한다

분석 시작 시 현재 run이 무엇을 판정하려는지 한 문장으로 정의한다.

예:

- 후보 자산을 추가할 가치가 있는가?
- 현재 포트폴리오가 frontier 대비 얼마나 비효율적인가?
- Maximum Sharpe보다 높은 수익을 얻으면서 효율을 크게 잃지 않는 구간이 있는가?
- 두 자산이 독립 역할인지 대체 관계인지?
- 특정 자산의 비중 상한이 결과를 제한하는가?

근거는 `Primary evidence / Supporting evidence / Missing evidence`로 구분한다.

---

## 1. Data Validity Gate

해석 전에 결과가 비교 가능한지 확인한다.

필수 확인:

- 공통 분석 기간과 observation 수
- 미완성 현재 월/일 데이터가 월간 표본에 포함되었는지
- benchmark가 portfolio와 동일한 기간으로 잘렸는지
- asset universe, objective, risk-free rate, rebalancing
- min/max weight constraint
- 짧은 history가 전체 기간을 축소했는지
- 단위와 결측치가 일관적인지

문제가 발견되면 다음처럼 분류한다.

- **Blocking**: optimizer 입력 자체를 오염시켜 allocation/frontier가 바뀔 수 있음. 핵심 판정을 보류한다.
- **Reporting**: optimizer 결과는 유효하지만 benchmark, drawdown 등 일부 비교 지표만 오염됨. 영향받는 결론만 제외한다.

오류를 발견했다고 분석 전체를 중단하지 않는다. **어떤 결론까지 유효하고 무엇을 재검증해야 하는지 범위를 명시한다.**

### Constraint rule

최적 비중이 min/max와 정확히 같으면 그 비중은 unconstrained optimum이 아니다.

예: GLD max 30%, optimized 30%라면 `적정 비중=30%`가 아니라 **optimizer 수요가 상한에 막혔다**고 해석한다.

---

## 2. 현재 포트폴리오의 Efficiency Gap을 먼저 본다

Provided Portfolio가 있으면 자산별 설명 전에 현재 포트가 frontier에서 얼마나 비효율적인지 먼저 보여준다.

가능하면 두 가지를 계산한다.

1. **같은 Expected Return에서 frontier가 Volatility를 얼마나 낮추는가**
2. **같은 Volatility에서 frontier가 Expected Return을 얼마나 높이는가**

예:

> 현재 포트의 Expected Return 18.4%를 유지하면 frontier에서는 Volatility를 16.4%에서 14.1%로 낮출 수 있다. 반대로 현재와 같은 16.4% Volatility를 허용하면 Expected Return을 약 20.2%까지 높일 수 있다.

이 비교가 optimizer의 실질적 개선 여지를 가장 직관적으로 보여준다.

그 다음 Maximum Sharpe 등 objective portfolio를 기준점으로 확인한다.

---

## 3. Efficient Frontier를 중심으로 해석한다

Efficient Frontier는 자산의 역할, 대체 관계, 안정 구간을 읽는 핵심 표면이다. Raw point를 그대로 설명하지 말고 **위험 예산과 trade-off의 언어로 번역한다.**

### 3.1 먼저 frontier의 좌표계를 만든다

최소한 다음 기준점을 잡는다.

- Minimum Volatility와 그 Expected Return
- Maximum Sharpe의 Volatility / Expected Return / Sharpe
- Maximum Return 쪽의 Volatility / Expected Return
- near-Max-Sharpe plateau
- 주요 allocation transition과 binding constraint

특정 지점의 상대적인 위험 위치가 필요하면 다음처럼 계산한다.

```text
Risk Position (%) =
(해당 Volatility - Frontier 최소 Volatility)
/ (Frontier 최대 Volatility - Frontier 최소 Volatility) × 100
```

이 값은 raw point 번호가 아니라 **전체 frontier 위험 범위 중 어느 정도 위험 예산을 쓰는 지점인지** 설명하기 위한 좌표다.

예: `Risk Position 4%`라면 단순히 “왼쪽”이라고 하지 않고 **전체 위험범위 중 가장 보수적인 약 4% 영역**이라고 설명한다.

### 3.2 자산 trajectory는 위험 수준과 대가를 함께 설명한다

자산별로 다음을 추적한다.

- 어느 Volatility 수준에서 등장/퇴출하는가
- 전체 Risk Position 중 어느 범위에서 살아 있는가
- 그 구간의 Expected Return은 얼마인가
- Maximum Sharpe 대비 위험을 얼마나 줄이거나 늘리는 대신 수익을 얼마나 포기하거나 얻는가
- 비중이 증가할 때 어떤 자산이 감소하는가
- min/max constraint에 붙는가

**`point 15에서 퇴출`, `point 55에서 16.7%` 같은 raw point 중심 설명은 피한다.** Point 번호는 필요하면 괄호 안 audit reference로만 사용한다.

좋은 설명의 형태:

> **AIA(아시아 대형주)는 전체 frontier 변동성 범위 중 가장 보수적인 약 4% 이내에서만 존재한다.** Volatility를 약 12.8% 이하로 강하게 제한할 때 최대 약 9%까지 들어가지만, Maximum Sharpe 수준의 약 13.0% Volatility를 허용하면 필요가 없어진다. 즉 약 0.2~0.4%p의 Volatility를 더 줄이기 위해 Expected Return 일부를 포기할 때만 선택되는 저위험 전용 보조 자산이다.

이렇게 `어디서 존재 → 어떤 trade-off → 무슨 역할` 순서로 설명한다.

### 3.3 숫자는 transition만 보고한다

모든 중간 비중을 나열하지 않는다. 다음 사건만 우선한다.

- 최초 등장
- 의미 있는 비중 도달
- 상한/하한 도달
- 감소 시작
- 퇴출
- 역할을 바꾸는 대체 관계

예를 들어 GLD가 30% → 30% → 30% → 16.7% → 6.1% → 0.3% → 0%라면 모든 숫자를 읊지 않는다.

> 저위험부터 Maximum Sharpe까지 상한 30%를 유지하고, 이후 Expected Return을 높일수록 점진적으로 감소하며, frontier의 상당히 높은 위험 구간까지 살아 있다.

필요한 경우에만 대표 Volatility/Expected Return 좌표 2~3개를 붙인다.

### 3.4 Plateau와 안정 구간을 Exact Optimum보다 우선한다

Maximum Sharpe 한 점보다 인접한 portfolio에서 Sharpe와 구성의 질이 비슷하게 유지되는 구간을 찾는다.

가능하면 near-optimal band에서 다음을 제시한다.

- Expected Return 범위
- Volatility 범위
- 주요 자산 비중 범위
- Sharpe 하락폭

작은 risk-return 차이에 allocation이 크게 뒤집히면 exact weight의 신뢰도를 낮추고 **안정적인 비중 범위 또는 역할 수준의 결론**을 우선한다.

### 3.5 대체 관계와 집중도를 본다

후보 비중이 증가할 때 무엇이 줄어드는지 추적한다.

- QQQ를 밀어낸다 → 성장/고베타 역할 대체 가능성
- GLD를 밀어낸다 → 같은 방어/귀금속 축에서 risk gear를 높이는 가능성
- 기존 핵심 자산을 거의 밀어내지 않는다 → 새로운 독립 역할 가능성

또한 high-return 쪽으로 갈수록 자산 수가 줄고 한두 자산에 집중되는지 확인한다. 높은 Expected Return이 단순 concentration의 결과인지 구분한다.

---

## 4. Supporting Evidence로 optimizer의 이유를 설명한다

Frontier에서 역할을 파악한 뒤 다음 자료로 설명하거나 반증한다.

### Correlation + Return + Volatility

낮은 correlation 자체를 좋은 자산의 증거로 사용하지 않는다. 낮은 상관을 얻기 위해 얼마의 낮은 수익 또는 높은 변동성을 감수하는지 함께 본다.

### Standalone metrics

Expected Return, CAGR, Volatility, Sharpe, Sortino, MDD는 optimizer 행동을 설명하는 보조 근거다. Portfolio marginal utility보다 우선하지 않는다.

### Regime / Annual Return

특정 자산의 효용이 어떤 시장 환경에서 발생했는지 확인한다. 통계적 역할에 경제적 설명이 실제로 뒷받침될 때만 `defensive`, `inflation hedge` 같은 경제적 라벨을 붙인다.

### Drawdown / Recovery

MDD 깊이와 Recovery/Underwater 기간을 함께 본다.

### Rolling Return

특히 Rolling 3Y/5Y Low로 full-period 결과가 특정 시기에 의존하는지 확인한다.

### Return / Risk Contribution

Allocation weight 대비 Return Contribution과 Risk Contribution을 비교해 숨은 비용을 본다.

---

## 5. 한계 효용과 Robustness를 확인한다

가능하면 기준 portfolio와 후보 허용 portfolio 사이에서 다음 변화를 본다.

- Δ Expected Return / CAGR
- Δ Volatility / Sharpe / Sortino
- Δ MDD / Recovery
- 동일 Return에서 Δ Volatility
- 동일 Volatility에서 Δ Expected Return
- Risk / Return Contribution 구조 변화

후보의 진짜 marginal utility를 강하게 확인해야 할 때는 **후보 포함 vs 제외 ablation**을 사용한다.

하나의 run에서 exact weight를 확정하지 않는다. 기간, objective, constraint가 다른 실험에서도 역할이 유지되는지 확인한다.

> 역할은 반복되지만 비중만 흔들리면 `robust role / uncertain exact weight`로 본다.

---

## 6. Role, Decision, Confidence를 분리한다

한 run의 결과를 곧바로 투자 결론으로 바꾸지 않는다.

각 주요 자산은 세 축으로 요약한다.

| 구분 | 예시 |
|---|---|
| **Role** | Core Engine, Return Enhancer, Diversifier, Low-risk-only Contributor, Redundant |
| **Decision** | Keep candidate, Watch, Re-test, Exclude candidate |
| **Confidence** | High / Medium / Low |

예:

`GDX | Role: Return Enhancer | Decision: Re-test | Confidence: Low`

Frontier상 역할은 선명해도 데이터 문제나 기간 의존성이 크면 Decision과 Confidence는 보수적으로 둔다.

`REDUNDANT`는 단순 0%가 아니라 **어떤 기존 자산이 같은 역할을 더 효율적으로 대체하는지 확인됐을 때** 사용한다.

---

## 7. 다음 실험은 정보가치가 높은 것부터 제안한다

많은 sensitivity run을 나열하지 않는다. 현재 결론을 가장 크게 바꿀 수 있는 불확실성부터 1~3개 제안한다.

우선순위 예:

1. Blocking data issue 수정 후 동일 run 재실행
2. Binding constraint 완화
3. 후보 포함/제외 ablation
4. 동일 risk budget 또는 target return에서 재검증
5. 기간/objective 변경 robustness

---

## 사용자에게 결과를 전달하는 순서

1. **Data validity와 결론 사용 가능 범위**
2. **핵심 결론 + 현재 Portfolio의 Frontier Efficiency Gap**
3. **Frontier 지도**: 전체 Volatility/Return 범위, Max Sharpe 위치, 의미 있는 plateau
4. **주요 자산 3~5개의 역할**: `자산명(Ticker) + 위험구간 + trade-off + 대체 관계`
5. **Correlation / Drawdown / Rolling 등 필요한 보조 근거만**
6. **Role / Decision / Confidence 요약**
7. **가장 정보가치 높은 다음 실험**

### 가독성 규칙

- 첫 등장 시 `Ticker + 짧은 사람이 읽을 수 있는 자산명/성격`을 함께 쓴다. 예: `GLD(금 현물)`, `SPMO(S&P500 모멘텀)`.
- `point 29`, `point 55`처럼 raw frontier 번호를 주 설명 좌표로 사용하지 않는다.
- `왼쪽`, `초반`, `고수익 쪽`만으로 끝내지 않는다. **Volatility, 전체 Risk Position, Expected Return trade-off를 함께 설명한다.**
- 숫자는 구조를 이해하는 데 필요한 대표값만 쓴다. 숫자 열거 자체를 분석으로 간주하지 않는다.
- 자산별 설명은 **어느 위험 구간에서 존재 → 무엇을 얻고 무엇을 포기 → 그래서 어떤 역할** 순서로 쓴다.

---

## 핵심 원칙

> **Optimization은 최적 비중 한 점을 찾는 도구가 아니라, 위험 예산을 바꿀 때 포트폴리오 구조가 어떻게 변하는지 이해하는 도구다. Raw frontier를 사용자에게 그대로 보여주지 말고, 절대 변동성·전체 위험범위 내 위치·Expected Return의 대가로 번역하여 각 자산의 한계 효용과 역할을 설명한다.**
