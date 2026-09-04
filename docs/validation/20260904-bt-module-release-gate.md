# bt-module Release Gate — 2026-09-04

## Decision

`bt-module` core is accepted for OpenSpec sync/archive and promotion to `main`.

Post-release standalone Input UI, automated Study/Experiment lifecycle enforcement, broader market-data provider coverage, and additional `docs/` → OpenSpec migration are explicitly deferred in `openspec/TODO.md` and are not release blockers.

## Source under validation

- Branch: `bt-module`
- Core validation source HEAD: `2d2a41d1958eee4a295ff4399d6b94b8855cf3f9`
- Final release-gate workflow run: `33864677208`
- Existing affected-regression workflow run at the same source HEAD: `33864618611`

## Automated regression

Final release gate:

```text
201 passed in 4.26s
```

The full-suite audit first exposed stale regression fixtures caused by the now-mandatory `product_mode`, the new constituent-asset-only correlation contract, and an incomplete investable-path test fixture. The test contracts were corrected without changing product finance behavior, then the full suite passed.

`validate-bt-module.yml` affected/shared regression also passed at source HEAD `2d2a41d...`.

## OpenSpec

```text
openspec validate --all --strict --no-interactive
PASS
```

The active `bt-module` task list is complete for the core release scope. Deferred work is explicitly recorded in `openspec/TODO.md` before archiving.

## Canonical total-return policy

The current FDR loader is source-aware:

- Prefer verified `Adj Close` when available.
- Allow Korean ETF default/NAVER `Close` only after ETF listing verification under the documented provider semantics.
- Do not silently accept generic price-only `Close` as canonical total return.
- Reject unsupported routes/instruments with explicit validation error.
- The same canonical market-data path is shared by Optimization and Backtest.

The release matrix additionally asserted `return_semantics=total_return` for the real FDR QQQ / GLD / IEF / SPY series used in validation.

## Real-data Backtest release matrix

A common real FDR dataset for QQQ / GLD / IEF with SPY where applicable was hydrated once and reused across policy cases. All cases completed through canonical Backtest execution and report generation.

Validated cases:

1. 3 portfolios, no benchmark, Month-to-Month, Monthly, Calendar Aligned Yes
2. 1 portfolio, SPY benchmark, Month-to-Month, Monthly, Calendar Aligned Yes
3. 1 portfolio, SPY benchmark, Year-to-Year, Yearly, Calendar Aligned Yes
4. Quarterly, Calendar Aligned Yes
5. Quarterly, Calendar Aligned No
6. Semiannual, Calendar Aligned Yes
7. Semiannual, Calendar Aligned No
8. Yearly, Calendar Aligned No
9. No rebalancing
10. Monthly, Calendar Aligned No

Behavioral invariants checked on real data:

- Monthly result is alignment-invariant.
- Calendar-aligned vs first-active-month anchored Quarterly results differ on nontrivial data.
- Calendar-aligned vs first-active-month anchored Semiannual results differ on nontrivial data.
- Monthly rebalancing and No Rebalancing results differ on nontrivial data.
- No-benchmark report omits benchmark-relative sections.
- Benchmark runs include benchmark-relative context.
- Backtest reports exclude Efficient Frontier.
- Portfolio count and persisted schedule/product identity match the requested case.

## Visual / semantic acceptance

The user directly reviewed the latest Backtest reporting page and identified final asset-identity and Monthly Correlations issues. Those were implemented as:

- combined asset identity: `Name` + line break + `(Ticker)`
- Backtest Monthly Correlations: constituent assets only, excluding portfolio and separate benchmark series

Focused regression and subsequent real E2E/report checks passed. No new material layout redesign was introduced after that direct user review; the follow-up changes were semantic/identity corrections covered by regression.

## Control state

`control/execute.yaml` was verified idle:

```yaml
run: false
```

## Blocker status

- P0: none
- P1: none
- Core release blocker: none

Next release step: sync the active `bt-module` OpenSpec delta into baseline specs, archive the completed change, validate again, then promote `bt-module` to `main` without rewriting its source tree.
