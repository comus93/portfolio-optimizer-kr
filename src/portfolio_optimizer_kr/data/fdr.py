from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from portfolio_optimizer_kr.errors import DataValidationError
from portfolio_optimizer_kr.models import AssetSpec
from .transform import select_canonical_price, select_total_return_price


class FDRLoader:
    """Thin FinanceDataReader adapter. Network behavior stays at this boundary."""

    def load(self, asset: AssetSpec, start=None, end=None) -> pd.Series:
        import FinanceDataReader as fdr

        frame = fdr.DataReader(asset.symbol, start, end)
        out = select_total_return_price(frame).rename(asset.symbol)
        out.attrs["provider"] = "FinanceDataReader"
        out.attrs["provider_symbol"] = asset.symbol
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
