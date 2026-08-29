from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from portfolio_optimizer_kr.models import AssetSpec, OptimizationRequest
from portfolio_optimizer_kr.pipeline import _asset_price_coverage, _portfolio_metrics_table
from portfolio_optimizer_kr.viewer.builder import build_report_model_from_artifacts
from portfolio_optimizer_kr.viewer.loader import RunArtifacts


def _template() -> str:
    return (Path(__file__).resolve().parents[1] / "site" / "report-template.html").read_text(
        encoding="utf-8"
    )


def test_user_feedback_report_layer_contains_requested_interactions_and_layouts():
    html = _template()
    assert 'id="report-user-feedback-v2"' in html
    assert "groupedYearHover('annual-returns'" in html
    assert "groupedYearHover('annualized-active-return'" in html
    assert "groupedYearHover('annual-asset-returns'" in html
    assert "interactiveDonut('provided-portfolio'" in html
    assert "Assets outside chart scale" in html
    assert "weights_pct" in html and "Efficient Frontier" in html
    assert "Efficient Frontier Transition Map (${period})" in html
    assert "renderUpDown" in html
    assert "contributionTable.remove()" in html
    assert "Sharpe Ratio (ex-ante)" in html
    assert "Annualized Return %" in html
    assert "Month / Year" in html


def test_user_feedback_report_uses_dynamic_period_and_risk_free_notes():
    html = _template()
    assert "optimization_monthly_returns" in html
    assert "asset_prices" in html
    assert "reqEndMonthComplete" in html
    assert "rfMeta.requested_mode==='us_3m_tbill'" in html
    assert "fixed annual risk-free rate" in html


def test_asset_price_coverage_records_asset_identity_and_observed_bounds():
    request = OptimizationRequest(
        assets=(AssetSpec("AAA", name="Asset A", currency="USD"),),
        start="2020-01-01",
        end="2020-12-31",
    )
    prices = {
        "AAA": pd.Series(
            [1.0, 2.0],
            index=pd.to_datetime(["2020-03-02", "2020-12-30"]),
            name="AAA",
        )
    }
    coverage = _asset_price_coverage(request, prices)
    assert coverage["AAA"] == {
        "name": "Asset A",
        "start": "2020-03-02",
        "end": "2020-12-30",
        "observations": 2,
    }


def test_portfolio_metrics_table_includes_benchmark_column():
    index = pd.date_range("2020-01-31", periods=24, freq="ME")
    benchmark = pd.Series([0.01, -0.005, 0.012, 0.004] * 6, index=index)
    provided = pd.Series([0.011, -0.004, 0.010, 0.006] * 6, index=index)
    optimized = pd.Series([0.009, -0.002, 0.013, 0.005] * 6, index=index)
    paths = {
        "provided": SimpleNamespace(returns=provided),
        "optimized": SimpleNamespace(returns=optimized),
    }
    table = _portfolio_metrics_table(paths, benchmark, 0.02)
    assert "benchmark" in table.columns
    beta = table.loc[table["metric"] == "beta", "benchmark"].iloc[0]
    r_squared = table.loc[table["metric"] == "r_squared", "benchmark"].iloc[0]
    assert abs(beta - 1.0) < 1e-12
    assert abs(r_squared - 1.0) < 1e-12


def test_report_model_exposes_canonical_metadata(tmp_path):
    artifacts = RunArtifacts(
        run_dir=tmp_path,
        result={
            "configuration": {"analysis_period": {"start": "2020-01-01", "end": "2020-12-31"}},
            "data_coverage": {"optimization_monthly_returns": {"start": "2020-01-31", "end": "2020-12-31"}},
        },
        parity=None,
        review={},
        raw={},
    )
    model = build_report_model_from_artifacts(artifacts, config={"run_id": "metadata-test"})
    assert model.metadata["configuration"]["analysis_period"]["start"] == "2020-01-01"
    assert model.metadata["data_coverage"]["optimization_monthly_returns"]["end"] == "2020-12-31"
