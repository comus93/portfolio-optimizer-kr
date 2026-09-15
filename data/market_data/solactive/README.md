# Solactive Global Defense Index PR

Repository-held market data for backtest/research use.

## Identity

- Name: Solactive Global Defense Index PR
- ISIN: `DE000SL0JKC0`
- RIC: `.SOLGDEFP`
- Bloomberg ticker: `SOLGDEFP Index`
- Currency: USD
- Return type: Price Return (PR)
- Official index start date: 2019-05-07
- Official initial level: 1000
- Live date: 2024-09-06

Solactive states that index levels published before the live date are back-tested history. This matters when the series is used as a long-history proxy for an ETF with a shorter live record.

## Source

- Index page: https://www.solactive.com/index/DE000SL0JKC0/
- History endpoint: https://www.solactive.com/_actions/getDayHistoryChartData/
- Guideline: https://www.solactive.com/downloads/Guideline-Solactive-SOLGDEF.pdf
- Retrieved/uploaded: 2026-09-15

The source history was obtained with the Solactive history endpoint using ISIN `DE000SL0JKC0`.

## Files

### `DE000SL0JKC0.raw.csv`

Exact uploaded extraction result.

- Rows: 1,920
- Extracted date range: 2019-05-06 to 2026-09-13
- Columns: `date,level,isin`

The extraction converted Solactive timestamps with JavaScript `new Date(timestamp).toISOString().slice(0, 10)`. The resulting dates are systematically one calendar day earlier than the official index date. Evidence:

- the first row is 2019-05-06 at level 1000, while the official guideline defines the index start date as 2019-05-07 at level 1000;
- the raw series has a repeating Mon/Tue/Wed/Thu/Sun pattern instead of normal Mon-Fri market dates.

### `DE000SL0JKC0.csv`

Canonical repository series for research/backtest use.

- Rows: 1,920
- Canonical date range: 2019-05-07 to 2026-09-14
- Columns: `date,level,isin`
- Normalization: `canonical_date = raw_date + 1 calendar day`
- Resulting observations fall on Monday-Friday only.

No index levels were changed. Only the calendar date was normalized.

## Usage note

Treat this as index-level market data, not as the realized trading history of PLUS 글로벌방산 (496770). For long-history research it can be used as a proxy for the fund's underlying index, while the ETF's post-listing history should be used separately to evaluate tracking behavior.
