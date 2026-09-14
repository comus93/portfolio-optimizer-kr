# Design: Shared Optimization execution core

## Invariants

The refactor MUST preserve:

- canonical monthly-return preparation semantics
- annualized mean/covariance semantics
- long-only fully-invested constraints and asset bounds
- Maximum Sharpe objective
- Maximum Return subject to Target Annual Volatility objective
- OSQP/CLARABEL routing
- solver residual validation
- Efficient Frontier boundary and target-return definitions
- persisted Optimization/report finance semantics

## A. Shared objective solver

Add a single `solve_optimization(...)` routing boundary that accepts prepared
moments, objective, bounds, risk-free rate and optional target volatility.

Normal Optimization MUST call this boundary. Future repeated robustness
analyses MUST reuse the same boundary rather than maintain a second objective or
solver implementation.

The shared boundary deliberately excludes market-data preparation, Efficient
Frontier generation, portfolio simulation, analytics and reporting.

## B. Efficient Frontier execution

Frontier generation remains a separate optional computation layered on top of
the same canonical moments.

The existing frontier definition is unchanged. For the sequence of target
returns, construct the minimum-variance CVXPY problem once, represent target
return as a `Parameter`, and reuse the problem with OSQP warm starts.

The public single-target `minimum_variance_for_return(...)` behavior remains
available and delegates to the same reusable solver implementation.

## C. Prepared Optimization data

Introduce an immutable prepared-data object containing canonical Optimization
monthly asset returns and optional benchmark returns.

During the default persisted Optimization run:

1. load raw market data once,
2. prepare Optimization return data once,
3. use its monthly-return index when resolving the default U.S. 3-Month T-Bill
   rate,
4. pass the same prepared object into the Optimization analysis pipeline.

Direct callers that do not provide prepared data retain the existing behavior:
`analyze_prices(...)` prepares it internally.

Custom analyzer injection remains compatible and does not acquire a new
`prepared_data` argument requirement.

## Capability impact

- `portfolio-optimization`: implementation architecture changes; requirements
  unchanged.
- `market-data`: no return or FX semantics change; a product-specific prepared
  aggregate is added on top of existing canonical preparation.
- `portfolio-backtest`: no behavior change.

## Regression focus

- shared engine equals existing canonical solver output for both objectives
- frontier still emits requested point count and instantiates one reusable
  target-return QP per frontier build
- default Optimization prepares the shared dataset once and does not reprepare
  monthly returns for risk-free resolution
- existing optimizer, pipeline and runner tests remain green
