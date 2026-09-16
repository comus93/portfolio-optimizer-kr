from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from portfolio_optimizer_kr.optimize.robustness import build_asset_year_influence_table
from portfolio_optimizer_kr.report.loyo import asset_year_influence_review_table


def backfill(run_dir: str | Path) -> Path:
    root = Path(run_dir)
    result_path = root / "result.json"
    annual_path = root / "raw" / "annual_asset_returns.csv"
    loyo_path = root / "raw" / "loyo_robustness.csv"

    if not result_path.is_file():
        raise FileNotFoundError(f"missing canonical result: {result_path}")
    if not annual_path.is_file():
        raise FileNotFoundError(f"missing annual asset returns: {annual_path}")
    if not loyo_path.is_file():
        raise FileNotFoundError(f"missing LOYO robustness table: {loyo_path}")

    result = json.loads(result_path.read_text(encoding="utf-8"))
    annual = pd.read_csv(annual_path)
    loyo = pd.read_csv(loyo_path)
    influence = build_asset_year_influence_table(result, annual, loyo)
    if influence.empty:
        raise ValueError("Asset-Year Influence projection is empty")

    raw_dir = root / "raw"
    review_dir = root / "review"
    raw_dir.mkdir(exist_ok=True)
    review_dir.mkdir(exist_ok=True)

    influence.to_csv(root / "asset_year_influence.csv", index=False, encoding="utf-8")
    influence.to_csv(raw_dir / "asset_year_influence.csv", index=False, encoding="utf-8")
    asset_year_influence_review_table(influence).to_csv(
        review_dir / "asset_year_influence.csv", index=False, encoding="utf-8"
    )
    return root / "asset_year_influence.csv"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Backfill Asset-Year Influence from persisted LOYO artifacts without reoptimization."
    )
    parser.add_argument("run_dir")
    args = parser.parse_args()
    path = backfill(args.run_dir)
    print(path)


if __name__ == "__main__":
    main()
