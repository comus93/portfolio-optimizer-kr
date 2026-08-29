# LLM ↔ User Research Input Contract

## 목적

이 문서는 LLM과 사용자가 포트폴리오 최적화 연구를 시작할 때, 실제 Experiment를 만들고 실행하기 전에 **무엇을 사용자에게 물어야 하고 무엇을 시스템이 스스로 결정해야 하는지** 정의한다.

핵심 원칙은 다음과 같다.

> **YAML에 존재하는 값과 사용자가 결정해야 하는 값은 다르다. LLM은 사용자의 투자/연구 의사결정은 사용자에게 확인하고, project default와 구현 세부사항은 시스템이 흡수한다.**

또한 사용자에게 질문할 때는 내부 field 이름이나 optimizer 용어를 그대로 노출하기보다 **투자자가 이해하기 쉬운 자연어로 번역해서 묻는다.**

이 문서는 optimizer의 금융 계산 규칙이 아니라 **연구 실행 전 사용자-LLM 상호작용 계약**이다.

---

## 1. Conversation Protocol

사용자가 포트폴리오 구성이나 분석을 요청하면 LLM은 아래 순서로 응대한다.

### Step 1. 사용자에게서 이미 받은 정보를 먼저 추출한다

다음 항목을 대화에서 우선 복원한다.

```text
Asset Universe
Provided Portfolio weights
각 자산의 비중 허용 범위
Optimization Goal
Target Volatility (해당 시)
Analysis Period (사용자 지정이 있을 때)
Rebalancing (사용자 지정이 있을 때)
Benchmark (사용자 지정이 있을 때)
Risk-free convention (사용자 지정이 있을 때)
```

이미 대화에서 나온 값은 다시 묻지 않는다.

### Step 2. 기계적으로 검증 가능한 것은 LLM이 먼저 검증한다

예:

```text
- ticker가 명확한가
- Provided weights 합이 100%인가
- 같은 자산이 중복 입력됐는가
- target-vol objective인데 target vol이 빠졌는가
- 사용자가 정한 비중 제한이 서로 모순되지 않는가
```

기계적으로 판단 가능한 것을 사용자에게 되묻지 않는다.

### Step 3. 아래 질문표에 따라 실제로 물어볼 항목만 남긴다

| 항목 | 언제 질문하는가 | 언제 질문하지 않는가 |
|---|---|---|
| Asset Universe | 자산/티커가 모호하거나 후보 중 선택이 필요할 때 | 종목이 이미 명확할 때 |
| Provided weights | 사용자가 현재 포트폴리오 비교를 원하지만 비중이 빠졌을 때 | 비중이 이미 있거나 Provided Portfolio 자체가 필요 없는 연구일 때 |
| **비중 제한** | **실행 전에 아직 정해지지 않았을 때 반드시 질문한다** | 사용자가 이미 각 자산의 최소/최대 허용 범위를 정했을 때 |
| Optimization Goal | 사용자 의도에서 목표를 결정할 수 없고 canonical default가 없을 때 | 목표가 이미 명시됐을 때 |
| Target Volatility | 변동성 한도 안에서 수익 최대화를 선택했는데 한도가 없을 때 | Maximum Sharpe이거나 값이 이미 있을 때 |
| Analysis Period | 특정 기간 비교/국면 연구를 요청했는데 기간이 불명확할 때 | 일반 분석이면 common-overlap default 사용 |
| Rebalancing | 사용자가 월/연 리밸런싱 차이를 연구하려고 하는데 선택이 없을 때 | 일반 분석이면 canonical default 사용 |
| Benchmark | benchmark-relative 질문인데 기준지수가 불명확할 때 | benchmark가 필요 없는 연구이거나 사용자가 이미 지정했을 때 |
| Risk-free | 특정 convention 비교가 연구 질문일 때 | 일반 분석이면 canonical default 사용 |

**비중 제한은 optimizer 결과와 자산의 역할을 직접 바꾸는 투자 의사결정이므로 LLM이 임의로 정하지 않는다.**

Specification의 `0~100%` asset bound는 계산 엔진이 유효한 입력을 받기 위한 fallback 범위이지, Research Frontend가 사용자의 투자 제약을 대신 결정해도 된다는 의미가 아니다.

사용자가 명시적으로 `제약 없이`, `비중 제한 없음`이라고 하면 그 의도를 `0~100% 허용`으로 해석할 수 있다.

**이 표에 없는 system/internal parameter는 정상적인 Research Frontend 흐름에서 질문하지 않는다.**

### Step 4. 남은 질문만 한 번에, 자연어로 묻는다

질문의 개수를 채우지 않는다.

내부 용어를 그대로 읽어주는 식으로 묻지 않는다.

나쁜 예:

```text
각 ticker의 min_weight와 max_weight를 지정해줘.
Optimization objective와 target annual volatility를 선택해줘.
```

좋은 예:

```text
종목과 현재 비중은 정해졌어.
두 가지만 정하면 돼.

1. 비중 제한
   - 0%까지 빠져도 되는 자산이 있는지
   - 한 자산이 최대 몇 %까지 커져도 되는지
   모두 같은 제한을 써도 되고 자산별로 달라도 돼.

2. 무엇을 최우선으로 볼지
   - 변동성 대비 기대수익이 좋은 조합 (Sharpe 지수)
   - 허용한 변동성 안에서 기대수익이 가장 높은 조합
```

두 번째를 선택했을 때만 다음처럼 추가로 묻는다.

```text
연간 변동성은 최대 몇 %까지 허용할까?
```

이 상황에서 다음을 추가로 묻지 않는다.

```text
analysis period
rebalancing
risk-free
frontier resolution
solver
benchmark가 필요하지 않은 경우 benchmark
```

### Step 5. 사용자가 실행 의도를 이미 밝혔다면 다시 승인받지 않는다

사용자가 다음과 같이 말한 경우:

```text
분석해
돌려줘
최적화해줘
실행해
```

이는 실행 의도로 본다.

필수 User Research Decision이 모두 해결되면 짧은 sanity-check 요약 후 `진행할까?`를 다시 묻지 않고 바로 실행한다.

---

## 2. User Decision Boundary

모든 입력값을 사용자 질문으로 승격시키지 않는다.

LLM은 입력을 다음 세 범주로 분류한다.

### A. User Research Decision

다음 중 연구 결과와 실제 투자 해석을 직접 바꾸는 값은 사용자 결정으로 취급한다.

- 어떤 자산을 연구 대상으로 포함할지
- 사용자가 비교하려는 현재 포트폴리오 비중
- **각 자산의 최소/최대 허용 비중**
- canonical default가 없는 optimization objective
- target-volatility objective의 target annual volatility
- 사용자가 특정 기간 비교를 요구한 경우의 analysis period

이미 대화에서 결정된 값은 다시 묻지 않는다.

특히 **비중 제한은 canonical engine fallback이 존재하더라도 사용자 결정을 생략하지 않는다.** 상한 하나만 달라져도 frontier, 최적 비중, 자산의 역할 해석이 크게 바뀔 수 있기 때문이다.

### B. Canonical Project Default

프로젝트가 specification 또는 contract에 default를 정의했고 사용자 의사결정을 대신하지 않는 값은, 사용자가 별도로 지정하지 않으면 LLM이 자동 적용한다.

default가 존재한다는 이유로 다시 승인받지 않는다.

예:

- return frequency
- 기본 rebalancing convention
- risk-free convention
- analysis-period default
- 기타 연구 질문 자체를 바꾸지 않는 canonical default

해당 default가 결과 해석에 중요하면 실행 직전 요약이나 결과 설명에서 짧게 알릴 수 있다. 그러나 단순한 확인 질문으로 사용자 흐름을 막지 않는다.

### C. System / Implementation Decision

연구 질문 자체가 아니라 계산 품질, 실행 방식, 저장, 수치해석, 출력 생성 등을 위한 내부 파라미터는 시스템 책임이다.

정상적인 Research Frontend 흐름에서는 사용자에게 선택을 요구하지 않는다.

예:

- solver 선택
- numerical tolerance
- sampling / resolution 성격의 내부 파라미터
- run_id 생성
- output path
- GitHub Actions plumbing
- cache / retry / concurrency
- report generation detail

이러한 값이 사용자에게 노출되어 있다는 이유만으로 사용자 결정값이 되지 않는다.

### 핵심 판정 순서

LLM이 어떤 값을 사용자에게 물을지 고민될 때 다음 순서로 판정한다.

```text
1. 사용자가 이미 정했거나 대화에서 명확한가?
   -> 그렇다면 묻지 않는다.

2. 투자/연구 의사결정인가?
   -> 그렇다면 사용자에게 묻는다.
   -> 특히 자산별 비중 제한은 여기에 속한다.

3. 사용자 결정을 대신하지 않는 canonical project default인가?
   -> 그렇다면 적용하고 묻지 않는다.

4. 시스템/구현 품질을 위한 내부 파라미터인가?
   -> 그렇다면 시스템이 결정하고 묻지 않는다.
```

---

## 3. 주요 Research Input 처리 규칙

### 3.1 연구 대상 자산과 현재 비중

각 자산에 대해 최소한 ticker를 확인한다.

가능하면 다음도 함께 사용한다.

- 자산명
- 통화
- 기존 portfolio 비중

사용자가 기존 비중을 제공하면 합계가 100%인지 확인한다.

기존 비중은 optimizer의 제약 조건이 아니라 **Provided Portfolio baseline**으로 취급한다.

### 3.2 비중 제한

실제 optimization run 전에 각 자산의 허용 비중 범위를 사용자 의도에 따라 확정한다.

사용자에게는 `min_weight`, `max_weight`, `constraint` 같은 내부 용어보다 다음처럼 묻는다.

> **각 자산 비중에 제한을 어떻게 둘까? 0%까지 빠져도 되는지, 그리고 최대 몇 %까지 허용할지 정해줘. 모두 같은 상한을 써도 되고 자산별로 달라도 돼.**

사용자가 최소 비중을 따로 요구하지 않고 `0%까지 빠져도 된다`고 하면 최소 비중은 0%로 해석한다.

사용자가 `모두 최대 30%`라고 하면 모든 자산의 최대 비중을 30%로 해석한다.

사용자가 자산별로 다른 제한을 주면 그대로 반영한다.

LLM은 자산의 성격을 근거로 `주식 50%, 금 30%` 같은 제한을 임의 생성하지 않는다. 그런 값은 제안할 수는 있지만, 사용자가 선택하기 전에는 실행 조건으로 확정하지 않는다.

### 3.3 Optimization Goal

Optimization objective는 연구 결론을 직접 바꾸는 값이다.

사용자가 이미 목적을 명시했다면 다시 묻지 않는다.

사용자에게는 내부 objective 이름만 던지기보다 의미를 먼저 설명한다.

```text
- 변동성 대비 기대수익이 좋은 조합 (Sharpe 지수)
  = Maximum Sharpe

- 내가 허용한 변동성 안에서 기대수익이 가장 높은 조합
  = Maximum Return at Target Volatility
```

**사용자-facing 대화에서는 위 자연어 표현을 먼저 사용하고, `Maximum Sharpe` 같은 내부/전문 용어는 필요할 때 괄호나 보조 설명으로만 붙인다.**

두 번째를 선택하면 허용할 연환산 변동성 상한이 추가 User Research Decision이다.

그 값이 정해지지 않은 상태에서 LLM이 임의의 숫자를 넣지 않는다.

### 3.4 Rebalancing

사용자가 rebalancing을 지정하면 그 값을 사용한다.

지정하지 않았고 specification에 canonical default가 있으면 default를 자동 적용한다.

특정 연구 질문이 monthly vs yearly 차이 자체를 비교하는 경우에만 별도 연구 의사결정으로 올린다.

### 3.5 Analysis Period

사용자가 시작일/종료일을 지정하면 그 기간을 우선한다.

사용자가 별도 기간을 지정하지 않으면 project default인 **optimizer universe의 모든 자산에 유효한 데이터가 존재하는 공통 교집합 전체 기간**을 자동 적용한다.

기간 미지정은 미확정 상태가 아니다.

LLM은 generic research flow에서 단순히 기간을 지정하지 않았다는 이유로 질문을 만들지 않는다.

다만 사용자가 특정 시장 국면, 동일 기간 비교, listing-history 통제 등 기간 선택 자체가 연구 질문인 요청을 했다면 User Research Decision으로 취급한다.

실행 후에는 실제 data coverage의 시작일, 종료일, observation 수를 보고한다.

특정 자산의 짧은 history 때문에 공통 분석 기간이 크게 줄어들면 결과 해석에서 반드시 별도로 보고한다.

### 3.6 Benchmark

Benchmark는 optional input이다.

사용자가 benchmark를 지정하면 사용한다.

지정하지 않은 경우 benchmark-relative 분석이 연구 질문에 필수적이지 않다면 benchmark 선택을 사용자 질문으로 만들지 않는다.

연구 목적상 benchmark가 반드시 필요한데 후보에 따라 해석이 실질적으로 달라지고 합리적 default도 없다면 그때만 사용자에게 묻는다.

### 3.7 Risk-free Rate

사용자가 별도 convention을 요구하지 않으면 specification의 canonical default를 적용한다.

PV parity 등 특정 외부 결과와 직접 비교하는 연구라면 비교 목적에 맞는 convention이 필요한지 확인하고 그 사실을 결과에 명시한다.

---

## 4. LLM의 질문 방식

사용자가 이미 제공한 정보를 다시 묻지 않는다.

**질문의 수를 채우지 않는다.** 미해결 User Research Decision이 하나뿐이면 하나만 묻는다.

여러 개가 정말 미해결이면 한 번에 묶어서 간결하게 질문한다.

질문은 사용자 언어를 우선한다.

```text
내부 용어                사용자에게 우선할 표현
min/max constraint       비중을 최소/최대 어디까지 허용할지
optimization objective   무엇을 최우선으로 볼지
target annual volatility 연간 변동성을 어디까지 허용할지
common overlap period    모든 자산 데이터가 함께 있는 전체 기간
Maximum Sharpe           변동성 대비 기대수익이 좋은 조합 (Sharpe 지수)
```

필요하면 익숙한 표현 뒤에 기술 용어를 괄호로 붙일 수 있지만, 기술 용어 자체를 이해해야만 답할 수 있는 질문을 만들지 않는다.

다음은 금지되는 패턴이다.

```text
- specification의 입력 필드를 그대로 사용자에게 나열
- 내부 field 이름으로만 질문
- project default가 있는 시스템 값을 다시 선택하게 함
- 내부 구현/품질 파라미터를 사용자 설정처럼 제시
- sanity-check 요약을 승인 절차로 변환
- 이미 대화에서 명확해진 값을 다시 확인
```

좋은 질문은 다음 특성을 가진다.

```text
- 사용자가 투자 관점에서 바로 이해할 수 있다.
- 답에 따라 연구 의미가 실제로 달라진다.
- 시스템이 대신 결정해서는 안 되는 값이다.
```

---

## 5. Execution Gate

정식 실행 전에 필요한 것은 **모든 YAML 필드에 대한 사용자 승인**이 아니라, 모든 User Research Decision이 해소되어 있는지 여부다.

최소한 다음을 확인한다.

- Asset universe가 확정 또는 현재 요청에서 명확히 복원됨
- Provided Portfolio가 필요한 경우 확정되고 합계가 검증됨
- **각 자산의 비중 허용 범위가 사용자 의도로 확정됨**
- Optimization Goal이 사용자 의도 또는 명시적 선택으로 결정됨
- Target Volatility objective라면 허용 annual volatility가 결정됨
- 나머지 값은 사용자 지정값 또는 canonical default로 resolve됨

미해결 User Research Decision이 있으면 Experiment YAML을 초안으로 작성할 수는 있지만 `run: true`로 실행하지 않는다.

반대로 모든 User Research Decision이 해결되어 있고 나머지가 canonical default 또는 system decision으로 resolve된다면 **추가 승인 질문 없이 실행 단계로 진행할 수 있다.**

정식 실행 시 LLM은 필요한 Experiment 변경을 먼저 저장한 뒤 다음 형태로 실행을 요청한다.

```yaml
target: studies/<study-id>/experiments/<experiment>.yaml
run: true
```

`run: true`는 한 번의 실행 의도이며, 성공한 요청은 GitHub Actions가 안전하게 `run: false`로 consume한다.

정식 실행 경로는 `docs/research-operation-pipeline.md`를 따른다.

---

## 6. 실행 직전 LLM 요약

사용자가 별도로 요구하지 않는 한 장황한 승인 절차를 만들지 않는다.

실행 직전 요약은 **permission request가 아니라 sanity check**다.

사용자가 이미 `분석해`, `돌려줘`, `실행해`처럼 실행 의도를 명시했고 미해결 User Research Decision이 없다면 요약 후 다시 `진행할까?`라고 묻지 않는다. 바로 실행한다.

요약에는 연구 의미를 이해하는 데 필요한 항목만 넣는다.

예:

```text
Asset Universe / Provided Portfolio
각 자산의 비중 제한
Optimization Goal
사용자 지정 Analysis Period가 있으면 해당 기간
연구 해석에 중요한 benchmark 또는 non-default convention
```

다음은 일반적인 실행 요약에서 굳이 사용자에게 노출하지 않아도 된다.

```text
system-generated ID
저장 경로
solver / tolerance
내부 sampling / resolution
workflow plumbing
기타 연구 의미를 바꾸지 않는 implementation detail
```

---

## 7. Guiding Rule

Research Frontend의 목표는 **사용자가 optimizer UI의 모든 옵션을 직접 조작하게 만드는 것**이 아니다.

LLM은 사용자의 자연어 연구 의도를 canonical system input으로 번역하는 frontend다.

따라서 기본 행동은 다음과 같다.

> **사용자에게는 투자/연구 의사결정만 남기고, 그 질문도 투자자가 이해하기 쉬운 언어로 묻는다. project default와 구현 세부사항은 시스템이 흡수한다.**

비중 제한처럼 optimizer 결과를 직접 제약하는 투자 판단은 LLM이 임의로 채우지 않는다.

반대로 solver, sampling resolution, run ID처럼 연구 의도와 무관한 구현 세부사항은 사용자에게 떠넘기지 않는다.