"""Live diagnostic for the PV 15% target-volatility golden; not a pytest."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from portfolio_optimizer_kr.runner import run_yaml
from portfolio_optimizer_kr.viewer import load_run_artifacts

ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "configs/golden/pv-max-ret-vol15.yaml"
OUT = ROOT / "runs/20260828-pv-maxretvol15"
PV_WEIGHTS = {"QQQ": .1419, "SPMO": .4430, "GDX": 0., "GLD": .3, "SLV": 0., "AIA": 0., "XLE": .022, "PTF": 0., "QLD": .0931}


def main() -> None:
    run_yaml(CONFIG, ROOT / "runs")
    artifacts = load_run_artifacts(OUT)
    result = artifacts.result
    optimized = result["optimization_result"]
    parity = {
        "golden": {"objective": "target_volatility", "target_volatility": .15, "period": {"start": "2016-08", "end": "2026-07"}, "published_weights": PV_WEIGHTS, "benchmark": "SPY"},
        "optimizer": {"weights": optimized["weights"], "weight_delta_vs_pv": {key: optimized["weights"][key] - value for key, value in PV_WEIGHTS.items()}, "expected_return": optimized["expected_return"], "volatility": optimized["volatility"], "sharpe": optimized["sharpe"], "pv_published": {"expected_return": .1876, "volatility": .1489, "sharpe": 1.10}},
        "frontier": {"point_count": len(result["efficient_frontier"]), "return_min": result["efficient_frontier"][0]["expected_return"], "return_max": result["efficient_frontier"][-1]["expected_return"]},
        "data_coverage": result["data_coverage"],
        "note": "FDR market-data diagnostic; public PV moments and weights are rounded.",
    }
    pd.DataFrame({"ticker": list(PV_WEIGHTS), "pv_published_weight": list(PV_WEIGHTS.values()), "fdr_internal_weight": [optimized["weights"][ticker] for ticker in PV_WEIGHTS], "weight_delta_vs_pv": [optimized["weights"][ticker] - value for ticker, value in PV_WEIGHTS.items()]}).to_csv(OUT / "solver_parity.csv", index=False)
    stats = result["asset_statistics"]
    pd.DataFrame({"ticker": list(PV_WEIGHTS), "fdr_expected_return": [stats["expected_returns"][ticker] for ticker in PV_WEIGHTS], "fdr_volatility": [stats["volatility"][ticker] for ticker in PV_WEIGHTS]}).to_csv(OUT / "moment_parity.csv", index=False)
    (OUT / "parity.json").write_text(json.dumps(parity, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
