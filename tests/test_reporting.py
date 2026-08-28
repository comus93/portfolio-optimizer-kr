import json

import pandas as pd

from portfolio_optimizer_kr.models import AssetSpec, OptimizationRequest, RiskFreeConfig, RiskFreeMode
from portfolio_optimizer_kr.pipeline import analyze_prices
from portfolio_optimizer_kr.report import write_analysis_run


def _price(start: float, slope: float) -> pd.Series:
    index = pd.date_range("2019-12-31", periods=1600, freq="D")
    return pd.Series(start + slope * pd.RangeIndex(len(index)), index=index)


def test_benchmark_and_canonical_run_outputs(tmp_path):
    request = OptimizationRequest(
        assets=(AssetSpec("A"), AssetSpec("B")),
        benchmark=AssetSpec("BM"),
        provided_weights={"A": 0.5, "B": 0.5},
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
        frontier_points=3,
    )
    result = analyze_prices(request, {"A": _price(100, 0.12), "B": _price(100, 0.07), "BM": _price(100, 0.09)})
    assert set(result) >= {"configuration", "benchmark_analytics", "correlations", "return_decomposition", "risk_decomposition"}
    assert result["benchmark_analytics"]["coverage"]["observations"] > 0
    assert {"provided", "optimized", "benchmark"}.issubset(result["portfolio_performance"])
    assert result["risk_decomposition"]["provided"]
    write_analysis_run(result, tmp_path)
    assert (tmp_path / "result.json").is_file()
    assert (tmp_path / "active_returns.csv").is_file()
    assert json.loads((tmp_path / "result.json").read_text(encoding="utf-8"))["configuration"]["benchmark"] == "BM"
