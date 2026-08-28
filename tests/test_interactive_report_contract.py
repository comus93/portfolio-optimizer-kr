import json
from dataclasses import fields
from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.viewer.builder import build_report_model
from portfolio_optimizer_kr.viewer.report_model import ActiveReturnPoint, FrontierPoint
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
                "weight_QQQ_pct": 40.0,
                "weight_GLD_pct": 30.0,
            }
        ],
    )
    _write_csv(
        review / "active_returns.csv",
        [
            {
                "portfolio": "provided",
                "date": "2025-12-31",
                "annual_active_return_pct": 2.0,
                "rolling_active_return_pct": 1.5,
                "rolling_tracking_error_pct": 5.0,
            },
            {
                "portfolio": "optimized",
                "date": "2025-12-31",
                "annual_active_return_pct": 3.0,
                "rolling_active_return_pct": 2.5,
                "rolling_tracking_error_pct": 4.0,
            },
        ],
    )
    _write_csv(
        review / "portfolio_growth.csv",
        [
            {
                "date": "2025-12-31",
                "provided_balance": 12000.0,
                "optimized_balance": 11800.0,
                "benchmark_balance": 11000.0,
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
                "date": "2025-12-31",
                "portfolio": "provided",
                "ticker": "QQQ",
                "cumulative_active_contribution_pct": 1.2,
            }
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


def test_tooltip_contract_has_no_benchmark_active_return_field():
    names = {field.name for field in fields(ActiveReturnPoint)}
    assert names == {
        "date",
        "provided_active_return_pct",
        "optimized_active_return_pct",
    }


def test_frontier_tooltip_contract_contains_risk_return_sharpe_and_allocations():
    names = {field.name for field in fields(FrontierPoint)}
    assert names == {
        "volatility_pct",
        "expected_return_pct",
        "sharpe_ratio",
        "weights_pct",
    }


def test_builder_maps_chart_data_without_financial_recalculation(tmp_path: Path):
    model = build_report_model(_fixture_run(tmp_path))
    assert model.objective_name == "Maximum Sharpe Ratio"
    assert model.benchmark_symbol == "SPY"
    assert model.portfolio_growth[0].provided_balance == pytest.approx(12000.0)
    assert model.annual_returns[0].provided_return_pct == pytest.approx(14.0)
    assert model.efficient_frontier[0].weights_pct == {"QQQ": 40.0, "GLD": 30.0}
    assert model.annualized_active_returns[0].provided_active_return_pct == pytest.approx(2.0)
    assert model.annualized_active_returns[0].optimized_active_return_pct == pytest.approx(3.0)
    assert model.drawdowns[0].benchmark_drawdown_pct == pytest.approx(-6.0)
    assert model.annual_asset_returns[0].returns_pct == {"QQQ": 15.0, "GLD": 8.0}
    assert model.active_return_contribution[0].contributions_pct == {"QQQ": 1.2}
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
