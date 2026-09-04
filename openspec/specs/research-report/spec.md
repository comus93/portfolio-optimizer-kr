## Purpose

Canonical finance result와 user-facing report 사이의 presentation responsibility boundary를 정의한다. 세부 UI/interaction behavior는 해당 capability가 OpenSpec으로 완전 마이그레이션되기 전까지 `docs/report-ui-specification.md`를 migration baseline으로 유지한다.

## Requirements

### Requirement: Report does not redefine canonical finance semantics
Presentation layer는 canonical result의 finance 의미를 다시 정의하거나 별도 formula로 재계산해서는 안 된다(MUST NOT).

#### Scenario: canonical metric rendering
- GIVEN canonical result에 CAGR가 존재한다
- WHEN report를 렌더링한다
- THEN renderer는 CAGR formula를 별도 구현해 다른 값을 만들지 않고 canonical metric을 표시용으로 변환한다

### Requirement: View-only transformations are allowed
Browser/report layer는 formatting, coordinate mapping, grouping/binning, display ordering과 같은 view-only transformation을 수행할 수 있다(MAY). 해당 transformation은 canonical finance values 또는 observation semantics를 변경해서는 안 된다(MUST NOT).

#### Scenario: chart coordinate mapping
- GIVEN canonical monthly return series가 있다
- WHEN SVG chart를 생성한다
- THEN axis coordinate를 계산할 수 있지만 원래 return observation 값을 다른 finance metric으로 대체하지 않는다

### Requirement: Missing and non-applicable values preserve meaning
Canonical metric이 unavailable 또는 conceptually non-applicable인 경우 user-facing report는 이를 0과 구분해야 한다(MUST). 세부 표기 convention은 current report UI contract를 따른다.

#### Scenario: benchmark-relative metric on benchmark itself
- GIVEN benchmark의 Information Ratio가 conceptually non-applicable이다
- WHEN report를 렌더링한다
- THEN 0.00으로 표시해 실제 계산값처럼 보이게 하지 않는다

### Requirement: Identity and units remain observable
Presentation restructuring이 table/chart layout을 변경하더라도 canonical asset/portfolio identity와 metric unit information을 제거해서는 안 된다(MUST NOT).

#### Scenario: asset performance table redesign
- GIVEN asset performance에 Ticker, Name과 percentage/ratio metrics가 있다
- WHEN table presentation을 변경한다
- THEN 어떤 asset의 어떤 unit metric인지 사용자가 계속 식별할 수 있다

### Requirement: Report semantic validation uses canonical values
Report semantic test는 가능한 경우 canonical value와 rendered value의 대응을 검증해야 하며 단순 문자열 marker 존재만으로 finance semantic correctness를 대신해서는 안 된다(MUST NOT).

#### Scenario: balance display regression
- GIVEN canonical normalized Optimization balance 1.0의 display convention이 $10,000이다
- WHEN report semantic test를 수행한다
- THEN 실제 rendered balance가 그 convention과 일치하는지 검증한다
