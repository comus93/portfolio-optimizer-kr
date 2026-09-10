from pathlib import Path

import pandas as pd
import yaml

from portfolio_optimizer_kr.report.public_links import apply_public_report_links
from portfolio_optimizer_kr.viewer.shared_historical_overlay import build_optimizer_shared_sections


def test_run_index_separator_expands_with_report_column(tmp_path: Path):
    root = tmp_path / "runs"
    run = root / "20260910-0001"
    run.mkdir(parents=True)
    (run / "README.md").write_text("# Run\n", encoding="utf-8")
    (run / "links.yaml").write_text(
        "public_report_url: https://example.test/report.html\n", encoding="utf-8"
    )
    (root / "README.md").write_text(
        "| Run | Product | Study / Experiment | Period | Benchmark | Summary |\n"
        "|---|---|---|---|---|---|\n"
        "| [20260910-0001](20260910-0001/) | Optimization | S / E | P | B | Summary |\n",
        encoding="utf-8",
    )

    apply_public_report_links(run, update_index=True)

    lines = (root / "README.md").read_text(encoding="utf-8").splitlines()
    assert lines[0] == "| Run | Product | Study / Experiment | Period | Benchmark | Report | Summary |"
    assert lines[1] == "| --- | --- | --- | --- | --- | --- | --- |"
    assert "[Open](https://example.test/report.html)" in lines[2]


def test_optimizer_shared_sections_keep_asset_names_and_tickers(tmp_path: Path):
    root = tmp_path / "run"
    (root / "review").mkdir(parents=True)
    (root / "raw").mkdir()
    (root / "input.yaml").write_text(
        yaml.safe_dump(
            {
                "assets": [
                    {"symbol": "QQQ", "name": "Invesco QQQ Trust"},
                    {"symbol": "GLD", "name": "SPDR Gold Shares"},
                ]
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    pd.DataFrame([{"portfolio": "provided", "active_return_pct": 1.0}]).to_csv(
        root / "review" / "benchmark_summary.csv", index=False
    )
    pd.DataFrame(
        [
            {
                "date": "2025-12-31",
                "portfolio": portfolio,
                "ticker": ticker,
                "cumulative_active_contribution_pct": value,
            }
            for portfolio in ("provided", "optimized")
            for ticker, value in (("QQQ", 3.0), ("GLD", -1.0))
        ]
    ).to_csv(root / "review" / "active_return_contribution.csv", index=False)
    pd.DataFrame(
        [
            {"series": "QQQ", "QQQ": 1.0, "GLD": 0.2, "provided": 0.8},
            {"series": "GLD", "QQQ": 0.2, "GLD": 1.0, "provided": 0.4},
            {"series": "provided", "QQQ": 0.8, "GLD": 0.4, "provided": 1.0},
        ]
    ).to_csv(root / "raw" / "correlations.csv", index=False)
    pd.DataFrame(
        [
            {"year": 2025, "ticker": "QQQ", "return": 0.12},
            {"year": 2025, "ticker": "GLD", "return": 0.08},
        ]
    ).to_csv(root / "raw" / "annual_asset_returns.csv", index=False)

    sections = build_optimizer_shared_sections(
        root, objective_name="Maximum Sharpe Ratio", benchmark_label="SPY"
    )

    active = sections["#active-return-contribution .chart"]
    assert "Invesco QQQ Trust<br>(QQQ)" in active
    assert "<th>Ticker</th><th>Name</th>" in active
    assert "Invesco QQQ Trust" in active

    for selector in (
        "#asset-correlations .table-slot",
        "#portfolio-asset-correlations .table-slot",
    ):
        correlation = sections[selector]
        assert "<th>Ticker</th><th>Name</th><th>QQQ</th><th>GLD</th>" in correlation
        assert "Invesco QQQ Trust" in correlation
        assert "<th>provided</th>" not in correlation

    annual = sections["#annual-asset-returns .chart"]
    assert "Invesco QQQ Trust<br>(QQQ)" in annual
    assert "<th>Year</th><th>Ticker</th><th>Name</th>" in annual
    assert "SPDR Gold Shares" in annual


def test_frontier_portfolio_headers_use_stacked_asset_identity():
    template = Path("site/report-template.html").read_text(encoding="utf-8")
    assert "#frontier-portfolios th{white-space:pre-line" in template
    assert r"label:name?`${name}\n(${ticker})`:ticker" in template
