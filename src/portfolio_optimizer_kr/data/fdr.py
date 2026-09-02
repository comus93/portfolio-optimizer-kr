from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import AssetSpec
from .transform import select_canonical_price, select_total_return_price


class FDRLoader:
    """Thin FinanceDataReader adapter. Network behavior stays at this boundary."""

    def __init__(self) -> None:
        self._kr_etf_symbols: set[str] | None = None

    @staticmethod
    def _split_source(symbol: str) -> tuple[str | None, str]:
        source, code = symbol.split(":", 1) if ":" in symbol else (None, symbol)
        return (source.upper() if source else None, code.upper())

    def _load_kr_etf_symbols(self, fdr) -> set[str]:
        if self._kr_etf_symbols is not None:
            return self._kr_etf_symbols
        try:
            listing = fdr.StockListing("ETF/KR")
        except Exception as exc:
            raise DataValidationError(
                "canonical total-return asset data is unavailable: unable to verify "
                "Korean ETF adjusted-price semantics from FinanceDataReader"
            ) from exc
        if listing is None or listing.empty:
            raise DataValidationError(
                "canonical total-return asset data is unavailable: FinanceDataReader "
                "Korean ETF listing is empty"
            )
        code_column = next(
            (
                column
                for column in ("Code", "Symbol", "Ticker", "code", "symbol", "ticker")
                if column in listing.columns
            ),
            None,
        )
        if code_column is None:
            raise DataValidationError(
                "canonical total-return asset data is unavailable: cannot identify "
                "FinanceDataReader Korean ETF symbol column"
            )
        symbols = {
            str(value).strip().upper()
            for value in listing[code_column].dropna()
            if str(value).strip()
        }
        self._kr_etf_symbols = symbols
        return symbols

    def _verified_naver_korean_etf_close(self, asset: AssetSpec, fdr) -> bool:
        source, code = self._split_source(asset.symbol)
        if source not in {None, "NAVER"}:
            return False
        if asset.currency.upper() != "KRW":
            return False
        if len(code) != 6 or not code.isdigit():
            return False
        return code in self._load_kr_etf_symbols(fdr)

    def load(self, asset: AssetSpec, start=None, end=None) -> pd.Series:
        import FinanceDataReader as fdr

        frame = fdr.DataReader(asset.symbol, start, end)
        close_is_total_return = False
        if "Adj Close" not in frame.columns:
            close_is_total_return = self._verified_naver_korean_etf_close(asset, fdr)
        out = select_total_return_price(
            frame,
            close_is_total_return=close_is_total_return,
        ).rename(asset.symbol)
        source, _ = self._split_source(asset.symbol)
        if close_is_total_return:
            provider_route = "NAVER"
        elif source:
            provider_route = source
        else:
            provider_route = "YAHOO" if "Adj Close" in frame.columns else "UNKNOWN"
        out.attrs["provider"] = "FinanceDataReader"
        out.attrs["provider_symbol"] = asset.symbol
        out.attrs["provider_route"] = provider_route
        return out

    def load_many(
        self, assets: Iterable[AssetSpec], start=None, end=None
    ) -> dict[str, pd.Series]:
        return {asset.symbol: self.load(asset, start, end) for asset in assets}

    def load_series(self, symbol: str, start=None, end=None) -> pd.Series:
        """Load a non-asset price-like series such as FX."""
        import FinanceDataReader as fdr

        frame = fdr.DataReader(symbol, start, end)
        return select_canonical_price(frame).rename(symbol)

    def load_economic_series(self, symbol: str, start=None, end=None) -> pd.Series:
        """Load a one-dimensional economic series such as FRED:TB3MS."""
        import FinanceDataReader as fdr

        frame = fdr.DataReader(symbol, start, end)
        if frame.empty:
            raise DataValidationError(f"economic series is empty: {symbol}")

        preferred = symbol.split(":", 1)[-1]
        if preferred in frame.columns:
            values = frame[preferred]
        elif len(frame.columns) == 1:
            values = frame.iloc[:, 0]
        else:
            numeric = frame.apply(pd.to_numeric, errors="coerce")
            usable = [column for column in numeric.columns if numeric[column].notna().any()]
            if len(usable) != 1:
                raise DataValidationError(
                    f"cannot identify one economic value column for {symbol}"
                )
            values = numeric[usable[0]]

        out = pd.to_numeric(values, errors="coerce").dropna().astype(float)
        if out.empty:
            raise DataValidationError(f"economic series has no numeric observations: {symbol}")
        out.index = pd.DatetimeIndex(out.index)
        return out.sort_index().rename(symbol)
