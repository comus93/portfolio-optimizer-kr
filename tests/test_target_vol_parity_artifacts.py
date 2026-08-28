import json
from pathlib import Path

import pandas as pd


RUN_DIR = Path(__file__).parent.parent / "runs" / "20260828-pv-maxretvol15"


def test_target_vol_parity_json_has_reusable_regression_diagnostics():
    parity = json.loads((RUN_DIR / "parity.json").read_text(encoding="utf-8"))

    assert {
        "golden",
        "moment_parity",
        "solver_only_parity",
        "optimizer",
        "frontier",
        "data_coverage",
        "performance_diagnostic",
    } <= set(parity)

    golden = parity["golden"]
    assert golden["objective"] == "target_volatility"
    assert golden["target_volatility"] == 0.15
    assert set(golden["assets"]) == {"QQQ", "SPMO", "GDX", "GLD", "SLV", "AIA", "XLE", "PTF", "QLD"}
    assert golden["bounds"]["PTF"][1] == 0.30
    assert golden["bounds"]["QLD"][1] == 0.30
    assert abs(sum(golden["provided_weights"].values()) - 1.0) < 1e-10

    moments = parity["moment_parity"]
    assert len(moments["per_asset"]) == 9
    assert "correlation_max_abs_delta" in moments
    assert "correlation_mean_abs_delta" in moments

    solver = parity["solver_only_parity"]
    assert set(solver["internal_weights_from_pv_moments"]) == set(golden["assets"])
    assert set(solver["published_pv_weights"]) == set(golden["assets"])
    assert "expected_return" in solver
    assert "volatility" in solver


def test_target_vol_parity_csvs_compare_pv_rounded_moments_solver_and_fdr():
    moments = pd.read_csv(RUN_DIR / "moment_parity.csv")
    assert {
        "ticker",
        "pv_expected_return",
        "fdr_expected_return",
        "expected_return_delta",
        "pv_volatility",
        "fdr_volatility",
        "volatility_delta",
    } <= set(moments.columns)
    assert len(moments) == 9

    solver = pd.read_csv(RUN_DIR / "solver_parity.csv")
    assert {
        "ticker",
        "pv_published_weight",
        "internal_weight_from_pv_moments",
        "fdr_internal_weight",
        "weight_delta_solver_vs_pv",
        "weight_delta_fdr_vs_pv",
    } <= set(solver.columns)
    assert len(solver) == 9
