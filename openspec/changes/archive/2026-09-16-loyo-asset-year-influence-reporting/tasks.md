# Tasks

- [x] Add an in-memory Asset-Year Influence projection from existing annual asset return, baseline weight and LOYO results without re-running finance calculations.
- [x] Persist `asset_year_influence.csv` through the existing raw/review artifact layers with correct decimal vs percentage-point units.
- [x] Add a no-reoptimization legacy backfill path for existing LOYO runs.
- [x] Redesign the default Optimization LOYO section into Asset-Year Influence, LOYO Summary and Allocation Changes.
- [x] Render metric-specific conditional cell backgrounds and keep numeric values visible.
- [x] Rename user-facing Turnover to Reallocation and show top 3 signed allocation shifts.
- [x] Remove user-facing Removed Start/End, observation counts and Solver; show Status/Reason only for abnormal scenarios.
- [x] Use 2-decimal user-facing formatting without rounding canonical/raw values.
- [x] Add targeted tests for projection reuse/values, persistence units, report semantics and Backtest exclusion.
- [x] Backfill and regenerate run `20260914-0003` without reoptimization, then validate the rendered report.
- [x] Update `docs/report-ui-specification.md` and promote the completed delta into baseline after validation.
