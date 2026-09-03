from __future__ import annotations

from typing import Any, Iterable

import pandas as pd


ASSET_PALETTE = [
    "#1200FF",
    "#50E2B0",
    "#85ACD0",
    "#2D7186",
    "#A45EE5",
    "#E59F3A",
    "#D45050",
    "#6F8F3D",
    "#7A5195",
    "#EF5675",
    "#FFA600",
    "#003F5C",
    "#665191",
    "#2F4B7C",
    "#F95D6A",
    "#88CCEE",
]


def asset_names_from_configuration(configuration: dict[str, Any]) -> dict[str, str]:
    return {
        str(asset.get("symbol")): str(asset.get("name") or "")
        for asset in configuration.get("assets", [])
        if isinstance(asset, dict) and asset.get("symbol") is not None
    }


def _sort_key(ticker: str, score: float, asset_names: dict[str, str]) -> tuple[float, str, str]:
    name = str(asset_names.get(ticker) or ticker)
    return (-float(score), name.casefold(), ticker.casefold())


def asset_display_order(
    result: dict[str, Any],
    asset_names: dict[str, str] | None = None,
) -> list[str]:
    """Return report-level asset order without mutating canonical configuration.

    Order contract: aggregate target weight across displayed portfolios DESC,
    then asset name ASC, then ticker ASC. Assets configured but not held are
    retained with score 0 and therefore sort to the bottom.
    """
    configuration = result.get("configuration") or {}
    names = dict(asset_names or asset_names_from_configuration(configuration))
    scores: dict[str, float] = {ticker: 0.0 for ticker in names}
    definitions = result.get("portfolio_definitions") or {}
    if isinstance(definitions, dict):
        for definition in definitions.values():
            if not isinstance(definition, dict):
                continue
            weights = definition.get("target_weights") or {}
            if not isinstance(weights, dict):
                continue
            for ticker, value in weights.items():
                key = str(ticker)
                scores.setdefault(key, 0.0)
                try:
                    scores[key] += float(value)
                except (TypeError, ValueError):
                    continue
    return sorted(scores, key=lambda ticker: _sort_key(ticker, scores[ticker], names))


def asset_display_order_from_allocations(frame: pd.DataFrame) -> list[str]:
    if frame.empty or "ticker" not in frame:
        return []
    names: dict[str, str] = {}
    scores: dict[str, float] = {}
    for _, row in frame.iterrows():
        ticker = str(row.get("ticker") or "")
        if not ticker:
            continue
        if ticker not in names:
            names[ticker] = str(row.get("name") or "")
        value = row.get("target_weight_pct", row.get("target_weight", 0.0))
        try:
            scores[ticker] = scores.get(ticker, 0.0) + float(value)
        except (TypeError, ValueError):
            scores.setdefault(ticker, 0.0)
    return sorted(scores, key=lambda ticker: _sort_key(ticker, scores[ticker], names))


def ordered_asset_names(
    asset_names: dict[str, str],
    order: Iterable[str],
) -> dict[str, str]:
    ordered: dict[str, str] = {}
    for ticker in order:
        key = str(ticker)
        if key in asset_names:
            ordered[key] = asset_names[key]
    for ticker, name in asset_names.items():
        if ticker not in ordered:
            ordered[ticker] = name
    return ordered


def asset_color_map(order: Iterable[str]) -> dict[str, str]:
    return {
        str(ticker): ASSET_PALETTE[index % len(ASSET_PALETTE)]
        for index, ticker in enumerate(order)
    }


def sort_asset_frame(
    frame: pd.DataFrame,
    order: Iterable[str],
    *,
    ticker_column: str = "ticker",
    strip_prefix: str | None = None,
) -> pd.DataFrame:
    if frame.empty or ticker_column not in frame:
        return frame
    ranking = {str(ticker): index for index, ticker in enumerate(order)}
    rendered = frame.copy()

    def key(value: Any) -> int:
        ticker = str(value)
        if strip_prefix and ticker.startswith(strip_prefix):
            ticker = ticker[len(strip_prefix) :]
        return ranking.get(ticker, len(ranking))

    rendered["_asset_display_order"] = rendered[ticker_column].map(key)
    rendered["_asset_display_ticker"] = rendered[ticker_column].astype(str)
    return (
        rendered.sort_values(
            ["_asset_display_order", "_asset_display_ticker"],
            kind="stable",
        )
        .drop(columns=["_asset_display_order", "_asset_display_ticker"])
        .reset_index(drop=True)
    )
