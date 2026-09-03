from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from portfolio_optimizer_kr.config import hydrate_asset_names
from portfolio_optimizer_kr.data import FDRLoader


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Snapshot FDR ETF names into an existing Optimization/Backtest YAML."
    )
    parser.add_argument("config")
    args = parser.parse_args()

    path = Path(args.config)
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    hydrated = hydrate_asset_names(loaded, FDRLoader())
    path.write_text(
        yaml.safe_dump(hydrated, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    for asset in hydrated.get("assets", []):
        print(f"{asset['symbol']}\t{asset['name']}")
    benchmark = hydrated.get("benchmark")
    if isinstance(benchmark, dict) and benchmark.get("symbol"):
        print(f"benchmark:{benchmark['symbol']}\t{benchmark.get('name', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
