# Backtest PV parity Year-to-Year v7

v7 preserves the v6 financial/report contract and changes instrument naming provenance only.

- `AssetSpec.name` remains part of the shared Optimization/Backtest input contract.
- asset and benchmark names in the canonical YAML are snapshots from FinanceDataReader `StockListing("ETF/US")` metadata.
- report labels use the persisted source-backed names; runtime finance calculations are unchanged.
- equal-weight asset display ordering may move where the existing deterministic tie-break uses asset name.
