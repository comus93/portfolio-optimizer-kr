from __future__ import annotations

from pathlib import Path

import pandas as pd

CATALOG_COLUMNS = [
    "symbol",
    "name",
    "market",
    "country",
    "currency",
    "asset_type",
    "listing_date",
]


def empty_catalog() -> pd.DataFrame:
    return pd.DataFrame(columns=CATALOG_COLUMNS)


def load_catalog(path: str | Path) -> pd.DataFrame:
    source = Path(path)
    if not source.is_file():
        return empty_catalog()
    if source.suffix.lower() != ".csv":
        raise ValueError("v1 asset catalog loader currently supports CSV only")
    frame = pd.read_csv(source, dtype=str).fillna("")
    if "symbol" not in frame.columns or "name" not in frame.columns:
        raise ValueError("asset catalog requires symbol and name columns")
    for column in CATALOG_COLUMNS:
        if column not in frame.columns:
            frame[column] = ""
    return frame[CATALOG_COLUMNS].copy()


def search_catalog(catalog: pd.DataFrame, query: str, limit: int = 50) -> pd.DataFrame:
    if limit < 1:
        raise ValueError("limit must be positive")
    if catalog.empty:
        return catalog.head(0).copy()

    text = query.strip()
    if not text:
        return catalog.head(limit).copy()

    symbol = catalog["symbol"].astype(str)
    name = catalog["name"].astype(str)
    symbol_prefix = symbol.str.startswith(text, na=False)
    symbol_contains = symbol.str.contains(text, case=False, regex=False, na=False)
    name_contains = name.str.contains(text, case=False, regex=False, na=False)
    mask = symbol_contains | name_contains
    result = catalog.loc[mask].copy()
    if result.empty:
        return result
    result["_rank"] = 2
    result.loc[name_contains[mask], "_rank"] = 1
    result.loc[symbol_prefix[mask], "_rank"] = 0
    result = result.sort_values(["_rank", "symbol", "name"], kind="stable")
    return result.drop(columns="_rank").head(limit).reset_index(drop=True)
