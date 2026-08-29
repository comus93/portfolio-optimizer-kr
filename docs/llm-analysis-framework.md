# 포트폴리오 최적화 결과 LLM 분석 프레임워크

## 목적

이 문서는 Portfolio Visualizer 또는 이에 준하는 포트폴리오 최적화 결과를 LLM이 일관되게 해석하기 위한 참조 문서다.

핵심 목적은 과거 최적 비중을 복사하는 것이 아니라 다음을 판단하는 것이다.

> **현재 포트폴리오가 얼마나 비효율적인가, 각 자산이 어떤 한계 효용을 추가하는가, 그 효용이 어느 위험 수준에서 나타나는가, 그리고 그 역할과 비중에 대한 판단이 얼마나 견고한가?**

개별 자산 성과보다 포트폴리오 수준의 효용을 우선한다. 모든 metric을 나열하지 말고 현재 Study의 질문에 직접 답하는 evidence에 집중한다.

LLM은 분석 과정에서 다음 세 층위를 섞지 않는다.

- **Observation**: artifact에서 직접 확인되는 사실
- **Interpretation**: 그 사실이 포트폴리오 구조에서 의미하는 역할
- **Decision**: 다음 연구 또는 후보 유지/재검증에 대한 잠정 판단

한 run의 Observation이 곧바로 미래 성과나 투자 권고를 의미하지 않는다.

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

### 0.1 Run Identity / Evidence Provenance Gate

숫자를 읽기 전에 **지금 해석하는 run이 정확히 무엇인지** 고정한다.

최소한 다음을 canonical artifact에서 확인한다.

- run_id
- asset universe
- provided portfolio
- benchmark 유무와 symbol
- objective
- risk-free convention
- rebalancing
- min/max weight constraints
- 실제 analysis period

Repository 기반 시스템에서는 `LLM-README.md`의 source priority를 따른다.

```text
1. result.json
2. review/*.csv
3. 필요한 경우 raw/*.csv
```

`report.html`은 user-facing presentation surface다. HTML에 보이는 값을 canonical 계산 결과로 다시 만들지 않는다.

**사용자가 붙여준 과거 분석문, 이전 대화의 숫자, 다른 run의 결과를 현재 run과 자동으로 섞지 않는다.**

다음 중 하나라도 충돌하면 먼저 mismatch를 명시한다.

- 요청된 run_id와 artifact의 run_id가 다름
- 분석문이 benchmark 없음이라고 말하지만 input에는 benchmark가 있음
- constraint/objective가 서로 다름
- 분석 기간이 다름

충돌 시 현재 요청에서 지정된 canonical run을 우선하고, 다른 run은 별도 비교 대상으로만 취급한다.

핵심 숫자는 나중에 다시 추적할 수 있어야 한다. 중요한 결론이 다른 run의 숫자에 의존하지 않도록 한다.

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

### 1.1 In-sample / Ex-post discipline

같은 역사 표본으로 expected return, covariance를 추정하고 최적화한 뒤 같은 표본에서 CAGR, MDD 등을 비교하면 결과에는 **in-sample optimization bias**가 포함된다.

따라서 다음 표현을 기본으로 한다.

- `이 표본에서는 frontier가 더 효율적이었다`
- `동일 역사 구간의 ex-post 경로에서는 MDD가 더 얕았다`
- `현재 추정치 기준 optimizer가 이 자산을 더 요구했다`

다음처럼 미래 성과가 확정된 것처럼 쓰지 않는다.

- `수익률을 3.7%p 높일 수 있다`
- `MDD를 줄여준다`
- `적정 비중은 31.4%다`

`Expected Return`과 `CAGR`도 같은 개념으로 섞지 않는다. Expected Return은 optimizer 입력/추정의 중심이고, CAGR은 실제 역사 경로의 복리 결과다. 둘의 방향이 같아도 각각 별도의 evidence다.

### 1.2 Constraint rule

최적 비중이 min/max와 같거나 solver tolerance 내에서 경계에 붙으면 그 비중은 unconstrained optimum이 아니다.

예: GLD max 30%, optimized 30%라면 `적정 비중=30%`가 아니라 **optimizer 수요가 상한에 막혔다**고 해석한다.

또한 `Maximum Return`, `Minimum Volatility`, `Maximum Sharpe`는 모두 **현재 constraints 아래에서의 결과**다. Constraint가 바뀌면 frontier 자체가 바뀔 수 있다.

---

## 2. 먼저 Executive Thesis와 Efficiency Gap을 만든다

Data Validity에 Blocking 문제가 없다면 사용자가 긴 숫자 목록을 읽기 전에 2~4문장으로 핵심 구조를 먼저 제시한다.

Executive Thesis는 가능하면 다음 세 질문에 답한다.

1. 현재 portfolio는 frontier에서 얼마나 비효율적인가?
2. 어떤 자산/역할이 frontier의 핵심 구조를 만드는가?
3. 가장 큰 불확실성 또는 binding constraint는 무엇인가?

예:

> 이 표본에서 현재 포트폴리오는 같은 위험 수준의 frontier보다 기대수익이 낮아 개선 여지가 크다. Max-Sharpe 주변은 미국 주식과 금 중심의 구조가 안정적으로 유지되지만 성장자산 하나가 상한에 붙어 정확한 최적 비중은 식별되지 않는다. 따라서 이번 run의 강한 결론은 특정 비중 한 점보다 `주식 return engine + 금 diversifier` 구조이고, 다음 검증의 1순위는 상한 sensitivity다.

### 2.1 Provided Portfolio의 Efficiency Gap

Provided Portfolio가 있으면 자산별 설명 전에 현재 포트가 frontier에서 얼마나 비효율적인지 보여준다.

가능하면 두 가지를 계산한다.

1. **같은 Expected Return에서 frontier가 Volatility를 얼마나 낮추는가**
2. **같은 Volatility에서 frontier가 Expected Return을 얼마나 높이는가**

예:

> 현재 포트의 Expected Return 18.4%와 같은 수준에서 frontier Volatility는 16.4%가 아니라 약 14.1%다. 반대로 현재와 같은 16.4% Volatility에서 frontier Expected Return은 약 20.2%다.

이 비교는 optimizer의 실질적 개선 여지를 가장 직관적으로 보여준다.

단, interpolation은 frontier가 해당 Expected Return 또는 Volatility를 **실제로 bracket하는 범위 안에서만** 사용한다. 범위 밖이면 extrapolation하지 말고 `직접 비교 불가`라고 쓴다.

그리고 이것을 미래의 달성 가능한 개선폭으로 표현하지 않는다. **현재 역사 표본과 추정치에서의 efficiency gap**이다.

---

## 3. Efficient Frontier를 중심으로 해석한다

Efficient Frontier는 자산의 역할, 대체 관계, 안정 구간을 읽는 핵심 표면이다. Raw point를 그대로 설명하지 말고 **위험 예산과 trade-off의 언어로 번역한다.**

### 3.1 먼저 frontier의 사용자용 좌표계를 만든다

최소한 다음 기준점을 잡는다.

- Minimum Volatility와 그 Expected Return
- Provided Portfolio의 위치
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

하지만 Risk Position 하나만으로 끝내지 않는다. 사용자가 위치를 직관적으로 잡을 수 있도록 가능하면 다음 anchor와 함께 설명한다.

```text
Minimum Volatility
-> pre-Max-Sharpe 구간
-> near-Max-Sharpe plateau
-> post-Max-Sharpe return-seeking 구간
-> Maximum Return 끝점
```

예:

> 이 자산은 전체 위험범위의 약 55% 지점에서 사라지는데, 이는 거의 정확히 Max-Sharpe 직전이다.

이 방식이 `point 57에서 0%`보다 훨씬 유용하다.

### 3.2 자산 trajectory는 lifecycle로 설명한다

자산별로 모든 비중을 나열하지 말고 다음 lifecycle을 추적한다.

```text
등장
-> 의미 있는 비중 형성
-> plateau 또는 constraint 접촉
-> 감소 시작
-> 실질적 퇴출
```

그리고 각 transition에서 다음을 본다.

- 어느 Volatility 수준에서 등장/퇴출하는가
- 전체 Risk Position 중 어느 범위에서 살아 있는가
- Maximum Sharpe 이전/주변/이후 중 어디에 존재하는가
- 그 구간의 Expected Return은 얼마인가
- Maximum Sharpe 대비 위험을 얼마나 줄이거나 늘리는 대신 수익을 얼마나 포기하거나 얻는가
- 비중이 증가할 때 어떤 자산이 감소하는가
- min/max constraint에 붙는가

좋은 설명의 형태:

> **AIA(아시아 대형주)는 전체 frontier 중 가장 보수적인 영역에서만 선택된다.** Volatility를 약 12.8% 이하로 강하게 제한할 때 의미 있는 비중이 생기지만 Max-Sharpe 위험 수준에 도달하기 전에 빠진다. 즉 이 자산은 수익 엔진이 아니라, Expected Return 일부를 포기해 극저위험을 추구할 때만 필요한 방어 보조 역할이다.

이렇게 `어디서 존재 -> 어떤 trade-off -> 무슨 역할` 순서로 설명한다.

### 3.3 Material weight threshold: 숫자 먼지를 사용자 결론으로 만들지 않는다

Solver의 아주 작은 non-zero weight는 사용자에게 경제적으로 의미 있는 비중이 아닐 수 있다.

사용자 서술에서는 별도 기준이 없으면 **1%를 기본 material-weight threshold**로 사용한다.

- `weight >= 1%`: economically active
- `0 < weight < 1%`: audit상 non-zero이지만 사용자 서술에서는 `사실상 퇴출`로 취급 가능
- 정확히 0%가 되는 point는 필요할 때만 audit reference로 사용

예:

`6.1% -> 0.3% -> 0%`를 그대로 읊지 말고:

> 고위험 구간으로 갈수록 빠르게 축소되어 frontier 후반부에서는 사실상 퇴출된다.

Study 특성상 1% 미만도 중요한 경우에는 threshold를 명시적으로 바꾼다.

### 3.4 숫자는 transition과 trade-off를 설명할 때만 쓴다

모든 중간 비중을 나열하지 않는다. 다음 사건만 우선한다.

- 최초 등장
- 의미 있는 비중 도달
- 상한/하한 도달
- 감소 시작
- 실질적 퇴출
- 역할을 바꾸는 대체 관계

그리고 **orphan number를 만들지 않는다.**

숫자는 가능하면 다음 중 하나와 짝을 이룬다.

- 현재 portfolio 대비
- Minimum Volatility 대비
- Maximum Sharpe 대비
- 전체 frontier 위험 범위 대비
- 인접 transition 전후 대비

나쁜 예:

> TLT는 12.67%에서 사라진다.

좋은 예:

> TLT는 Volatility 약 12.7%까지 살아 있지만 Max-Sharpe 위험 수준에 도달하기 전에 사라진다. 즉 frontier의 보수적 절반가량에서는 변동성을 낮추는 데 쓰이지만, 더 높은 수익을 선택하면 빠르게 필요성이 줄어든다.

사용자가 이미 report에서 정확한 표를 볼 수 있다면 LLM text는 표를 재출력하기보다 **숫자의 의미와 구조**를 설명한다.

### 3.5 Constraint pressure는 `touch`와 `persistent pressure`를 구분한다

한 점에서 상한에 닿는 것과 넓은 위험 구간에서 계속 상한에 붙는 것은 의미가 다르다.

- **Isolated boundary touch**: 특정 objective 또는 좁은 구간에서만 경계 접촉
- **Persistent boundary pressure**: 의미 있는 frontier 구간 또는 near-Max-Sharpe plateau에서 계속 경계 접촉

Persistent pressure가 있으면 다음을 분리해서 말한다.

```text
Role inference       = 강할 수 있음
Exact weight inference = 약함
```

예:

> QQQ가 Max-Sharpe에서 50%라는 사실보다, Max-Sharpe 주변의 넓은 구간에서 50% 상한을 계속 요구한다는 사실이 더 중요하다. 이는 QQQ의 return-engine 역할은 강하게 지지하지만 자연스러운 최적 비중이 50%라고 말할 근거는 약하게 만든다.

### 3.6 Plateau와 안정 구간을 Exact Optimum보다 우선한다

Maximum Sharpe 한 점보다 인접 portfolio에서 Sharpe와 구성의 질이 비슷하게 유지되는 구간을 찾는다.

System이 별도 plateau 정의를 제공하지 않으면 설명용 default로 다음을 사용할 수 있다.

```text
Near-Max-Sharpe band =
Sharpe >= Max Sharpe - max(0.01, 1% × |Max Sharpe|)
```

이 threshold는 투자 규칙이 아니라 **한 점 과적합을 줄이기 위한 서술용 기준**이다. 사용했다면 분석에 기준을 짧게 명시한다.

near-optimal band에서 다음을 제시한다.

- Expected Return 범위
- Volatility 범위
- 주요 자산 비중 범위
- Sharpe 하락폭
- constraint 접촉 여부

작은 risk-return 차이에 allocation이 크게 뒤집히면 exact weight의 신뢰도를 낮추고 **안정적인 비중 범위 또는 역할 수준의 결론**을 우선한다.

### 3.7 대체 관계와 집중도를 본다

후보 비중이 증가할 때 무엇이 줄어드는지 추적한다.

- QQQ를 밀어낸다 -> 성장/고베타 역할 대체 가능성
- GLD를 밀어낸다 -> 같은 방어/귀금속 축에서 risk gear를 높이는 가능성
- 기존 핵심 자산을 거의 밀어내지 않는다 -> 새로운 독립 역할 가능성

또한 high-return 쪽으로 갈수록 자산 수가 줄고 한두 자산에 집중되는지 확인한다. 높은 Expected Return이 단순 concentration의 결과인지 구분한다.

특히 여러 자산이 동일 max-weight에 묶여 있으면 Maximum Return 끝점 자체가 **constraint-shaped concentration**일 수 있다.

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

같은 표본으로 최적화한 optimized portfolio의 historical MDD가 더 작다고 해서 미래 downside protection이 입증된 것은 아니다.

### Rolling Return

특히 Rolling 3Y/5Y Low로 full-period 결과가 특정 시기에 의존하는지 확인한다.

### Return / Risk Contribution

Allocation weight 대비 Return Contribution과 Risk Contribution을 비교해 숨은 비용을 본다.

### Benchmark-relative metrics

Benchmark는 reference이지 optimizer의 정답이 아니다. Benchmark-relative 지표는 Study 질문에 필요할 때만 supporting evidence로 사용한다.

Benchmark가 asset universe 안의 한 자산과 동일하더라도 `benchmark 역할`과 `optimizer 후보 자산 역할`을 구분한다.

---

## 5. 0% 자산과 한계 효용을 과해석하지 않는다

### 5.1 `0% everywhere`가 의미하는 것

어떤 자산이 Efficient Frontier 전체에서 0%라면 안전하게 말할 수 있는 것은 다음뿐이다.

> **현재 표본, 현재 expected-return/covariance 추정, 현재 constraints 아래에서는 optimizer가 이 자산을 선택하지 않았다.**

이 사실만으로 다음을 결론내리지 않는다.

- 장기적으로 필요 없다
- 나쁜 자산이다
- diversification 역할이 없다
- 다른 자산과 완전히 redundant하다

왜 선택되지 않았는지 설명하려면 Expected Return, Volatility, Correlation, 대체 자산을 함께 본다.

`REDUNDANT`는 단순 0%가 아니라 **어떤 기존 자산이 같은 역할을 더 효율적으로 대체한다는 evidence가 확인됐을 때** 사용한다.

확인이 부족하면 role label은 `Not Selected in Current Model` 또는 `Role not confirmed`를 우선한다.

### 5.2 Marginal Utility / Ablation

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

## 6. Role, Decision, Role Confidence, Weight Confidence를 분리한다

한 run의 결과를 곧바로 투자 결론으로 바꾸지 않는다.

각 주요 자산은 최소 네 축으로 요약한다.

| 구분 | 예시 |
|---|---|
| **Role** | Core Engine, Return Enhancer, Diversifier, Low-risk-only Contributor, Not Selected in Current Model, Redundant |
| **Decision** | Keep candidate, Watch, Re-test, Exclude candidate |
| **Role Confidence** | High / Medium / Low |
| **Weight Confidence** | High / Medium / Low |

예:

`QQQ | Role: Return Engine | Decision: Keep candidate | Role Confidence: High | Weight Confidence: Low`

이렇게 하면 `역할은 선명하지만 상한 때문에 정확한 비중은 알 수 없음`을 한 표 안에서 표현할 수 있다.

### 6.1 Role Confidence

Role Confidence는 **현재 run에서 포트폴리오 역할을 얼마나 명확하게 관찰했는가**에 대한 신뢰도다. 미래 수익률에 대한 confidence가 아니다.

일반적인 기준:

- **High**: 넓거나 의사결정상 중요한 frontier 구간에서 역할이 반복되고 supporting evidence와 모순이 적음
- **Medium**: 역할은 보이지만 좁은 구간, constraint, sample dependency 등 중요한 단서가 있음
- **Low**: 한두 point, numerical dust, 약한 supporting evidence, 또는 데이터 이슈에 크게 의존

### 6.2 Weight Confidence

Weight Confidence는 **정확한 비중 또는 비중 범위를 얼마나 신뢰할 수 있는가**에 대한 판단이다.

다음 경우 낮춘다.

- min/max constraint에 binding
- near-Max-Sharpe band 안에서 비중이 크게 흔들림
- 작은 Sharpe 차이에 allocation이 급변
- 역할은 유지되지만 기간/objective 변경에 exact weight가 크게 바뀜
- material threshold 근처에서만 존재

반대로 plateau 안에서 비중 범위가 안정되고 constraint에 닿지 않으면 높일 수 있다.

**Role Confidence와 Weight Confidence가 다르게 나오는 것은 정상이다.** 오히려 optimizer 해석에서 자주 발생한다.

---

## 7. 다음 실험은 `불확실성 -> 조작 -> 관찰 -> 판정`으로 제안한다

많은 sensitivity run을 나열하지 않는다. 현재 결론을 가장 크게 바꿀 수 있는 불확실성부터 1~3개 제안한다.

우선순위 예:

1. Blocking data issue 수정 후 동일 run 재실행
2. Binding constraint 완화
3. 후보 포함/제외 ablation
4. 동일 risk budget 또는 target return에서 재검증
5. 기간/objective 변경 robustness

단순히 `QQQ 상한을 풀어보자`에서 끝내지 않는다.

좋은 다음 실험은 다음 네 요소를 가진다.

```text
Uncertainty: 무엇을 아직 모르는가
Manipulation: 다른 것은 고정하고 무엇만 바꾸는가
Observation: 어떤 지표/trajectory를 볼 것인가
Decision rule: 어떤 결과면 현재 해석을 강화하거나 약화하는가
```

예:

> **Uncertainty:** QQQ의 자연스러운 optimizer 수요가 50%보다 큰지 알 수 없다.  
> **Manipulation:** 다른 조건은 고정하고 QQQ max만 완화한다.  
> **Observation:** Max Sharpe 개선폭, 새 최적 비중, near-Max-Sharpe plateau 구성, concentration 변화를 본다.  
> **Decision:** Sharpe가 거의 변하지 않으면 50% cap은 실질적으로 중요하지 않았던 것이고, Sharpe와 plateau가 크게 이동하면 현재 결과는 cap에 의해 강하게 형성된 것으로 본다.

Constraint를 푸는 실험은 deployment recommendation이 아니라 **diagnostic run**일 수 있음을 명시한다.

---

## 사용자에게 결과를 전달하는 순서

1. **Run identity + Data Validity 상태**: 문제가 없으면 1~2문장으로 짧게
2. **Executive Thesis**: 이번 run에서 가장 중요한 구조 2~4문장
3. **현재 Portfolio의 Frontier Efficiency Gap**
4. **Frontier 지도**: Minimum Volatility -> Provided -> Max Sharpe -> Maximum Return의 위치와 의미 있는 plateau
5. **주요 자산 역할**: 개별 ticker 나열보다 역할 그룹을 우선
6. **필요한 Supporting Evidence만**: Correlation / Drawdown / Rolling / Contribution
7. **Role / Decision / Role Confidence / Weight Confidence 요약**
8. **가장 정보가치 높은 다음 실험 1~3개**

Data Validity에 특별한 문제가 없다면 긴 validity 설명으로 시작하지 않는다. `정상, 분석 가능` 상태를 짧게 확인하고 바로 insight로 이동한다.

---

## 가독성 및 Narrative Compression 규칙

### 사람에게 자산을 먼저 설명한다

- 첫 등장 시 `자산명/성격 (Ticker)` 순서를 기본으로 한다.
- 예: `금 현물 (GLD)`, `나스닥100 성장주 (QQQ)`, `미국 장기국채 (TLT)`.
- 최종 Role 표에서도 ticker만 단독으로 나열하지 않는다.

### Raw point는 audit reference일 뿐이다

- `point 29`, `point 55`처럼 raw frontier 번호를 주 설명 좌표로 사용하지 않는다.
- 필요하면 문장 끝 괄호 안 audit reference로만 남긴다.

### 위치 표현에는 anchor가 필요하다

- `왼쪽`, `초반`, `고수익 쪽`만으로 끝내지 않는다.
- 절대 Volatility, Risk Position, Max-Sharpe와의 상대 위치, Expected Return trade-off 중 필요한 anchor를 붙인다.

### 숫자는 질문에 답할 때만 사용한다

- 숫자 열거 자체를 분석으로 간주하지 않는다.
- 한 문장에 많은 숫자를 몰아넣지 않는다.
- 이미 report에 있는 전체 metric table을 LLM text에서 반복하지 않는다.
- `어디에 있는가`, `무엇과 비교해 다른가`, `그래서 무엇을 의미하는가`가 없는 숫자는 삭제 후보로 본다.

### 자산별 백과사전식 설명보다 역할 그룹을 우선한다

예:

```text
Return engines
- 미국 대형주 / 성장주

Broad diversifier
- 금

Low-risk-only contributors
- 장기채 / 일부 원자재

Not selected in current model
- 지역주식 A / B
```

그 다음 의사결정에 중요한 자산만 깊게 설명한다.

### Report와 LLM text의 역할을 분리한다

```text
report.html = 정확한 표, 차트, 전체 수치 확인
LLM text    = 구조, trade-off, 역할, 불확실성, 다음 실험
```

LLM은 report를 말로 다시 읽어주는 narrator가 아니라 **research interpreter**다.

---

## 최종 Self-Check

사용자에게 답하기 전에 다음을 확인한다.

- [ ] 현재 분석문과 canonical artifact의 run_id가 일치하는가?
- [ ] benchmark / objective / constraints를 현재 run에서 직접 확인했는가?
- [ ] in-sample 결과를 미래 성과처럼 표현하지 않았는가?
- [ ] 같은 Return / 같은 Volatility 비교에서 extrapolation하지 않았는가?
- [ ] ticker 첫 등장에 사람이 읽을 수 있는 자산명을 붙였는가?
- [ ] raw point 번호를 핵심 설명 좌표로 사용하지 않았는가?
- [ ] 1% 미만 numerical dust를 과해석하지 않았는가?
- [ ] 중요한 숫자마다 비교 기준 또는 의미가 있는가?
- [ ] constraint-bound weight를 `적정 비중`으로 단정하지 않았는가?
- [ ] isolated boundary touch와 persistent boundary pressure를 구분했는가?
- [ ] Maximum Sharpe 한 점보다 near-optimal plateau를 확인했는가?
- [ ] `0% everywhere`를 곧바로 `불필요/Redundant`로 해석하지 않았는가?
- [ ] Role Confidence와 Weight Confidence를 분리했는가?
- [ ] report의 표를 반복하기보다 insight를 추가했는가?
- [ ] 다음 실험에 uncertainty, manipulation, observation, decision rule이 있는가?

---

## 핵심 원칙

> **Optimization은 최적 비중 한 점을 찾는 도구가 아니라, 위험 예산을 바꿀 때 포트폴리오 구조가 어떻게 변하는지 이해하는 도구다. LLM은 raw frontier와 report의 숫자를 그대로 다시 읽지 말고, 절대 변동성, 전체 위험범위 내 위치, Maximum Sharpe와의 상대 위치, Expected Return의 대가로 번역하여 각 자산의 한계 효용을 설명해야 한다. 역할에 대한 신뢰와 정확한 비중에 대한 신뢰를 분리하고, 남은 불확실성은 다음 실험의 형태로 연결한다.**
