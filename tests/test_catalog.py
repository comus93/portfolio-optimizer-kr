from pathlib import Path

import pandas as pd

from portfolio_optimizer_kr.catalog import load_catalog, search_catalog


def test_catalog_preserves_numeric_tickers_as_strings(tmp_path: Path):
    path = tmp_path / "catalog.csv"
    path.write_text(
        "symbol,name,currency\n140710,KODEX 운송,KRW\nQQQ,Invesco QQQ Trust,USD\n",
        encoding="utf-8",
    )
    catalog = load_catalog(path)
    assert catalog.loc[0, "symbol"] == "140710"
    assert catalog.loc[0, "currency"] == "KRW"


def test_catalog_search_matches_symbol_and_name_and_prioritizes_symbol_prefix():
    catalog = pd.DataFrame(
        [
            {"symbol": "QQQ", "name": "Invesco QQQ Trust"},
            {"symbol": "AQQQ", "name": "Other QQQ Fund"},
            {"symbol": "140710", "name": "KODEX 운송"},
        ]
    )
    for column in ["market", "country", "currency", "asset_type", "listing_date"]:
        catalog[column] = ""

    qqq = search_catalog(catalog, "QQQ")
    assert list(qqq["symbol"])[:2] == ["QQQ", "AQQQ"]

    korean = search_catalog(catalog, "운송")
    assert list(korean["symbol"]) == ["140710"]
