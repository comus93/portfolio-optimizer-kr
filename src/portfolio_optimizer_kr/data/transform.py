from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from portfolio_optimizer_kr.errors import DataValidationError


def _numeric_price_column(frame: pd.DataFrame, column: str) -> pd.Series:
    out = pd.to_numeric(frame[column], errors="coerce").dropna().astype(float)
    if out.empty:
        raise DataValidationError(f"{column} price series has no valid observations")
    out.index = pd.DatetimeIndex(out.index)
    return out.sort_index()


def select_canonical_price(frame: pd.DataFrame) -> pd.Series:
    """Select a generic price-like series.

    This helper remains appropriate for FX and other non-asset price series where
    total-return semantics are not required. Asset investment returns use
    ``select_total_return_price`` instead.
    """
    if frame.empty:
        raise DataValidationError("price frame is empty")
    column = "Adj Close" if "Adj Close" in frame.columns else "Close"
    if column not in frame.columns:
        raise DataValidationError("price frame has neither 'Adj Close' nor 'Close'")
    return _numeric_price_column(frame, column)


def select_total_return_price(
    frame: pd.DataFrame,
    *,
    close_is_total_return: bool = False,
) -> pd.Series:
    """Return a provider-verified total-return-capable asset price series.

    ``Adj Close`` remains the preferred explicit signal. Some providers expose
    adjusted/distribution-aware series under ``Close`` instead of a dedicated
    column. Callers may opt into that path only after verifying the provider and
    instrument semantics at the adapter boundary.
    """
    if frame.empty:
        raise DataValidationError("price frame is empty")

    if "Adj Close" in frame.columns:
        column = "Adj Close"
    elif close_is_total_return and "Close" in frame.columns:
        column = "Close"
    else:
        raise DataValidationError(
            "canonical total-return asset data is unavailable: provider response "
            "does not expose a verified dividend/distribution-adjusted series"
        )

    out = _numeric_price_column(frame, column)
    out.attrs["return_semantics"] = "total_return"
    out.attrs["source_column"] = column
    return out


def convert_usd_price_to_krw(price_usd: pd.Series, usdkrw: pd.Series) -> pd.Series:
    prices = price_usd.sort_index().astype(float)
    fx = usdkrw.sort_index().astype(float)
    aligned_fx = fx.reindex(prices.index, method="ffill")
    if aligned_fx.isna().any():
        first_missing = aligned_fx[aligned_fx.isna()].index[0]
        raise DataValidationError(
            f"no same-day or earlier USD/KRW rate for {first_missing.date()}"
        )
    out = (prices * aligned_fx).rename(price_usd.name)
    out.attrs.update(price_usd.attrs)
    return out


def align_common_prices(
    series_by_symbol: Mapping[str, pd.Series], start=None, end=None
) -> pd.DataFrame:
    if not series_by_symbol:
        raise DataValidationError("asset universe is empty")
    cleaned: dict[str, pd.Series] = {}
    for symbol, series in series_by_symbol.items():
        s = series.dropna().astype(float).sort_index().rename(symbol)
        if s.empty:
            raise DataValidationError(f"{symbol} has no valid price observations")
        cleaned[symbol] = s
    frame = pd.concat(cleaned.values(), axis=1, join="inner")
    if start is not None:
        frame = frame.loc[pd.Timestamp(start) :]
    if end is not None:
        frame = frame.loc[: pd.Timestamp(end)]
    frame = frame.dropna(how="any")
    if frame.empty:
        raise DataValidationError("assets have no common price coverage")
    return frame


def month_end_prices(prices: pd.DataFrame) -> pd.DataFrame:
    if prices.empty:
        raise DataValidationError("price frame is empty")
    return prices.sort_index().resample("ME").last().dropna(how="any")


def to_monthly_returns(monthly_prices: pd.DataFrame) -> pd.DataFrame:
    if len(monthly_prices) < 2:
        raise DataValidationError("at least two month-end prices are required")
    return monthly_prices.pct_change(fill_method=None).dropna(how="any")
