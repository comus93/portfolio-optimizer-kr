from __future__ import annotations

from pathlib import Path

from portfolio_optimizer_kr.viewer.shared_historical_overlay import (
    apply_optimizer_shared_historical_components,
)


def test_optimizer_shared_rolling_5y_mounts_on_next_frame_without_legacy_delay(tmp_path: Path):
    review = tmp_path / "review"
    review.mkdir()
    (review / "rolling_returns_5y.csv").write_text(
        "date,optimized_annualized_return_pct,provided_annualized_return_pct,benchmark_annualized_return_pct\n"
        "2026-07-31,23.68,23.13,17.79\n"
        "2026-08-31,23.70,23.13,16.78\n",
        encoding="utf-8",
    )
    report = tmp_path / "report.html"
    report.write_text(
        '<html><body><section id="rolling-returns-5y"><div class="chart"></div></section></body></html>',
        encoding="utf-8",
    )

    apply_optimizer_shared_historical_components(
        tmp_path,
        report,
        objective_name="Maximum Return at 11.5% Target Volatility",
        benchmark_label="SPDR S&P 500 ETF Trust",
    )

    html = report.read_text(encoding="utf-8")
    assert 'id="shared-historical-component-overlay"' in html
    assert '"#rolling-returns-5y .chart"' in html
    assert 'rolling-5y-annualized-return' in html
    assert "requestAnimationFrame(mount)" in html
    assert "setTimeout(mount, 180)" not in html
    assert "sharedRendererMounted = 'true'" in html


def test_optimizer_shared_mount_is_idempotent(tmp_path: Path):
    review = tmp_path / "review"
    review.mkdir()
    (review / "rolling_returns_5y.csv").write_text(
        "date,optimized_annualized_return_pct,provided_annualized_return_pct,benchmark_annualized_return_pct\n"
        "2026-08-31,23.70,23.13,16.78\n",
        encoding="utf-8",
    )
    report = tmp_path / "report.html"
    report.write_text(
        '<html><body><section id="rolling-returns-5y"><div class="chart"></div></section></body></html>',
        encoding="utf-8",
    )

    for _ in range(2):
        apply_optimizer_shared_historical_components(
            tmp_path,
            report,
            objective_name="Maximum Return at 11.5% Target Volatility",
            benchmark_label="SPDR S&P 500 ETF Trust",
        )

    html = report.read_text(encoding="utf-8")
    assert html.count('id="shared-historical-component-overlay"') == 1
