from __future__ import annotations

from collections.abc import Mapping
from typing import Any


_KAW_NATIVE_ASSETS: tuple[dict[str, str], ...] = (
    {"symbol": "133690", "name": "TIGER 미국나스닥100", "currency": "KRW"},
    {"symbol": "402970", "name": "ACE 미국배당다우존스", "currency": "KRW"},
    {"symbol": "069500", "name": "KODEX 200", "currency": "KRW"},
    {"symbol": "192090", "name": "TIGER 차이나CSI300", "currency": "KRW"},
    {"symbol": "200250", "name": "KIWOOM 인도Nifty50(합성)", "currency": "KRW"},
    {"symbol": "101280", "name": "KODEX 일본TOPIX100", "currency": "KRW"},
    {"symbol": "267440", "name": "RISE 미국장기국채선물(H)", "currency": "KRW"},
    {"symbol": "385560", "name": "RISE KIS국고채30년Enhanced", "currency": "KRW"},
    {"symbol": "GLD", "name": "SPDR Gold Shares", "currency": "USD"},
)

_KAW_CORE_ASSETS: tuple[dict[str, str], ...] = (
    {"symbol": "QQQ", "name": "Invesco QQQ Trust  Series 1", "currency": "USD"},
    {"symbol": "SCHD", "name": "Schwab US Dividend Equity ETF", "currency": "USD"},
    {"symbol": "EWY", "name": "Ishares Msci South Korea ETF", "currency": "USD"},
    {"symbol": "192090", "name": "TIGER 차이나CSI300", "currency": "KRW"},
    {"symbol": "200250", "name": "KIWOOM 인도Nifty50(합성)", "currency": "KRW"},
    {"symbol": "EWJ", "name": "iShares MSCI Japan ETF", "currency": "USD"},
    {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "currency": "USD"},
    {"symbol": "GLD", "name": "SPDR Gold Shares", "currency": "USD"},
)

KAW_BENCHMARK_PRESETS: dict[str, dict[str, Any]] = {
    "kaw_native": {
        "name": "KAW Native Proxy",
        "usable_from": "2021-11",
        "assets": _KAW_NATIVE_ASSETS,
        "weights_pct": {
            "133690": 10.0,
            "402970": 10.0,
            "069500": 8.0,
            "192090": 8.5,
            "200250": 8.5,
            "101280": 5.0,
            "267440": 15.0,
            "385560": 15.0,
            "GLD": 20.0,
        },
    },
    "kaw_core": {
        "name": "KAW Core Revised Internal",
        "usable_from": "2014-07",
        "assets": _KAW_CORE_ASSETS,
        "weights_pct": {
            "QQQ": 10.0,
            "SCHD": 10.0,
            "EWY": 8.0,
            "192090": 8.5,
            "200250": 8.5,
            "EWJ": 5.0,
            "TLT": 30.0,
            "GLD": 20.0,
        },
    },
}

KAW_BENCHMARK_ALIASES: dict[str, str] = {
    "kaw_native": "kaw_native",
    "kaw_short": "kaw_native",
    "kaw_core": "kaw_core",
    "kaw_long": "kaw_core",
}


def _normalise_preset(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def benchmark_preset_id(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return KAW_BENCHMARK_ALIASES.get(_normalise_preset(value))


def materialize_benchmark_preset(config: Mapping[str, Any]) -> dict[str, Any]:
    """Expand a KAW benchmark shortcut into an explicit reproducible config.

    Non-preset benchmark values are returned unchanged. Existing asset rows are
    preserved, while missing benchmark constituents are appended to the shared
    Backtest asset universe.
    """
    effective = dict(config)
    preset_id = benchmark_preset_id(effective.get("benchmark"))
    if preset_id is None:
        return effective

    preset = KAW_BENCHMARK_PRESETS[preset_id]
    raw_assets = effective.get("assets")
    assets = list(raw_assets) if isinstance(raw_assets, list) else []
    positions: dict[str, int] = {}
    for index, raw in enumerate(assets):
        if isinstance(raw, Mapping):
            symbol = str(raw.get("symbol") or "").strip()
            if symbol:
                positions[symbol] = index

    for preset_asset in preset["assets"]:
        symbol = preset_asset["symbol"]
        if symbol in positions:
            current = assets[positions[symbol]]
            if isinstance(current, Mapping):
                row = dict(current)
                row.setdefault("name", preset_asset["name"])
                row.setdefault("currency", preset_asset["currency"])
                assets[positions[symbol]] = row
            continue
        positions[symbol] = len(assets)
        assets.append(dict(preset_asset))

    effective["assets"] = assets
    effective["benchmark"] = {
        "type": "portfolio",
        "preset": preset_id,
        "name": preset["name"],
        "usable_from": preset["usable_from"],
        "weights_pct": dict(preset["weights_pct"]),
    }
    return effective
