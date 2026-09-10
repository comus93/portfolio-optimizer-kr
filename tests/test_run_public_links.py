from __future__ import annotations

import json
from pathlib import Path

import yaml

from portfolio_optimizer_kr.report.navigation import refresh_run_navigation
from portfolio_optimizer_kr.report.public_links import (
    public_report_url,
    refresh_all_public_report_links,
    register_public_report_url,
)


def _write_run(run_dir: Path) -> None:
    run_dir.mkdir(parents=True)
    (run_dir / "input.yaml").write_text(
        yaml.safe_dump(
            {
                "product_mode": "backtest",
                "run_id": run_dir.name,
                "time_period": {
                    "mode": "month_to_month",
                    "start_year": 2021,
                    "first_month": "Nov",
                    "end_year": 2026,
                    "last_month": "Aug",
                },
                "portfolios": [
                    {"name": "Candidate", "weights_pct": {"QQQ": 100}}
                ],
                "benchmark": {"symbol": "SPY", "currency": "USD"},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "context.yaml").write_text(
        yaml.safe_dump(
            {
                "run_id": run_dir.name,
                "study": "studies/example/study.md",
                "experiment": "studies/example/experiments/001.yaml",
                "product_mode": "backtest",
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "result.json").write_text(
        json.dumps(
            {
                "configuration": {
                    "run_id": run_dir.name,
                    "product_mode": "backtest",
                }
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "report.html").write_text("<html></html>\n", encoding="utf-8")


def test_public_report_url_is_persisted_and_rendered_exactly(tmp_path: Path):
    runs = tmp_path / "runs"
    run_dir = runs / "20260910-0005"
    _write_run(run_dir)
    refresh_run_navigation(run_dir)

    exact_url = "https://reports.example.net/custom/location/result-42.html?view=full"
    register_public_report_url(run_dir, exact_url)

    assert public_report_url(run_dir) == exact_url
    links = yaml.safe_load((run_dir / "links.yaml").read_text(encoding="utf-8"))
    assert links == {"public_report_url": exact_url}

    run_readme = (run_dir / "README.md").read_text(encoding="utf-8")
    assert f"[Public Report]({exact_url})" in run_readme

    index = (runs / "README.md").read_text(encoding="utf-8")
    assert "| Run | Product | Study / Experiment | Period | Benchmark | Report | Summary |" in index
    assert f"[Open]({exact_url})" in index


def test_public_report_link_survives_navigation_rebuild(tmp_path: Path):
    runs = tmp_path / "runs"
    run_dir = runs / "20260910-0005"
    _write_run(run_dir)
    refresh_run_navigation(run_dir)
    exact_url = "https://cdn.example.org/reports/abc.html"
    register_public_report_url(run_dir, exact_url)

    refresh_run_navigation(run_dir)
    assert exact_url not in (run_dir / "README.md").read_text(encoding="utf-8")

    refresh_all_public_report_links(runs)

    assert exact_url in (run_dir / "README.md").read_text(encoding="utf-8")
    assert exact_url in (runs / "README.md").read_text(encoding="utf-8")
