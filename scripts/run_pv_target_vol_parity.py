"""Live diagnostic for the PV 15% target-volatility golden; not a pytest."""
from __future__ import annotations

import json
from pathlib import Path
import shutil

import numpy as np
import pandas as pd

from portfolio_optimizer_kr.golden import load_target_vol_golden
from portfolio_optimizer_kr.optimize import target_volatility
from portfolio_optimizer_kr.runner import run_yaml
from portfolio_optimizer_kr.viewer import load_run_artifacts

ROOT = Path(__file__).parents[1]
CONFIG = ROOT / "configs/golden/pv-max-ret-vol15.yaml"
OUT = ROOT / "runs/20260828-pv-maxretvol15"
GOLDEN = ROOT / "tests/golden/pv/260828_PTF_maxRetVol15.md"


def main() -> None:
    golden = load_target_vol_golden(GOLDEN)
    if OUT.exists():
        shutil.rmtree(OUT)
    run_yaml(CONFIG, ROOT / "runs")
    artifacts = load_run_artifacts(OUT)
    result = artifacts.result
    optimized = result["optimization_result"]
    symbols = list(golden.symbols)
    covariance = pd.DataFrame(
        np.outer(golden.volatilities, golden.volatilities) * golden.correlation.to_numpy(),
        index=symbols,
        columns=symbols,
    )
    solver_only = target_volatility(
        golden.expected_returns,
        covariance,
        golden.target_volatility,
        bounds=golden.bounds,
    )
    stats = result["asset_statistics"]
    fdr_expected = pd.Series(stats["expected_returns"])[symbols]
    fdr_volatility = pd.Series(stats["volatility"])[symbols]
    fdr_correlation = pd.DataFrame(stats["correlation"]).loc[symbols, symbols]
    moment = pd.DataFrame({
        "ticker": symbols,
        "pv_expected_return": golden.expected_returns.values,
        "fdr_expected_return": fdr_expected.values,
        "expected_return_delta": (fdr_expected - golden.expected_returns).values,
        "pv_volatility": golden.volatilities.values,
        "fdr_volatility": fdr_volatility.values,
        "volatility_delta": (fdr_volatility - golden.volatilities).values,
    })
    solver_table = pd.DataFrame({
        "ticker": symbols,
        "pv_published_weight": golden.published_weights.values,
        "internal_weight_from_pv_moments": solver_only.weights[symbols].values,
        "fdr_internal_weight": [optimized["weights"][symbol] for symbol in symbols],
    })
    solver_table["weight_delta_solver_vs_pv"] = solver_table["internal_weight_from_pv_moments"] - solver_table["pv_published_weight"]
    solver_table["weight_delta_fdr_vs_pv"] = solver_table["fdr_internal_weight"] - solver_table["pv_published_weight"]
    correlation_delta = (fdr_correlation - golden.correlation).abs()
    performance = result["portfolio_performance"]["summary"]["optimized"]
    parity = {
        "golden": {"objective": "target_volatility", "target_volatility": golden.target_volatility, "period": golden.period, "assets": symbols, "bounds": golden.bounds, "provided_weights": golden.provided_weights.to_dict(), "published_weights": golden.published_weights.to_dict(), "benchmark": "SPY"},
        "moment_parity": {"per_asset": moment.to_dict(orient="records"), "correlation_max_abs_delta": float(correlation_delta.to_numpy().max()), "correlation_mean_abs_delta": float(correlation_delta.to_numpy().mean())},
        "solver_only_parity": {"internal_weights_from_pv_moments": solver_only.weights.to_dict(), "published_pv_weights": golden.published_weights.to_dict(), "weight_delta_vs_pv": dict(zip(symbols, solver_table["weight_delta_solver_vs_pv"])), "expected_return": solver_only.expected_return, "volatility": solver_only.volatility, "sharpe": solver_only.sharpe, "note_on_golden_rounding": "PV displayed moments, correlations, and weights are rounded; no exact-equality assertion is applied."},
        "optimizer": {"weights": optimized["weights"], "weight_delta_vs_pv": dict(zip(symbols, solver_table["weight_delta_fdr_vs_pv"])), "expected_return": optimized["expected_return"], "volatility": optimized["volatility"], "sharpe": optimized["sharpe"], "pv_published": {key: golden.published_metrics[key] for key in ("expected_return", "volatility", "sharpe")}},
        "frontier": {"point_count": len(result["efficient_frontier"]), "return_min": result["efficient_frontier"][0]["expected_return"], "return_max": result["efficient_frontier"][-1]["expected_return"]},
        "performance_diagnostic": {"optimized": {"cagr": {"internal": performance["cagr"], "pv": golden.published_metrics["cagr"], "delta": performance["cagr"] - golden.published_metrics["cagr"]}, "max_drawdown": {"internal": performance["max_drawdown"], "pv": golden.published_metrics["max_drawdown"], "delta": performance["max_drawdown"] - golden.published_metrics["max_drawdown"]}}},
        "data_coverage": result["data_coverage"],
        "note": "FDR market-data diagnostic; public PV moments and weights are rounded.",
    }
    moment.to_csv(OUT / "moment_parity.csv", index=False)
    solver_table.to_csv(OUT / "solver_parity.csv", index=False)
    (OUT / "parity.json").write_text(json.dumps(parity, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
