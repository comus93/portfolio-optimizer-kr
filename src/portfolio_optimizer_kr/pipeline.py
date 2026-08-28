from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from portfolio_optimizer_kr.analytics import (
    active_analytics, active_return_metrics, annual_returns, drawdown_episodes,
    performance_summary, return_decomposition,
    risk_contribution, rolling_returns, trailing_returns,
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


def prepare_monthly_returns(request: OptimizationRequest, prices: Mapping[str, pd.Series], usdkrw: pd.Series | None = None) -> pd.DataFrame:
    converted: dict[str, pd.Series] = {}
    for asset in request.assets:
        if asset.symbol not in prices:
            raise DataValidationError(f"missing price series: {asset.symbol}")
        converted[asset.symbol] = _asset_price(request, asset.symbol, prices[asset.symbol], asset.currency, usdkrw)
    return to_monthly_returns(month_end_prices(align_common_prices(converted, request.start, request.end)))


def _benchmark_returns(request: OptimizationRequest, prices: Mapping[str, pd.Series], usdkrw: pd.Series | None) -> pd.Series | None:
    if request.benchmark is None:
        return None
    benchmark = request.benchmark
    if benchmark.symbol not in prices:
        raise DataValidationError(f"missing benchmark price series: {benchmark.symbol}")
    price = _asset_price(request, benchmark.symbol, prices[benchmark.symbol], benchmark.currency, usdkrw)
    frame = align_common_prices({benchmark.symbol: price}, request.start, request.end)
    return to_monthly_returns(month_end_prices(frame)).iloc[:, 0].rename(benchmark.symbol)


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
    drawdown_rows = []
    for name, path in paths.items():
        table = drawdown_episodes(path.returns).copy()
        table.insert(0, "portfolio", name)
        drawdown_rows.append(table)
    drawdowns = pd.concat(drawdown_rows, ignore_index=True) if drawdown_rows else pd.DataFrame()
    return_decomp = {name: return_decomposition(monthly_returns, path.weights).iloc[-1].to_dict() for name, path in paths.items() if name != "benchmark"}
    risk_decomp = {name: risk_contribution(pd.Series(path.weights.iloc[0], index=monthly_returns.columns), stats.covariance).to_dict() for name, path in paths.items() if name != "benchmark"}
    correlation = _correlations(monthly_returns, paths, benchmark_returns)
    canonical = CanonicalResult(
        configuration={"assets": [a.symbol for a in request.assets], "benchmark": request.benchmark.symbol if request.benchmark else None, "objective": request.objective, "rebalancing": request.rebalancing, "risk_free_mode": request.risk_free.mode, "annual_risk_free_rate": rf, "frontier_points": request.frontier_points},
        data_coverage={"start": str(monthly_returns.index.min().date()), "end": str(monthly_returns.index.max().date()), "observations": len(monthly_returns)},
        asset_statistics={"expected_returns": stats.expected_returns.to_dict(), "volatility": stats.volatility.to_dict(), "correlation": stats.correlation.to_dict(), "asset_performance": asset_performance},
        optimization_result={"weights": optimized.weights.to_dict(), "expected_return": optimized.expected_return, "volatility": optimized.volatility, "sharpe": optimized.sharpe, "solver": optimized.solver, "status": optimized.status},
        efficient_frontier=frontier.to_dict(orient="records"),
        portfolio_performance={**performance, "summary": performance, "trailing_returns": {name: trailing_returns(path.returns) for name, path in paths.items()}, "annual_returns": annual_table.to_dict(orient="records"), "monthly_returns": monthly_table.to_dict(orient="records"), "drawdowns": drawdowns.to_dict(orient="records"), "rolling_returns": {name: {"36m": {str(k.date()): v for k, v in rolling_returns(path.returns, 36).dropna().items()}, "60m": {str(k.date()): v for k, v in rolling_returns(path.returns, 60).dropna().items()}} for name, path in paths.items()}},
        benchmark_analytics={**benchmark_summary, "active_returns": {name: table.reset_index(names="date").to_dict(orient="records") for name, table in active_tables.items()}},
        correlations=correlation.to_dict(), return_decomposition=return_decomp, risk_decomposition=risk_decomp,
    )
    result = canonical.to_dict()
    result["_tables"] = {"efficient_frontier": frontier, "asset_statistics": asset_stats_table, "correlations": correlation.reset_index(names="series"), "portfolio_performance": performance_table, "annual_returns": annual_table, "monthly_returns": monthly_table, "drawdowns": drawdowns, "return_decomposition": pd.DataFrame(return_decomp).rename_axis("asset").reset_index(), "risk_decomposition": pd.DataFrame(risk_decomp).rename_axis("asset").reset_index(), "benchmark_analytics": pd.DataFrame(benchmark_summary).T if benchmark_summary else pd.DataFrame(), "rolling_returns": pd.concat({name: pd.DataFrame(values) for name, values in {name: {"36m": rolling_returns(path.returns, 36), "60m": rolling_returns(path.returns, 60)} for name, path in paths.items()}.items()}, axis=1).reset_index(names="date"), "active_returns": pd.concat(active_tables, names=["portfolio", "date"]).reset_index() if active_tables else pd.DataFrame()}
    return result
