# Design

## LOYO reporting
The report reads the existing persisted `loyo_robustness.csv`; no optimization is rerun in the browser or renderer.

## Correlations
`annualized_statistics(monthly_returns).correlation` remains the single Optimization asset-correlation source. The previous `historical.correlations_table(monthly_returns, paths, benchmark_returns)` call is removed from Optimization because it expanded the matrix with portfolio and benchmark series. Persisted/report correlation tables are presentation views of the existing asset-only matrix.

Backtest correlation behavior is unchanged.
