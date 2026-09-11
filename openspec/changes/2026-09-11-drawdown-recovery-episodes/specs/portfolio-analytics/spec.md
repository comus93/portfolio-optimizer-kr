## ADDED Requirements

### Requirement: Drawdown episode recovery timing
Canonical drawdown episode는 기존 Rank, Start, Bottom, Recovery, Maximum Drawdown과 함께 `decline_months`, `recovery_months`, `underwater_months`를 제공해야 한다(MUST).

```text
month_delta(a,b) = (year_b-year_a)*12 + (month_b-month_a)
decline_months    = month_delta(start,bottom) + 1
recovery_months   = month_delta(bottom,recovery)
underwater_months = month_delta(start,recovery) + 1
```

Recovery가 없는 ongoing episode에서 `recovery_months`는 unavailable이어야 하며(MUST), `underwater_months`는 latest available observation까지 계산해야 한다(MUST).

#### Scenario: recovered episode
- GIVEN Start가 2020-09, Bottom이 2020-10, Recovery가 2021-05이다
- WHEN episode timing을 계산한다
- THEN decline_months=2, recovery_months=7, underwater_months=9이다

#### Scenario: ongoing episode
- GIVEN latest observation까지 이전 peak를 회복하지 못했다
- WHEN episode timing을 계산한다
- THEN recovery_months와 recovery rate는 unavailable이고 underwater_months는 latest observation까지의 기간이다

### Requirement: Annualized recovery rate
Recovered drawdown episode의 Bottom drawdown `d < 0`와 recovery month count `m > 0`에 대해 annualized recovery rate는 다음 공식을 사용해야 한다(MUST).

```text
annualized_recovery_rate = (1 / (1 + d))^(12 / m) - 1
```

이 값은 Bottom wealth에서 이전 peak wealth까지 회복하는 과정의 복리 연환산 수익률이다. Ongoing episode 또는 유효한 `m`이 없는 경우 unavailable이어야 한다(MUST).

#### Scenario: 20% drawdown recovered in 6 months
- GIVEN Bottom drawdown=-20%, recovery_months=6
- WHEN annualized recovery rate를 계산한다
- THEN `(1/0.8)^(12/6)-1 = 56.25%`이다

### Requirement: Recovery progress path
각 drawdown episode는 Bottom 이후 Recovery 또는 latest observation까지의 normalized monthly recovery progress를 보존할 수 있어야 한다(MUST).

```text
recovery_progress_t = (drawdown_t - drawdown_bottom) / (0 - drawdown_bottom) * 100
```

Bottom observation은 0%, recovered episode의 Recovery observation은 100%여야 한다(MUST). Ongoing episode는 future recovery를 fabricate하지 않고 latest observation에서 끝나야 한다(MUST).

#### Scenario: partial recovery
- GIVEN Bottom=-20%, 다음 month drawdown=-12%이다
- WHEN recovery progress를 계산한다
- THEN progress는 40%이다
