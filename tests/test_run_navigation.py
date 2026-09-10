from __future__ import annotations

import json
from pathlib import Path

import yaml

from portfolio_optimizer_kr.report.navigation import refresh_run_navigation


def _write_backtest_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    (run_dir / "review").mkdir()
    input_data = {
        "product_mode": "backtest",
        "run_id": run_dir.name,
        "time_period": {
            "mode": "month_to_month",
            "start_year": 2021,
            "first_month": "Nov",
            "end_year": 2026,
            "last_month": "Aug",
        },
        "assets": [
            {"symbol": "QQQ", "name": "Invesco QQQ", "currency": "USD"},
            {"symbol": "411060", "name": "ACE KRX Gold", "currency": "KRW"},
        ],
        "portfolios": [
            {
                "name": "Candidate",
                "weights_pct": {"QQQ": 70, "411060": 30},
            }
        ],
        "benchmark": {
            "type": "portfolio",
            "preset": "kaw_short",
            "name": "KAW Native Proxy",
        },
        "rebalancing": {"period": "monthly", "calendar_aligned": True},
        "fx": {"usdkrw_symbol": "USD/KRW"},
    }
    (run_dir / "input.yaml").write_text(
        yaml.safe_dump(input_data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    (run_dir / "context.yaml").write_text(
        yaml.safe_dump(
            {
                "run_id": run_dir.name,
                "study": "studies/kaw-target-reconstruction/study.md",
                "experiment": (
                    "studies/kaw-target-reconstruction/experiments/"
                    "030-provided-vs-kaw-short.yaml"
                ),
                "product_mode": "backtest",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    result = {
        "configuration": {"run_id": run_dir.name, "product_mode": "backtest"},
        "portfolio_definitions": {
            "Candidate": {"target_weights": {"QQQ": 0.7, "411060": 0.3}}
        },
    }
    (run_dir / "result.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "review" / "performance_summary.csv").write_text(
        "metric,unit,Candidate,benchmark\n"
        "CAGR,pct,12.3456,9.8765\n"
        "Annualized Return,pct,12.8,10.1\n"
        "Standard Deviation,pct,9.9,9.7\n"
        "Maximum Drawdown,pct,-11.2,-13.8\n"
        "Sharpe Ratio (ex-post),ratio,0.91,0.60\n"
        "Sortino Ratio,ratio,1.22,0.88\n",
        encoding="utf-8",
    )
    (run_dir / "report.html").write_text("<html></html>\n", encoding="utf-8")


def _write_optimization_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    (run_dir / "review").mkdir()
    input_data = {
        "product_mode": "optimization",
        "run_id": run_dir.name,
        "analysis_period": {"start": "2019-01-01", "end": "2025-12-31"},
        "assets": [
            {
                "symbol": "QQQ",
                "name": "Invesco QQQ",
                "currency": "USD",
                "provided_weight_pct": 60,
            },
            {
                "symbol": "GLD",
                "name": "SPDR Gold Shares",
                "currency": "USD",
                "provided_weight_pct": 40,
            },
        ],
        "benchmark": {"symbol": "SPY", "name": "SPDR S&P 500", "currency": "USD"},
        "portfolio": {"rebalancing_period": "monthly"},
    }
    (run_dir / "input.yaml").write_text(
        yaml.safe_dump(input_data, sort_keys=False), encoding="utf-8"
    )
    result = {
        "configuration": {"run_id": run_dir.name, "product_mode": "optimization"},
        "optimization_result": {"weights": {"QQQ": 0.75, "GLD": 0.25}},
    }
    (run_dir / "result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    (run_dir / "review" / "performance_summary.csv").write_text(
        "metric,unit,provided,optimized,benchmark\n"
        "CAGR,pct,10.0,12.0,11.0\n"
        "Annualized Return,pct,10.3,12.4,11.3\n"
        "Expected Return,pct,,13.2,\n"
        "Standard Deviation,pct,11.0,10.5,12.0\n"
        "Maximum Drawdown,pct,-15.0,-13.0,-16.0\n"
        "Sharpe Ratio (ex-post),ratio,0.60,0.80,0.65\n"
        "Sortino Ratio,ratio,0.90,1.10,0.95\n",
        encoding="utf-8",
    )


def test_backtest_run_readme_is_structured_navigation_projection(tmp_path: Path):
    runs = tmp_path / "runs"
    run_dir = runs / "20260910-0005"
    _write_backtest_run(run_dir)
    before = (run_dir / "result.json").read_bytes()

    refresh_run_navigation(run_dir)

    readme = (run_dir / "README.md").read_text(encoding="utf-8")
    sections = [
        "## Metadata",
        "## Purpose",
        "## Portfolios",
        "## Key Results",
        "## Notes",
        "## Artifacts",
    ]
    assert [readme.index(section) for section in sections] == sorted(
        readme.index(section) for section in sections
    )
    assert "`20260910-0005`" in readme
    assert "`kaw-target-reconstruction`" in readme
    assert "`030-provided-vs-kaw-short`" in readme
    assert "2021-11 ~ 2026-08" in readme
    assert "KAW Native Proxy" in readme
    assert "QQQ 70%, 411060 30%" in readme
    assert "12.35%" in readme
    assert "[Report](report.html)" in readme
    assert (run_dir / "result.json").read_bytes() == before

    index = (runs / "README.md").read_text(encoding="utf-8")
    assert "[20260910-0005](20260910-0005/)" in index
    assert "kaw-target-reconstruction / 030-provided-vs-kaw-short" in index


def test_optimization_navigation_supports_analysis_period_and_allocations(tmp_path: Path):
    runs = tmp_path / "runs"
    old_run = runs / "20260909-0001"
    new_run = runs / "20260910-0001"
    _write_backtest_run(old_run)
    _write_optimization_run(new_run)

    refresh_run_navigation(old_run)
    refresh_run_navigation(new_run)

    readme = (new_run / "README.md").read_text(encoding="utf-8")
    assert "Optimization" in readme
    assert "2019-01-01 ~ 2025-12-31" in readme
    assert "SPDR S&P 500 (SPY)" in readme
    assert "QQQ 60%, GLD 40%" in readme
    assert "QQQ 75%, GLD 25%" in readme
    assert "12.00%" in readme

    index = (runs / "README.md").read_text(encoding="utf-8")
    assert index.index("20260910-0001") < index.index("20260909-0001")
