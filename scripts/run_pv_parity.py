"""Explicit live FDR diagnostic run; intentionally not part of pytest."""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from portfolio_optimizer_kr.data import FDRLoader
from portfolio_optimizer_kr.models import AssetSpec, OptimizationRequest, RiskFreeConfig, RiskFreeMode
from portfolio_optimizer_kr.pipeline import analyze_prices
from portfolio_optimizer_kr.optimize import maximum_sharpe
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


def golden_moments(text: str) -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    rows = re.findall(r"\| \d+ \| .*? \| ([\d.]+)% \| ([\d.]+)% \| ([\d.]+) \|", text)[:9]
    expected = pd.Series([float(row[0]) / 100 for row in rows], index=SYMBOLS)
    volatility = pd.Series([float(row[1]) / 100 for row in rows], index=SYMBOLS)
    section = re.search(r"#### Asset Correlations(.*?)#### Efficient Frontier\s*$", text, re.S | re.M)
    if section is None:
        raise ValueError("could not locate PV asset-correlation table")
    lines = section.group(1).splitlines()
    corr_rows = []
    for line in lines:
        cells = [cell.strip().replace("\\-", "-") for cell in line.split("|")[1:-1]]
        if len(cells) == 11 and cells[1] in SYMBOLS:
            corr_rows.append([float(cell) for cell in cells[2:]])
    correlation = pd.DataFrame(corr_rows[:9], index=SYMBOLS, columns=SYMBOLS)
    return expected, volatility, correlation


def main() -> None:
    golden = GOLDEN.read_text(encoding="utf-8")
    implied = golden_implied_rf(golden)
    pv_expected, pv_volatility, pv_correlation = golden_moments(golden)
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
    rolling = pd.read_csv(OUT / "rolling_returns_summary.csv")
    pv_rolling = {1: {"provided": (21.22, 81.63, -19.44), "optimized": (19.33, 46.78, -12.33), "benchmark": (15.78, 56.25, -18.17)}, 3: {"provided": (17.83, 39.07, 4.13), "optimized": (17.17, 35.98, 7.03), "benchmark": (14.30, 25.99, 5.05)}, 5: {"provided": (17.07, 23.40, 10.19), "optimized": (16.17, 21.55, 10.16), "benchmark": (14.09, 18.81, 9.16)}, 7: {"provided": (17.61, 25.91, 13.09), "optimized": (16.94, 22.58, 12.02), "benchmark": (14.20, 17.28, 12.09)}}
    parity_rows = []
    for _, row in rolling.iterrows():
        years = int(row["roll_period_years"])
        for portfolio, values in pv_rolling[years].items():
            for metric, pv_value in zip(("average", "high", "low"), values):
                internal = row[f"{portfolio}_{metric}_pct"]
                parity_rows.append({"roll_period_years": years, "portfolio": portfolio, "metric": metric, "pv_pct": pv_value, "internal_pct": internal, "delta_pct_points": internal - pv_value})
    pd.DataFrame(parity_rows).to_csv(OUT / "rolling_returns_parity.csv", index=False, encoding="utf-8")
    pv_covariance = pd.DataFrame(np.outer(pv_volatility, pv_volatility) * pv_correlation.to_numpy(), index=SYMBOLS, columns=SYMBOLS)
    solver_pv = maximum_sharpe(pv_expected, pv_covariance, dict(zip(SYMBOLS, [(0.0, value) for value in MAX])), rf)
    fdr_stats = result["asset_statistics"]
    fdr_expected = pd.Series(fdr_stats["expected_returns"])[list(SYMBOLS)]
    fdr_volatility = pd.Series(fdr_stats["volatility"])[list(SYMBOLS)]
    fdr_correlation = pd.DataFrame(fdr_stats["correlation"]).loc[list(SYMBOLS), list(SYMBOLS)]
    moment = pd.DataFrame({"asset": SYMBOLS, "pv_expected_return": pv_expected.values, "fdr_expected_return": fdr_expected.values, "expected_return_delta": (fdr_expected - pv_expected).values, "pv_volatility": pv_volatility.values, "fdr_volatility": fdr_volatility.values, "volatility_delta": (fdr_volatility - pv_volatility).values})
    corr_delta = (fdr_correlation - pv_correlation).abs()
    solver_table = pd.DataFrame({"asset": SYMBOLS, "pv_published_weight": [0.2461, .4072, 0, .3, 0, 0, .0466, 0, 0], "internal_weight_from_pv_moments": solver_pv.weights.values})
    solver_table["weight_delta_vs_pv"] = solver_table["internal_weight_from_pv_moments"] - solver_table["pv_published_weight"]
    moment.to_csv(OUT / "moment_parity.csv", index=False, encoding="utf-8")
    solver_table.to_csv(OUT / "solver_parity.csv", index=False, encoding="utf-8")
    weights = result["optimization_result"]["weights"]
    pv_weights = {"QQQ": .2461, "SPMO": .4072, "GDX": 0., "GLD": .3, "SLV": 0., "AIA": 0., "XLE": .0466, "PTF": 0., "QLD": 0.}
    parity = {
        "golden": {"assets": list(SYMBOLS), "bounds": dict(zip(SYMBOLS, MAX)), "provided_weights": PROVIDED, "benchmark": "SPY", "analysis_period": {"start": "2016-08", "end": "2026-07"}},
        "implied_risk_free": {"per_asset": implied, "min": min(implied.values()), "max": max(implied.values()), "spread": max(implied.values()) - min(implied.values()), "mean": float(np.mean(list(implied.values()))), "median_effective_annual_rate": rf},
        "fdr_coverage": result["data_coverage"],
        "moment_parity": {"per_asset": moment.to_dict(orient="records"), "correlation_max_abs_delta": float(corr_delta.to_numpy().max()), "correlation_mean_abs_delta": float(corr_delta.to_numpy().mean())},
        "solver_only_parity": {"internal_weights_from_pv_moments": solver_pv.weights.to_dict(), "weight_delta_vs_pv": dict(zip(SYMBOLS, solver_table["weight_delta_vs_pv"])), "expected_return": solver_pv.expected_return, "volatility": solver_pv.volatility, "sharpe": solver_pv.sharpe, "note_on_golden_rounding": "PV displayed moments and weights are rounded; no exact-equality assertion is applied."},
        "optimizer": {"weights": weights, "weight_delta_vs_pv": {s: weights[s] - pv_weights[s] for s in SYMBOLS}, "expected_return": result["optimization_result"]["expected_return"], "volatility": result["optimization_result"]["volatility"], "sharpe": result["optimization_result"]["sharpe"], "pv": {"expected_return": .1721, "volatility": .1310, "sharpe": 1.13}},
        "frontier": {"point_count": len(result["efficient_frontier"]), "return_min": result["efficient_frontier"][0]["expected_return"], "return_max": result["efficient_frontier"][-1]["expected_return"], "shape_sanity": "ordered target-return minimum-variance frontier"},
        "diagnostic": "FDR vs PV data-source differences and CVXPY vs PV optimizer differences are not assigned a numeric pass/fail tolerance.",
        "code_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    (OUT / "parity.json").write_text(json.dumps(parity, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
