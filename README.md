# portfolio-optimizer-kr

Mean-variance portfolio research toolkit with first-class support for Korean investment assets such as individual stocks, ETFs, and ETNs. Portfolio Visualizer is a golden reference, not an implementation target.

## Development

```powershell
uv sync --extra dev
uv run pytest
```

The financial conventions and acceptance criteria are defined in `specification.md`. Agent workflow rules are in `AGENTS.md`.

## Current skeleton

The initial skeleton contains:

- FinanceDataReader adapter boundary
- canonical adjusted-price and FX normalization
- monthly return/statistics engine
- CVXPY optimization using OSQP for QP and CLARABEL for SOCP
- efficient frontier generation
- monthly/yearly historical rebalancing
- basic performance, benchmark, and decomposition analytics
- structured result model
- synthetic pytest suite plus PV golden-reference smoke tests
