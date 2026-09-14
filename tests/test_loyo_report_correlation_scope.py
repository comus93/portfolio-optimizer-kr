from pathlib import Path

import pandas as pd

from portfolio_optimizer_kr.models import AssetSpec, OptimizationRequest, RiskFreeConfig, RiskFreeMode
from portfolio_optimizer_kr.pipeline import analyze_prices
from portfolio_optimizer_kr.viewer import generate_report


def _price(start: float, slope: float) -> pd.Series:
    index = pd.date_range("2020-01-01", periods=1100, freq="D")
    return pd.Series(start + slope * pd.RangeIndex(len(index)), index=index)


def test_optimization_correlation_scope_reuses_asset_only_matrix():
    request = OptimizationRequest(
        assets=(AssetSpec("A"), AssetSpec("B")),
        benchmark=AssetSpec("BM"),
        provided_weights={"A": 0.5, "B": 0.5},
        risk_free=RiskFreeConfig(mode=RiskFreeMode.FIXED, annual_rate=0.02),
        frontier_points=3,
    )
    result = analyze_prices(
        request,
        {"A": _price(100, 0.12), "B": _price(100, 0.07), "BM": _price(100, 0.09)},
    )

    assert set(result["correlations"]) == {"A", "B"}
    table = result["_tables"]["correlations"]
    assert list(table.columns) == ["series", "A", "B"]
    assert set(table["series"]) == {"A", "B"}
    assert not {"provided", "optimized", "benchmark"} & set(table.columns)


def test_default_optimization_report_includes_loyo_and_no_portfolio_asset_correlations(tmp_path):
    run_dir = Path("runs/20260914-0003")
    target = tmp_path / "report.html"
    generate_report(run_dir, output_path=target)
    html = target.read_text(encoding="utf-8")

    assert "Leave-One-Year-Out Robustness" in html
    assert 'id="loyo-robustness"' in html
    assert "Portfolio / Asset Correlations" not in html
    assert 'id="portfolio-asset-correlations"' not in html
