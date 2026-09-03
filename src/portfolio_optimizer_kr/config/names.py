from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from portfolio_optimizer_kr.models import AssetSpec

from .yaml import ConfigValidationError


def hydrate_asset_names(config: Mapping[str, Any], loader) -> dict[str, Any]:
    """Return a config copy whose asset/benchmark names come from provider metadata."""
    out = deepcopy(dict(config))
    asset_rows = out.get("assets")
    if not isinstance(asset_rows, list) or not asset_rows:
        raise ConfigValidationError("assets must be a non-empty list")

    specs: dict[str, AssetSpec] = {}
    for index, raw in enumerate(asset_rows):
        if not isinstance(raw, dict):
            raise ConfigValidationError(f"assets[{index}] must be a mapping")
        symbol = str(raw.get("symbol") or "").strip()
        if not symbol:
            raise ConfigValidationError(f"assets[{index}].symbol is required")
        currency = str(raw.get("currency") or "KRW").upper()
        specs.setdefault(symbol, AssetSpec(symbol=symbol, currency=currency))

    benchmark = out.get("benchmark")
    if isinstance(benchmark, dict):
        symbol = str(benchmark.get("symbol") or "").strip()
        if symbol and symbol not in specs:
            currency = str(benchmark.get("currency") or "KRW").upper()
            specs[symbol] = AssetSpec(symbol=symbol, currency=currency)
    elif isinstance(benchmark, str) and benchmark.strip():
        symbol = benchmark.strip()
        matched = next(
            (
                row
                for row in asset_rows
                if str(row.get("symbol") or "").strip() == symbol
            ),
            None,
        )
        if matched is None:
            raise ConfigValidationError(
                "string benchmark must match an asset or use mapping form with currency for name hydration"
            )
        benchmark = {
            "symbol": symbol,
            "currency": str(matched.get("currency") or "KRW").upper(),
        }
        out["benchmark"] = benchmark

    resolved = loader.load_asset_names(specs.values())
    missing = [symbol for symbol in specs if not resolved.get(symbol)]
    if missing:
        raise ConfigValidationError(
            "FDR ETF name metadata unavailable for: " + ", ".join(missing)
        )

    for row in asset_rows:
        symbol = str(row.get("symbol") or "").strip()
        row["name"] = resolved[symbol]

    benchmark = out.get("benchmark")
    if isinstance(benchmark, dict):
        symbol = str(benchmark.get("symbol") or "").strip()
        if symbol:
            benchmark["name"] = resolved[symbol]
    return out
