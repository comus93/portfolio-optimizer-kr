# Design

## Decision

Default RF resolution is owned by the Research Frontend input policy, not by portfolio analytics formulas.

When the user does not mention RF, the generated effective YAML contains the previously resolved U.S. 3-Month T-Bill effective annual rate explicitly:

```yaml
risk_free:
  mode: fixed
  annual_rate_pct: 3.8394827586206895
```

This keeps the run deterministic and prevents a FDR/FRED economic-series fetch on the default path.

## Semantics

- Economic source/provenance: U.S. 3-Month T-Bill (`TB3MS`), resolved by run `20260908-0002`.
- Execution representation: `fixed`, because the value is already resolved and should be persisted directly.
- `us_3m_tbill` remains available as an explicit dynamic refresh/provider mode.
- User-specified RF always overrides the default.
- The pinned value equals the dynamic `us_3m_tbill` result for the source run period. For other analysis periods it is a project default convention, not a claim that the period-specific TB3MS average is mathematically identical.

## Affected capabilities

- `research-input`: default materialization changes.
- `market-data`: supported modes remain unchanged; default research path no longer requires provider resolution.
- `portfolio-optimization`: consumes the same effective RF input.
- `portfolio-backtest`: consumes the same effective RF input.
- `run-artifacts`: existing requested/effective RF metadata contract remains unchanged.

## Verification

- Optimization input with no user RF includes fixed 3.8394827586206895%.
- Backtest input with no user RF includes the same value.
- Explicit fixed RF is preserved.
- Explicit `us_3m_tbill` remains selectable.
- Default fixed-mode runs do not call the economic-series provider.
