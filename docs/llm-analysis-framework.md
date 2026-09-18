# 포트폴리오 연구 결과 LLM 분석 프레임워크

## 목적

이 문서는 Optimization / Backtest 결과를 LLM이 **사용자 의사결정에 도움이 되게 해석하는 최소 운용 규칙**이다.

핵심 원칙은 하나다.

> **Report를 빠짐없이 설명하지 말고, 사용자의 질문에 답하는 데 필요한 evidence만 사용한다. 답이 나오면 멈춘다.**

숫자가 존재한다는 이유만으로 분석하지 않는다. 각 숫자는 다음 중 하나를 해야 한다.

- 비교 결과를 바꾼다.
- 구조적 해석을 뒷받침하거나 반박한다.
- 사용자의 다음 의사결정에 영향을 준다.

셋 다 아니면 생략한다.

---

# 1. 시작점: 질문부터 정한다

먼저 canonical Run에서 `product_mode`를 확인한다.

```text
optimization -> Optimization evidence 사용
backtest     -> Backtest evidence 사용
```

Source priority:

```text
1. result.json
2. review/*.csv
3. 필요한 경우 raw/*.csv
```

`report.html`은 presentation surface다.

그 다음 사용자의 질문이 무엇인지 정한다.

대표적으로:

- 전체 portfolio가 좋은 구조인가?
- A와 B 중 무엇이 실제로 달랐나?
- 특정 자산 X가 portfolio 안에서 가치가 있나?
- optimizer의 비중을 얼마나 믿어야 하나?
- 특정 약점이 실제 stress에서도 나타났나?

**질문을 정한 뒤 필요한 분석만 한다.**

---

# 2. 분석 선택 규칙

Metric이나 chart를 순서대로 훑지 않는다.

각 evidence를 보기 전에 묻는다.

> **이 숫자를 보면 현재 해석이 달라질 수 있는가?**

아니면 보지 않아도 된다.

예:

- CAGR 차이가 이미 큰데 Best Year를 추가로 읽는 것은 대개 정보가 적다.
- 낮은 correlation이 보여도 실제 drawdown 방어나 portfolio 개선이 없으면 강한 diversifier evidence가 아니다.
- MDD가 다르면 recovery duration이 의사결정에 영향을 줄 때만 더 본다.
- 최근 1Y 수익률이 장기 구조와 관계없다면 언급하지 않는다.

**가용 artifact의 개수와 분석의 길이는 비례하지 않는다.**

---

# 3. Optimization을 볼 때

Optimization의 질문은:

> **주어진 universe와 constraint 안에서 어떤 구조가 효율적이었고, 그 구조를 얼마나 믿을 수 있는가?**

필요한 경우에만 다음 evidence를 사용한다.

### Efficiency

현재 portfolio와 optimized portfolio의 차이가 실질적인가?

- 같은 risk에서 return 개선
- 같은 return에서 risk 감소
- Sharpe 또는 frontier 위치 변화

차이가 미미하면 optimizer 숫자를 과대해석하지 않는다.

### Structure

정확한 weight보다 먼저 본다.

- 어떤 자산/cluster가 반복적으로 핵심인가
- 어떤 자산이 대체 관계인가
- min/max constraint에 붙어 있는가
- risk contribution이 특정 자산에 몰리는가

### Weight confidence

정확한 최적 비중은 다음 경우 신뢰를 낮춘다.

- constraint boundary에 붙음
- 인접 frontier에서 비중이 크게 흔들림
- 기간/objective 변경 시 크게 변함
- 작은 expected-return 차이로 allocation이 크게 바뀜

이 경우:

> **role은 의미 있지만 exact weight confidence는 낮다**

처럼 설명한다.

### Optimization에서 하지 않을 것

- frontier가 있다고 모든 frontier metric을 설명하지 않는다.
- 0% 자산을 자동으로 불필요하다고 단정하지 않는다.
- Max Sharpe 한 점을 미래의 적정 비중으로 표현하지 않는다.
- historical CAGR/MDD만으로 optimizer 구조를 대신 설명하지 않는다.

---

# 4. Backtest를 볼 때

Backtest의 질문은:

> **이 역사 표본에서 portfolio가 실제로 어떻게 행동했고, 차이를 만든 구조는 무엇인가?**

기본적으로 필요한 것만 고른다.

### Return / Risk

보통 CAGR, Volatility, MDD, Sharpe/Sortino 중 질문에 필요한 조합만 사용한다.

한 지표가 높다는 이유로 승자를 만들지 않는다.

### Time consistency

Full-period 결과가 특정 시기에 의존하는지가 중요한 경우에만:

- annual
- rolling
- sub-period

를 본다.

### Stress behavior

평균 성과보다 나쁜 시기 행동이 중요한 질문이면:

- worst months
- major drawdowns
- recovery
- conditional behavior

를 우선한다.

### Correlation / contribution

Correlation은 역할의 단서다. 결론이 아니다.

가능하면 다음과 함께 본다.

- 실제 allocation
- Return Contribution
- Risk Contribution
- stress behavior
- 제거/대체 시 portfolio 변화

---

# 5. 특정 자산 질문의 기본 경로: Asset Role Audit

Optimization 또는 Backtest 뒤에 사용자가 다음처럼 묻는 경우:

```text
SCHD 가치가 있어?
콩선물이 왜 들어가?
XLE를 유지해야 해?
AIA가 portfolio에서 하는 일이 뭐야?
```

별도 지시가 없으면 아래 순서를 기본으로 사용한다.

단, **모든 단계를 억지로 출력하지 않는다. 앞 단계에서 답이 충분하면 멈춘다.**

## 5.1 Slot Value

가장 먼저 묻는다.

> **이 자산이 차지한 비중을 다른 곳에 썼다면 portfolio가 더 좋아졌는가?**

예를 들어 SCHD 5%라면 다른 조건을 고정하고:

```text
SCHD 5% 유지
vs
SCHD 5% -> QQQ
SCHD 5% -> SPMO
SCHD 5% -> GLD
...
```

를 비교한다.

핵심 출력은 절대값보다 변화량이다.

```text
ΔCAGR
ΔVolatility
ΔMDD
ΔSharpe
```

이것을 **Slot Replacement Test**로 부른다.

좋은 대체 후보는 무작정 전 자산이 아니다.

- 현재 portfolio의 주요 엔진
- 역할이 겹치는 자산
- 실제 대체 후보
- 필요하면 cash / short-duration proxy

중 질문에 의미 있는 것만 고른다.

### 계산 원칙

현재 Run의 월별 자산 수익률과 rebalancing semantics만으로 동일 조건의 대체 portfolio를 정확히 재구성할 수 있으면 LLM이 파생 계산할 수 있다.

이 경우 반드시 **현재 Run 데이터에서 계산한 counterfactual**이라고 구분한다.

거래비용, path dependency, 별도 constraint 등으로 기존 simulation 의미론을 그대로 보존할 수 없으면 새 Backtest/Optimization을 실행한다.

Cash 대체를 0% return으로 몰래 가정하지 않는다. 실제 cash proxy 또는 명시적 가정을 사용한다.

---

## 5.2 Stress / Conditional Utility

Slot Value만으로 자산의 역할이 충분히 설명되지 않으면 본다.

먼저 현재 portfolio의 **dominant risk / return engine**을 식별한다.

QQQ/SPMO 같은 특정 ticker를 규칙에 하드코딩하지 않는다.

그 engine의 약세 구간에서 대상 자산이:

- 플러스였던 비율
- engine보다 덜 빠진 비율
- 평균적으로 몇 %p 방어했는지
- severe-down 구간에서도 같은 특성이 있었는지

를 본다.

중요:

```text
절대 방어 = 대상 자산이 플러스인가?
상대 방어 = 대상 자산도 하락했지만 주력 엔진보다 덜 빠졌는가?
```

둘을 섞지 않는다.

---

## 5.3 Contribution Efficiency

필요하면 세 숫자를 같이 본다.

```text
Current Weight
Return Contribution
Risk Contribution
```

질문은:

> **배정한 자본과 가져간 위험에 비해 portfolio 결과에 무엇을 보탰는가?**

Return Contribution이 작다고 바로 제거하지 않는다.

Risk Contribution이 낮거나 음수이면서 stress utility가 있으면 작은 return contribution도 가치가 있을 수 있다.

---

## 5.4 Role Consistency

마지막으로 숫자를 역할과 연결한다.

예:

- Growth / Momentum engine
- Value / Quality equity diversifier
- Inflation / Cyclical engine
- Crisis diversifier
- Low-risk stabilizer
- Independent return engine

질문:

> **우리가 기대한 역할과 실제 관측 행동이 일치했는가?**

역할은 이름이나 ETF 마케팅 문구가 아니라 portfolio 안에서 관측된 행동으로 판단한다.

---

# 6. Counterfactual을 우선하는 이유

특정 자산의 standalone CAGR이나 Sharpe만으로 portfolio 가치를 판단하지 않는다.

좋은 질문은:

```text
이 자산이 얼마나 올랐나?
```

보다:

```text
이 자산 대신 같은 자본을 다른 곳에 썼다면
portfolio 전체가 더 좋아졌나?
```

에 가깝다.

따라서 특정 자산의 필요성을 평가할 때 가능하면:

```text
standalone metric
< portfolio counterfactual
```

순으로 evidence 강도를 본다.

---

# 7. Evidence discipline

### Fact / Interpretation / Hypothesis를 구분한다

- Fact: artifact 또는 직접 계산에서 확인됨
- Interpretation: portfolio 구조에서의 의미
- Hypothesis: 경제적 원인 또는 다음 실험 가설

원인 데이터가 없으면 경제적 설명을 사실처럼 쓰지 않는다.

### Ex-post discipline

역사 표본에서 좋았다는 것을 미래 성과 보장으로 표현하지 않는다.

Optimization Expected Return과 Backtest realized CAGR을 섞지 않는다.

### Materiality

작은 차이를 의미 있는 차이처럼 포장하지 않는다.

차이가 작으면:

> **사실상 비슷하다**

라고 말해도 된다.

---

# 8. 기본 답변 형태

기본 답변은 짧게 유지한다.

권장:

```text
1. 핵심 결론 1~2문장
2. 필요한 경우 작은 비교표 1개
3. 왜 그런지 핵심 evidence 2~4개
4. 결론을 바꿀 수 있는 불확실성이 있을 때만 다음 실험
```

피한다:

- report 목차를 그대로 따라가는 답변
- 모든 metric을 한 번씩 언급하는 답변
- 의미 없는 숫자 나열
- 매번 새로운 후속 실험을 제안하는 습관
- 사용자가 특정 자산을 물었는데 portfolio 전체를 다시 설명하는 답변

---

# 9. Stop Rule

가장 중요한 규칙이다.

> **사용자의 질문에 답할 만큼 evidence가 모이면 분석을 멈춘다.**

더 볼 수 있다는 이유로 더 보지 않는다.

다음 연구는 **현재 불확실성이 실제 의사결정을 바꿀 수 있을 때만** 제안한다.

---

# 핵심 요약

```text
Question first
-> 필요한 evidence만 선택
-> 가능하면 counterfactual 우선
-> stress에서 역할 확인
-> contribution으로 보강
-> role과 연결
-> 답이 나오면 stop
```

**분석의 품질은 사용한 숫자의 개수가 아니라, 사용자의 의사결정에 추가된 정보의 양으로 판단한다.**
