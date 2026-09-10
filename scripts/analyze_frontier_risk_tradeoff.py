from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

import pandas as pd
import yaml

from portfolio_optimizer_kr.analytics.frontier_risk import frontier_risk_dataset
from portfolio_optimizer_kr.viewer.frontier_risk_dashboard import (
    build_frontier_interactive_payload,
    inject_frontier_risk_dashboard,
    write_frontier_interactive_payload,
)


def _asset_returns_from_review(monthly: pd.DataFrame) -> pd.DataFrame:
    asset_columns = [
        column
        for column in monthly.columns
        if column.startswith("asset_") and column.endswith("_return_pct")
    ]
    if not asset_columns:
        raise ValueError("monthly_return_series.csv has no asset return columns")

    data = {}
    for column in asset_columns:
        symbol = column[len("asset_") : -len("_return_pct")]
        data[symbol] = pd.to_numeric(monthly[column], errors="raise") / 100.0
    return pd.DataFrame(data, index=monthly.index)


def analyze_run(run_path: Path) -> Path:
    started = perf_counter()
    review = run_path / "review"
    frontier_path = review / "efficient_frontier.csv"
    monthly_path = review / "monthly_return_series.csv"
    input_path = run_path / "input.yaml"
    report_path = run_path / "report.html"

    for required in (frontier_path, monthly_path, input_path, report_path):
        if not required.exists():
            raise FileNotFoundError(required)

    frontier = pd.read_csv(frontier_path)
    monthly = pd.read_csv(monthly_path, parse_dates=["date"]).set_index("date")
    asset_returns = _asset_returns_from_review(monthly)

    config = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
    rebalancing = str(
        ((config.get("portfolio") or {}).get("rebalancing_period") or "monthly")
    )
    risk_free = config.get("risk_free") or {}
    annual_rf = float(risk_free.get("annual_rate_pct") or 0.0) / 100.0

    overlay, portfolio_returns = frontier_risk_dataset(
        frontier,
        asset_returns,
        rebalancing=rebalancing,
        annual_rf=annual_rf,
    )

    output_path = review / "frontier_risk_tradeoff.csv"
    overlay.to_csv(output_path, index=False)

    payload = build_frontier_interactive_payload(
        frontier,
        overlay,
        portfolio_returns,
        list(asset_returns.columns),
    )
    payload_path = review / "frontier_interactive.json"
    write_frontier_interactive_payload(payload_path, payload)
    inject_frontier_risk_dashboard(report_path, payload)

    elapsed = perf_counter() - started
    max_row = overlay.loc[overlay["ex_post_sharpe"].idxmax()]
    print(
        "frontier-risk: "
        f"points={len(overlay)} observations={int(max_row['observations'])} "
        f"elapsed_seconds={elapsed:.6f}"
    )
    print(
        "frontier-risk: max_ex_post_sharpe "
        f"point={int(max_row['point'])} sharpe={max_row['ex_post_sharpe']:.6f} "
        f"cagr={max_row['cagr_pct']:.4f}% "
        f"monthly_gpr={max_row['monthly_gain_to_pain_ratio']:.4f} "
        f"mdd={max_row['maximum_drawdown_pct']:.4f}% "
        f"tuw={max_row['tuw_pct']:.4f}% "
        f"pain={max_row['pain_index_pct']:.4f}% "
        f"pain_ratio={max_row['pain_ratio']:.4f} "
        f"max_underwater_months={int(max_row['max_underwater_months'])}"
    )
    print(output_path)
    print(payload_path)
    print(report_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_path", type=Path)
    args = parser.parse_args()
    analyze_run(args.run_path)


if __name__ == "__main__":
    main()
