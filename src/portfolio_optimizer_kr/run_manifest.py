from __future__ import annotations

import json
from pathlib import Path

from portfolio_optimizer_kr.models import ProductMode


_MANIFEST_ARTIFACTS: dict[str, str] = {
    "input_yaml": "input.yaml",
    "context_yaml": "context.yaml",
    "result_json": "result.json",
    "report_html": "report.html",
    "monthly_return_series": "review/monthly_return_series.csv",
    "efficient_frontier": "review/efficient_frontier.csv",
}


def write_run_manifest(
    output_dir: str | Path,
    *,
    product_mode: ProductMode,
) -> Path:
    """Persist run artifacts and post-processing capabilities discovered after execution."""
    run_path = Path(output_dir)
    artifacts = {
        name: (run_path / relative_path).is_file()
        for name, relative_path in _MANIFEST_ARTIFACTS.items()
    }
    capabilities = {
        "frontier_risk_tradeoff": all(
            artifacts[name]
            for name in (
                "input_yaml",
                "report_html",
                "monthly_return_series",
                "efficient_frontier",
            )
        ),
    }
    payload = {
        "schema_version": 1,
        "product_mode": product_mode.value,
        "artifacts": artifacts,
        "capabilities": capabilities,
    }
    manifest_path = run_path / "run_manifest.json"
    manifest_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest_path
