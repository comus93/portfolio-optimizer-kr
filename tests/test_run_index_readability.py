from __future__ import annotations

import json
from pathlib import Path

import yaml

from portfolio_optimizer_kr.report.navigation import write_runs_index
from portfolio_optimizer_kr.report.public_links import apply_public_report_links


def _run(root: Path, run_id: str, experiment: str, url: str | None = None) -> Path:
    run = root / run_id
    run.mkdir(parents=True)
    (run / "result.json").write_text(json.dumps({"configuration": {"run_id": run_id, "product_mode": "optimization", "analysis_period": {"start": "2020-01-01", "end": "2026-08-31"}, "benchmark": {"symbol": "SPY", "name": "SPY"}}}), encoding="utf-8")
    (run / "input.yaml").write_text("product_mode: optimization\n", encoding="utf-8")
    (run / "context.yaml").write_text(yaml.safe_dump({"study": "studies/demo", "experiment": f"studies/demo/experiments/{experiment}.yaml"}), encoding="utf-8")
    if url:
        (run / "links.yaml").write_text(yaml.safe_dump({"public_report_url": url}), encoding="utf-8")
    return run


def test_runs_index_is_readable_and_public_link_refresh_is_idempotent(tmp_path: Path) -> None:
    _run(tmp_path, "20260910-0001", "001-alpha")
    latest = _run(tmp_path, "20260911-0001", "001-alpha", "https://reports.example/a.html")
    _run(tmp_path, "20260911-0002", "002-beta")

    index = write_runs_index(tmp_path)
    apply_public_report_links(latest, update_index=True)
    apply_public_report_links(latest, update_index=True)
    text = index.read_text(encoding="utf-8")

    assert "## Latest by Experiment" in text
    assert "## Recent Runs" in text
    assert "Full Run History (3 runs)" in text
    assert "| Optimization | demo / 001-alpha | [20260911-0001]" in text
    assert "| 2 | 2020-01-01 ~ 2026-08-31 |" in text
    assert "[Open](https://reports.example/a.html)" in text
    assert "|---|---|---|---|---|N/A|---|" not in text.replace(" ", "")
    assert text.replace(" ", "").count("|---|---|---|---|---|---|---|") == 2
