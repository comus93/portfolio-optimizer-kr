from __future__ import annotations

from pathlib import Path

import pandas as pd


_ASSET_YEAR_PERCENTAGE_COLUMNS = (
    "asset_annual_return",
    "baseline_weight",
    "excluded_year_weight",
    "delta_weight",
)


def asset_year_influence_review_table(table: pd.DataFrame) -> pd.DataFrame:
    """Convert the raw Asset-Year Influence projection to review units.

    Raw finance values stay in decimal units. The review table exposes the same
    observations in percentage-point units and does not change their semantics.
    """
    if table.empty:
        return table.copy()

    out = table.copy()
    rename = {
        column: f"{column}_pct"
        for column in _ASSET_YEAR_PERCENTAGE_COLUMNS
        if column in out.columns
    }
    out = out.rename(columns=rename)
    for column in rename.values():
        out[column] = pd.to_numeric(out[column], errors="coerce") * 100.0
    return out


def write_asset_year_influence_review(
    result: dict,
    output_dir: str | Path,
) -> Path | None:
    """Overwrite the generic review projection with explicit LOYO review units."""
    tables = result.get("_tables")
    if not isinstance(tables, dict):
        return None
    table = tables.get("asset_year_influence")
    if not isinstance(table, pd.DataFrame) or table.empty:
        return None

    target = Path(output_dir) / "review" / "asset_year_influence.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    asset_year_influence_review_table(table).to_csv(target, index=False, encoding="utf-8")
    return target
