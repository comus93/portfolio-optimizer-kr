from functools import wraps
from pathlib import Path

from portfolio_optimizer_kr.report.navigation import try_refresh_run_navigation

from .builder import build_report_model, build_report_model_from_artifacts
from .final_renderer import generate_report as _generate_report, render_report
from .loader import RunArtifacts, load_run_artifacts
from .pv_pagination import apply_monthly_returns_pagination
from .report_model import ReportModel


@wraps(_generate_report)
def generate_report(*args, **kwargs):
    rendered = _generate_report(*args, **kwargs)
    rendered = apply_monthly_returns_pagination(rendered)

    run_dir_value = args[0] if args else kwargs.get("run_dir")
    if run_dir_value is not None:
        run_dir = Path(run_dir_value)
        try_refresh_run_navigation(
            run_dir,
            update_index=run_dir.parent.name == "runs",
        )
    return rendered


__all__ = [
    "RunArtifacts",
    "ReportModel",
    "build_report_model",
    "build_report_model_from_artifacts",
    "generate_report",
    "load_run_artifacts",
    "render_report",
]
