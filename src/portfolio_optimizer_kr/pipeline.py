from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from portfolio_optimizer_kr.analytics import performance_summary, risk_contribution
from portfolio_optimizer_kr.data import (
    align_common_prices,
    convert_usd_price_to_krw,
    month_end_prices,
    to_monthly_returns,
)
from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import OptimizationObjective, OptimizationRequest, RiskFreeMode
from portfolio_optimizer_kr.optimize import build_efficient_frontier, maximum_sharpe, target_volatility
from portfolio_optimizer_kr.portfolio import build_portfolio_path
from portfolio_optimizer_kr.stats import annualized_statistics


def _annual_rf(request: OptimizationRequest, supplied_annual_rf: float | None) -> float:
    if request.risk_free.mode is RiskFreeMode.FIXED:
        if request.risk_free.annual_rate is None:
            raise ValueError("fixed risk-free mode requires annual_rate")
        return float(request.risk_free.annual_rate)
    if supplied_annual_rf is None:
        raise NotImplementedError(
            "U.S. 3-Month T-Bill provider is an external-data boundary; supply annual_rf until implemented"
        )
    return float(supplied_annual_rf)


def prepare_monthly_returns(
    request: OptimizationRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
) -> pd.DataFrame:
    currencies = {asset.currency.upper() for asset in request.assets}
    converted: dict[str, pd.Series] = {}
    mixed_with_krw = len(currencies) > 1 and "KRW" in currencies
    for asset in request.assets:
        if asset.symbol not in prices:
            raise DataValidationError(f"missing price series: {asset.symbol}")
        series = prices[asset.symbol]
        if mixed_with_krw and asset.currency.upper() == "USD":
            if usdkrw is None:
                raise DataValidationError("mixed KRW/USD universe requires USD/KRW series")
            series = convert_usd_price_to_krw(series, usdkrw)
        elif mixed_with_krw and asset.currency.upper() != "KRW":
            raise DataValidationError(f"unsupported mixed currency: {asset.currency}")
        converted[asset.symbol] = series

    aligned = align_common_prices(converted, request.start, request.end)
    return to_monthly_returns(month_end_prices(aligned))


def analyze_prices(
    request: OptimizationRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
    annual_rf: float | None = None,
) -> dict:
    monthly_returns = prepare_monthly_returns(request, prices, usdkrw)
    stats = annualized_statistics(monthly_returns)
    bounds = {a.symbol: (a.min_weight, a.max_weight) for a in request.assets}
    rf = _annual_rf(request, annual_rf)

    if request.objective is OptimizationObjective.MAX_SHARPE:
        optimized = maximum_sharpe(stats.expected_returns, stats.covariance, bounds, rf)
    else:
        if request.target_volatility is None:
            raise ValueError("target-volatility objective requires target_volatility")
        optimized = target_volatility(
            stats.expected_returns, stats.covariance, request.target_volatility, bounds, rf
        )

    frontier = build_efficient_frontier(
        stats.expected_returns, stats.covariance, bounds, rf, request.frontier_points
    )
    optimized_path = build_portfolio_path(
        monthly_returns, optimized.weights.to_dict(), request.rebalancing
    )

    result = {
        "data_coverage": {
            "start": str(monthly_returns.index.min().date()),
            "end": str(monthly_returns.index.max().date()),
            "observations": len(monthly_returns),
        },
        "asset_statistics": {
            "expected_returns": stats.expected_returns.to_dict(),
            "volatility": stats.volatility.to_dict(),
            "correlation": stats.correlation.to_dict(),
        },
        "optimization_result": {
            "weights": optimized.weights.to_dict(),
            "expected_return": optimized.expected_return,
            "volatility": optimized.volatility,
            "sharpe": optimized.sharpe,
            "solver": optimized.solver,
            "status": optimized.status,
        },
        "efficient_frontier": frontier.to_dict(orient="records"),
        "portfolio_performance": {
            "optimized": performance_summary(optimized_path.returns, rf)
        },
        "risk_decomposition": risk_contribution(optimized.weights, stats.covariance).to_dict(),
    }

    if request.provided_weights is not None:
        provided_path = build_portfolio_path(
            monthly_returns, request.provided_weights, request.rebalancing
        )
        result["portfolio_performance"]["provided"] = performance_summary(
            provided_path.returns, rf
        )

    return result
