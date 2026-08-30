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

Optimization 1차 baseline은 `migrate-optimizer-to-openspec` change를 통해 기존 `docs/` contract에서 OpenSpec으로 이관한다. Migration parity가 확인되기 전까지 기존 docs가 baseline이며, 이관 완료된 capability는 `openspec/specs/`가 normative source다.

Backtest는 `bt-module` change에서 신규 capability로 정의한다. Shared capability를 변경하면 영향을 받는 기존 product capability의 regression 범위를 함께 관리한다.

Current feature branch:

```text
branch: bt-module
changes:
- openspec/changes/migrate-optimizer-to-openspec/
- openspec/changes/bt-module/
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
