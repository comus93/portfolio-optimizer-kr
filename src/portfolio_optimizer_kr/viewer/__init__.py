from .builder import build_report_model, build_report_model_from_artifacts
from .final_renderer import generate_report as _generate_report, render_report
from .loader import RunArtifacts, load_run_artifacts
from .pv_round1_overlay import apply_backtest_round1_overlay
from .report_model import ReportModel


def generate_report(
    run_dir,
    *,
    output_path=None,
    template_path=None,
):
    rendered = _generate_report(
        run_dir,
        output_path=output_path,
        template_path=template_path,
    )
    return apply_backtest_round1_overlay(run_dir, rendered)


__all__ = [
    "RunArtifacts",
    "ReportModel",
    "build_report_model",
    "build_report_model_from_artifacts",
    "generate_report",
    "load_run_artifacts",
    "render_report",
]
