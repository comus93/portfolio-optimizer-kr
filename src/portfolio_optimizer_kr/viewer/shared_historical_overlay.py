from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from . import historical_active_components as active
from . import historical_components as hc
from . import pv_visual as pv


# Explicit shared presentation identities. Backtest and Optimization both consume
# these functions for canonical historical views.
_annual_returns_chart = pv.annual_returns_chart
_drawdown_presentation = pv.drawdown_presentation
_annual_asset_returns_chart = pv.annual_asset_returns_chart
_correlations_table = pv.correlations_table
_rolling_returns_chart = pv.rolling_returns_chart
_growth_svg = pv.growth_svg
_trailing_returns_table = pv.trailing_returns_table


_STYLE = r"""
<style id="shared-historical-component-style">
.shared-historical-host .table-wrap{overflow-x:auto;border:1px solid #e2e8f0;margin-bottom:12px}
.shared-historical-host table{border-collapse:collapse;width:100%;min-width:640px}
.shared-historical-host th,.shared-historical-host td{padding:8px 10px;border-bottom:1px solid #e8ecf1;text-align:right;font-size:12px}
.shared-historical-host th:first-child,.shared-historical-host td:first-child{text-align:left}
.shared-historical-host th{background:#f5f7fa;color:#374151;font-weight:600}
.shared-historical-host thead tr:first-child th[colspan]{text-align:center;background:#edf3fa;border-bottom:1px solid #d4deea}
.shared-historical-host .legend{display:flex;flex-wrap:wrap;gap:18px;justify-content:center;margin:8px 0 10px}
.shared-historical-host .legend-item{display:inline-flex;align-items:center;gap:6px;font-size:12px}
.shared-historical-host .legend-item i{width:18px;height:3px;display:inline-block}
.shared-historical-host .chart-wrap{overflow-x:auto;position:relative;margin-bottom:12px}
.shared-historical-host .analysis-chart{width:100%;min-width:860px;height:auto;display:block;background:#fff}
.shared-historical-host .axis{stroke:#ccd6eb;stroke-width:1}.shared-historical-host .zero-axis{stroke:#8894a5;stroke-width:1.2}
.shared-historical-host .grid-line{stroke:#e6e6e6;stroke-width:1}.shared-historical-host .axis-label{font-size:11px;fill:#333}
.shared-historical-host .axis-title{font-size:12px;fill:#333}.shared-historical-host .chart-mark{cursor:crosshair}
.shared-historical-host .chart-tooltip{display:none;position:absolute;z-index:12;pointer-events:none;background:rgba(255,255,255,.98);color:#111827;border:1px solid #9ca3af;box-shadow:0 3px 12px rgba(0,0,0,.12);padding:9px 11px;font-size:12px;border-radius:3px;min-width:180px;max-width:min(540px,82vw)}
.shared-historical-host .chart-tooltip .tooltip-title{font-weight:700;margin-bottom:6px}
.shared-historical-host .chart-tooltip .tooltip-row{display:flex;align-items:center;justify-content:space-between;gap:18px;white-space:nowrap}
.shared-historical-host .chart-tooltip .tooltip-label{display:inline-flex;align-items:center;gap:6px}
.shared-historical-host .chart-tooltip .tooltip-dot{width:8px;height:8px;border-radius:50%;display:inline-block}
.shared-historical-host .chart-tooltip .tooltip-note{margin-top:6px;color:#6b7280}
.shared-historical-host .analysis-panel{border-top:1px solid #eef1f5;padding-top:8px;margin-top:18px}
.shared-historical-host .panel-subtitle,.shared-historical-host .muted{color:#6b7280;font-size:12px}
</style>
"""


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype={"portfolio":"string","ticker":"string","series":"string","asset":"string"})
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _artifact(root: Path, name: str, *, raw_first: bool = False) -> pd.DataFrame:
    first = root / ("raw" if raw_first else "review") / name
    second = root / ("review" if raw_first else "raw") / name
    frame = _read_csv(first)
    return frame if not frame.empty else _read_csv(second)


def _rename_identities(frame: pd.DataFrame, labels: dict[str, str]) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    out = frame.copy()
    for identity_column in ("portfolio", "series"):
        if identity_column in out:
            out[identity_column] = out[identity_column].map(lambda value: labels.get(str(value), str(value)))
    rename: dict[str, str] = {}
    for column in out.columns:
        text = str(column)
        for key, label in labels.items():
            if text == key:
                rename[column] = label
                break
            if text.startswith(f"{key}_"):
                rename[column] = f"{label}{text[len(key):]}"
                break
    return out.rename(columns=rename)


def _scale_optimizer_balance(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame.copy()
    out = frame.copy()
    for column in out.columns:
        if str(column).endswith("_balance"):
            out[column] = pd.to_numeric(out[column], errors="coerce") * 10000.0
    return out


def _scale_performance_balance(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "unit" not in frame:
        return frame.copy()
    out = frame.copy()
    mask = out["unit"].astype(str).eq("balance")
    for column in out.columns:
        if column in {"metric", "unit"}:
            continue
        out.loc[mask, column] = pd.to_numeric(out.loc[mask, column], errors="coerce") * 10000.0
    return out


def _active_up_down_html(stats: pd.DataFrame, observations: pd.DataFrame, portfolio_order: list[str], benchmark_label: str | None) -> str:
    return "".join(
        f'<div class="analysis-panel up-down-panel" data-portfolio="{hc.esc(portfolio)}">'
        f'<h3>{hc.esc(portfolio)} vs. {hc.esc(benchmark_label or "Benchmark")}</h3>'
        f'{active.up_down_statistics_table(stats, portfolio)}'
        '<h4>Return vs. Benchmark</h4>'
        f'{active.up_down_paired_chart(observations, portfolio, benchmark_label)}</div>'
        for portfolio in portfolio_order
    )


def build_optimizer_shared_sections(
    run_dir: str | Path,
    *,
    objective_name: str,
    benchmark_label: str | None,
) -> dict[str, str]:
    """Render persisted canonical historical artifacts through shared components."""
    root = Path(run_dir)
    labels = {"provided":"Provided Portfolio", "optimized":objective_name or "Optimized Portfolio"}
    portfolio_order = [labels["provided"], labels["optimized"]]

    performance = _scale_performance_balance(_rename_identities(_artifact(root, "performance_summary.csv"), labels))
    benchmark = _rename_identities(_artifact(root, "benchmark_summary.csv"), labels)
    growth = _scale_optimizer_balance(_rename_identities(_artifact(root, "portfolio_growth.csv"), labels))
    annual = _rename_identities(_artifact(root, "annual_returns.csv"), labels)
    trailing = _rename_identities(_artifact(root, "trailing_returns.csv"), labels)
    correlations = _rename_identities(_artifact(root, "correlations.csv", raw_first=True), labels)
    metrics = _rename_identities(_artifact(root, "portfolio_metrics.csv"), labels)
    monthly = _rename_identities(_artifact(root, "monthly_returns_calendar.csv"), labels)
    drawdown_series = _rename_identities(_artifact(root, "drawdown_series.csv"), labels)
    drawdowns = _rename_identities(_artifact(root, "drawdowns.csv"), labels)
    asset_performance = _artifact(root, "portfolio_asset_performance.csv")
    annual_assets = _artifact(root, "annual_asset_returns.csv", raw_first=True)
    rolling3 = _rename_identities(_artifact(root, "rolling_returns_3y.csv"), labels)
    rolling5 = _rename_identities(_artifact(root, "rolling_returns_5y.csv"), labels)
    active_returns = _rename_identities(_artifact(root, "active_returns.csv"), labels)
    active_contribution = _rename_identities(_artifact(root, "active_return_contribution.csv"), labels)
    up_down = _rename_identities(_artifact(root, "up_down_market_performance.csv"), labels)
    up_down_observations = _rename_identities(_artifact(root, "up_down_market_scatter.csv"), labels)

    sections: dict[str, str] = {}
    def add(selector: str, available: bool, markup: str) -> None:
        if available and markup:
            sections[selector] = markup

    add("#performance-summary .table-slot", not performance.empty, hc.performance_summary(performance, benchmark, portfolio_order, benchmark_label, "USD"))
    add("#portfolio-growth .chart", not growth.empty, _growth_svg(growth, portfolio_order, {"benchmark": benchmark_label or "Benchmark"}, "USD"))
    add("#annual-returns .chart", not annual.empty, _annual_returns_chart(annual, portfolio_order, benchmark_label))
    add("#trailing-returns .table-slot", not trailing.empty, _trailing_returns_table(trailing, portfolio_order, benchmark_label))
    add("#asset-correlations .table-slot", not correlations.empty, _correlations_table(correlations, benchmark_label))
    add("#portfolio-metrics .table-slot", not metrics.empty, hc.metrics_matrix(metrics, portfolio_order, benchmark_label, performance, "USD"))
    add("#monthly-returns .table-slot", not monthly.empty, hc.friendly_table(monthly, portfolio_order=portfolio_order, benchmark_label=benchmark_label))
    add("#drawdown-chart .chart", not drawdown_series.empty, _drawdown_presentation(drawdown_series, drawdowns, portfolio_order, benchmark_label))
    add("#asset-performance .table-slot", not asset_performance.empty, hc.asset_performance_table(asset_performance))
    add("#portfolio-asset-correlations .table-slot", not correlations.empty, _correlations_table(correlations, benchmark_label))
    add("#annual-asset-returns .chart", not annual_assets.empty, _annual_asset_returns_chart(annual_assets) + hc.annual_asset_returns_table(annual_assets))
    add("#rolling-returns-3y .chart", not rolling3.empty, _rolling_returns_chart(rolling3, portfolio_order, benchmark_label, 3))
    add("#rolling-returns-5y .chart", not rolling5.empty, _rolling_returns_chart(rolling5, portfolio_order, benchmark_label, 5))

    if not benchmark.empty:
        add("#annualized-active-return .chart", not active_returns.empty, active.annual_active_return(active_returns, portfolio_order))
        add("#active-return-contribution .chart", not active_contribution.empty, active.active_contribution(active_contribution, portfolio_order))
        if not active_contribution.empty:
            sections["#active-return-contribution .table-slot"] = ""
        add(
            "#rolling-active-return .chart",
            not active_returns.empty,
            "".join(active.rolling_active_risk_panel(active_returns, portfolio, benchmark_label) for portfolio in portfolio_order),
        )
        add("#up-down-market .chart", not up_down.empty and not up_down_observations.empty, _active_up_down_html(up_down, up_down_observations, portfolio_order, benchmark_label))
        if not up_down.empty and not up_down_observations.empty:
            sections["#up-down-market .table-slot"] = ""
    return sections


def apply_optimizer_shared_historical_components(
    run_dir: str | Path,
    output_path: str | Path,
    *,
    objective_name: str,
    benchmark_label: str | None,
) -> Path:
    target = Path(output_path)
    document = target.read_text(encoding="utf-8")
    sections = build_optimizer_shared_sections(run_dir, objective_name=objective_name, benchmark_label=benchmark_label)
    if not sections or 'id="shared-historical-component-overlay"' in document:
        return target

    payload = json.dumps(sections, ensure_ascii=False).replace("</", "<\\/")
    script = f'''{_STYLE}
<script id="shared-historical-component-overlay">
(() => {{
  const replacements = {payload};
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
  const renderTooltip = mark => {{
    const raw = mark.dataset.tooltipJson;
    if (!raw) return esc(mark.dataset.tooltip || mark.getAttribute('aria-label') || '');
    try {{
      const data = JSON.parse(raw);
      const rows = (data.items || []).map(item => `<div class="tooltip-row"><span class="tooltip-label"><i class="tooltip-dot" style="background:${{esc(item.color)}}"></i>${{esc(item.label)}}</span><b>${{esc(item.value)}}</b></div>`).join('');
      const note = data.note ? `<div class="tooltip-note">${{esc(data.note)}}</div>` : '';
      return `<div class="tooltip-title">${{esc(data.title)}}</div>${{rows}}${{note}}`;
    }} catch (_error) {{ return esc(mark.dataset.tooltip || mark.getAttribute('aria-label') || ''); }}
  }};
  const mount = () => {{
    for (const [selector, markup] of Object.entries(replacements)) {{
      const host = document.querySelector(selector); if (!host) continue;
      host.classList.add('shared-historical-host'); host.innerHTML = markup;
    }}
    document.querySelectorAll('.shared-historical-host .chart-mark[data-tooltip]').forEach(mark => {{
      const show = event => {{
        const host = mark.closest('.chart-wrap'); const tip = host?.querySelector('.chart-tooltip'); if (!host || !tip) return;
        tip.innerHTML = renderTooltip(mark); tip.style.display = 'block';
        const bounds = host.getBoundingClientRect(); const markBounds = mark.getBoundingClientRect();
        const x = event?.clientX || markBounds.left; const y = event?.clientY || markBounds.top;
        tip.style.left = `${{Math.max(6, x - bounds.left + host.scrollLeft + 12)}}px`;
        tip.style.top = `${{Math.max(6, y - bounds.top + host.scrollTop - 44)}}px`;
      }};
      const hide = () => {{ const tip = mark.closest('.chart-wrap')?.querySelector('.chart-tooltip'); if (tip) tip.style.display='none'; }};
      mark.addEventListener('mouseenter', show); mark.addEventListener('mousemove', show); mark.addEventListener('mouseleave', hide); mark.addEventListener('focus', show); mark.addEventListener('blur', hide);
    }});
  }};
  if (document.readyState === 'complete') setTimeout(mount, 180);
  else window.addEventListener('load', () => setTimeout(mount, 180), {{once:true}});
}})();
</script>'''
    document = document.replace("</body>", f"{script}\n</body>", 1) if "</body>" in document else f"{document}\n{script}"
    target.write_text(document, encoding="utf-8")
    return target
