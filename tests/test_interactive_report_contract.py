import json
from dataclasses import fields
from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.viewer.builder import build_report_model
from portfolio_optimizer_kr.viewer.report_model import (
    ActiveContributionPoint,
    AnnualizedActiveReturnPoint,
    FrontierLandmark,
    FrontierPoint,
    ReportModel,
)
from portfolio_optimizer_kr.viewer.renderer import generate_report


def _write_csv(path: Path, rows: list[dict]):
    pd.DataFrame(rows).to_csv(path, index=False)


def _fixture_run(tmp_path: Path) -> Path:
    run = tmp_path / "run-1"
    review = run / "review"
    raw = run / "raw"
    review.mkdir(parents=True)
    raw.mkdir()
    (run / "result.json").write_text(
        json.dumps({"configuration": {"run_id": "run-1"}}), encoding="utf-8"
    )
    (run / "input.yaml").write_text(
        """run_id: run-1
benchmark:
  symbol: SPY
  name: SPDR S&P 500 ETF Trust
optimization:
  objective: max_sharpe
""",
        encoding="utf-8",
    )
    _write_csv(
        review / "annual_returns.csv",
        [
            {
                "year": 2025,
                "optimized_return_pct": 12.0,
                "provided_return_pct": 14.0,
                "benchmark_return_pct": 10.0,
            }
        ],
    )
    _write_csv(
        review / "efficient_frontier.csv",
        [
            {
                "point": 1,
                "sharpe": 1.1,
                "expected_return_pct": 16.0,
                "volatility_pct": 12.5,
                "weight_QQQ_pct": 70.0,
                "weight_GLD_pct": 30.0,
            },
            {
                "point": 2,
                "sharpe": 1.08,
                "expected_return_pct": 17.0,
                "volatility_pct": 13.5,
                "weight_QQQ_pct": 75.0,
                "weight_GLD_pct": 25.0,
            },
        ],
    )
    _write_csv(
        review / "active_returns.csv",
        [
            {
                "portfolio": "provided",
                "date": "2025-01-31",
                "annual_active_return_pct": 2.0,
                "rolling_active_return_pct": 1.5,
                "rolling_tracking_error_pct": 5.0,
            },
            {
                "portfolio": "optimized",
                "date": "2025-01-31",
                "annual_active_return_pct": 3.0,
                "rolling_active_return_pct": 2.5,
                "rolling_tracking_error_pct": 4.0,
            },
            {
                "portfolio": "provided",
                "date": "2025-12-31",
                "annual_active_return_pct": 2.0,
                "rolling_active_return_pct": 1.7,
                "rolling_tracking_error_pct": 5.2,
            },
            {
                "portfolio": "optimized",
                "date": "2025-12-31",
                "annual_active_return_pct": 3.0,
                "rolling_active_return_pct": 2.7,
                "rolling_tracking_error_pct": 4.2,
            },
        ],
    )
    _write_csv(
        review / "portfolio_growth.csv",
        [
            {
                "date": "2025-12-31",
                "provided_balance": 1.20,
                "optimized_balance": 1.18,
                "benchmark_balance": 1.10,
            }
        ],
    )
    _write_csv(
        review / "drawdown_series.csv",
        [
            {
                "date": "2025-12-31",
                "provided_drawdown_pct": -5.0,
                "optimized_drawdown_pct": -3.0,
                "benchmark_drawdown_pct": -6.0,
            }
        ],
    )
    _write_csv(
        review / "annual_asset_returns.csv",
        [
            {"year": 2025, "ticker": "QQQ", "return_pct": 15.0},
            {"year": 2025, "ticker": "GLD", "return_pct": 8.0},
        ],
    )
    _write_csv(
        review / "active_return_contribution.csv",
        [
            {
                "date": "2025-01-31",
                "portfolio": "provided",
                "ticker": "QQQ",
                "cumulative_active_contribution_pct": 1.0,
            },
            {
                "date": "2025-01-31",
                "portfolio": "optimized",
                "ticker": "QQQ",
                "cumulative_active_contribution_pct": 2.0,
            },
            {
                "date": "2025-12-31",
                "portfolio": "provided",
                "ticker": "QQQ",
                "cumulative_active_contribution_pct": 1.2,
            },
            {
                "date": "2025-12-31",
                "portfolio": "optimized",
                "ticker": "QQQ",
                "cumulative_active_contribution_pct": 2.4,
            },
        ],
    )
    _write_csv(
        review / "up_down_market_performance.csv",
        [
            {
                "portfolio": "provided",
                "market_type": "up",
                "portfolio_return_pct": 2.0,
                "benchmark_return_pct": 1.5,
                "active_return_pct": 0.5,
                "occurrences": 10,
            }
        ],
    )
    rolling = [
        {
            "date": "2025-12-31",
            "optimized_annualized_return_pct": 11.0,
            "provided_annualized_return_pct": 12.0,
            "benchmark_annualized_return_pct": 10.0,
        }
    ]
    _write_csv(review / "rolling_returns_3y.csv", rolling)
    _write_csv(review / "rolling_returns_5y.csv", rolling)
    return run


def test_annualized_active_return_contract_is_year_based_and_has_no_benchmark():
    names = {field.name for field in fields(AnnualizedActiveReturnPoint)}
    assert names == {
        "year",
        "provided_active_return_pct",
        "optimized_active_return_pct",
    }


def test_frontier_contract_contains_true_xy_risk_return_and_allocations():
    names = {field.name for field in fields(FrontierPoint)}
    assert names == {
        "volatility_pct",
        "expected_return_pct",
        "sharpe_ratio",
        "weights_pct",
    }


def test_frontier_landmark_contract_supports_asset_portfolio_and_benchmark_markers():
    names = {field.name for field in fields(FrontierLandmark)}
    assert names == {
        "kind",
        "label",
        "volatility_pct",
        "expected_return_pct",
        "sharpe_ratio",
        "weights_pct",
    }


def test_report_model_forces_active_contribution_portfolio_separation():
    names = {field.name for field in fields(ReportModel)}
    assert "active_return_contribution" not in names
    assert "active_return_contribution_provided" in names
    assert "active_return_contribution_optimized" in names
    assert "rolling_active_provided" in names
    assert "rolling_active_optimized" in names


def test_active_contribution_point_keeps_portfolio_identity():
    names = {field.name for field in fields(ActiveContributionPoint)}
    assert names == {"date", "portfolio", "contributions_pct"}


def test_builder_shapes_annual_active_return_once_per_year(tmp_path: Path):
    model = build_report_model(_fixture_run(tmp_path))
    assert len(model.annualized_active_returns) == 1
    point = model.annualized_active_returns[0]
    assert point.year == 2025
    assert point.provided_active_return_pct == pytest.approx(2.0)
    assert point.optimized_active_return_pct == pytest.approx(3.0)


def test_builder_never_cross_connects_active_contribution_portfolios(tmp_path: Path):
    model = build_report_model(_fixture_run(tmp_path))
    provided = model.active_return_contribution_provided
    optimized = model.active_return_contribution_optimized

    assert [point.portfolio for point in provided] == ["provided", "provided"]
    assert [point.portfolio for point in optimized] == ["optimized", "optimized"]
    assert [point.date for point in provided] == ["2025-01-31", "2025-12-31"]
    assert [point.date for point in optimized] == ["2025-01-31", "2025-12-31"]
    assert provided[-1].contributions_pct == {"QQQ": 1.2}
    assert optimized[-1].contributions_pct == {"QQQ": 2.4}


def test_builder_keeps_rolling_active_portfolios_separate(tmp_path: Path):
    model = build_report_model(_fixture_run(tmp_path))
    assert len(model.rolling_active_provided) == 2
    assert len(model.rolling_active_optimized) == 2
    assert model.rolling_active_provided[-1].active_return_pct == pytest.approx(1.7)
    assert model.rolling_active_optimized[-1].active_return_pct == pytest.approx(2.7)


def test_frontier_points_use_volatility_as_x_contract_and_weights_sum_to_100(tmp_path: Path):
    model = build_report_model(_fixture_run(tmp_path))
    assert [point.volatility_pct for point in model.efficient_frontier] == [12.5, 13.5]
    assert [point.expected_return_pct for point in model.efficient_frontier] == [16.0, 17.0]
    for point in model.efficient_frontier:
        assert sum(point.weights_pct.values()) == pytest.approx(100.0)


def test_builder_maps_chart_data_without_financial_recalculation(tmp_path: Path):
    model = build_report_model(_fixture_run(tmp_path))
    assert model.objective_name == "Maximum Sharpe Ratio"
    assert model.benchmark_symbol == "SPY"
    assert model.portfolio_growth[0].provided_balance == pytest.approx(1.20)
    assert model.annual_returns[0].provided_return_pct == pytest.approx(14.0)
    assert model.efficient_frontier[0].weights_pct == {"QQQ": 70.0, "GLD": 30.0}
    assert model.drawdowns[0].benchmark_drawdown_pct == pytest.approx(-6.0)
    assert model.annual_asset_returns[0].returns_pct == {"QQQ": 15.0, "GLD": 8.0}
    assert model.up_down_market_performance[0].benchmark_return_pct == pytest.approx(1.5)
    assert model.rolling_returns_3y[0].provided_return_pct == pytest.approx(12.0)


def test_generate_report_is_self_contained_file_html_with_golden_sections(tmp_path: Path):
    run = _fixture_run(tmp_path)
    template = Path(__file__).resolve().parents[1] / "site" / "report-template.html"
    report = generate_report(run, template_path=template)
    html = report.read_text(encoding="utf-8")

    assert report == run / "report.html"
    assert "__REPORT_DATA_JSON__" not in html
    assert 'id="report-data"' in html
    assert 'id="efficient-frontier"' in html
    assert 'id="frontier-transition"' in html
    assert 'id="portfolio-growth"' in html
    assert 'id="drawdown-chart"' in html
    assert "http://" not in html
    assert "https://" not in html
    assert '"benchmark_symbol":"SPY"' in html
    assert '"active_return_contribution_provided"' in html
    assert '"active_return_contribution_optimized"' in html
    assert '"year":2025' in html
