from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from . import historical_active_components as active_components
from . import historical_components


_OPTION_LABELS = {
    "month_to_month": "Month-to-Month",
    "year_to_year": "Year-to-Year",
    "canonical_total_return": "Total Return",
    "none": "None",
    "yearly": "Yearly",
    "semiannual": "Semiannual",
    "quarterly": "Quarterly",
    "monthly": "Monthly",
}

# Compatibility names for callers/tests. Implementations are deliberately
# shared report components rather than Backtest-owned copies.
_money = historical_components.money
_table = historical_components.table
_friendly_table = historical_components.friendly_table
_calendar_ticks = historical_components.calendar_ticks
_growth_svg = historical_components.growth_svg
_performance_summary = historical_components.performance_summary
_trailing_returns_table = historical_components.trailing_returns_table
_metrics_matrix = historical_components.metrics_matrix
_annual_returns_chart = historical_components.annual_returns_chart
_annual_asset_returns_table = historical_components.annual_asset_returns_table
_annual_asset_returns_chart = historical_components.annual_asset_returns_chart
_correlations_table = historical_components.correlations_table
_decomposition_table = historical_components.decomposition_table
_asset_performance_table = historical_components.asset_performance_table
_drawdown_presentation = historical_components.drawdown_presentation
_rolling_returns_chart = historical_components.rolling_returns_chart
_active_returns_presentation = active_components.active_returns_presentation


def _esc(value: Any) -> str:
    return historical_components.esc(value)


def _pct(value: Any) -> str:
    return historical_components.pct(value)


def _display_option(value: Any) -> str:
    text = str(value or "")
    return _OPTION_LABELS.get(text, historical_components.human_column(text))


def _base_currency(configuration: dict[str, Any]) -> str:
    currencies = {
        str(asset.get("currency") or "").upper()
        for asset in configuration.get("assets", [])
        if isinstance(asset, dict) and asset.get("currency")
    }
    benchmark = configuration.get("benchmark")
    if isinstance(benchmark, dict) and benchmark.get("currency"):
        currencies.add(str(benchmark["currency"]).upper())
    if "KRW" in currencies:
        return "KRW"
    return next(iter(currencies)) if len(currencies) == 1 else "USD"


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(
            path,
            dtype={
                "asset": "string",
                "portfolio": "string",
                "series": "string",
                "ticker": "string",
            },
        )
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _portfolio_order(frame: pd.DataFrame, requested: list[str]) -> list[str]:
    available: list[str] = []
    if "portfolio" in frame.columns:
        candidates = (str(value) for value in frame["portfolio"].dropna())
    else:
        candidates = (str(column) for column in frame.columns)
    for candidate in candidates:
        if candidate not in available:
            available.append(candidate)
    ordered = [name for name in requested if name in available]
    for name in available:
        if name not in ordered and name != "benchmark":
            ordered.append(name)
    return ordered


def _allocation_matrix(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    required = {"portfolio", "ticker", "target_weight_pct"}
    if not required.issubset(frame.columns):
        return _friendly_table(frame, portfolio_order=portfolio_order)
    shaped = frame.copy()
    shaped["asset"] = shaped.apply(
        lambda row: (
            f"{row.get('name')} ({row.get('ticker')})"
            if pd.notna(row.get("name")) and str(row.get("name")).strip()
            else str(row.get("ticker"))
        ),
        axis=1,
    )
    pivot = shaped.pivot_table(
        index="asset",
        columns="portfolio",
        values="target_weight_pct",
        aggfunc="first",
        fill_value=0.0,
    )
    requested = portfolio_order or _portfolio_order(shaped, [])
    columns = [name for name in requested if name in pivot.columns]
    columns.extend(column for column in pivot.columns if column not in columns)
    pivot = pivot.reindex(columns=columns).reset_index()
    for column in pivot.columns:
        if column != "asset":
            pivot[column] = pivot[column].map(_pct)
    return _table(
        pivot.rename(columns={"asset": "Asset"}),
        table_id="allocation-matrix",
    )


def _allocation_from_result(result: dict[str, Any]) -> pd.DataFrame:
    definitions = result.get("portfolio_definitions") or {}
    configuration = result.get("configuration") or {}
    assets = {
        str(asset.get("symbol")): str(asset.get("name") or "")
        for asset in configuration.get("assets", [])
        if isinstance(asset, dict) and asset.get("symbol") is not None
    }
    rows: list[dict[str, object]] = []
    if not isinstance(definitions, dict):
        return pd.DataFrame()
    for portfolio, definition in definitions.items():
        if not isinstance(definition, dict):
            continue
        weights = definition.get("target_weights") or {}
        if not isinstance(weights, dict):
            continue
        for ticker, weight in weights.items():
            rows.append(
                {
                    "portfolio": str(portfolio),
                    "ticker": str(ticker),
                    "name": assets.get(str(ticker), ""),
                    "target_weight_pct": float(weight) * 100.0,
                }
            )
    return pd.DataFrame(rows)


def _asset_performance_from_result(result: dict[str, Any]) -> pd.DataFrame:
    """Presentation fallback for historical runs, without recomputing finance."""
    asset_statistics = result.get("asset_statistics") or {}
    values = (
        asset_statistics.get("asset_performance")
        if isinstance(asset_statistics, dict)
        else None
    )
    if not isinstance(values, dict):
        return pd.DataFrame()
    assets = {
        str(asset.get("symbol")): str(asset.get("name") or "")
        for asset in (result.get("configuration") or {}).get("assets", [])
        if isinstance(asset, dict) and asset.get("symbol") is not None
    }
    rows: list[dict[str, object]] = []
    for ticker, payload in values.items():
        if not isinstance(payload, dict):
            continue
        trailing = payload.get("trailing_returns") or {}
        row: dict[str, object] = {
            "ticker": str(ticker),
            "name": assets.get(str(ticker), ""),
            "cagr_pct": _decimal_pct(payload.get("cagr")),
            "annualized_return_pct": _decimal_pct(
                payload.get("annualized_return")
            ),
            "annualized_volatility_pct": _decimal_pct(
                payload.get("annualized_volatility")
            ),
            "best_year_pct": _decimal_pct(payload.get("best_year")),
            "worst_year_pct": _decimal_pct(payload.get("worst_year")),
            "max_drawdown_pct": _decimal_pct(payload.get("max_drawdown")),
            "sharpe_ratio": payload.get("sharpe_ex_post"),
            "sortino_ratio": payload.get("sortino"),
        }
        for key in ("3m", "ytd", "1y", "3y", "5y", "10y"):
            row[f"{key}_pct"] = _decimal_pct(
                trailing.get(key) if isinstance(trailing, dict) else None
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _decimal_pct(value: Any) -> float | None:
    try:
        return float(value) * 100.0 if value is not None else None
    except (TypeError, ValueError):
        return None


def _period_note(
    configuration: dict[str, Any],
    coverage: dict[str, Any],
) -> str:
    period = configuration.get("analysis_period", {}) or {}
    requested_start = str(period.get("start") or "")
    requested_end = str(period.get("end") or "")
    effective_start = str(coverage.get("start") or "")
    effective_end = str(coverage.get("end") or "")
    if requested_start and requested_end and (
        requested_start[:7] != effective_start[:7]
        or requested_end[:7] != effective_end[:7]
    ):
        return (
            '<div class="coverage-note"><b>Data coverage:</b> Requested period '
            f'{_esc(requested_start)} → {_esc(requested_end)} was constrained to '
            f'{_esc(effective_start)} → {_esc(effective_end)} by common available data.</div>'
        )
    return ""


def generate_backtest_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
) -> Path:
    """Compose a Backtest report strictly from persisted canonical artifacts."""
    root = Path(run_dir)
    result_path = root / "result.json"
    if not result_path.is_file():
        raise FileNotFoundError(f"missing canonical result: {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    configuration = result.get("configuration", {})
    if configuration.get("product_mode") != "backtest":
        raise ValueError("backtest renderer requires product_mode=backtest")

    review, raw = root / "review", root / "raw"

    def artifact(name: str) -> pd.DataFrame:
        reviewed = _read_csv(review / name)
        return reviewed if not reviewed.empty else _read_csv(raw / name)

    def raw_artifact(name: str) -> pd.DataFrame:
        full_precision = _read_csv(raw / name)
        return full_precision if not full_precision.empty else _read_csv(review / name)

    allocations = artifact("target_allocations.csv")
    if allocations.empty:
        allocations = _allocation_from_result(result)
    performance = artifact("performance_summary.csv")
    trailing = artifact("trailing_returns.csv")
    annual = artifact("annual_returns.csv")
    monthly = artifact("monthly_returns_calendar.csv")
    benchmark = artifact("benchmark_summary.csv")
    growth = artifact("portfolio_growth.csv")
    drawdowns = artifact("drawdowns.csv")
    drawdown_series = artifact("drawdown_series.csv")
    rolling3 = artifact("rolling_returns_3y.csv")
    rolling5 = artifact("rolling_returns_5y.csv")
    correlations = raw_artifact("correlations.csv")
    returns_decomp = artifact("return_decomposition.csv")
    risk_decomp = artifact("risk_decomposition.csv")
    portfolio_metrics = artifact("portfolio_metrics.csv")
    annual_assets = raw_artifact("annual_asset_returns.csv")
    active_returns = artifact("active_returns.csv")
    active_contribution = artifact("active_return_contribution.csv")
    up_down = artifact("up_down_market_performance.csv")
    up_down_observations = artifact("up_down_market_scatter.csv")
    asset_performance = artifact("portfolio_asset_performance.csv")
    if asset_performance.empty:
        asset_performance = _asset_performance_from_result(result)

    period = configuration.get("analysis_period", {}) or {}
    benchmark_configuration = configuration.get("benchmark")
    benchmark_label = (
        (
            benchmark_configuration.get("name")
            or benchmark_configuration.get("symbol")
        )
        if isinstance(benchmark_configuration, dict)
        else None
    )
    currency = _base_currency(configuration)
    portfolio_order = list((result.get("portfolio_definitions") or {}).keys())
    if not portfolio_order:
        portfolio_order = _portfolio_order(allocations, [])
    coverage = (
        result.get("data_coverage", {}).get("backtest_monthly_returns", {}) or {}
    )
    alignment = "Yes" if configuration.get("calendar_aligned") else "No"
    effective_label = f"{coverage.get('start')} - {coverage.get('end')}"
    series_labels = {"benchmark": benchmark_label or "Benchmark"}
    asset_names = {
        str(asset.get("symbol")): str(asset.get("name") or "")
        for asset in configuration.get("assets", [])
        if isinstance(asset, dict)
    }

    nav_sections = [("overview", "Summary")]
    if benchmark_label and not benchmark.empty:
        nav_sections.append(("activeReturns", "Active Returns"))
    nav_sections.extend(
        [
            ("metrics", "Metrics"),
            ("annualReturns", "Annual Returns"),
            ("monthlyReturns", "Monthly Returns"),
            ("drawdowns", "Drawdowns"),
            ("assets", "Assets"),
            ("rollingReturns", "Rolling Returns"),
        ]
    )
    nav = "".join(
        f'<a href="#{section}">{_esc(label)}</a>'
        for section, label in nav_sections
    )

    active_section = ""
    if benchmark_label and not benchmark.empty:
        active_section = (
            '<section id="activeReturns" class="result-section benchmark-relative">'
            '<h2>Active Returns</h2>'
            + _active_returns_presentation(
                active_returns,
                active_contribution,
                benchmark,
                up_down,
                portfolio_order,
                benchmark_label,
                asset_names,
                up_down_observations,
            )
            + "</section>"
        )

    document = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Portfolio Backtest Report</title>
<style>
:root {{ color-scheme:light; font-family:Roboto,"Work Sans","Helvetica Neue",Arial,sans-serif; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:#fff; color:#333; }}
.topbar {{ border-bottom:1px solid #d8dee8; padding:14px 24px; font-weight:600; font-size:20px; }}
.shell {{ display:grid; grid-template-columns:190px minmax(0,1fr); max-width:1400px; margin:0 auto; }}
.sidebar {{ border-right:1px solid #e2e8f0; padding:22px 14px; min-height:100vh; position:sticky; top:0; align-self:start; }}
.sidebar a {{ display:block; color:#374151; text-decoration:none; padding:10px 9px; border-radius:5px; font-size:14px; }}
.sidebar a:hover,.sidebar a:focus {{ background:#eef4ff; color:#184f9d; outline:none; }}
main {{ min-width:0; padding:26px 32px 72px; }}
.result-header {{ margin:0 0 12px; color:#1f2937; font-size:25px; font-weight:500; }}
.coverage-note {{ border-left:3px solid #316db5; padding:8px 12px; margin:0 0 20px; background:#f8fbff; font-size:13px; }}
.result-section {{ border:1px solid #e0e5ec; padding:22px; margin:0 0 24px; background:#fff; }}
.result-section h2 {{ margin:0 0 18px; font-size:21px; color:#1d5c9b; font-weight:500; }}
.result-section h3 {{ margin:28px 0 10px; font-size:17px; font-weight:500; color:#1d5c9b; }}
.result-section h4 {{ margin:20px 0 8px; font-size:15px; color:#374151; }}
.result-section h5 {{ margin:18px 0 8px; font-size:14px; }}
.meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1px; background:#e5e7eb; border:1px solid #e5e7eb; margin-bottom:20px; }}
.meta div {{ background:#fff; padding:10px 12px; font-size:13px; }}
.meta b {{ display:block; font-size:11px; color:#6b7280; margin-bottom:4px; text-transform:uppercase; }}
.table-wrap {{ overflow-x:auto; border:1px solid #e2e8f0; margin-bottom:12px; }}
table {{ border-collapse:collapse; width:100%; min-width:640px; }}
th,td {{ padding:8px 10px; border-bottom:1px solid #e8ecf1; text-align:right; font-size:13px; }}
th:first-child,td:first-child {{ text-align:left; }} th {{ background:#f5f7fa; color:#374151; font-weight:600; }}
tbody tr:nth-child(even) {{ background:#fafbfc; }} .heatmap td {{ font-variant-numeric:tabular-nums; }}
.identity-cell {{ font-weight:500; }}
.legend {{ display:flex; flex-wrap:wrap; gap:18px; justify-content:center; margin:8px 0 10px; }}
.legend-item {{ display:inline-flex; align-items:center; gap:6px; font-size:12px; }} .legend-item i {{ width:18px; height:3px; display:inline-block; }}
.chart-wrap {{ overflow-x:auto; position:relative; margin-bottom:12px; }}
.analysis-chart {{ width:100%; min-width:900px; height:auto; display:block; }}
.axis {{ stroke:#ccd6eb; stroke-width:1; }} .zero-axis {{ stroke:#9ca3af; }} .grid-line {{ stroke:#e6e6e6; stroke-width:1; }}
.axis-label {{ font-size:11px; fill:#333; }} .axis-title {{ font-size:12px; fill:#333; }} .chart-mark {{ cursor:crosshair; }}
.line-point,.growth-point,.tracking-error-point {{ opacity:0; }}
.line-point:hover,.line-point:focus,.growth-point:hover,.growth-point:focus,.tracking-error-point:hover,.tracking-error-point:focus {{ opacity:1; stroke:#fff; stroke-width:2; outline:none; }}
.chart-tooltip {{ display:none; position:absolute; z-index:4; pointer-events:none; background:rgba(255,255,255,.98); border:1px solid #9ca3af; box-shadow:0 3px 12px rgba(0,0,0,.12); padding:8px 10px; font-size:12px; border-radius:3px; max-width:min(520px,80vw); }}
.muted,.panel-subtitle {{ color:#6b7280; font-size:12px; }} .summary-block {{ margin-top:24px; }}
.analysis-panel {{ border-top:1px solid #eef1f5; padding-top:8px; margin-top:18px; }}
@media (max-width:800px) {{ .shell {{ display:block; }} .sidebar {{ min-height:0; position:sticky; top:0; z-index:5; display:flex; gap:4px; overflow-x:auto; border-right:0; border-bottom:1px solid #e2e8f0; background:#fff; padding:8px 10px; }} .sidebar a {{ white-space:nowrap; padding:7px 9px; }} main {{ padding:18px 12px 50px; }} .result-section {{ padding:14px; }} }}
</style></head><body>
<div class="topbar">Portfolio Research · Backtest</div>
<div class="shell"><nav class="sidebar" aria-label="Backtest result sections">{nav}</nav><main>
<h1 class="result-header">Portfolio Analysis Results ({_esc(effective_label)})</h1>{_period_note(configuration, coverage)}
<section id="overview" class="result-section"><h2>Summary</h2><div class="meta">
<div><b>Run ID</b>{_esc(configuration.get('run_id'))}</div>
<div><b>Time Period</b>{_esc(_display_option(configuration.get('time_period_mode')))}</div>
<div><b>Requested</b>{_esc(period.get('start'))} → {_esc(period.get('end'))}</div>
<div><b>Effective</b>{_esc(coverage.get('start'))} → {_esc(coverage.get('end'))} ({_esc(coverage.get('observations'))} months)</div>
<div><b>Initial Amount</b>{_money(configuration.get('initial_balance'), currency)}</div>
<div><b>Benchmark</b>{_esc(benchmark_label or 'None')}</div>
<div><b>Rebalancing</b>{_esc(_display_option(configuration.get('rebalancing_period')))}</div>
<div><b>Calendar Aligned</b>{alignment}</div>
<div><b>Return Semantics</b>{_esc(_display_option(configuration.get('return_semantics')))}</div></div>
<div id="allocation" class="summary-block"><h3>Target Allocation</h3>{_allocation_matrix(allocations, portfolio_order)}</div>
<div id="performance" class="summary-block"><h3>Performance Summary</h3>{_performance_summary(performance, benchmark, portfolio_order, benchmark_label, currency)}</div>
<div id="growth" class="summary-block"><h3>Portfolio Growth</h3>{_growth_svg(growth, portfolio_order, series_labels, currency)}</div>
<div id="trailing" class="summary-block"><h3>Trailing Returns</h3>{_trailing_returns_table(trailing, portfolio_order, benchmark_label)}</div></section>
{active_section}
<section id="metrics" class="result-section"><h2>Metrics</h2>{_metrics_matrix(portfolio_metrics, portfolio_order, benchmark_label, performance, currency)}</section>
<section id="annualReturns" class="result-section"><h2>Annual Returns</h2>{_annual_returns_chart(annual, portfolio_order, benchmark_label)}{_friendly_table(annual, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
<section id="monthlyReturns" class="result-section"><h2>Monthly Returns</h2>{_friendly_table(monthly, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
<section id="drawdowns" class="result-section"><h2>Drawdowns</h2>{_drawdown_presentation(drawdown_series, drawdowns, portfolio_order, benchmark_label)}</section>
<section id="assets" class="result-section"><h2>Assets</h2>
<h3>Portfolio Asset Performance</h3>{_asset_performance_table(asset_performance)}
<h3>Annual Asset Returns</h3>{_annual_asset_returns_table(annual_assets)}{_annual_asset_returns_chart(annual_assets, asset_names)}
<h3>Correlations</h3>{_correlations_table(correlations, benchmark_label)}
<h3>Return Decomposition</h3>{_decomposition_table(returns_decomp, portfolio_order, currency=currency)}
<h3>Risk Decomposition</h3>{_decomposition_table(risk_decomp, portfolio_order, currency=currency)}</section>
<section id="rollingReturns" class="result-section"><h2>Rolling Returns</h2>
<h3>Rolling 3 Year Annualized Return</h3>{_rolling_returns_chart(rolling3, portfolio_order, benchmark_label, 3)}{_friendly_table(rolling3, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}
<h3>Rolling 5 Year Annualized Return</h3>{_rolling_returns_chart(rolling5, portfolio_order, benchmark_label, 5)}{_friendly_table(rolling5, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
</main></div>
<script>
(() => {{
  const marks = document.querySelectorAll('.chart-mark[data-tooltip]');
  const show = (mark, event) => {{
    const host = mark.closest('.chart-wrap'); if (!host) return;
    const tooltip = host.querySelector('.chart-tooltip'); if (!tooltip) return;
    tooltip.textContent = mark.dataset.tooltip || mark.getAttribute('aria-label') || '';
    tooltip.style.display = 'block';
    const hostRect = host.getBoundingClientRect(); const markRect = mark.getBoundingClientRect();
    const clientX = event?.clientX || (markRect.left + markRect.width / 2);
    const clientY = event?.clientY || markRect.top;
    tooltip.style.left = `${{Math.max(6, clientX - hostRect.left + host.scrollLeft + 12)}}px`;
    tooltip.style.top = `${{Math.max(6, clientY - hostRect.top + host.scrollTop - 44)}}px`;
  }};
  const hide = mark => {{
    const tooltip = mark.closest('.chart-wrap')?.querySelector('.chart-tooltip');
    if (tooltip) tooltip.style.display = 'none';
  }};
  marks.forEach(mark => {{
    mark.addEventListener('mouseenter', event => show(mark, event));
    mark.addEventListener('mousemove', event => show(mark, event));
    mark.addEventListener('mouseleave', () => hide(mark));
    mark.addEventListener('focus', event => show(mark, event));
    mark.addEventListener('blur', () => hide(mark));
  }});
}})();
</script></body></html>'''
    target = Path(output_path) if output_path is not None else root / "report.html"
    target.write_text(document, encoding="utf-8")
    return target
