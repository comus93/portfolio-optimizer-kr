"""Explicit live FDR diagnostic run; intentionally not part of pytest."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import numpy as np

from portfolio_optimizer_kr.data import FDRLoader
from portfolio_optimizer_kr.models import AssetSpec, OptimizationRequest, RiskFreeConfig, RiskFreeMode
from portfolio_optimizer_kr.pipeline import analyze_prices
from portfolio_optimizer_kr.report import write_analysis_run

ROOT = Path(__file__).parents[1]
GOLDEN = ROOT / "tests/golden/pv/260828_PTF_maxsharpe.md"
OUT = ROOT / "runs/20260828-pv-maxsharpe"
SYMBOLS = ("QQQ", "SPMO", "GDX", "GLD", "SLV", "AIA", "XLE", "PTF", "QLD")
MAX = (0.5, 0.5, 0.3, 0.3, 0.3, 0.3, 0.3, 0.5, 0.5)
PROVIDED = {"QQQ": .2, "SPMO": .1, "GDX": .1, "GLD": 0.0, "SLV": .1, "AIA": .15, "XLE": .15, "PTF": .1, "QLD": .1}


def golden_implied_rf(text: str) -> dict[str, float]:
    rows = re.findall(r"\| \d+ \| .*? \| ([\d.]+)% \| ([\d.]+)% \| ([\d.]+) \|", text)
    if len(rows) < 9:
        raise ValueError("could not parse nine PV asset-statistic rows")
    return {symbol: float(mu) / 100 - float(sharpe) * float(vol) / 100 for symbol, (mu, vol, sharpe) in zip(SYMBOLS, rows[:9])}


def main() -> None:
    golden = GOLDEN.read_text(encoding="utf-8")
    implied = golden_implied_rf(golden)
    rf = float(np.median(list(implied.values())))
    loader = FDRLoader()
    prices = loader.load_many([AssetSpec(s, currency="USD") for s in (*SYMBOLS, "SPY")], start="2016-07-01", end="2026-07-31")
    request = OptimizationRequest(
        assets=tuple(AssetSpec(s, currency="USD", max_weight=maximum) for s, maximum in zip(SYMBOLS, MAX)),
        run_id="20260828-pv-maxsharpe", start="2016-08-01", end="2026-07-31",
        provided_weights=PROVIDED, benchmark=AssetSpec("SPY", currency="USD"),
        risk_free=RiskFreeConfig(RiskFreeMode.FIXED, rf), frontier_points=100,
    )
    result = analyze_prices(request, prices)
    result["configuration"]["risk_free"]["parity_derivation"] = {"method": "median(expected_return - sharpe * volatility) from PV Efficient Frontier Assets", "per_asset": implied}
    write_analysis_run(result, OUT)
    weights = result["optimization_result"]["weights"]
    pv_weights = {"QQQ": .2461, "SPMO": .4072, "GDX": 0., "GLD": .3, "SLV": 0., "AIA": 0., "XLE": .0466, "PTF": 0., "QLD": 0.}
    parity = {
        "golden": {"assets": list(SYMBOLS), "bounds": dict(zip(SYMBOLS, MAX)), "provided_weights": PROVIDED, "benchmark": "SPY", "analysis_period": {"start": "2016-08", "end": "2026-07"}},
        "implied_risk_free": {"per_asset": implied, "min": min(implied.values()), "max": max(implied.values()), "spread": max(implied.values()) - min(implied.values()), "mean": float(np.mean(list(implied.values()))), "median_effective_annual_rate": rf},
        "fdr_coverage": result["data_coverage"],
        "optimizer": {"weights": weights, "weight_delta_vs_pv": {s: weights[s] - pv_weights[s] for s in SYMBOLS}, "expected_return": result["optimization_result"]["expected_return"], "volatility": result["optimization_result"]["volatility"], "sharpe": result["optimization_result"]["sharpe"], "pv": {"expected_return": .1721, "volatility": .1310, "sharpe": 1.13}},
        "frontier": {"point_count": len(result["efficient_frontier"]), "return_min": result["efficient_frontier"][0]["expected_return"], "return_max": result["efficient_frontier"][-1]["expected_return"], "shape_sanity": "ordered target-return minimum-variance frontier"},
        "diagnostic": "FDR vs PV data-source differences and CVXPY vs PV optimizer differences are not assigned a numeric pass/fail tolerance.",
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    (OUT / "parity.json").write_text(json.dumps(parity, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
