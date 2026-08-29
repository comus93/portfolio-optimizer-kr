# portfolio-optimizer-kr

Mean-variance portfolio research toolkit with first-class support for Korean investment assets such as individual stocks, ETFs, and ETNs. Portfolio Visualizer is a reference, not an implementation target.

## Development

```powershell
uv sync --extra dev
uv run pytest
```

The financial conventions are defined in `docs/specification.md`.

The canonical user research operation flow is defined in `docs/research-operation-pipeline.md`:

```text
User <-> ChatGPT
-> Experiment
-> GitHub Actions
-> Run / Result
-> GitHub Pages + ChatGPT interpretation
-> User discussion
-> Confirmed Analysis
-> Repository
```

Agent workflow rules for development and validation are in `AGENTS.md`.

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
- synthetic pytest suite plus external-reference smoke tests
