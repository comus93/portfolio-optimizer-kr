# 포트폴리오 최적화 결과 LLM 분석 프레임워크

## 목적

이 문서는 Portfolio Visualizer 또는 이에 준하는 포트폴리오 최적화 결과를 LLM이 **사용자 의사결정 관점에서 해석**하기 위한 기준이다.

LLM의 주된 가치는 report의 숫자를 다시 읽어주는 것이 아니다. 여러 표와 Efficient Frontier를 연결하여 다음 질문에 답하는 것이다.

> **현재 포트는 효율적인가? 어디가 취약한가? Optimizer는 어떤 구조를 발견했는가? 각 자산은 왜, 얼마나, 어느 위험/수익 목표에서 필요한가? 그 구조는 얼마나 안정적인가? 그리고 현재 evidence가 부족하다면 어떤 다음 실험이 필요한가?**

이 문서의 우선순위는 다음과 같다.

```text
사용자 질문
-> 정량적 insight
-> 구조적 해석
-> 필요한 supporting evidence
-> 부족한 evidence를 채우는 다음 실험
```

정성적 경제/regime 설명은 중요하지만 **정량 분석을 대체하지 않는다.** `주식이 많다`, `인플레이션 자산이 없다` 같은 일반론은 데이터에서 확인된 구조적 취약성을 설명하거나 다음 실험의 가설을 만들 때만 사용한다.

---

# 1. 사용자가 Optimization 결과에서 궁금한 질문

분석은 아래 질문 순서로 진행한다. 모든 항목을 억지로 채우지 말고 Study 질문에 중요한 것부터 답한다.

## 1.1 현재 포트는 효율적인가?

Provided Portfolio가 있으면 먼저 frontier 대비 **Efficiency Gap**을 본다.

가능하면 두 질문에 답한다.

1. 같은 Expected Return에서 frontier는 Volatility를 얼마나 낮출 수 있었는가?
2. 같은 Volatility에서 frontier는 Expected Return을 얼마나 높였는가?

예:

> 이 역사 표본에서 현재 포트의 Expected Return을 유지하면 frontier에서는 Volatility가 12.7%가 아니라 약 10.8%였다. 반대로 현재와 같은 12.7% Volatility를 허용하면 frontier Expected Return은 약 14.8%였다. 현재 포트는 frontier 안쪽에 상당한 efficiency gap이 있다.

이 값은 **현재 역사 표본과 추정치에서의 in-sample 효율성**이며 미래 달성 가능 수익으로 표현하지 않는다.

---

## 1.2 현재 포트는 어디가 취약한가?

Efficiency와 Robustness는 다르다. 현재 포트가 frontier에 가까워도 구조적 취약성이 있을 수 있다.

취약성은 가능한 한 **정량 evidence를 먼저 제시하고, 숫자는 핵심 1~3개만 사용해 의미를 압축한다.**

우선 검토축:

### Risk Concentration

- 특정 자산 또는 상관 cluster가 portfolio risk를 얼마나 지배하는가?
- Allocation weight와 Risk Contribution이 크게 다른가?
- 자산 수는 많지만 실제 risk source가 소수에 집중되는가?

좋은 해석:

> 명목상 5개 자산에 분산되어 있지만 portfolio risk의 대부분이 미국 성장주 cluster에서 발생한다. 따라서 자산 수보다 실제 위험 분산 정도가 낮다.

### Correlation Redundancy

Correlation matrix를 나열하지 않는다. 서로 높은 상관을 갖는 자산을 묶어 **실질적인 독립 움직임이 얼마나 되는지** 설명한다.

필요하면 correlation clustering, PCA/effective independent bets 같은 정량 분석을 후속 기능 또는 실험으로 제안할 수 있다.

### Drawdown Co-failure

평균 correlation이 낮아도 stress 구간에서 같이 무너질 수 있다.

가능하면 다음을 본다.

- 주요 drawdown에서 어떤 자산이 동시에 하락했는가
- worst-N months에서 동시 하락 비율
- stress 기간 conditional correlation
- portfolio drawdown에 가장 크게 기여한 자산/cluster

핵심 질문은 `평균적으로 분산되는가?`가 아니라 **`나쁜 시기에 실제로 분산되는가?`**다.

### Return Dependence

- 역사적 수익의 대부분이 한 자산/cluster에서 발생했는가?
- 해당 엔진이 약해질 경우 portfolio return 구조가 크게 흔들리는가?

Return Contribution이 있으면 allocation weight와 함께 본다.

---

## 1.3 Optimized Portfolio도 구조적으로 건전한가?

Optimizer는 **주어진 Asset Universe 안에서** 효율적인 조합을 찾을 뿐, universe 자체가 충분하거나 결과가 robust하다고 보장하지 않는다.

따라서 Optimized Portfolio에도 동일한 vulnerability 진단을 적용한다.

특히 본다.

- 최적화 후 Risk Concentration이 증가했는가?
- 서로 높은 상관의 자산이 동시에 큰 비중을 차지하는가?
- 안정성이 특정 diversifier 하나에 과도하게 의존하는가?
- drawdown protection이 특정 역사 구간에만 의존하는가?
- 작은 risk/return 조건 변화에도 allocation이 크게 뒤집히는가?

**`Efficient within universe`와 `Structurally robust`를 구분한다.**

---

# 2. Optimizer가 발견한 핵심 구조를 읽는다

Maximum Sharpe의 정확한 비중부터 설명하지 않는다.

먼저 묻는다.

> **여러 후보 중 실제 frontier를 만드는 핵심 자산 조합은 무엇인가?**

예:

> 이 표본의 optimizer는 여러 지역주식과 원자재를 함께 보유하는 구조보다 `미국 주식 return engine + 금 diversifier`라는 단순한 구조를 반복적으로 선택했다.

그 다음에야 exact weight, constraint, correlation 등을 근거로 붙인다.

### Constraint rule

최적 비중이 min/max와 같거나 solver tolerance 내에서 경계에 붙으면 그 비중을 `적정 비중`으로 해석하지 않는다.

```text
Role inference        = 강할 수 있음
Exact weight inference = 약함
```

한 점의 boundary touch보다 near-optimal 구간에서 계속 상한/하한에 붙는 **persistent pressure**를 더 중요하게 본다.

---

# 3. 각 자산은 `왜 / 얼마나 / 언제` 필요한가?

개별 자산 해석은 세 질문으로 통일한다.

## 3.1 왜 필요한가?  Role

- Return Engine
- Diversifier
- Low-risk Stabilizer
- Return Enhancer
- 대체 자산
- 현재 model에서 선택되지 않음

Role은 standalone Sharpe만으로 정하지 않고 frontier trajectory와 portfolio interaction으로 판단한다.

## 3.2 얼마나 필요한가?  Utility Magnitude

단순히 `선택됨 / 0%`가 아니라 portfolio 효용의 **크기**를 본다.

가능하면 다음 중 Study 질문에 가장 직접적인 것을 사용한다.

### 수익 기여

- Allocation 대비 Return Contribution
- 자산을 제거했을 때 동일 Volatility에서 Expected Return이 얼마나 감소하는가
- 더 높은 Return target에서 비중이 지속적으로 증가하는가

### 안정성 기여

- 자산을 제거했을 때 동일 Expected Return에서 Volatility가 얼마나 증가하는가
- Risk Contribution 대비 allocation이 효율적인가
- 주요 drawdown / downside / recovery가 개선되는가
- 낮은 risk budget으로 갈수록 비중이 증가하는가

### Breadth of Utility

- frontier의 넓은 위험구간에서 지속적으로 필요한가
- 특정 좁은 risk budget에서만 필요한가
- 아주 작은 비중으로만 등장하는가

필요성 강도는 다음처럼 해석할 수 있다.

- **Structural**: 넓은 risk/return 영역에서 반복적으로 필요
- **Target-dependent**: 특정 사용자 목표에서만 필요
- **Marginal**: 아주 좁은 영역 또는 작은 비중에서만 필요
- **Not selected in current model**: 현재 조건에서 frontier 효용이 확인되지 않음

`REDUNDANT`는 단순 0%가 아니라 **다른 자산이 같은 역할을 더 효율적으로 대체한다는 evidence가 있을 때만** 사용한다.

## 3.3 언제, 몇 %가 역사적으로 효율적이었나?  Efficient Allocation Range

Max Sharpe 한 점보다 **사용자의 목표 risk/return 구간에서 반복적으로 선택되는 비중 범위**를 우선한다.

예:

> 변동성 12~14%를 목표로 한 frontier 구간에서는 금이 대략 15~23% 범위에서 반복적으로 선택됐다. 따라서 Max Sharpe의 18.6% 한 점보다 `중간 risk budget에서 10%대 후반~20%대 초반`이라는 범위가 더 유용한 역사적 evidence다.

이 범위는 미래 적정 비중이 아니라 **현재 표본에서의 efficient allocation range**다.

---

# 4. Frontier를 사용자 목표의 메뉴판으로 해석한다

Efficient Frontier는 추상적인 곡선이 아니라 **사용자가 감수할 Risk와 원하는 Return에 따라 어떤 portfolio 구조가 역사적으로 효율적이었는지 보여주는 메뉴판**이다.

## 4.1 사용자에게 risk budget이 있으면 그 구간을 우선한다

예:

- Volatility 10~12%
- Volatility 12~14%
- 현재 포트와 비슷한 Volatility

이때 해당 frontier 구간에서:

- 각 자산의 비중 범위
- 어떤 자산이 새로 등장/퇴출하는지
- 추가 Return을 얻기 위해 무엇을 줄이는지
- risk concentration이 어떻게 바뀌는지

를 설명한다.

## 4.2 사용자에게 Return target이 있으면 같은 방식으로 본다

예:

- Expected Return 12~14%
- Expected Return 14~16%

해당 Return을 만들기 위해 필요한 Volatility와 allocation 변화를 본다.

## 4.3 현재 run만으로 충분하지 않으면 추가 실험을 제안한다

Frontier에서 대략적인 범위를 읽을 수 있어도 사용자의 실제 목표에 대한 evidence가 부족하면 거기서 멈추지 않는다.

예: 사용자가 Volatility 12~14%를 실제 risk budget으로 본다면 다음 run을 제안할 수 있다.

```text
Maximum Return @ Vol 12%
Maximum Return @ Vol 13%
Maximum Return @ Vol 14%
```

또는 Return target이 중요하면:

```text
Minimum Volatility @ Expected Return 12%
Minimum Volatility @ Expected Return 14%
Minimum Volatility @ Expected Return 16%
```

목적은 많은 sensitivity run을 만드는 것이 아니라 **사용자 목표 안에서 자산의 efficient allocation range를 더 정확하게 식별하는 것**이다.

---

# 5. Frontier Fragility를 반드시 본다

Frontier Fragility는 중요한 insight source다.

> **Risk 또는 Return 목표를 조금만 바꿨는데 portfolio allocation이 크게 바뀐다면, exact optimal weight는 불안정하다.**

반대로 넓은 목표 구간에서 특정 자산의 비중과 역할이 안정적이면 그 역할과 allocation range에 대한 신뢰는 높아진다.

## 5.1 어떻게 본다

Max Sharpe 한 점뿐 아니라 사용자가 관심 있는 risk/return 구간에서 인접한 efficient portfolios를 비교한다.

예:

```text
Vol 12.5% -> 13.0%
```

처럼 작은 위험 변화에서:

- 주요 자산 비중이 얼마나 움직이는가
- 새 자산이 갑자기 등장/퇴출하는가
- 상관 cluster 간 자금이 크게 이동하는가
- Sharpe/Expected Return 개선은 작은데 turnover는 큰가

를 본다.

필요하면 두 portfolio의 allocation 차이를 다음처럼 요약할 수 있다.

```text
Allocation Distance = 0.5 × Σ |weight_A - weight_B|
```

이는 두 efficient portfolios 사이에서 **전체 자산의 몇 %가 재배치되는지**를 직관적으로 보여준다.

절대 threshold를 기계적으로 적용하지 않는다. 핵심은 **작은 risk/return 변화 대비 allocation 변화가 큰지**다.

좋은 해석:

> Volatility를 0.5%p만 높였는데 portfolio의 약 25%가 다른 자산으로 재배치된다. Sharpe 차이는 거의 없으므로 exact optimum은 fragile하며, 특정 비중보다 공통으로 유지되는 core structure를 신뢰하는 편이 낫다.

또는:

> Volatility 12~14% 전 구간에서 금 비중은 17~22%에 머문다. 따라서 exact Max-Sharpe weight보다 `약 20% 내외의 안정적 역할`이 더 강한 evidence다.

---

# 6. Diversifier Dependency와 Leave-one-out 분석

특정 diversifier가 중요해 보인다면 단순 correlation보다 **그 자산이 없을 때 portfolio가 얼마나 악화되는지**가 더 직접적인 evidence다.

후속 ablation 또는 새 Experiment로 자산을 하나씩 제거해 다음을 비교한다.

- 동일 Expected Return에서 Δ Volatility
- 동일 Volatility에서 Δ Expected Return
- Δ Max Sharpe
- drawdown / recovery 변화
- risk concentration 변화

예:

> 금을 제거하면 같은 Expected Return을 유지하는 데 필요한 Volatility가 1.6%p 상승했다. 현재 구조의 안정성이 금 하나에 상당 부분 의존하고 있다는 정량 evidence다.

이 결과가 있을 때만 `single-diversifier dependency` 같은 구조적 취약성을 강하게 말한다.

---

# 7. 정량 취약점에서 Missing Engine 가설로 이동한다

Missing Engine은 **정성 체크리스트로 먼저 선언하지 않는다.**

순서는 반드시 다음과 같다.

```text
정량적 취약성 발견
-> 구조적 문제 정의
-> 가능한 경제적 원인/대체 엔진 가설
-> 새 Asset Universe 실험
-> 실제 frontier 개선 여부 검증
```

예:

> 최적화 후에도 risk의 대부분이 한 equity cluster에 집중되고, portfolio 안정성은 단일 diversifier에 크게 의존한다. 이는 추가적인 독립 수익/위험 엔진을 시험할 필요성을 시사한다.

여기까지는 데이터 기반 결론이다.

그 다음 `어떤 자산군을 후보로 시험할 것인가`는 경제적 가설이며, 실제로 추가했을 때:

- 기존 concentration이 낮아지는가
- diversifier dependency가 줄어드는가
- 동일 risk에서 return이 개선되는가
- 동일 return에서 risk가 줄어드는가

를 새 Experiment로 검증한다.

`원자재가 없으니 원자재를 넣어야 한다`처럼 범용 자산배분 상식만으로 결론내리지 않는다.

---

# 8. Supporting Evidence는 이유를 설명할 때만 사용한다

## Correlation + Return + Volatility

낮은 correlation 자체를 좋은 자산의 증거로 사용하지 않는다. 낮은 상관을 얻기 위해 얼마의 낮은 return 또는 높은 volatility를 감수하는지 함께 본다.

## Return / Risk Contribution

Allocation weight와 contribution의 불균형을 통해 숨은 return dependence 또는 risk concentration을 찾는다.

## Drawdown / Recovery

MDD 깊이뿐 아니라 recovery/underwater 기간, 주요 자산의 동시 하락 여부를 본다.

## Rolling Return

Rolling 3Y/5Y Low 등으로 full-period 결과가 특정 시기에 과도하게 의존하는지 본다.

## Regime / Annual Return

정량 구조를 설명하기 위한 보조 evidence다. 데이터로 확인되지 않은 경제적 라벨을 먼저 붙이지 않는다.

---

# 9. 결과를 얼마나 믿을 수 있는가?

역할과 비중의 신뢰를 분리한다.

| 구분 | 의미 |
|---|---|
| **Role Confidence** | 이 자산이 어떤 portfolio 역할을 하는지 얼마나 명확한가 |
| **Weight Confidence** | exact weight 또는 efficient range를 얼마나 신뢰할 수 있는가 |

Weight Confidence는 다음 경우 낮춘다.

- min/max constraint binding
- Frontier Fragility가 큼
- near-efficient 구간에서 비중이 크게 흔들림
- 기간/objective 변경 시 exact weight가 크게 변함
- material threshold 근처에서만 존재

Role은 안정적이지만 Weight Confidence가 낮은 것은 정상이다.

---

# 10. Evidence가 부족하면 다음 실험을 설계한다

LLM은 optimizer 결과의 수동 해설자가 아니라 **research analyst**다.

현재 run으로 사용자의 질문에 충분히 답하지 못하면 다음 실험을 제안한다.

좋은 후속 실험은 다음 네 요소를 가진다.

```text
Uncertainty : 무엇을 아직 모르는가
Manipulation: 무엇만 바꾸는가
Observation : 어떤 결과를 볼 것인가
Decision    : 어떤 결과면 현재 해석이 강화/약화되는가
```

대표 유형:

1. **Target-risk runs**  
   사용자 risk budget에서 efficient allocation range를 확인

2. **Target-return runs**  
   원하는 return을 위한 minimum risk와 구성 확인

3. **Constraint sensitivity**  
   binding cap/floor가 결과를 얼마나 왜곡하는지 확인

4. **Leave-one-out / ablation**  
   특정 자산의 marginal utility와 diversifier dependency 확인

5. **Universe expansion**  
   정량적으로 확인된 구조적 취약성을 다른 독립 엔진이 실제로 개선하는지 확인

6. **Period / objective robustness**  
   역할과 allocation range가 표본이나 objective에 과도하게 의존하는지 확인

실험을 많이 제안하지 않는다. **사용자 의사결정을 가장 크게 바꿀 수 있는 불확실성부터 1~3개**만 우선한다.

---

# 11. 사용자에게 전달하는 기본 순서

1. **Executive Thesis**  
   지금 결과에서 가장 중요한 구조 2~4문장

2. **현재 Portfolio의 Efficiency Gap**  
   같은 Return / 같은 Risk에서 얼마나 frontier 안쪽인가

3. **현재 Portfolio의 Quantitative Vulnerability**  
   risk concentration, redundancy, drawdown co-failure, return dependence 중 핵심만

4. **Optimizer가 발견한 Core Structure**  
   exact weight보다 어떤 엔진 조합이 반복적으로 선택되는가

5. **Optimized Portfolio의 구조적 취약성**  
   concentration, diversifier dependency, frontier fragility

6. **주요 자산의 Why / How much / When**  
   왜 필요한가, 얼마나 기여하는가, 어떤 risk/return 목표에서 어느 정도 비중이 효율적이었는가

7. **Stable Range와 Frontier Fragility**  
   exact optimum을 얼마나 믿어야 하는가

8. **남은 불확실성과 다음 실험**

Data Validity에 문제가 없으면 긴 validity 설명으로 시작하지 않는다. 짧게 확인하고 바로 insight로 이동한다.

---

# 12. Narrative Compression 규칙

## 숫자는 report가 아니라 insight를 위해 사용한다

- 이미 report에 있는 표 전체를 다시 출력하지 않는다.
- 한 문장에 숫자를 많이 넣지 않는다.
- 숫자는 `무엇과 비교해`, `얼마나 다른지`, `그래서 무엇을 의미하는지`가 있을 때만 사용한다.

## Raw frontier point는 audit reference다

`point 29`, `point 55`를 주 설명 좌표로 사용하지 않는다.

사용자에게는 실제 Volatility / Expected Return 목표와 allocation 변화를 설명한다.

## 자산은 사람이 읽을 수 있게 쓴다

첫 등장 시 `자산명/성격 (Ticker)`를 쓴다.

예:

- 금 현물 (GLD)
- 나스닥100 성장주 (QQQ)
- 미국 장기국채 (TLT)

## Numerical dust를 과해석하지 않는다

별도 기준이 없으면 1% 미만 비중은 사용자 서술에서 `사실상 퇴출`로 취급할 수 있다.

## Observation / Interpretation / Decision을 섞지 않는다

- **Observation**: 데이터에서 직접 확인
- **Interpretation**: portfolio 구조에서 의미
- **Decision**: 다음 연구 또는 후보 판단

---

# 13. Run Identity / Data Validity Guardrail

사용자 중심 분석을 하기 전에 현재 run이 맞는지 최소한 확인한다.

- run_id
- asset universe
- provided portfolio
- benchmark
- objective
- risk-free convention
- rebalancing
- constraints
- analysis period

Repository 기반 시스템에서는 `LLM-README.md`의 canonical source priority를 따른다.

```text
1. result.json
2. review/*.csv
3. 필요한 경우 raw/*.csv
```

다른 run의 분석문이나 과거 대화 숫자를 현재 run과 자동으로 섞지 않는다.

Data 문제는:

- **Blocking**: optimizer input/frontier 자체가 바뀔 수 있음
- **Reporting**: 일부 비교/report만 오염

으로 구분하고 영향을 받는 결론 범위를 명시한다.

---

# 최종 Self-Check

- [ ] report 숫자를 반복하는 대신 사용자의 질문에 답했는가?
- [ ] 현재 portfolio의 efficiency와 vulnerability를 구분했는가?
- [ ] optimized portfolio 자체의 구조적 취약성도 확인했는가?
- [ ] Risk Concentration / Correlation Redundancy / Drawdown Co-failure / Return Dependence 중 중요한 것을 정량적으로 압축했는가?
- [ ] 각 주요 자산에 대해 `왜 필요한가 / 얼마나 필요한가 / 언제 몇 %가 효율적이었나`를 설명했는가?
- [ ] 사용자 risk/return 목표에서 필요한 evidence가 부족하면 target-risk/target-return run을 제안했는가?
- [ ] Frontier Fragility를 확인했는가?
- [ ] exact optimum보다 stable allocation range와 core structure를 우선했는가?
- [ ] diversifier importance를 correlation만이 아니라 가능하면 ablation으로 확인했는가?
- [ ] Missing Engine을 정성적으로 먼저 선언하지 않고 정량 취약성에서 출발했는가?
- [ ] binding constraint를 적정 비중으로 오해하지 않았는가?
- [ ] 남은 불확실성을 정보가치 높은 다음 실험으로 연결했는가?

---

# 핵심 원칙

> **Optimizer는 답을 주는 기계가 아니라 사용자의 risk/return 선택에 따라 portfolio 구조가 어떻게 변하는지 보여주는 실험 도구다. LLM의 역할은 현재 포트와 optimized 포트의 효율성과 취약성을 정량적으로 진단하고, 각 자산이 왜·얼마나·언제 필요한지 설명하며, 작은 조건 변화에 구조가 얼마나 흔들리는지까지 읽어내는 것이다. 현재 결과만으로 답이 부족하면 사용자의 목표에 직접 답하는 다음 실험을 설계한다.**
