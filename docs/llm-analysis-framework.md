# 포트폴리오 최적화 결과 LLM 분석 프레임워크

## 목적

이 문서는 Portfolio Visualizer 또는 이에 준하는 포트폴리오 최적화 결과를 LLM이 **사용자 의사결정 관점에서 해석**하기 위한 기준이다.

LLM의 주된 가치는 report의 숫자를 다시 읽어주는 것이 아니다. 여러 분석 결과와 Efficient Frontier를 연결하여 사용자가 실제로 궁금한 질문에 답해야 한다.

> **현재 포트는 효율적인가? 어디가 취약한가? Optimizer는 어떤 구조를 발견했는가? 각 자산은 왜, 얼마나 필요한가? 사용자의 목표에서는 어느 정도 비중이 역사적으로 효율적이었는가? 그 구조는 안정적인가? 현재 evidence가 부족하다면 어떤 다음 실험이 필요한가?**

기본 우선순위는 다음과 같다.

```text
사용자 질문
-> 정량적 insight
-> 구조적 해석
-> 필요한 supporting evidence
-> 부족한 evidence를 채우는 다음 실험
```

정성적 경제/regime 설명은 중요하지만 **정량 분석을 대체하지 않는다.** `주식이 많다`, `인플레이션 자산이 없다` 같은 일반론은 데이터에서 확인된 구조적 취약성을 설명하거나 다음 실험의 가설을 만들 때만 사용한다.

---

# LLM 해석 순서

아래 7단계는 **사고 순서의 기본 가이드라인**이다.

모든 단계를 사용자 답변에 동일한 길이로 출력할 필요는 없다. 내부 분석은 이 순서를 따르되, 사용자에게는 현재 Study에서 의미 있는 insight만 압축해 전달한다.

```text
1. Portfolio Diagnosis
2. Optimizer Structure
3. Asset Utility
4. Efficient Allocation Range
5. Frontier Fragility
6. Evidence Sufficiency & Robustness
7. Next Research
```

---

# 1. Portfolio Diagnosis

핵심 질문:

> **현재 구조는 얼마나 비효율적이고 어디가 취약한가? 최적화 후에도 어떤 취약성이 남는가?**

Provided Portfolio가 있으면 현재 포트와 Optimized Portfolio를 모두 진단한다.

## 1.1 Efficiency Gap

현재 포트가 frontier에서 얼마나 안쪽에 있는지 본다.

가능하면 두 질문에 답한다.

1. **같은 Expected Return에서 frontier는 Volatility를 얼마나 낮출 수 있었는가?**
2. **같은 Volatility에서 frontier는 Expected Return을 얼마나 높였는가?**

예:

> 이 역사 표본에서 현재 포트의 Expected Return을 유지하면 frontier에서는 Volatility가 12.7%가 아니라 약 10.8%였다. 반대로 현재와 같은 12.7% Volatility를 허용하면 frontier Expected Return은 약 14.8%였다. 현재 포트는 frontier 안쪽에 상당한 efficiency gap이 있다.

Interpolation은 frontier가 해당 Return 또는 Volatility를 실제로 bracket하는 범위 안에서만 사용한다. 범위 밖이면 extrapolation하지 않는다.

## 1.2 Quantitative Vulnerability

Efficiency와 Robustness는 다르다. 현재 포트가 frontier에 가까워도 구조적 취약성이 있을 수 있다.

가능하면 다음 축 중 **실제로 의미 있는 문제만 선택하여 정량적으로 압축**한다.

### Risk Concentration

- 특정 자산 또는 상관 cluster가 portfolio risk를 얼마나 지배하는가?
- Allocation Weight와 Risk Contribution이 크게 다른가?
- 명목상 자산 수보다 실제 risk source가 훨씬 적은가?

### Correlation Redundancy

Correlation matrix를 나열하지 않는다.

서로 강하게 함께 움직이는 자산을 묶어 **실질적인 독립 움직임이 얼마나 되는지** 설명한다.

필요하면 correlation clustering, PCA, effective independent bets 같은 정량 분석을 후속 기능 또는 실험으로 제안할 수 있다.

### Drawdown Co-failure

평균 correlation이 낮아도 stress 구간에서는 함께 무너질 수 있다.

가능하면 다음을 본다.

- 주요 drawdown에서 어떤 자산/cluster가 동시에 하락했는가
- worst-N months의 동시 하락 정도
- stress-period conditional correlation
- portfolio drawdown에 크게 기여한 자산/cluster

핵심 질문은 `평균적으로 분산되는가?`가 아니라 **`나쁜 시기에 실제로 분산되는가?`**다.

### Return Dependence

- 역사적 수익의 대부분이 특정 자산/cluster에서 발생했는가?
- Allocation 대비 Return Contribution이 과도하게 집중되는가?

숫자는 표 전체를 반복하지 말고 취약성의 크기를 이해시키는 핵심 1~3개만 사용한다.

## 1.3 Optimized Portfolio도 다시 진단한다

Optimizer는 **주어진 Asset Universe 안에서** 효율적인 조합을 찾을 뿐, 결과 자체가 구조적으로 robust하다고 보장하지 않는다.

따라서 최적화 후에도 확인한다.

- Risk Concentration이 더 커졌는가?
- 높은 상관의 자산들이 큰 비중을 동시에 차지하는가?
- 안정성이 특정 diversifier 하나에 과도하게 의존하는가?
- drawdown protection이 특정 역사 구간에만 의존하는가?

> **Efficient within universe ≠ Structurally robust**

---

# 2. Optimizer Structure

핵심 질문:

> **Optimizer는 어떤 포트폴리오 구조를 발견했는가?**

Maximum Sharpe의 정확한 비중부터 설명하지 않는다.

먼저 여러 후보 중 실제 frontier를 반복적으로 만드는 **핵심 엔진 조합**을 찾는다.

예:

> 이 표본의 optimizer는 여러 지역주식과 원자재를 함께 보유하는 구조보다 `미국 주식 return engine + 금 diversifier`라는 단순한 구조를 반복적으로 선택했다.

그 다음에 exact weight, frontier trajectory, constraint, correlation 등을 근거로 붙인다.

## Constraint Pressure

최적 비중이 min/max에 붙으면 그 비중을 `적정 비중`으로 해석하지 않는다.

```text
Role inference         = 강할 수 있음
Exact weight inference = 약함
```

한 점의 boundary touch보다 near-efficient 구간에서 계속 상한/하한에 붙는 **persistent pressure**를 더 중요하게 본다.

---

# 3. Asset Utility

핵심 질문:

> **이 자산은 왜 필요한가? 그리고 그 필요성은 얼마나 큰가?**

주요 자산은 `Role -> Utility Magnitude` 순으로 해석한다.

## 3.1 Role: 왜 필요한가?

예:

- Return Engine
- Return Enhancer
- Diversifier
- Low-risk Stabilizer
- Substitute
- Not Selected in Current Model

Role은 standalone Sharpe만으로 정하지 않는다. Frontier trajectory와 portfolio interaction을 우선한다.

## 3.2 Utility Magnitude: 얼마나 필요한가?

단순 `선택됨 / 0%`가 아니라 portfolio 효용의 **크기**를 본다.

### 수익 기여

- Allocation 대비 Return Contribution
- 자산을 제거했을 때 동일 Volatility에서 Expected Return이 얼마나 감소하는가
- 높은 Return target으로 갈수록 비중이 지속적으로 증가하는가

### 안정성 기여

- 자산을 제거했을 때 동일 Expected Return에서 Volatility가 얼마나 증가하는가
- Risk Contribution 대비 allocation이 효율적인가
- 낮은 risk budget으로 갈수록 비중이 증가하는가
- drawdown / downside / recovery에서 실제 보호 효과가 관찰되는가

### Breadth of Utility

- 넓은 risk/return 영역에서 지속적으로 필요한가
- 특정 사용자 목표에서만 필요한가
- 아주 좁은 frontier 구간 또는 작은 비중에서만 필요한가

필요성 강도는 다음처럼 해석할 수 있다.

- **Structural**: 넓은 risk/return 영역에서 반복적으로 필요
- **Target-dependent**: 특정 목표에서만 필요
- **Marginal**: 아주 좁은 영역 또는 작은 비중에서만 필요
- **Not Selected in Current Model**: 현재 조건에서 frontier 효용이 확인되지 않음

`REDUNDANT`는 단순 0%가 아니라 **다른 자산이 같은 역할을 더 효율적으로 대체한다는 evidence가 있을 때만** 사용한다.

## 3.3 Diversifier Dependency는 correlation보다 ablation을 우선한다

특정 diversifier가 중요해 보인다면 가능하면 **그 자산이 없을 때 portfolio가 얼마나 악화되는지** 확인한다.

Leave-one-out / ablation에서 본다.

- 동일 Expected Return에서 Δ Volatility
- 동일 Volatility에서 Δ Expected Return
- Δ Max Sharpe
- drawdown / recovery 변화
- risk concentration 변화

예:

> 금을 제거하면 같은 Expected Return을 유지하는 데 필요한 Volatility가 1.6%p 상승했다. 현재 구조의 안정성이 금 하나에 상당 부분 의존하고 있다는 evidence다.

이런 정량 evidence가 있을 때 `single-diversifier dependency` 같은 강한 구조적 표현을 사용한다.

---

# 4. Efficient Allocation Range

핵심 질문:

> **사용자의 목표 Risk / Return에서는 이 자산을 어느 정도 비중으로 가져가는 것이 역사적으로 효율적이었는가?**

Max Sharpe 한 점보다 **사용자의 실제 목표 구간에서 반복적으로 선택되는 비중 범위**를 우선한다.

## 4.1 Risk Budget 기준

사용자가 예를 들어 Volatility 12~14%를 감수할 수 있다면 그 frontier 구간에서 본다.

- 주요 자산의 비중 범위
- 어떤 자산이 등장/퇴출하는가
- 추가 Return을 얻기 위해 무엇을 줄이는가
- Risk Concentration이 어떻게 변하는가

예:

> Volatility 12~14% 구간에서 금은 대략 15~23% 범위에서 반복적으로 선택됐다. 따라서 Max Sharpe의 18.6% 한 점보다 `중간 risk budget에서 10%대 후반~20%대 초반`이라는 범위가 더 유용한 역사적 evidence다.

## 4.2 Return Target 기준

사용자가 Expected Return 목표를 제시하면 해당 Return을 만들기 위한:

- Minimum Volatility
- Allocation Range
- 구조 변화

를 같은 방식으로 본다.

## 4.3 Frontier를 메뉴판으로 사용한다

Efficient Frontier는 추상적인 곡선이 아니라 **Risk를 더 감수하거나 Return을 더 요구할 때 어떤 자산을 늘리고 무엇을 포기해야 했는지 보여주는 메뉴판**으로 해석한다.

예:

> Max-Sharpe보다 더 높은 수익을 요구할수록 금이 줄고 성장주 비중이 증가한다. 즉 추가 수익은 diversification을 일부 포기하고 equity concentration을 높이는 방식으로 얻어진다.

## 4.4 현재 Run만으로 부족하면 목표 조건의 추가 Run을 제안한다

현재 frontier만으로 대략적인 범위는 읽을 수 있지만 사용자의 실제 목표에 대해 더 직접적인 evidence가 필요할 수 있다.

예: 사용자 Risk Budget이 Volatility 12~14%라면:

```text
Maximum Return @ Vol 12%
Maximum Return @ Vol 13%
Maximum Return @ Vol 14%
```

Return target이 중요하면:

```text
Minimum Volatility @ Expected Return 12%
Minimum Volatility @ Expected Return 14%
Minimum Volatility @ Expected Return 16%
```

목적은 sensitivity run을 많이 만드는 것이 아니라 **사용자의 목표 안에서 efficient allocation range를 더 정확히 식별하는 것**이다.

이 단계에서 얻은 비중 범위는 미래 적정 비중이 아니라 **현재 역사 표본에서의 efficient range**다.

---

# 5. Frontier Fragility

핵심 질문:

> **이 비중과 구조는 안정적인가, 아니면 칼날 위의 optimum인가?**

Frontier Fragility는 중요한 insight source다.

Risk 또는 Return 목표를 조금만 바꿨는데 allocation이 크게 바뀐다면 exact optimal weight는 불안정하다.

반대로 넓은 목표 구간에서 특정 자산의 비중과 역할이 유지되면 해당 역할과 allocation range에 대한 신뢰는 높아진다.

## 5.1 인접 Efficient Portfolio를 비교한다

예를 들어:

```text
Vol 12.5% -> 13.0%
```

같은 작은 변화에서 확인한다.

- 주요 자산 비중이 얼마나 움직이는가
- 자산이 갑자기 등장/퇴출하는가
- cluster 간 자금이 크게 이동하는가
- Sharpe/Expected Return 개선은 작은데 allocation 변화는 큰가

필요하면 다음을 보조지표로 사용할 수 있다.

```text
Allocation Distance = 0.5 × Σ |weight_A - weight_B|
```

이는 두 포트 사이에서 전체 자산의 몇 %가 재배치되는지를 나타낸다.

절대 threshold를 기계적으로 적용하지 않는다. 핵심은 **작은 risk/return 변화 대비 allocation 변화가 큰지**다.

예:

> Volatility를 0.5%p만 높였는데 portfolio의 약 25%가 다른 자산으로 재배치되고 성과 차이는 미미하다. Exact optimum은 fragile하며 특정 비중보다 공통으로 유지되는 core structure를 신뢰하는 편이 낫다.

반대 사례:

> Volatility 12~14% 전 구간에서 금 비중이 17~22%에 머문다. 따라서 Max-Sharpe의 정확한 한 점보다 `약 20% 내외의 안정적 역할`이 더 강한 evidence다.

## 5.2 Role Confidence와 Weight Confidence를 분리한다

| 구분 | 의미 |
|---|---|
| **Role Confidence** | 어떤 portfolio 역할을 하는지 얼마나 명확한가 |
| **Weight Confidence** | exact weight 또는 efficient range를 얼마나 신뢰할 수 있는가 |

Weight Confidence는 다음 경우 낮춘다.

- min/max constraint binding
- Frontier Fragility가 큼
- near-efficient 구간에서 비중이 크게 흔들림
- 기간/objective 변경 시 exact weight가 크게 변함
- material threshold 근처에서만 존재

Role은 안정적이지만 Weight Confidence가 낮은 것은 정상이다.

---

# 6. Evidence Sufficiency & Robustness

핵심 질문:

> **현재 evidence로 이 결론에 충분히 답할 수 있는가? 그리고 이 결과를 얼마나 믿을 수 있는가?**

현재 Run에서 관찰된 사실과 더 강한 결론에 필요한 evidence를 구분한다.

## 6.1 Supporting Evidence는 이유를 설명하거나 반증할 때만 사용한다

### Correlation + Return + Volatility

낮은 correlation 자체를 좋은 자산의 증거로 사용하지 않는다. 낮은 상관을 얻기 위해 얼마의 낮은 return 또는 높은 volatility를 감수하는지 함께 본다.

### Return / Risk Contribution

Allocation Weight와 Contribution의 불균형을 통해 Return Dependence 또는 Risk Concentration을 찾는다.

### Drawdown / Recovery

MDD 깊이뿐 아니라 recovery/underwater 기간과 동시 하락 여부를 본다.

### Rolling Return

Rolling 3Y/5Y Low 등으로 full-period 결과가 특정 시기에 과도하게 의존하는지 본다.

### Regime / Annual Return

정량 구조를 설명하기 위한 보조 evidence다. 데이터로 확인되지 않은 경제적 라벨을 먼저 붙이지 않는다.

## 6.2 Missing Engine은 정량 취약점 뒤에만 제안한다

Missing Engine을 정성 체크리스트로 먼저 선언하지 않는다.

순서는 반드시 다음과 같다.

```text
정량적 취약성 발견
-> 구조적 문제 정의
-> 가능한 경제적 원인/대체 엔진 가설
-> 새 Asset Universe 실험
-> 실제 개선 여부 검증
```

예:

> 최적화 후에도 risk의 대부분이 한 equity cluster에 집중되고 portfolio 안정성이 단일 diversifier에 크게 의존한다. 이는 추가적인 독립 엔진을 시험할 필요성을 시사한다.

여기까지는 데이터 기반 판단이다.

`어떤 자산군을 추가할 것인가`는 가설이며, 새로운 Experiment에서 실제로:

- concentration이 낮아지는가
- diversifier dependency가 줄어드는가
- 동일 Risk에서 Return이 개선되는가
- 동일 Return에서 Risk가 감소하는가

를 검증한다.

## 6.3 Robustness 확인

필요하면 다음을 비교한다.

- 기간 변경
- objective 변경
- target risk / target return 변경
- constraint sensitivity
- 후보 포함/제외 ablation

역할은 반복되지만 정확한 비중만 흔들리면:

> `robust role / uncertain exact weight`

로 해석한다.

---

# 7. Next Research

핵심 질문:

> **다음에 어떤 실험을 하면 사용자 의사결정에 가장 많은 정보를 추가할 수 있는가?**

LLM은 optimizer 결과의 수동 해설자가 아니라 **research analyst**다.

현재 Run으로 질문에 충분히 답할 수 없으면 다음 실험을 설계한다.

좋은 후속 실험은 다음 네 요소를 가진다.

```text
Uncertainty : 무엇을 아직 모르는가
Manipulation: 무엇만 바꾸는가
Observation : 어떤 결과를 볼 것인가
Decision    : 어떤 결과면 현재 해석이 강화/약화되는가
```

대표 유형:

1. **Target-risk runs**  
   사용자 Risk Budget에서 efficient allocation range 확인

2. **Target-return runs**  
   원하는 Return을 위한 minimum risk와 구성 확인

3. **Constraint sensitivity**  
   binding cap/floor가 결과를 얼마나 형성했는지 확인

4. **Leave-one-out / ablation**  
   특정 자산의 marginal utility와 diversifier dependency 확인

5. **Universe expansion**  
   정량적으로 발견된 구조적 취약성을 다른 독립 엔진이 실제로 개선하는지 확인

6. **Period / objective robustness**  
   역할과 allocation range가 표본이나 objective에 과도하게 의존하는지 확인

실험을 많이 제안하지 않는다. **사용자 의사결정을 가장 크게 바꿀 수 있는 불확실성부터 1~3개**만 우선한다.

---

# 전 단계 공통 Guardrail

아래 규칙은 7단계와 별개의 분석 단계가 아니라 **모든 단계에 적용되는 품질 규칙**이다.

## Run Identity / Data Validity

분석 전에 현재 Run을 canonical artifact에서 확인한다.

- run_id
- asset universe
- provided portfolio
- benchmark
- objective
- risk-free convention
- rebalancing
- constraints
- 실제 analysis period

Repository 기반 시스템에서는 `LLM-README.md`의 source priority를 따른다.

```text
1. result.json
2. review/*.csv
3. 필요한 경우 raw/*.csv
```

다른 Run의 분석문이나 과거 대화 숫자를 현재 Run과 자동으로 섞지 않는다.

Data 문제는:

- **Blocking**: optimizer input/frontier 자체가 바뀔 수 있음
- **Reporting**: 일부 비교/report만 오염됨

으로 구분하고 영향을 받는 결론의 범위를 명시한다.

## In-sample / Ex-post Discipline

같은 역사 표본에서 추정하고 최적화한 결과를 미래 성과처럼 표현하지 않는다.

좋은 표현:

- `이 역사 표본에서는 더 효율적이었다`
- `현재 추정치에서는 이 자산의 optimizer 수요가 강했다`
- `동일 역사 구간에서 MDD가 더 얕았다`

피해야 할 표현:

- `앞으로 수익률을 3%p 높일 수 있다`
- `MDD를 줄여준다`
- `적정 비중은 20%다`

Expected Return과 CAGR도 같은 개념으로 섞지 않는다.

## Numerical Materiality

별도 기준이 없으면 1% 미만 weight는 사용자 서술에서 numerical dust로 보고 `사실상 퇴출`로 취급할 수 있다.

Study 특성상 작은 비중도 중요한 경우에는 기준을 명시적으로 바꾼다.

---

# Narrative Compression 규칙

## 1. Report를 다시 읽어주지 않는다

```text
report.html = 정확한 표, 차트, 전체 숫자 확인
LLM text    = 구조, trade-off, 취약성, 효용, 안정성, 다음 실험
```

## 2. 숫자는 insight를 위해서만 사용한다

숫자는 가능하면 다음 질문 중 하나에 답해야 한다.

- 무엇과 비교해 다른가?
- 얼마나 큰 차이인가?
- 어떤 Risk / Return 위치인가?
- 그래서 무엇을 의미하는가?

맥락 없는 숫자는 삭제 후보로 본다.

## 3. Raw frontier point는 audit reference다

`point 29`, `point 55`를 주 설명 좌표로 사용하지 않는다.

사용자에게는 실제 Volatility / Expected Return / allocation 변화로 설명한다.

## 4. Frontier 위치는 사용자 목표와 연결한다

`왼쪽`, `초반`, `고수익 쪽`만으로 설명하지 않는다.

예:

> 이 자산은 Volatility를 10% 이하로 강하게 제한할 때만 필요하고, 12% 정도의 위험을 허용하면 frontier에서 빠진다.

## 5. 자산은 사람이 읽을 수 있게 쓴다

첫 등장 시 `자산명/성격 (Ticker)`를 기본으로 한다.

예:

- 금 현물 (GLD)
- 나스닥100 성장주 (QQQ)
- 미국 장기국채 (TLT)

## 6. Observation / Interpretation / Decision을 섞지 않는다

- **Observation**: artifact에서 직접 확인되는 사실
- **Interpretation**: 그 사실이 portfolio 구조에서 의미하는 것
- **Decision**: 다음 연구 또는 후보 판단

---

# 사용자 답변의 기본 Narrative

7단계를 그대로 7개 제목으로 출력할 필요는 없다.

일반적인 답변은 다음 순서가 자연스럽다.

1. **Executive Thesis**  
   가장 중요한 결과를 2~4문장으로 압축

2. **Portfolio Diagnosis**  
   현재 efficiency gap과 핵심 vulnerability

3. **Optimizer Structure**  
   optimizer가 발견한 core engine 조합과 최적화 후 남은 취약성

4. **주요 Asset Utility와 Allocation Range**  
   왜 필요한가, 얼마나 필요한가, 사용자의 목표에서 몇 %가 효율적이었는가

5. **Fragility / Confidence**  
   exact weight보다 stable range를 얼마나 믿을 수 있는가

6. **다음 Research**  
   현재 결론을 가장 크게 개선할 1~3개 후속 실험

Data Validity에 특별한 문제가 없으면 긴 validity 설명으로 시작하지 않는다. 짧게 확인하고 바로 insight로 이동한다.

---

# 최종 Self-Check

- [ ] 현재 포트의 Efficiency와 Vulnerability를 구분했는가?
- [ ] Optimized Portfolio 자체의 구조적 취약성도 확인했는가?
- [ ] Risk Concentration / Correlation Redundancy / Drawdown Co-failure / Return Dependence 중 실제로 중요한 것을 정량적으로 압축했는가?
- [ ] Optimizer가 발견한 core structure를 exact weight보다 먼저 설명했는가?
- [ ] 주요 자산에 대해 `왜 필요한가 / 얼마나 필요한가`를 설명했는가?
- [ ] 사용자 목표 Risk / Return에서 efficient allocation range를 해석했는가?
- [ ] 현재 Run만으로 그 범위를 충분히 식별할 수 없으면 target-risk 또는 target-return Run을 제안했는가?
- [ ] Frontier Fragility를 확인했는가?
- [ ] exact optimum보다 stable allocation range와 core structure를 우선했는가?
- [ ] diversifier importance를 correlation만이 아니라 가능하면 ablation으로 확인했는가?
- [ ] Missing Engine을 정성적으로 먼저 선언하지 않고 정량 취약성에서 출발했는가?
- [ ] binding constraint를 적정 비중으로 오해하지 않았는가?
- [ ] report 숫자를 반복하기보다 새로운 insight를 추가했는가?
- [ ] 남은 불확실성을 정보가치 높은 다음 실험으로 연결했는가?

---

# 핵심 원칙

> **Optimizer는 답을 주는 기계가 아니라 사용자의 Risk / Return 선택에 따라 portfolio 구조가 어떻게 변하는지 보여주는 실험 도구다. LLM은 `Portfolio Diagnosis -> Optimizer Structure -> Asset Utility -> Efficient Allocation Range -> Frontier Fragility -> Evidence Sufficiency & Robustness -> Next Research` 순서로 사고한다. 현재 포트와 optimized 포트의 효율성과 취약성을 정량적으로 진단하고, 각 자산이 왜·얼마나 필요한지, 사용자의 목표에서는 어느 정도 비중이 역사적으로 효율적이었는지 설명한다. 작은 조건 변화에 구조가 얼마나 흔들리는지 확인하고, 현재 결과만으로 답이 부족하면 사용자의 의사결정 질문에 직접 답하는 다음 실험을 설계한다.**