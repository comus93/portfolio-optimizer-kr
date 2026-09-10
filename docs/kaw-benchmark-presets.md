# KAW Benchmark Presets

KAW reconstruction is a reusable baseline for Backtest portfolio comparisons.

Canonical portfolio definitions and availability are owned by:

```text
studies/kaw-target-reconstruction/study.md
```

## Usage

Backtest Research Frontend keeps `SPY` as the default benchmark when the benchmark field is omitted.

To replace SPY with KAW, use one explicit line.

### Recent / short-period comparison

```yaml
benchmark: kaw_short
```

Equivalent alias:

```yaml
benchmark: kaw_native
```

This selects **KAW Native Proxy**, usable from **2021-11 onward**.

### Long-history internal-engine comparison

```yaml
benchmark: kaw_long
```

Equivalent alias:

```yaml
benchmark: kaw_core
```

This selects **KAW Core Revised Internal**, usable from **2014-07 onward**.

### Portfolio Visualizer

Portfolio Visualizer does not consume the internal preset. Use the documented **KAW Core PV** holdings instead:

```text
QQQ 10 / SCHD 10 / EWY 8 / ASHR 8.5 / INDY 8.5 / EWJ 5 / TLT 30 / GLD 20
```

## Execution semantics

A KAW preset is only an input shortcut. Before execution the Research Frontend materializes it into an explicit fixed-weight benchmark portfolio and appends any required constituent assets to the shared asset universe.

The persisted run `input.yaml` therefore contains:

- canonical preset id and benchmark name
- every benchmark constituent
- currency metadata
- full target weights

The benchmark portfolio uses the same run-level:

- requested analysis period / common availability alignment
- rebalancing frequency
- calendar-alignment rule
- canonical total-return handling
- KRW reporting / USD-KRW conversion rule

Existing benchmark-relative analytics are reused without a KAW-specific calculation path, including active return, tracking error, information ratio, active-return contribution, and up/down-market analysis.

## Selection rule

```text
recent internal comparison  -> kaw_short / kaw_native
long internal comparison    -> kaw_long  / kaw_core
Portfolio Visualizer        -> KAW Core PV holdings
```

There is deliberately no hidden period-based automatic switch between Native and Core. The selected KAW representation must be explicit in the Experiment so historical runs remain reproducible.

## Compatibility

- Existing single-asset benchmark configurations such as `benchmark: SPY` remain supported.
- Explicit no-benchmark Backtest remains supported.
- KAW composite benchmark presets are Backtest-only; Optimization benchmark semantics are unchanged.
