from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


_DEF_WIDTH = 960
_DEF_HEIGHT = 320


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _pct(value: Any) -> str:
    return f"{float(value):,.2f}%" if _finite(value) else "N/A"


def _money(value: Any) -> str:
    return f"${float(value):,.0f}" if _finite(value) else "N/A"


def _ratio(value: Any) -> str:
    return f"{float(value):,.3f}" if _finite(value) else "N/A"


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _table(frame: pd.DataFrame, *, table_id: str | None = None) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    identifier = f' id="{_esc(table_id)}"' if table_id else ""
    headers = "".join(f"<th>{_esc(column)}</th>" for column in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = "".join(
            f"<td>{_esc('N/A' if pd.isna(value) else value)}</td>" for value in row
        )
        rows.append(f"<tr>{cells}</tr>")
    return (
        f'<div class="table-wrap"><table{identifier}><thead><tr>{headers}</tr></thead>'
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _growth_svg(frame: pd.DataFrame) -> str:
    if frame.empty or "date" not in frame:
        return '<p class="muted">N/A</p>'
    series_columns = [column for column in frame.columns if column.endswith("_balance")]
    if not series_columns:
        return '<p class="muted">N/A</p>'

    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"])
    if shaped.empty:
        return '<p class="muted">N/A</p>'

    values = pd.to_numeric(shaped[series_columns].stack(), errors="coerce").dropna()
    if values.empty:
        return '<p class="muted">N/A</p>'
    y_min = float(values.min())
    y_max = float(values.max())
    if math.isclose(y_min, y_max):
        y_min *= 0.95
        y_max *= 1.05 if y_max else 1.0
    margin_left, margin_right, margin_top, margin_bottom = 78, 22, 18, 44
    plot_w = _DEF_WIDTH - margin_left - margin_right
    plot_h = _DEF_HEIGHT - margin_top - margin_bottom
    denom = max(y_max - y_min, 1e-12)
    count = max(len(shaped) - 1, 1)

    palette = ["#2563eb", "#16a34a", "#ea580c", "#7c3aed"]
    paths: list[str] = []
    points: list[str] = []
    legend: list[str] = []
    for idx, column in enumerate(series_columns):
        label = column[: -len("_balance")]
        color = palette[idx % len(palette)]
        coords: list[tuple[float, float, str, float]] = []
        for position, (_, row) in enumerate(shaped.iterrows()):
            value = row[column]
            if not _finite(value):
                continue
            x = margin_left + plot_w * position / count
            y = margin_top + plot_h * (y_max - float(value)) / denom
            coords.append((x, y, str(pd.Timestamp(row["date"]).date()), float(value)))
        if coords:
            polyline = " ".join(f"{x:.2f},{y:.2f}" for x, y, _, _ in coords)
            paths.append(
                f'<polyline fill="none" stroke="{color}" stroke-width="2.5" points="{polyline}" />'
            )
            for x, y, date, value in coords:
                title = _esc(f"{date} | {label}: ${value:,.0f}")
                points.append(
                    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}" '
                    f'tabindex="0" aria-label="{title}"><title>{title}</title></circle>'
                )
        legend.append(
            f'<span class="legend-item"><i style="background:{color}"></i>{_esc(label)}</span>'
        )

    start = str(shaped["date"].iloc[0].date())
    end = str(shaped["date"].iloc[-1].date())
    svg = f"""
    <div class="legend">{''.join(legend)}</div>
    <div class="chart-wrap">
      <svg class="growth-chart" viewBox="0 0 {_DEF_WIDTH} {_DEF_HEIGHT}" role="img" aria-label="Portfolio balance growth over time">
        <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" class="axis" />
        <line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" class="axis" />
        <text x="8" y="{margin_top + 8}" class="axis-label">{_esc(_money(y_max))}</text>
        <text x="8" y="{margin_top + plot_h}" class="axis-label">{_esc(_money(y_min))}</text>
        <text x="{margin_left}" y="{_DEF_HEIGHT - 12}" class="axis-label">{_esc(start)}</text>
        <text x="{margin_left + plot_w}" y="{_DEF_HEIGHT - 12}" text-anchor="end" class="axis-label">{_esc(end)}</text>
        {''.join(paths)}
        {''.join(points)}
      </svg>
    </div>
    <p class="muted">각 point에 마우스를 올리거나 키보드 focus하면 날짜, portfolio identity, balance를 확인할 수 있다.</p>
    """
    return svg


def _performance_summary(frame: pd.DataFrame) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    unit = rendered.get("unit", pd.Series(index=rendered.index, dtype=object))
    for column in rendered.columns:
        if column in {"metric", "unit"}:
            continue
        formatted = []
        for idx, value in rendered[column].items():
            kind = unit.loc[idx] if idx in unit.index else None
            if kind == "pct":
                formatted.append(_pct(value))
            elif kind == "balance":
                formatted.append(_money(value))
            else:
                formatted.append(_ratio(value))
        rendered[column] = formatted
    return _table(rendered)


def generate_backtest_report(
    run_dir: str | Path,
    *,
    output_path: str | Path | None = None,
) -> Path:
    root = Path(run_dir)
    result_path = root / "result.json"
    if not result_path.is_file():
        raise FileNotFoundError(f"missing canonical result: {result_path}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    configuration = result.get("configuration", {})
    if configuration.get("product_mode") != "backtest":
        raise ValueError("backtest renderer requires product_mode=backtest")

    review = root / "review"
    raw = root / "raw"
    allocations = _read_csv(review / "target_allocations.csv")
    performance = _read_csv(review / "performance_summary.csv")
    trailing = _read_csv(review / "trailing_returns.csv")
    annual = _read_csv(review / "annual_returns.csv")
    monthly = _read_csv(review / "monthly_returns_calendar.csv")
    benchmark = _read_csv(review / "benchmark_summary.csv")
    growth = _read_csv(raw / "portfolio_growth.csv")
    drawdowns = _read_csv(review / "drawdowns.csv")
    rolling3 = _read_csv(raw / "rolling_returns_3y.csv")
    rolling5 = _read_csv(raw / "rolling_returns_5y.csv")
    correlations = _read_csv(review / "correlations.csv")
    returns_decomp = _read_csv(review / "return_decomposition.csv")
    risk_decomp = _read_csv(review / "risk_decomposition.csv")

    period = configuration.get("analysis_period", {}) or {}
    benchmark_cfg = configuration.get("benchmark")
    benchmark_label = (
        benchmark_cfg.get("name") or benchmark_cfg.get("symbol")
        if isinstance(benchmark_cfg, dict)
        else None
    )
    coverage = result.get("data_coverage", {}).get("backtest_monthly_returns", {}) or {}
    alignment = "Yes" if configuration.get("calendar_aligned") else "No"

    nav_sections = [
        ("overview", "Overview"),
        ("allocation", "Allocation"),
        ("growth", "Growth"),
        ("performance", "Performance"),
        ("annual", "Annual Returns"),
        ("monthly", "Monthly Returns"),
        ("drawdowns", "Drawdowns"),
        ("rolling", "Rolling Returns"),
        ("correlations", "Correlations"),
        ("decomposition", "Decomposition"),
    ]
    if not benchmark.empty:
        nav_sections.append(("active", "Benchmark-relative"))
    nav = "".join(f'<a href="#{section}">{_esc(label)}</a>' for section, label in nav_sections)

    active_section = ""
    if not benchmark.empty:
        active_section = f"""
        <section id="active">
          <h2>Benchmark-relative Analytics</h2>
          {_table(benchmark)}
        </section>
        """

    document = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Portfolio Backtest Report</title>
<style>
:root {{ color-scheme: light; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
body {{ margin:0; background:#f5f7fb; color:#172033; }}
header {{ padding:28px clamp(18px,4vw,48px); background:#111827; color:white; }}
header h1 {{ margin:0 0 8px; font-size:clamp(24px,4vw,38px); }}
header p {{ margin:4px 0; color:#d1d5db; }}
nav {{ position:sticky; top:0; z-index:3; display:flex; gap:8px; overflow-x:auto; padding:10px clamp(14px,4vw,48px); background:white; border-bottom:1px solid #e5e7eb; }}
nav a {{ white-space:nowrap; padding:7px 10px; border-radius:8px; text-decoration:none; color:#1f2937; background:#f3f4f6; }}
main {{ max-width:1180px; margin:0 auto; padding:22px clamp(14px,3vw,28px) 60px; }}
section {{ background:white; border:1px solid #e5e7eb; border-radius:14px; padding:20px; margin:16px 0; box-shadow:0 3px 14px rgba(17,24,39,.04); }}
h2 {{ margin-top:0; font-size:20px; }}
.meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:10px; }}
.meta div {{ background:#f8fafc; border-radius:10px; padding:10px 12px; }}
.meta b {{ display:block; font-size:12px; color:#64748b; margin-bottom:3px; }}
.table-wrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; min-width:620px; }}
th,td {{ padding:9px 10px; border-bottom:1px solid #e5e7eb; text-align:right; font-size:13px; }}
th:first-child,td:first-child {{ text-align:left; }}
th {{ position:sticky; top:0; background:#f8fafc; color:#475569; }}
.legend {{ display:flex; flex-wrap:wrap; gap:14px; margin-bottom:8px; }}
.legend-item {{ display:inline-flex; align-items:center; gap:6px; font-size:13px; }}
.legend-item i {{ width:18px; height:3px; display:inline-block; border-radius:3px; }}
.chart-wrap {{ overflow-x:auto; }}
.growth-chart {{ width:100%; min-width:720px; height:auto; }}
.axis {{ stroke:#94a3b8; stroke-width:1; }}
.axis-label {{ font-size:12px; fill:#64748b; }}
.muted {{ color:#64748b; font-size:13px; }}
@media (max-width:640px) {{ section {{ padding:14px; }} header {{ padding:22px 16px; }} }}
</style>
</head>
<body>
<header>
  <h1>Portfolio Backtest</h1>
  <p>Run ID: {_esc(configuration.get('run_id'))}</p>
  <p>Realized historical comparison. Optimization-specific results are not included.</p>
</header>
<nav>{nav}</nav>
<main>
<section id="overview">
  <h2>Overview</h2>
  <div class="meta">
    <div><b>Time Period Mode</b>{_esc(configuration.get('time_period_mode'))}</div>
    <div><b>Requested Period</b>{_esc(period.get('start'))} → {_esc(period.get('end'))}</div>
    <div><b>Effective Period</b>{_esc(coverage.get('start'))} → {_esc(coverage.get('end'))} ({_esc(coverage.get('observations'))} months)</div>
    <div><b>Initial Amount</b>{_money(configuration.get('initial_balance'))}</div>
    <div><b>Benchmark</b>{_esc(benchmark_label or 'None')}</div>
    <div><b>Rebalancing</b>{_esc(configuration.get('rebalancing_period'))}</div>
    <div><b>Calendar Aligned</b>{alignment}</div>
    <div><b>Return Semantics</b>{_esc(configuration.get('return_semantics'))}</div>
  </div>
</section>
<section id="allocation"><h2>Target Allocation</h2>{_table(allocations)}</section>
<section id="growth"><h2>Portfolio Growth</h2>{_growth_svg(growth)}</section>
<section id="performance"><h2>Performance Summary</h2>{_performance_summary(performance)}<h3>Trailing Returns</h3>{_table(trailing)}</section>
<section id="annual"><h2>Annual Returns</h2>{_table(annual)}</section>
<section id="monthly"><h2>Monthly Returns</h2>{_table(monthly)}</section>
<section id="drawdowns"><h2>Drawdowns</h2>{_table(drawdowns)}</section>
<section id="rolling"><h2>Rolling Returns</h2><h3>3 Year</h3>{_table(rolling3)}<h3>5 Year</h3>{_table(rolling5)}</section>
<section id="correlations"><h2>Correlations</h2>{_table(correlations)}</section>
<section id="decomposition"><h2>Return Decomposition</h2>{_table(returns_decomp)}<h3>Risk Decomposition</h3>{_table(risk_decomp)}</section>
{active_section}
</main>
</body>
</html>
"""
    target = Path(output_path) if output_path is not None else root / "report.html"
    target.write_text(document, encoding="utf-8")
    return target
