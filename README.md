# portfolio-optimizer-kr

Mean-variance portfolio research toolkit with first-class support for Korean investment assets such as individual stocks, ETFs, and ETNs. Portfolio Visualizer is a reference, not an implementation target.

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

Existing detailed contracts in `docs/` remain the baseline for capabilities not yet migrated to OpenSpec. New or modified behavior is planned through OpenSpec and archived into `openspec/specs/` over time.

Current feature work:

```text
branch: bt-module
change: openspec/changes/bt-module/
```

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
