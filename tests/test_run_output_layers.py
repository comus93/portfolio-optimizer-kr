from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.report import write_analysis_run


def test_generic_run_writer_preserves_raw_precision_and_builds_review_layer(tmp_path: Path):
    result = {
        "configuration": {
            "run_id": "writer-contract",
            "assets": [
                {
                    "symbol": "A",
                    "name": "Asset A",
                    "currency": "USD",
                    "min_weight": 0.0,
                    "max_weight": 1.0,
                }
            ],
            "provided_weights": {"A": 1.0},
        },
        "data_coverage": {},
        "asset_statistics": {},
        "optimization_result": {"weights": {"A": 1.0}},
        "efficient_frontier": [],
        "portfolio_performance": {},
        "benchmark_analytics": {},
        "correlations": {},
        "return_decomposition": {},
        "risk_decomposition": {},
        "_tables": {
            "efficient_frontier": pd.DataFrame(
                [
                    {
                        "point": 1,
                        "expected_return": 0.171234567891,
                        "volatility": 0.123456789123,
                        "sharpe": 1.2345,
                        "weight_A": 1.0,
                    }
                ]
            )
        },
    }

    write_analysis_run(result, tmp_path)

    assert (tmp_path / "result.json").is_file()
    raw = pd.read_csv(tmp_path / "raw" / "efficient_frontier.csv")
    review = pd.read_csv(tmp_path / "review" / "efficient_frontier.csv")

    assert raw.loc[0, "expected_return"] == pytest.approx(0.171234567891)
    assert raw.loc[0, "volatility"] == pytest.approx(0.123456789123)
    assert review.loc[0, "expected_return_pct"] == pytest.approx(17.1234567891)
    assert review.loc[0, "volatility_pct"] == pytest.approx(12.3456789123)
    assert review.loc[0, "weight_A_pct"] == pytest.approx(100.0)
    assert review.loc[0, "sharpe"] == pytest.approx(1.2345)
