# Input, UI, Runner, and Viewer Contract

## Purpose

The optimizer core remains independently executable without a UI. YAML is the user-facing run contract shared by CLI, UI, and agents.

```text
Input UI / CLI / Agent
        ↓
      YAML
        ↓
YAML adapter + validator
        ↓
OptimizationRequest
        ↓
Optimizer core
        ↓
Canonical result + review/raw CSV
        ↓
Result Viewer
```

## Architectural rules

1. `OptimizationRequest` remains the canonical internal request model.
2. UI must generate YAML and then call the same YAML runner used by CLI. UI must not create a second execution path.
3. YAML percentage fields use percentage-point values for human readability. Example: `20` means 20% and becomes `0.20` internally.
4. The runner owns market-data loading, warm-up period loading, optional FX loading, optimizer invocation, and persisted run location.
5. A persisted run stores the exact input YAML as `runs/<run_id>/input.yaml`.
6. `result.json` is the canonical full-precision result.
7. `raw/` preserves machine-oriented full-precision CSV data.
8. `review/` contains human/LLM-oriented tables with explicit units and PV-like orientation where useful.
9. Viewer code does not recalculate financial metrics. It reads canonical/review/raw outputs and only selects or presents existing values.
10. UI and Viewer are logically independent. Existing run output must be viewable without rerunning the optimizer.

## YAML v1 shape

```yaml
run_id: example
analysis_period:
  start: 2020-01-01
  end: 2025-12-31
assets:
  - symbol: QQQ
    name: Invesco QQQ Trust
    currency: USD
    provided_weight_pct: 60
    min_weight_pct: 0
    max_weight_pct: 80
  - symbol: GLD
    currency: USD
    provided_weight_pct: 40
    min_weight_pct: 0
    max_weight_pct: 80
benchmark:
  symbol: SPY
  currency: USD
optimization:
  objective: max_sharpe
  frontier_points: 100
portfolio:
  rebalancing_period: monthly
risk_free:
  mode: us_3m_tbill
fx: {}
```

`us_3m_tbill` is the canonical/default risk-free mode. `fixed` remains available only when an explicit fixed annual rate is intentionally requested.

For mixed KRW/USD runs, `fx.usdkrw_symbol` must be explicitly supplied until the FX provider convention is centrally fixed.

## UI v1 responsibilities

- Search an asset catalog by ticker or name.
- Add/remove/edit assets.
- Edit provided weight and optimizer min/max constraints.
- Configure period, benchmark, objective, rebalancing, risk-free mode, and FX series when required.
- Default the risk-free selector to `us_3m_tbill`.
- Preview and save generated YAML.
- Execute the YAML runner.
- Open an existing run and render review tables plus charts sourced from run outputs.

## Viewer v1 responsibilities

- Load `result.json`, optional `parity.json`, `review/*.csv`, and `raw/*.csv`.
- Display review tables directly.
- Use raw/review chart-ready series without recomputing returns, risk, attribution, or optimization statistics.
- Fail clearly when a requested run artifact is absent.

## Testing loop

The established role split remains unchanged:

```text
LLM defines requirements
 → LLM writes/updates pytest contract
 → LLM writes minimum skeleton
 → Agent implements/hardens
 → affected tests during iteration
 → full regression suite before completion
```

Agent must not weaken or delete a contract test merely to make implementation pass. If the contract is infeasible or incorrect, report a blocker to the LLM first.
