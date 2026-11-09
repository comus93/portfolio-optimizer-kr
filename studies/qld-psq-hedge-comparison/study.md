# QLD / PSQ Hedge Comparison Study

## Research question
Does replacing 3 percentage points of GLD with PSQ improve the QLD-based portfolio's return/risk trade-off, drawdown and stress resilience?

Compare two fixed-weight portfolios holding identical assets other than the GLD vs PSQ 3% sleeve.

## Portfolio A: QLD Core (baseline)
- QLD 35%
- SPMO 15%
- AIA 5%
- XLE 5%
- SCHD 5%
- GLD 30%
- 138920 KODEX 콩선물(H) 5%
Total 100%

## Portfolio B: QLD + PSQ 3%
- QLD 35%
- SPMO 15%
- AIA 5%
- XLE 5%
- SCHD 5%
- GLD 27%
- PSQ 3%
- 138920 KODEX 콩선물(H) 5%
Total 100%

## Research design
- Product: Backtest, not Optimization
- Common period: 2015-11 to 2026-08 (using the original comparison run's common window)
- Monthly rebalance, calendar-aligned
- Reporting currency KRW (same FX rule for USD and KRW assets)
- Benchmark SPY
- Fixed risk-free annual rate: 3.8394827586206897% (same as prior comparable run)

## Analysis priority
1. CAGR / volatility / MDD / Sharpe and changes between A and B.
2. Risk concentration, QLD+SPMO reliance.
3. Stress/down-month behavior and PSQ slot replacement utility.
4. Return/risk contribution and whether PSQ actually diversifies economic engines.

Do not infer future hedge performance solely from historical outcomes; QLD and PSQ have daily reset and path-dependent compounding.
