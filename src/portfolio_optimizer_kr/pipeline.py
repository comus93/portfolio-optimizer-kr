from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from portfolio_optimizer_kr.analytics import (
    active_analytics, active_return_metrics, annual_returns, drawdown_episodes,
    drawdown_series, monthly_returns_table, performance_summary, portfolio_metrics,
    return_decomposition, risk_contribution, rolling_return_summary, rolling_returns,
    trailing_returns, wealth_series,
)
from portfolio_optimizer_kr.data import (
    align_common_prices, convert_usd_price_to_krw, month_end_prices, to_monthly_returns,
)
from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import OptimizationObjective, OptimizationRequest, RiskFreeMode
from portfolio_optimizer_kr.optimize import build_efficient_frontier, maximum_sharpe, target_volatility
from portfolio_optimizer_kr.portfolio import build_portfolio_path
from portfolio_optimizer_kr.report import CanonicalResult
from portfolio_optimizer_kr.stats import annualized_statistics, portfolio_expected_return


def _annual_rf(request: OptimizationRequest, supplied_annual_rf: float | None) -> float:
    if request.risk_free.mode is RiskFreeMode.FIXED:
        if request.risk_free.annual_rate is None:
            raise ValueError("fixed risk-free mode requires annual_rate")
        return float(request.risk_free.annual_rate)
    if supplied_annual_rf is None:
        raise NotImplementedError("U.S. 3-Month T-Bill provider is an external-data boundary; supply annual_rf until implemented")
    return float(supplied_annual_rf)


def _asset_price(request: OptimizationRequest, symbol: str, price: pd.Series, currency: str, usdkrw: pd.Series | None) -> pd.Series:
    asset_currencies = {asset.currency.upper() for asset in request.assets}
    if currency.upper() == "USD" and "KRW" in asset_currencies:
        if usdkrw is None:
            raise DataValidationError("mixed KRW/USD universe requires USD/KRW series")
        return convert_usd_price_to_krw(price, usdkrw)
    if currency.upper() not in {"KRW", "USD"}:
        raise DataValidationError(f"unsupported currency: {currency}")
    return price


def _completed_monthly_returns(
    returns: pd.DataFrame, end: str | pd.Timestamp | None
) -> pd.DataFrame:
    """Exclude only the terminal calendar month when it is not yet complete."""
    cutoff = pd.Timestamp(end).normalize() if end is not None else pd.Timestamp.today().normalize()
    month_end = cutoff + pd.offsets.MonthEnd(0)
    if cutoff != month_end:
        returns = returns.loc[returns.index.to_period("M") < cutoff.to_period("M")]
    if returns.empty:
        raise DataValidationError("at least one completed monthly return is required")
    return returns


def prepare_monthly_returns(request: OptimizationRequest, prices: Mapping[str, pd.Series], usdkrw: pd.Series | None = None) -> pd.DataFrame:
    converted: dict[str, pd.Series] = {}
    for asset in request.assets:
        if asset.symbol not in prices:
            raise DataValidationError(f"missing price series: {asset.symbol}")
        converted[asset.symbol] = _asset_price(request, asset.symbol, prices[asset.symbol], asset.currency, usdkrw)
    # Keep the prior month-end as a warm-up price; the requested period denotes return rows.
    aligned = align_common_prices(converted, end=request.end)
    returns = _completed_monthly_returns(
        to_monthly_returns(month_end_prices(aligned)), request.end
    )
    if request.start is not None:
        returns = returns.loc[pd.Timestamp(request.start):]
    return returns


def _benchmark_returns(request: OptimizationRequest, prices: Mapping[str, pd.Series], usdkrw: pd.Series | None) -> pd.Series | None:
    if request.benchmark is None:
        return None
    benchmark = request.benchmark
    if benchmark.symbol not in prices:
        raise DataValidationError(f"missing benchmark price series: {benchmark.symbol}")
    price = _asset_price(request, benchmark.symbol, prices[benchmark.symbol], benchmark.currency, usdkrw)
    frame = align_common_prices({benchmark.symbol: price}, end=request.end)
    returns = _completed_monthly_returns(
        to_monthly_returns(month_end_prices(frame)), request.end
    )
    if request.start is not None:
        returns = returns.loc[pd.Timestamp(request.start):]
    return returns.iloc[:, 0].rename(benchmark.symbol)


def _performance_table(paths: dict[str, object], rf: float, expected: dict[str, float]) -> tuple[dict, pd.DataFrame]:
    summary: dict = {}
    rows = []
    for name, path in paths.items():
        metrics = performance_summary(path.returns, rf)
        metrics["expected_return"] = expected.get(name)
        summary[name] = metrics
        rows.append({"portfolio": name, **metrics})
    return summary, pd.DataFrame(rows)


def _correlations(asset_returns: pd.DataFrame, paths: dict[str, object], benchmark: pd.Series | None) -> pd.DataFrame:
    inputs = [asset_returns]
    inputs.extend(path.returns.rename(name) for name, path in paths.items())
    if benchmark is not None and "benchmark" not in paths:
        inputs.append(benchmark.rename("benchmark"))
    return pd.concat(inputs, axis=1, join="inner").corr()


def _growth_table(paths: dict[str, object]) -> pd.DataFrame:
    values = {
        f"{name}_balance": wealth_series(path.returns)
        for name, path in paths.items()
    }
    return pd.DataFrame(values).rename_axis("date").reset_index()


def _drawdown_series_table(paths: dict[str, object]) -> pd.DataFrame:
    values = {
        f"{name}_drawdown": drawdown_series(path.returns)
        for name, path in paths.items()
    }
    return pd.DataFrame(values).rename_axis("date").reset_index()


def _annual_asset_returns(asset_returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for ticker in asset_returns:
        for year, value in annual_returns(asset_returns[ticker]).items():
            rows.append({"year": int(year), "ticker": ticker, "return": value})
    return pd.DataFrame(rows, columns=["year", "ticker", "return"])


def _active_contribution_table(
    asset_returns: pd.DataFrame, paths: dict[str, object], benchmark: pd.Series | None
) -> pd.DataFrame:
    if benchmark is None:
        return pd.DataFrame(columns=["date", "portfolio", "ticker", "cumulative_active_contribution"])
    rows = []
    for name in ("provided", "optimized"):
        path = paths.get(name)
        if path is None:
            continue
        joined = pd.concat([asset_returns, benchmark.rename("benchmark")], axis=1, join="inner").dropna()
        weights = path.weights.loc[joined.index, asset_returns.columns]
        contribution = weights.mul(joined[asset_returns.columns].sub(joined["benchmark"], axis=0)).cumsum()
        for ticker in contribution:
            rows.extend(
                {
                    "date": timestamp,
                    "portfolio": name,
                    "ticker": ticker,
                    "cumulative_active_contribution": value,
                }
                for timestamp, value in contribution[ticker].items()
            )
    return pd.DataFrame(rows, columns=["date", "portfolio", "ticker", "cumulative_active_contribution"])


def _up_down_market_table(paths: dict[str, object], benchmark: pd.Series | None) -> pd.DataFrame:
    if benchmark is None:
        return pd.DataFrame(columns=["portfolio", "market_type", "portfolio_return", "benchmark_return", "active_return", "occurrences"])
    rows = []
    for name in ("provided", "optimized"):
        path = paths.get(name)
        if path is None:
            continue
        joined = pd.concat([path.returns.rename("portfolio"), benchmark.rename("benchmark")], axis=1, join="inner").dropna()
        for market_type, selector in (("up", joined["benchmark"] > 0), ("down", joined["benchmark"] < 0)):
            selected = joined.loc[selector]
            if selected.empty:
                continue
            active = selected["portfolio"] - selected["benchmark"]
            above = active > 0
            below = active < 0
            rows.append({
                "portfolio": name, "market_type": market_type,
                "portfolio_return": float(selected["portfolio"].mean()),
                "benchmark_return": float(selected["benchmark"].mean()),
                "active_return": float(active.mean()), "occurrences": len(selected),
                "above_benchmark_count": int(above.sum()),
                "below_benchmark_count": int(below.sum()),
                "total_count": len(selected),
                "pct_above_benchmark": float(above.mean() * 100),
                "above_active_return": float(active.loc[above].mean()) if above.any() else None,
                "below_active_return": float(active.loc[below].mean()) if below.any() else None,
            })
    return pd.DataFrame(rows)


def _stress_periods_table(paths: dict[str, object]) -> pd.DataFrame:
    registry = {"COVID-19 Start": ("2020-01-01", "2020-03-31")}
    rows = []
    for label, (start, end) in registry.items():
        row = {"stress_period": label, "start": start, "end": end}
        has_data = False
        for name in ("provided", "optimized", "benchmark"):
            path = paths.get(name)
            if path is None:
                continue
            selected = path.returns.loc[pd.Timestamp(start) : pd.Timestamp(end)]
            if selected.empty:
                row[f"{name}_return"] = None
            else:
                row[f"{name}_return"] = float((1.0 + selected).prod() - 1.0)
                has_data = True
        if has_data:
            rows.append(row)
    return pd.DataFrame(rows)


def _portfolio_metrics_table(paths: dict[str, object], benchmark: pd.Series | None, rf: float) -> pd.DataFrame:
    if benchmark is None:
        return pd.DataFrame(columns=["metric", "provided", "optimized"])
    by_portfolio = {
        name: portfolio_metrics(path.returns, benchmark, rf)
        for name, path in paths.items()
        if name in {"provided", "optimized"}
    }
    metric_names = sorted({metric for values in by_portfolio.values() for metric in values})
    return pd.DataFrame([
        {"metric": metric, **{name: values.get(metric) for name, values in by_portfolio.items()}}
        for metric in metric_names
    ])


def analyze_prices(request: OptimizationRequest, prices: Mapping[str, pd.Series], usdkrw: pd.Series | None = None, annual_rf: float | None = None) -> dict:
    monthly_returns = prepare_monthly_returns(request, prices, usdkrw)
    stats = annualized_statistics(monthly_returns)
    bounds = {a.symbol: (a.min_weight, a.max_weight) for a in request.assets}
    rf = _annual_rf(request, annual_rf)
    if request.objective is OptimizationObjective.TARGET_VOLATILITY and request.target_volatility is None:
        raise ValueError("target-volatility objective requires target_volatility")
    optimized = (maximum_sharpe(stats.expected_returns, stats.covariance, bounds, rf)
                 if request.objective is OptimizationObjective.MAX_SHARPE else
                 target_volatility(stats.expected_returns, stats.covariance, request.target_volatility, bounds, rf))
    frontier = build_efficient_frontier(stats.expected_returns, stats.covariance, bounds, rf, request.frontier_points)
    paths: dict[str, object] = {"optimized": build_portfolio_path(monthly_returns, optimized.weights.to_dict(), request.rebalancing)}
    expected = {"optimized": optimized.expected_return}
    if request.provided_weights is not None:
        paths["provided"] = build_portfolio_path(monthly_returns, request.provided_weights, request.rebalancing)
        expected["provided"] = portfolio_expected_return([request.provided_weights[s] for s in monthly_returns.columns], stats.expected_returns)
    benchmark_returns = _benchmark_returns(request, prices, usdkrw)
    if benchmark_returns is not None:
        benchmark_returns = benchmark_returns.loc[
            monthly_returns.index.min() : monthly_returns.index.max()
        ]
        paths["benchmark"] = type("BenchmarkPath", (), {"returns": benchmark_returns})()
        expected["benchmark"] = float(benchmark_returns.mean() * 12.0)
    performance, performance_table = _performance_table(paths, rf, expected)
    active_tables: dict[str, pd.DataFrame] = {}
    benchmark_summary: dict = {}
    if benchmark_returns is not None:
        for name, path in paths.items():
            if name == "benchmark":
                continue
            active_tables[name] = active_analytics(path.returns, benchmark_returns)
            benchmark_summary[name] = active_return_metrics(path.returns, benchmark_returns)
        overlap = pd.concat([paths["optimized"].returns, benchmark_returns], axis=1, join="inner").dropna()
        benchmark_summary["coverage"] = {"start": str(overlap.index.min().date()), "end": str(overlap.index.max().date()), "observations": len(overlap)}
    asset_performance = {symbol: {**performance_summary(monthly_returns[symbol], rf), "trailing_returns": trailing_returns(monthly_returns[symbol])} for symbol in monthly_returns}
    asset_stats_table = pd.DataFrame([
        {"ticker": symbol, "expected_return": stats.expected_returns[symbol], "volatility": stats.volatility[symbol], **performance_summary(monthly_returns[symbol], rf), **trailing_returns(monthly_returns[symbol])}
        for symbol in monthly_returns
    ])
    annual_table = pd.DataFrame({name: annual_returns(path.returns) for name, path in paths.items()}).rename_axis("year").reset_index()
    monthly_table = pd.concat([monthly_returns.add_prefix("asset_"), *[path.returns.rename(name) for name, path in paths.items()]], axis=1).reset_index(names="date")
    monthly_review = pd.concat([
        monthly_returns_table(path.returns).assign(portfolio=name)
        for name, path in paths.items()
    ], ignore_index=True)
    drawdown_rows = []
    for name, path in paths.items():
        table = drawdown_episodes(path.returns).copy()
        table.insert(0, "portfolio", name)
        drawdown_rows.append(table)
    drawdowns = pd.concat(drawdown_rows, ignore_index=True) if drawdown_rows else pd.DataFrame()
    return_decomp = {name: return_decomposition(monthly_returns, path.weights).iloc[-1].to_dict() for name, path in paths.items() if name != "benchmark"}
    risk_decomp = {name: risk_contribution(pd.Series(path.weights.iloc[0], index=monthly_returns.columns), stats.covariance).to_dict() for name, path in paths.items() if name != "benchmark"}
    correlation = _correlations(monthly_returns, paths, benchmark_returns)
    growth = _growth_table(paths)
    drawdown_series_output = _drawdown_series_table(paths)
    annual_assets = _annual_asset_returns(monthly_returns)
    active_contribution = _active_contribution_table(monthly_returns, paths, benchmark_returns)
    up_down_market = _up_down_market_table(paths, benchmark_returns)
    stress_periods = _stress_periods_table(paths)
    metrics_table = _portfolio_metrics_table(paths, benchmark_returns, rf)
    canonical = CanonicalResult(
        configuration={"run_id": request.run_id, "market_data_source": "FinanceDataReader", "analysis_period": {"start": str(request.start) if request.start else None, "end": str(request.end) if request.end else None}, "assets": [{"symbol": a.symbol, "name": a.name, "currency": a.currency, "min_weight": a.min_weight, "max_weight": a.max_weight} for a in request.assets], "provided_weights": dict(request.provided_weights) if request.provided_weights else None, "benchmark": ({"symbol": request.benchmark.symbol, "name": request.benchmark.name, "currency": request.benchmark.currency} if request.benchmark else None), "objective": request.objective, "target_volatility": request.target_volatility, "rebalancing_period": request.rebalancing, "risk_free": {"requested_mode": request.risk_free.mode, "effective_annual_rate": rf}, "frontier_points": request.frontier_points, "solver_routing": {"qp": "OSQP", "socp": "CLARABEL"}},
        data_coverage={"optimization_monthly_returns": {"start": str(monthly_returns.index.min().date()), "end": str(monthly_returns.index.max().date()), "observations": len(monthly_returns)}, "benchmark_overlap": benchmark_summary.get("coverage")},
        asset_statistics={"expected_returns": stats.expected_returns.to_dict(), "volatility": stats.volatility.to_dict(), "correlation": stats.correlation.to_dict(), "asset_performance": asset_performance},
        optimization_result={"weights": optimized.weights.to_dict(), "expected_return": optimized.expected_return, "volatility": optimized.volatility, "sharpe": optimized.sharpe, "solver": optimized.solver, "status": optimized.status},
        efficient_frontier=frontier.to_dict(orient="records"),
        portfolio_performance={**performance, "summary": performance, "trailing_returns": {name: trailing_returns(path.returns) for name, path in paths.items()}, "annual_returns": annual_table.to_dict(orient="records"), "monthly_returns": monthly_table.to_dict(orient="records"), "drawdowns": drawdowns.to_dict(orient="records"), "rolling_returns": {name: {"36m": {str(k.date()): v for k, v in rolling_returns(path.returns, 36).dropna().items()}, "60m": {str(k.date()): v for k, v in rolling_returns(path.returns, 60).dropna().items()}} for name, path in paths.items()}},
        benchmark_analytics={**benchmark_summary, "active_returns": {name: table.reset_index(names="date").to_dict(orient="records") for name, table in active_tables.items()}},
        correlations=correlation.to_dict(), return_decomposition=return_decomp, risk_decomposition=risk_decomp,
    )
    result = canonical.to_dict()
    benchmark_table = pd.DataFrame(benchmark_summary).T.rename_axis("portfolio").reset_index() if benchmark_summary else pd.DataFrame()
    rolling_summary = pd.DataFrame([{"roll_period_years": years, **{f"{name}_{metric}": value for name, path in paths.items() for metric, value in rolling_return_summary(path.returns, years).items()}} for years in (1, 3, 5, 7)])
    def rolling_review(years: int) -> pd.DataFrame:
        series = [rolling_returns(path.returns, years * 12).rename(f"{name}_annualized_return_pct") * 100 for name, path in paths.items()]
        return pd.concat(series, axis=1).dropna(how="all").reset_index(names="date")
    result["_tables"] = {"efficient_frontier": frontier, "asset_statistics": asset_stats_table, "correlations": correlation.reset_index(names="series"), "portfolio_performance": performance_table, "annual_returns": annual_table, "monthly_returns": monthly_review, "monthly_return_series": monthly_table, "drawdowns": drawdowns, "return_decomposition": pd.DataFrame(return_decomp).rename_axis("asset").reset_index(), "risk_decomposition": pd.DataFrame(risk_decomp).rename_axis("asset").reset_index(), "benchmark_analytics": benchmark_table, "rolling_returns_raw": pd.concat({name: pd.DataFrame(values) for name, values in {name: {"36m": rolling_returns(path.returns, 36), "60m": rolling_returns(path.returns, 60)} for name, path in paths.items()}.items()}, axis=1).reset_index(names="date"), "rolling_returns_summary": rolling_summary, "rolling_returns_3y": rolling_review(3), "rolling_returns_5y": rolling_review(5), "active_returns": pd.concat(active_tables, names=["portfolio", "date"]).reset_index() if active_tables else pd.DataFrame(), "portfolio_growth": growth, "drawdown_series": drawdown_series_output, "annual_asset_returns": annual_assets, "active_return_contribution": active_contribution, "up_down_market_performance": up_down_market, "stress_periods": stress_periods, "portfolio_metrics": metrics_table}
    return result
