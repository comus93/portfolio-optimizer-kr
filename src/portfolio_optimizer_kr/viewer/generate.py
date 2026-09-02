from __future__ import annotations

import json
from pathlib import Path

from .backtest_renderer import generate_backtest_report
from .final_renderer import generate_report as generate_optimization_report


def generate_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    template_path: str | Path | None = None,
) -> Path:
    root = Path(run_dir)
    result_path = root / "result.json"
    if not result_path.is_file():
        raise FileNotFoundError(f"missing canonical result: {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    configuration = result.get("configuration", {})
    if isinstance(configuration, dict) and configuration.get("product_mode") == "backtest":
        return generate_backtest_report(root, output_path=output_path)
    return generate_optimization_report(
        root,
        output_path=output_path,
        template_path=template_path,
    )
