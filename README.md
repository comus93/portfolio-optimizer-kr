# portfolio-optimizer-kr

Mean-variance portfolio research toolkit with first-class support for Korean investment assets such as individual stocks, ETFs, and ETNs. Portfolio Visualizer is a reference, not an implementation target.

## Current baseline

Milestone 2 was completed on 2026-09-11.

```text
tag: baseline-20260911-milestone-2
representative run: 20260911-0007
branch: main
```

The baseline pins the repository state after the shared Optimization/Backtest drawdown-recovery analytics and report-comparison work, including the current Drawdown overlay presentation, `탄성회복도` comparison, Worst Drawdowns presentation, run-index cleanup, affected regression, and representative published report.

- Milestone manifest: [`docs/milestones/2026-09-11-milestone-2.md`](docs/milestones/2026-09-11-milestone-2.md)
- Representative report: https://comus93.github.io/portfolio-optimizer-kr/runs/20260911-0007/report.html
- Previous baseline: `baseline-20260910-pre-pain-metrics`

The recovery-resilience aggregation / Sweet Spot rule remains follow-up research and is intentionally outside the Milestone 2 baseline.

## Development

```powershell
uv sync --extra dev
uv run pytest
```

## Change workflow

OpenSpec manages requirements and change state.

```text
openspec/specs/                 current capability requirements
openspec/changes/<change>/      active proposal/spec/design/tasks
openspec/changes/archive/       completed changes
```

Target capability model:

```text
Product
- portfolio-optimization
- portfolio-backtest

Shared
- market-data
- portfolio-simulation
- portfolio-analytics
- run-artifacts
- research-report
```

Optimization and Backtest are separate product capabilities. Shared market data, calculation, simulation, artifact, and presentation behavior is defined once in shared capabilities and validated across affected products.

The default integration branch is `main`. Active work is represented by the current contents of `openspec/changes/`; completed capability requirements are carried by `openspec/specs/` and archived change history.

Codex uses the OpenSpec skills installed by `openspec init --tools codex`; its workflow is invoked with names such as `$openspec-propose` and `$openspec-apply-change`.

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

Agent workflow rules are in `AGENTS.md` and ChatGPT/Codex handoff rules are in `ai-share/PROTOCOL.md`.

## Current capabilities

The repository currently includes:

- FinanceDataReader adapter boundary
- canonical adjusted-price and FX normalization
- monthly return/statistics engine
- CVXPY optimization using OSQP for QP and CLARABEL for SOCP
- efficient frontier generation
- monthly/yearly historical rebalancing
- performance, benchmark, decomposition, pain, and drawdown-recovery analytics
- shared Optimization/Backtest historical report components
- structured result and persisted run-artifact model
- synthetic regression plus browser-level report validation
- GitHub Actions research execution and GitHub Pages report publishing
