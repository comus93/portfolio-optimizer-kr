# LLM ↔ User Research Input Contract

## 목적

이 문서는 LLM이 사용자와 포트폴리오 연구를 시작할 때 **무엇을 물어보고, 무엇을 고지하고, 무엇을 시스템 default로 처리할지** 정의한다.

핵심 원칙:

> **사용자의 투자/연구 의사결정은 사용자에게 확인한다. Canonical default가 있는 값은 선택 질문으로 만들지 않고 기본값과 변경 가능성을 고지한 뒤 실행 입력에 명시적으로 기록한다. 구현 세부사항은 시스템이 책임진다.**

사용자-facing 대화에서는 내부 YAML field나 optimizer 전문용어보다 투자자가 바로 이해할 수 있는 표현을 먼저 사용한다.

이 문서는 금융 계산 공식을 정의하는 문서가 아니라 **Research Frontend의 사용자 응대와 실행 입력 생성 계약**이다.

---

## 1. Conversation Protocol

사용자가 포트폴리오 구성, 비교, 최적화, 분석을 요청하면 아래 순서로 응대한다.

### Step 1. 이미 받은 정보를 먼저 추출한다

대화에서 다음 정보를 복원한다.

```text
Asset Universe
Provided Portfolio weights
각 자산의 비중 허용 범위
Optimization Goal
Target Volatility (해당 시)
Analysis Period (사용자 지정이 있을 때)
Rebalancing (사용자 지정이 있을 때)
Benchmark override (사용자 지정이 있을 때)
Risk-free override (사용자 지정이 있을 때)
```

이미 결정된 값은 다시 묻지 않는다.

### Step 2. 기계적으로 검증 가능한 것은 LLM이 먼저 검증한다

예:

```text
- ticker가 명확한가
- Provided weights 합이 100%인가
- 같은 자산이 중복됐는가
- target-volatility 방식인데 허용 변동성이 빠졌는가
- 사용자가 지정한 비중 제한이 서로 모순되지 않는가
```

기계적으로 판단 가능한 것을 사용자에게 되묻지 않는다.

### Step 3. 사용자에게 물어야 할 항목과 고지만 하면 되는 항목을 구분한다

| 항목 | 사용자에게 질문 | 질문하지 않고 처리 |
|---|---|---|
| Asset Universe | 자산/티커가 모호하거나 후보 선택이 필요할 때 | 이미 명확하면 그대로 사용 |
| Provided weights | 현재 포트폴리오 비교가 필요한데 비중이 빠졌을 때 | 이미 있으면 합계만 검증 |
| **비중 제한** | **실행 전에 아직 정해지지 않았다면 반드시 질문** | 사용자가 최소/최대 허용 범위를 이미 정했을 때 |
| Optimization Goal | 사용자 의도에서 목표가 결정되지 않았을 때 | 이미 명시됐을 때 |
| Target Volatility | 허용 변동성 내 최대수익 방식을 선택했는데 한도가 없을 때 | Sharpe 방식이거나 값이 이미 있을 때 |
| Analysis Period | 특정 기간/국면 자체가 연구 조건인데 불명확할 때 | 일반 분석은 모든 자산 데이터가 함께 있는 전체 기간 사용 |
| Rebalancing | 월/연 리밸런싱 차이 자체를 연구할 때 | 일반 분석은 canonical default 사용 |
| **Benchmark** | 사용자가 기본 비교대상을 바꾸고 싶지만 대상이 불명확할 때 | **기본 S&P 500(SPY)를 사용하고 변경 가능하다고 고지** |
| Risk-free | 특정 convention 비교가 연구 질문일 때 | 일반 분석은 canonical default 사용 |

### Step 4. 남은 질문만 한 번에 자연어로 묻는다

질문의 수를 채우지 않는다.

나쁜 예:

```text
각 ticker의 min_weight와 max_weight를 지정해줘.
Optimization objective와 target annual volatility를 선택해줘.
Benchmark symbol을 입력해줘.
```

좋은 예:

```text
종목과 현재 비중은 정해졌어. 두 가지만 정하면 돼.

1. 각 자산 비중을 어디까지 허용할지
   - 0%까지 빠져도 되는지
   - 한 자산이 최대 몇 %까지 커져도 되는지
   모두 같은 제한을 써도 되고 자산별로 달라도 돼.

2. 무엇을 최우선으로 볼지
   - 변동성 대비 기대수익이 좋은 조합 (Sharpe 지수)
   - 허용한 변동성 안에서 기대수익이 가장 높은 조합

비교대상은 기본적으로 S&P 500(SPY)으로 둘게. 다른 지수나 ETF와 비교하고 싶으면 바꿀 수 있어.
```

두 번째 최적화 방식을 선택했을 때만 추가로 묻는다.

```text
연간 변동성은 최대 몇 %까지 허용할까?
```

### Step 5. 실행 의도를 이미 밝혔다면 다시 승인받지 않는다

다음 표현은 실행 의도로 본다.

```text
분석해
돌려줘
최적화해줘
실행해
```

필수 User Research Decision이 모두 해소되면 짧게 조건을 요약한 뒤 `진행할까?`를 다시 묻지 않고 실행한다.

---

## 2. User Decision Boundary

### A. User Research Decision

다음은 결과와 투자 해석을 직접 바꾸므로 사용자 결정으로 취급한다.

- 어떤 자산을 포함할지
- 현재 포트폴리오 비중
- **각 자산의 최소/최대 허용 비중**
- 어떤 최적화 방향을 볼지
- target-volatility 방식의 허용 연간 변동성
- 특정 기간 자체가 연구 질문일 때의 analysis period
- 사용자가 기본 benchmark를 변경하려는 경우의 비교대상

이미 대화에서 결정된 값은 다시 묻지 않는다.

특히 비중 제한은 엔진 fallback이 존재하더라도 LLM이 임의로 정하지 않는다.

사용자가 `제약 없이` 또는 `비중 제한 없음`이라고 하면 `0~100% 허용`으로 해석할 수 있다.

### B. Canonical Project Default

프로젝트에 기본값이 있고 사용자의 투자 판단을 대신하지 않는 값은 **기본값과 필요시 변경 가능성을 고지하고 자동 적용**한다.

대표값:

```text
Benchmark                 = S&P 500 (SPY)
Analysis Period           = 모든 optimization asset의 공통 유효기간 전체
Portfolio Rebalancing     = Monthly
Risk-free                 = U.S. 3-Month T-Bill convention
Return Frequency          = Monthly
```

Default가 있다는 이유로 별도 승인 질문을 만들지 않는다.

### C. System / Implementation Decision

다음은 사용자 선택 항목이 아니다.

```text
solver
numerical tolerance
frontier sampling/resolution
run_id
output path
GitHub Actions plumbing
cache/retry/concurrency
report generation detail
```

정상적인 Research Frontend 흐름에서는 묻지 않는다.

---

## 3. 주요 Research Input 처리 규칙

### 3.1 연구 대상 자산과 현재 비중

각 자산의 ticker를 확인한다.

가능하면 자산명과 통화도 함께 기록한다.

Provided weights가 있으면 합계 100%를 검증한다.

Provided Portfolio는 optimizer 제약이 아니라 비교 baseline이다.

### 3.2 비중 제한

실행 전에 사용자 의도에 따라 각 자산의 허용 범위를 확정한다.

사용자에게는 다음처럼 묻는다.

> **각 자산 비중에 제한을 어떻게 둘까? 0%까지 빠져도 되는지, 그리고 최대 몇 %까지 허용할지 정해줘. 모두 같은 상한을 써도 되고 자산별로 달라도 돼.**

LLM은 자산 성격을 근거로 `주식 50%, 금 30%` 같은 제약을 임의로 확정하지 않는다.

제안은 가능하지만 사용자 선택 전에는 실행 입력으로 확정하지 않는다.

### 3.3 Optimization Goal

사용자-facing 표현은 의미를 먼저 보여준다.

```text
변동성 대비 기대수익이 좋은 조합 (Sharpe 지수)
= Maximum Sharpe

허용한 변동성 안에서 기대수익이 가장 높은 조합
= Maximum Return at Target Volatility
```

두 번째를 선택하면 허용할 연간 변동성 상한을 반드시 사용자에게 확인한다.

### 3.4 Analysis Period

사용자가 기간을 지정하면 그대로 사용한다.

기간 지정이 없으면 다음을 자동 적용한다.

> **모든 optimization asset의 유효 데이터가 함께 존재하는 전체 공통기간**

기간 미지정은 미확정 상태가 아니다.

실행 후 실제 시작일, 종료일, observation 수를 보고한다.

특정 자산의 짧은 history가 공통기간을 제한하면 결과 해석에서 별도로 밝힌다.

### 3.5 Rebalancing

사용자가 별도 지정하지 않으면 canonical default를 사용한다.

월/연 리밸런싱 차이 자체가 연구 질문일 때만 사용자 결정으로 올린다.

### 3.6 Benchmark

**Research Frontend에서 Benchmark는 항상 존재한다.**

Canonical default:

```yaml
benchmark:
  symbol: SPY
  name: SPDR S&P 500 ETF Trust
  currency: USD
```

사용자가 별도 benchmark를 지정하지 않으면 S&P 500(SPY)을 사용한다.

LLM은 초기 조건 정리 과정에서 다음 의미를 자연스럽게 고지한다.

> **비교대상은 기본적으로 S&P 500(SPY)으로 둘게. 다른 지수나 ETF와 비교하고 싶으면 바꿀 수 있어.**

`Benchmark를 뭘로 할까?`라고 기본값 선택을 다시 사용자에게 떠넘기지 않는다.

사용자가 QQQ, ACWI, 특정 ETF/지수 등 다른 비교대상을 명확히 지정하면 그 값으로 override한다.

**Research Frontend가 생성하거나 갱신하는 Experiment YAML에는 default를 사용하더라도 benchmark를 생략하지 않고 명시적으로 기록한다.**

이는 다음 이유 때문이다.

- 실행 입력만 보고도 비교 기준을 재현할 수 있어야 함
- Active Return / Tracking Error / Information Ratio의 의미가 명확해야 함
- Annualized Active Return / Active Return Contribution / Rolling Active / Up-vs-Down analytics가 누락되지 않아야 함
- 오래된 Experiment에서 benchmark가 빠져 있어도 Research execution boundary는 SPY default를 보충하여 effective `input.yaml`에 기록해야 함

### 3.7 Risk-free Rate

사용자가 별도 convention을 요구하지 않으면 canonical default를 적용한다.

외부 서비스와 parity를 직접 검증하는 연구라면 비교 convention 차이를 결과에서 명시한다.

---

## 4. 질문 표현 규칙

내부 용어를 그대로 사용자에게 던지지 않는다.

```text
내부 용어                  사용자에게 우선할 표현
min/max constraint         비중을 최소/최대 어디까지 허용할지
optimization objective     무엇을 최우선으로 볼지
target annual volatility   연간 변동성을 어디까지 허용할지
common overlap period      모든 자산 데이터가 함께 있는 전체 기간
Maximum Sharpe             변동성 대비 기대수익이 좋은 조합 (Sharpe 지수)
benchmark                  비교대상
```

금지 패턴:

```text
- YAML field를 그대로 나열해 답을 요구
- 이미 받은 값을 다시 질문
- canonical default를 다시 선택하게 함
- 내부 구현 파라미터를 사용자 설정처럼 제시
- sanity-check를 승인 절차로 바꿈
```

좋은 응대는 다음 특성을 가진다.

```text
- 투자 관점에서 바로 이해 가능
- 답에 따라 연구 의미가 실제로 달라지는 것만 질문
- default는 짧게 고지하고 자동 적용
- 변경 가능한 default는 변경 가능하다고 알림
```

---

## 5. Execution Gate

정식 실행 전에 필요한 것은 모든 YAML field에 대한 사용자 승인이 아니다.

다음을 확인한다.

```text
Asset Universe              확정
Provided weights            필요한 연구라면 확정 및 합계 검증
Asset min/max bounds        사용자 결정 완료
Optimization Goal           확정
Target Volatility           해당 objective일 때 확정
Benchmark                   명시적 override 또는 canonical SPY default 적용
```

다음은 일반 연구에서 자동 적용 가능하다.

```text
Analysis Period             common-overlap default
Rebalancing                 canonical default
Risk-free                   canonical default
Benchmark                   SPY default, 단 Experiment YAML에는 명시적으로 기록
Internal implementation     system responsibility
```

사용자가 이미 실행을 요청했다면 Execution Gate가 충족되는 즉시 실행한다.

---

## 6. 실행 직전 사용자-facing 요약 예시

```text
조건은 이렇게 잡혔어.

- 자산: SPY / QQQ / TLT / GLD
- 현재 비중: 30 / 30 / 20 / 20
- 비중 허용범위: 전부 0~50%
- 목표: 변동성 대비 기대수익이 좋은 조합 (Sharpe 지수)
- 기간: 모든 자산 데이터가 함께 있는 전체 기간
- 비교대상: S&P 500 (SPY), 원하면 변경 가능

바로 실행할게.
```

이미 실행 의도가 있는 상황에서는 마지막에 `진행할까?`를 붙이지 않는다.

---

## 7. 핵심 원칙 요약

> **LLM은 투자 의사결정은 묻고, canonical default는 고지하고 적용하며, 구현 세부사항은 숨긴다.**

> **Benchmark는 Research Frontend의 항상-존재 입력이며 기본값은 S&P 500(SPY)이다. Default를 사용하더라도 Experiment/Input YAML에 명시적으로 기록한다.**
