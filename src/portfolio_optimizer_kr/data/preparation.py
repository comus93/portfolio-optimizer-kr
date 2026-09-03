from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol

import pandas as pd

from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import AssetSpec, RiskFreeConfig, RiskFreeMode

from .transform import (
    align_common_prices,
    convert_usd_price_to_krw,
    month_end_prices,
    to_monthly_returns,
)


class HistoricalDataRequest(Protocol):
    """Structural request boundary shared by Optimization and Backtest."""

    assets: Sequence[AssetSpec]
    benchmark: AssetSpec | None
    start: str | pd.Timestamp | None
    end: str | pd.Timestamp | None
    risk_free: RiskFreeConfig


def resolve_annual_rf(
    request: HistoricalDataRequest,
    supplied_annual_rf: float | None,
) -> float:
    """Resolve the annual risk-free rate used by historical analysis.

    RF stays intentionally colocated with historical data preparation. It is a
    small shared input-resolution concern, not a separate capability/module.
    """
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
    request: HistoricalDataRequest,
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


def asset_price_coverage(
    request: HistoricalDataRequest,
    prices: Mapping[str, pd.Series],
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
    returns: pd.DataFrame,
    end: str | pd.Timestamp | None,
) -> pd.DataFrame:
    """Exclude only a terminal calendar month that is not yet complete."""
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
    request: HistoricalDataRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None = None,
) -> pd.DataFrame:
    """Normalize canonical asset prices into the shared monthly return matrix."""
    converted: dict[str, pd.Series] = {}
    for asset in request.assets:
        if asset.symbol not in prices:
            raise DataValidationError(f"missing price series: {asset.symbol}")
        converted[asset.symbol] = _asset_price(
            request,
            prices[asset.symbol],
            asset.currency,
            usdkrw,
        )
    # The prior month-end is retained as a warm-up price. Requested period
    # boundaries denote return rows, not raw price rows.
    aligned = align_common_prices(converted, end=request.end)
    returns = _completed_monthly_returns(
        to_monthly_returns(month_end_prices(aligned)), request.end
    )
    if request.start is not None:
        returns = returns.loc[pd.Timestamp(request.start) :]
    return returns


def prepare_benchmark_returns(
    request: HistoricalDataRequest,
    prices: Mapping[str, pd.Series],
    usdkrw: pd.Series | None,
) -> pd.Series | None:
    benchmark = request.benchmark
    if benchmark is None:
        return None
    if benchmark.symbol not in prices:
        raise DataValidationError(
            f"missing benchmark price series: {benchmark.symbol}"
        )
    price = _asset_price(
        request,
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
