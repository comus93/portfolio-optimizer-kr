from __future__ import annotations

from pathlib import Path
from typing import Any

from .backtest import write_backtest_analysis_run
from .result import write_analysis_run as write_optimization_analysis_run


def write_analysis_run(result: dict[str, Any], output_dir: str | Path) -> None:
    configuration = result.get("configuration", {})
    product_mode = configuration.get("product_mode") if isinstance(configuration, dict) else None
    if str(product_mode) == "backtest":
        write_backtest_analysis_run(result, output_dir)
        return
    write_optimization_analysis_run(result, output_dir)
