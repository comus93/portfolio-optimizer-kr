from functools import wraps

from .builder import build_report_model, build_report_model_from_artifacts
from .final_renderer import generate_report as _generate_report, render_report
from .loader import RunArtifacts, load_run_artifacts
from .pv_pagination import apply_monthly_returns_pagination
from .report_model import ReportModel


@wraps(_generate_report)
def generate_report(*args, **kwargs):
    rendered = _generate_report(*args, **kwargs)
    return apply_monthly_returns_pagination(rendered)


__all__ = [
    "RunArtifacts",
    "ReportModel",
    "build_report_model",
    "build_report_model_from_artifacts",
    "generate_report",
    "load_run_artifacts",
    "render_report",
]
