import json
from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimizer_kr.viewer import load_run_artifacts


def test_viewer_loader_reads_canonical_review_and_raw_without_recalculation(tmp_path: Path):
    run = tmp_path / "run-1"
    (run / "review").mkdir(parents=True)
    (run / "raw").mkdir(parents=True)
    (run / "result.json").write_text(
        json.dumps({"configuration": {"run_id": "run-1"}}), encoding="utf-8"
    )
    (run / "parity.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
    pd.DataFrame([{"metric": "CAGR", "optimized": 17.5}]).to_csv(
        run / "review" / "performance_summary.csv", index=False
    )
    pd.DataFrame([{"expected_return": 0.175123456789}]).to_csv(
        run / "raw" / "efficient_frontier.csv", index=False
    )

    artifacts = load_run_artifacts(run)
    assert artifacts.result["configuration"]["run_id"] == "run-1"
    assert artifacts.parity == {"ok": True}
    assert artifacts.table("performance_summary").iloc[0]["optimized"] == pytest.approx(17.5)
    assert artifacts.table("efficient_frontier", "raw").iloc[0]["expected_return"] == pytest.approx(0.175123456789)


def test_viewer_loader_requires_result_json(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match="result.json"):
        load_run_artifacts(tmp_path / "missing")
