from __future__ import annotations

from pathlib import Path
from typing import Any

from .backtest import write_backtest_analysis_run
from .navigation import try_refresh_run_navigation
from .public_links import apply_public_report_links
from .result import write_analysis_run as write_optimization_analysis_run


def write_analysis_run(result: dict[str, Any], output_dir: str | Path) -> None:
    configuration = result.get("configuration", {})
    product_mode = configuration.get("product_mode") if isinstance(configuration, dict) else None
    if str(product_mode) == "backtest":
        write_backtest_analysis_run(result, output_dir)
    else:
        write_optimization_analysis_run(result, output_dir)

    # Product writers persist canonical artifacts first. Navigation files are
    # derived projections and may be regenerated after input/context/report are
    # available. Only the canonical `runs/` root receives an aggregate index.
    directory = Path(output_dir)
    update_index = directory.parent.name == "runs"
    try_refresh_run_navigation(
        directory,
        result=result,
        update_index=update_index,
    )
    apply_public_report_links(directory, update_index=update_index)
