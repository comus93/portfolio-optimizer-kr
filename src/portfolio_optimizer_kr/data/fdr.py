from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from portfolio_optimizer_kr.models import AssetSpec
from .transform import select_canonical_price


class FDRLoader:
    """Thin FinanceDataReader adapter. Network behavior stays at this boundary."""

    def load(self, asset: AssetSpec, start=None, end=None) -> pd.Series:
        import FinanceDataReader as fdr

        frame = fdr.DataReader(asset.symbol, start, end)
        return select_canonical_price(frame).rename(asset.symbol)

    def load_many(
        self, assets: Iterable[AssetSpec], start=None, end=None
    ) -> dict[str, pd.Series]:
        return {asset.symbol: self.load(asset, start, end) for asset in assets}

    def load_series(self, symbol: str, start=None, end=None) -> pd.Series:
        """Load a non-asset series such as FX. The exact FDR symbol is caller-owned."""
        import FinanceDataReader as fdr

        frame = fdr.DataReader(symbol, start, end)
        return select_canonical_price(frame).rename(symbol)
