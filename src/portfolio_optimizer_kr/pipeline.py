from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from portfolio_optimizer_kr.analytics import (
    drawdown_episodes,
    monthly_returns_table,
    return_decomposition,
    risk_contribution,
    rolling_returns,
    trailing_returns,
)
from portfolio_optimizer_kr.analytics import historical
from portfolio_optimizer_kr.data import (
    align_common_prices,
    convert_usd_price_to_krw,
    month_end_prices,
    to_monthly_returns,
)
from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import (
    OptimizationObjective,
    OptimizationRequest,
    RiskFreeMode,
)
from portfolio_optimizer_kr.optimize import (
    build_efficient_frontier,
    maximum_sharpe,
    target_volatility,
)
from portfolio_optimizer_kr.portfolio import build_portfolio_path
from portfolio_optimizer_kr.report import CanonicalResult
from portfolio_optimizer_kr.stats import (
    annualized_statistics,
    portfolio_expected_return,
    portfolio_volatility,
)


# Compatibility names remain public for existing tests/callers, but the
# implementation lives in the shared historical analytics capability.
_annual_asset_returns = historical.annual_asset_returns_table
_active_contribution_table = historical.active_contribution_table
_up_down_market_table = historical.up_down_market_table
_up_down_scatter_table = historical.up_down_market_observations
_portfolio_metrics_table = historical.portfolio_metrics_table
_correlations = historical.correlations_table
_growth_table = historical.growth_table
_drawdown_series_table = historical.drawdown_series_table


def _annual_rf(
    request: OptimizationRequest, supplied_annual_rf: float | None
) -> float:
    if request.risk_free.mode is RiskFreeMode.FIXED:
        if request.risk_free.annual_rate is None:
            raise ValueError("fixed risk-free mode requires annual_rate")
        return float(request.risk_free.annual_rate)
    if supplied_annual_rf is None:
        raise NotImplementedError(
            "U.S. 3-Month T-Bill provider is an external-data boundary; "
            "supply annual_rf until implemented"
        )
    return float(supplied_annual_rf)


def _asset_price(
    request: OptimizationRequest,
    symbol: str,
    price: pd.Series,
    currency: str,
    usdkrw: pd.Series | None,
) -> pd.Series:
    asset_currencies = {asset.currency.upper() for asset in request.assets}
    if currency.upper() == "USD" and "KRW" in asset_currencies:
        if usdkrw is None:
            raise DataValidationError(
                "mixed KRW/USD universe requires USD/KRW series"
            )
        return convert_usd_price_to_krw(price, usdkrw)
    if currency.upper() not in {"KRW", "USD"}:
        raise DataValidationError(f"unsupported currency: {currency}")
    return price


def _asset_price_coverage(
    request: OptimizationRequest, prices: Mapping[str, pd.Series]
) -> dict[str, dict[str, object]]:
    coverage: dict[str, dict[str, object]] = {}
    for asset in request.assets:
        series = prices.get(asset.symbol)
        if series is None:
            continue
        observed = series.dropna()
        if observed.empty:
            continue
        coverage[asset.symbol] = {
            "name": asset.name,
            "start": str(pd.Timestamp(observed.index.min()).date()),
            "end": str(pd.Timestamp(observed.index.max()).date()),
            "observations": int(len(observed)),
        }
    return coverage


def _completed_monthly_returns(
    returns: pd.DataFrame, end: str | pd.Timestamp | None
) -> pd.DataFrame:
    """Exclude only the terminal calendar month when it is not yet complete."""
    cutoff = (
        pd.Timestamp(end).normalize()
        if end is not None
        else pd.Timestamp.today().normalize()
    )
    month_end = cutoff + pd.offsets.MonthEnd(0)
    if cutoff != month_end:
        returns = returns.loc[
            returns.index.to_period("M") < cutoff.to_period("M")
        ]
    if returns.empty:
        raise DataValidationError(
            "at least one completed monthly return is required"
        )
    return returns


def prepare_monthly_returns(
    request: OptimizationRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
) -> pd.DataFrame:
    converted: dict[str, pd.Series] = {}
    for asset in request.assets:
        if asset.symbol not in prices:
            raise DataValidationError(f"missing price series: {asset.symbol}")
        converted[asset.symbol] = _asset_price(
            request,
            asset.symbol,
            prices[asset.symbol],
            asset.currency,
            usdkrw,
        )
    # Keep the prior month-end as a warm-up price; requested period denotes
    # return rows rather than price rows.
    aligned = align_common_prices(converted, end=request.end)
    returns = _completed_monthly_returns(
        to_monthly_returns(month_end_prices(aligned)), request.end
    )
    if request.start is not None:
        returns = returns.loc[pd.Timestamp(request.start) :]
    return returns


def _benchmark_returns(
    request: OptimizationRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None,
) -> pd.Series | None:
    if request.benchmark is None:
        return None
    benchmark = request.benchmark
    if benchmark.symbol not in prices:
        raise DataValidationError(
            f"missing benchmark price series: {benchmark.symbol}"
        )
    price = _asset_price(
        request,
        benchmark.symbol,
        prices[benchmark.symbol],
        benchmark.currency,
        usdkrw,
    )
    frame = align_common_prices({benchmark.symbol: price}, end=request.end)
    returns = _completed_monthly_returns(
        to_monthly_returns(month_end_prices(frame)), request.end
    )
    if request.start is not None:
        returns = returns.loc[pd.Timestamp(request.start) :]
    return returns.iloc[:, 0].rename(benchmark.symbol)


def _frontier_landmarks_table(
    request: OptimizationRequest,
    stats,
    optimized,
    benchmark_returns: pd.Series | None,
    rf: float,
) -> pd.DataFrame:
    symbols = list(stats.expected_returns.index)
    rows: list[dict] = []

    if request.provided_weights is not None:
        weights = [float(request.provided_weights[symbol]) for symbol in symbols]
        expected_return = portfolio_expected_return(
            weights, stats.expected_returns
        )
        volatility = portfolio_volatility(weights, stats.covariance)
        row = {
            "kind": "provided",
            "label": "Provided Portfolio",
            "expected_return": expected_return,
            "volatility": volatility,
            "sharpe": (
                (expected_return - rf) / volatility if volatility > 0 else None
            ),
        }
        row.update(
            {
                f"weight_{symbol}": float(request.provided_weights[symbol])
                for symbol in symbols
            }
        )
        rows.append(row)

    optimized_row = {
        "kind": "optimized",
        "label": "Optimized Portfolio",
        "expected_return": float(optimized.expected_return),
        "volatility": float(optimized.volatility),
        "sharpe": float(optimized.sharpe),
    }
    optimized_row.update(
        {
            f"weight_{symbol}": float(optimized.weights[symbol])
            for symbol in symbols
        }
    )
    rows.append(optimized_row)

    if benchmark_returns is not None:
        aligned = benchmark_returns.dropna()
        if not aligned.empty:
            expected_return = float(aligned.mean() * 12.0)
            volatility = float(aligned.std(ddof=1) * (12.0**0.5))
            rows.append(
                {
                    "kind": "benchmark",
                    "label": "Benchmark",
                    "expected_return": expected_return,
                    "volatility": volatility,
                    "sharpe": (
                        (expected_return - rf) / volatility
                        if volatility > 0
                        else None
                    ),
                }
            )
    return pd.DataFrame(rows)


def _stress_periods_table(paths: Mapping[str, object]) -> pd.DataFrame:
    registry = {"COVID-19 Start": ("2020-01-01", "2020-03-31")}
    rows = []
    for label, (start, end) in registry.items():
        row = {"stress_period": label, "start": start, "end": end}
        has_data = False
        for name, path in paths.items():
            selected = path.returns.loc[pd.Timestamp(start) : pd.Timestamp(end)]
            if selected.empty:
                row[f"{name}_return"] = None
            else:
                row[f"{name}_return"] = float((1.0 + selected).prod() - 1.0)
                has_data = True
        if has_data:
            rows.append(row)
    return pd.DataFrame(rows)


def analyze_prices(
    request: OptimizationRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
    annual_rf: float | None = None,
) -> dict:
    """Optimization product orchestration over shared data/simulation/analytics."""
    monthly_returns = prepare_monthly_returns(request, prices, usdkrw)
    stats = annualized_statistics(monthly_returns)
    bounds = {
        asset.symbol: (asset.min_weight, asset.max_weight)
        for asset in request.assets
    }
    rf = _annual_rf(request, annual_rf)

    if (
        request.objective is OptimizationObjective.TARGET_VOLATILITY
        and request.target_volatility is None
    ):
        raise ValueError("target-volatility objective requires target_volatility")

    optimized = (
        maximum_sharpe(
            stats.expected_returns, stats.covariance, bounds, rf
        )
        if request.objective is OptimizationObjective.MAX_SHARPE
        else target_volatility(
            stats.expected_returns,
            stats.covariance,
            request.target_volatility,
            bounds,
            rf,
        )
    )
    frontier = build_efficient_frontier(
        stats.expected_returns,
        stats.covariance,
        bounds,
        rf,
        request.frontier_points,
    )

    paths: dict[str, object] = {
        "optimized": build_portfolio_path(
            monthly_returns,
            optimized.weights.to_dict(),
            request.rebalancing,
        )
    }
    expected = {"optimized": float(optimized.expected_return)}
    if request.provided_weights is not None:
        paths["provided"] = build_portfolio_path(
            monthly_returns,
            request.provided_weights,
            request.rebalancing,
        )
        expected["provided"] = portfolio_expected_return(
            [request.provided_weights[s] for s in monthly_returns.columns],
            stats.expected_returns,
        )

    benchmark_returns = _benchmark_returns(request, prices, usdkrw)
    if benchmark_returns is not None:
        benchmark_returns = benchmark_returns.loc[
            monthly_returns.index.min() : monthly_returns.index.max()
        ]
        paths["benchmark"] = type(
            "BenchmarkPath", (), {"returns": benchmark_returns}
        )()
        expected["benchmark"] = float(benchmark_returns.mean() * 12.0)

    performance, performance_table = historical.performance_table(
        paths, rf, initial_balance=1.0, expected_returns=expected
    )
    benchmark_summary, active_tables = historical.active_tables(
        paths, benchmark_returns
    )
    if benchmark_returns is not None:
        overlap = pd.concat(
            [paths["optimized"].returns, benchmark_returns],
            axis=1,
            join="inner",
        ).dropna()
        benchmark_summary["coverage"] = {
            "start": str(overlap.index.min().date()),
            "end": str(overlap.index.max().date()),
            "observations": len(overlap),
        }

    asset_names = {asset.symbol: asset.name for asset in request.assets}
    asset_performance_table = historical.asset_performance_table(
        monthly_returns, rf, asset_names=asset_names
    )
    asset_performance = historical.asset_performance_mapping(
        asset_performance_table
    )

    asset_stats_table = asset_performance_table.copy()
    asset_stats_table.insert(
        2,
        "expected_return",
        asset_stats_table["ticker"].map(stats.expected_returns),
    )
    asset_stats_table.insert(
        3,
        "volatility",
        asset_stats_table["ticker"].map(stats.volatility),
    )

    annual_table = pd.DataFrame(
        {
            name: historical.annual_returns(path.returns)
            for name, path in paths.items()
        }
    ).rename_axis("year").reset_index()
    monthly_table = pd.concat(
        [
            monthly_returns.add_prefix("asset_"),
            *[
                path.returns.rename(name)
                for name, path in paths.items()
            ],
        ],
        axis=1,
    ).reset_index(names="date")
    monthly_review = pd.concat(
        [
            monthly_returns_table(path.returns).assign(portfolio=name)
            for name, path in paths.items()
        ],
        ignore_index=True,
    )

    drawdown_rows = []
    for name, path in paths.items():
        table = drawdown_episodes(path.returns).copy()
        table.insert(0, "portfolio", name)
        drawdown_rows.append(table)
    drawdowns = (
        pd.concat(drawdown_rows, ignore_index=True)
        if drawdown_rows
        else pd.DataFrame()
    )

    investable_paths = dict(historical.portfolio_paths(paths))
    return_decomp = {
        name: return_decomposition(monthly_returns, path.weights)
        .iloc[-1]
        .to_dict()
        for name, path in investable_paths.items()
    }
    risk_decomp = {
        name: risk_contribution(
            pd.Series(path.weights.iloc[0], index=monthly_returns.columns),
            stats.covariance,
        ).to_dict()
        for name, path in investable_paths.items()
    }

    correlation = historical.correlations_table(
        monthly_returns, paths, benchmark_returns
    )
    growth = historical.growth_table(paths)
    drawdown_series_output = historical.drawdown_series_table(paths)
    annual_assets = historical.annual_asset_returns_table(monthly_returns)
    active_contribution = historical.active_contribution_table(
        monthly_returns, paths, benchmark_returns
    )
    up_down_market = historical.up_down_market_table(
        paths, benchmark_returns
    )
    up_down_scatter = historical.up_down_market_observations(
        paths, benchmark_returns
    )
    frontier_landmarks = _frontier_landmarks_table(
        request, stats, optimized, benchmark_returns, rf
    )
    stress_periods = _stress_periods_table(paths)
    metrics_table = historical.portfolio_metrics_table(
        paths, benchmark_returns, rf
    )
    asset_price_coverage = _asset_price_coverage(request, prices)

    canonical = CanonicalResult(
        configuration={
            "run_id": request.run_id,
            "market_data_source": "FinanceDataReader",
            "analysis_period": {
                "start": str(request.start) if request.start else None,
                "end": str(request.end) if request.end else None,
            },
            "assets": [
                {
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "currency": asset.currency,
                    "min_weight": asset.min_weight,
                    "max_weight": asset.max_weight,
                }
                for asset in request.assets
            ],
            "provided_weights": (
                dict(request.provided_weights)
                if request.provided_weights
                else None
            ),
            "benchmark": (
                {
                    "symbol": request.benchmark.symbol,
                    "name": request.benchmark.name,
                    "currency": request.benchmark.currency,
                }
                if request.benchmark
                else None
            ),
            "objective": request.objective,
            "target_volatility": request.target_volatility,
            "rebalancing_period": request.rebalancing,
            "risk_free": {
                "requested_mode": request.risk_free.mode,
                "effective_annual_rate": rf,
            },
            "frontier_points": request.frontier_points,
            "solver_routing": {"qp": "OSQP", "socp": "CLARABEL"},
        },
        data_coverage={
            "optimization_monthly_returns": {
                "start": str(monthly_returns.index.min().date()),
                "end": str(monthly_returns.index.max().date()),
                "observations": len(monthly_returns),
            },
            "benchmark_overlap": benchmark_summary.get("coverage"),
            "asset_prices": asset_price_coverage,
        },
        asset_statistics={
            "expected_returns": stats.expected_returns.to_dict(),
            "volatility": stats.volatility.to_dict(),
            "correlation": stats.correlation.to_dict(),
            "asset_performance": asset_performance,
        },
        optimization_result={
            "weights": optimized.weights.to_dict(),
            "expected_return": optimized.expected_return,
            "volatility": optimized.volatility,
            "sharpe": optimized.sharpe,
            "solver": optimized.solver,
            "status": optimized.status,
        },
        efficient_frontier=frontier.to_dict(orient="records"),
        portfolio_performance={
            **performance,
            "summary": performance,
            "trailing_returns": {
                name: trailing_returns(path.returns)
                for name, path in paths.items()
            },
            "annual_returns": annual_table.to_dict(orient="records"),
            "monthly_returns": monthly_table.to_dict(orient="records"),
            "drawdowns": drawdowns.to_dict(orient="records"),
            "rolling_returns": {
                name: {
                    "36m": {
                        str(k.date()): v
                        for k, v in rolling_returns(path.returns, 36)
                        .dropna()
                        .items()
                    },
                    "60m": {
                        str(k.date()): v
                        for k, v in rolling_returns(path.returns, 60)
                        .dropna()
                        .items()
                    },
                }
                for name, path in paths.items()
            },
        },
        benchmark_analytics={
            **benchmark_summary,
            "active_returns": {
                name: table.reset_index(names="date").to_dict(
                    orient="records"
                )
                for name, table in active_tables.items()
            },
        },
        correlations=correlation.to_dict(),
        return_decomposition=return_decomp,
        risk_decomposition=risk_decomp,
    )
    result = canonical.to_dict()

    benchmark_table = (
        pd.DataFrame(benchmark_summary)
        .T.rename_axis("portfolio")
        .reset_index()
        if benchmark_summary
        else pd.DataFrame()
    )
    rolling_summary = historical.rolling_summary_table(paths)
    rolling_raw = pd.concat(
        {
            name: pd.DataFrame(
                {
                    "36m": rolling_returns(path.returns, 36),
                    "60m": rolling_returns(path.returns, 60),
                }
            )
            for name, path in paths.items()
        },
        axis=1,
    ).reset_index(names="date")

    result["_tables"] = {
        "efficient_frontier": frontier,
        "frontier_landmarks": frontier_landmarks,
        "asset_statistics": asset_stats_table,
        "portfolio_asset_performance": asset_performance_table,
        "correlations": correlation.reset_index(names="series"),
        "portfolio_performance": performance_table,
        "annual_returns": annual_table,
        "monthly_returns": monthly_review,
        "monthly_return_series": monthly_table,
        "drawdowns": drawdowns,
        "return_decomposition": pd.DataFrame(return_decomp)
        .rename_axis("asset")
        .reset_index(),
        "risk_decomposition": pd.DataFrame(risk_decomp)
        .rename_axis("asset")
        .reset_index(),
        "benchmark_analytics": benchmark_table,
        "rolling_returns_raw": rolling_raw,
        "rolling_returns_summary": rolling_summary,
        "rolling_returns_3y": historical.rolling_review_table(paths, 3),
        "rolling_returns_5y": historical.rolling_review_table(paths, 5),
        "active_returns": (
            pd.concat(active_tables, names=["portfolio", "date"])
            .reset_index()
            if active_tables
            else pd.DataFrame()
        ),
        "portfolio_growth": growth,
        "drawdown_series": drawdown_series_output,
        "annual_asset_returns": annual_assets,
        "active_return_contribution": active_contribution,
        "up_down_market_performance": up_down_market,
        "up_down_market_scatter": up_down_scatter,
        "stress_periods": stress_periods,
        "portfolio_metrics": metrics_table,
    }
    return result
