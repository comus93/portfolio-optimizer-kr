from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

import pandas as pd

from . import backtest_renderer as br
from . import historical_components as hc
from . import pv_visual as pv


_MARKER = '<meta name="pv-round1-review" content="applied" />'


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.is_file() or path.stat().st_size == 0:
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _artifact(root: Path, name: str, *, raw_first: bool = False) -> pd.DataFrame:
    choices = (
        [root / "raw" / name, root / "review" / name]
        if raw_first
        else [root / "review" / name, root / "raw" / name]
    )
    for path in choices:
        frame = _read_csv(path)
        if not frame.empty:
            return frame
    return pd.DataFrame()


def _portfolio_order(result: dict[str, Any]) -> list[str]:
    explicit = [str(value) for value in result.get("portfolio_order", []) if str(value).strip()]
    if explicit:
        return explicit
    definitions = result.get("portfolio_definitions") or {}
    return list(definitions) if isinstance(definitions, dict) else []


def _benchmark_label(configuration: dict[str, Any]) -> str | None:
    benchmark = configuration.get("benchmark")
    if not isinstance(benchmark, dict):
        return None
    return str(benchmark.get("name") or benchmark.get("symbol") or "Benchmark")


def _asset_names(configuration: dict[str, Any]) -> dict[str, str]:
    return {
        str(asset.get("symbol")): str(asset.get("name") or "")
        for asset in configuration.get("assets", [])
        if isinstance(asset, dict) and asset.get("symbol") is not None
    }


def _currency(configuration: dict[str, Any]) -> str:
    currencies = {
        str(asset.get("currency") or "").upper()
        for asset in configuration.get("assets", [])
        if isinstance(asset, dict) and asset.get("currency")
    }
    benchmark = configuration.get("benchmark")
    if isinstance(benchmark, dict) and benchmark.get("currency"):
        currencies.add(str(benchmark.get("currency") or "").upper())
    return "KRW" if "KRW" in currencies else (next(iter(currencies)) if len(currencies) == 1 else "USD")


def _display_series(name: str, benchmark_label: str | None) -> str:
    return (benchmark_label or "Benchmark") if name == "benchmark" else name


def _performance_summary(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    currency: str,
) -> str:
    if frame.empty or "metric" not in frame:
        return '<p class="muted">N/A</p>'
    lookup = frame.set_index("metric")
    columns = [name for name in portfolio_order if name in frame.columns]
    if "benchmark" in frame.columns:
        columns.append("benchmark")
    specs = [
        ("Start Balance", "Start Balance", "money"),
        ("End Balance", "End Balance", "money"),
        ("Annualized Return (CAGR)", "CAGR", "pct"),
        ("Standard Deviation", "Standard Deviation", "pct"),
        ("Best Year", "Best Year", "pct"),
        ("Worst Year", "Worst Year", "pct"),
        ("Maximum Drawdown", "Maximum Drawdown", "pct"),
        ("Sharpe Ratio", "Sharpe Ratio (ex-post)", "ratio"),
        ("Sortino Ratio", "Sortino Ratio", "ratio"),
    ]
    headers = "".join(
        f"<th>{hc.esc(_display_series(name, benchmark_label))}</th>"
        for name in columns
    )
    rows: list[str] = []
    for label, source, unit in specs:
        if source not in lookup.index:
            continue
        source_row = lookup.loc[source]
        cells: list[str] = []
        for name in columns:
            value = source_row.get(name)
            if unit == "money":
                text = hc.money(value, currency)
            elif unit == "pct":
                text = hc.pct(value)
            else:
                text = f"{float(value):.2f}" if hc.finite(value) else "N/A"
            cells.append(f"<td>{hc.esc(text)}</td>")
        rows.append(
            f'<tr><td class="identity-cell">{hc.esc(label)}</td>{"".join(cells)}</tr>'
        )
    return (
        '<div class="table-wrap"><table id="performance-summary-pv">'
        f'<thead><tr><th>Metric</th>{headers}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _metric_text(value: Any, unit: str) -> str:
    if unit == "count":
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return "N/A"
        return str(value)
    if not hc.finite(value):
        return "N/A"
    number = float(value)
    if unit == "pct":
        return f"{number * 100.0:.2f}%"
    return f"{number:.2f}"


def _risk_metrics_table(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    if frame.empty or not {"metric", "unit"}.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    columns = [name for name in portfolio_order if name in frame.columns]
    if "benchmark" in frame.columns:
        columns.append("benchmark")
    headers = "".join(
        f"<th>{hc.esc(_display_series(name, benchmark_label))}</th>"
        for name in columns
    )
    rows: list[str] = []
    for _, row in frame.iterrows():
        unit = str(row.get("unit") or "ratio")
        cells = "".join(
            f"<td>{hc.esc(_metric_text(row.get(name), unit))}</td>"
            for name in columns
        )
        rows.append(
            f'<tr><td class="identity-cell">{hc.esc(row.get("metric", ""))}</td>{cells}</tr>'
        )
    return (
        '<p class="panel-subtitle">Portfolio return and risk metrics</p>'
        '<div class="table-wrap"><table id="risk-and-return-metrics">'
        f'<thead><tr><th>Metric</th>{headers}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
        f'<p class="muted">* {hc.esc(benchmark_label or "Benchmark")} is used as the benchmark for calculations. '
        'Value-at-risk metrics are monthly values.</p>'
    )


def _detail_structure(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    asset_names: dict[str, str],
) -> tuple[list[str], list[str]]:
    series = [
        name
        for name in portfolio_order
        if f"series::{name}::return" in frame.columns
    ]
    if "series::benchmark::return" in frame.columns:
        series.append("benchmark")
    tickers = [
        ticker
        for ticker in asset_names
        if f"asset::{ticker}::return" in frame.columns
    ]
    return series, tickers


def _detail_header(
    series: list[str],
    tickers: list[str],
    benchmark_label: str | None,
    asset_names: dict[str, str],
    *,
    monthly: bool,
) -> tuple[str, str]:
    top = [
        '<th rowspan="2">Year</th>',
        '<th rowspan="2">Month</th>' if monthly else '<th rowspan="2">Inflation</th>',
    ]
    second: list[str] = []
    for name in series:
        top.append(
            f'<th colspan="2">{hc.esc(_display_series(name, benchmark_label))}</th>'
        )
        second.extend(["<th>Return</th>", "<th>Balance</th>"])
    for ticker in tickers:
        name = asset_names.get(ticker, "").strip()
        label = f"{name} ({ticker})" if name else ticker
        top.append(f'<th rowspan="2">{hc.esc(label)}</th>')
    return "".join(top), "".join(second)


def _annual_detail_table(
    frame: pd.DataFrame,
    monthly_detail: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    asset_names: dict[str, str],
    currency: str,
) -> str:
    if frame.empty or "year" not in frame:
        return '<p class="muted">N/A</p>'
    series, tickers = _detail_structure(frame, portfolio_order, asset_names)
    top, second = _detail_header(
        series, tickers, benchmark_label, asset_names, monthly=False
    )
    rows: list[str] = []
    for _, row in frame.sort_values("year", ascending=False).iterrows():
        cells = [
            f'<td class="identity-cell">{int(row["year"])}</td>',
            f'<td>{hc.esc(hc.fraction_pct(row.get("inflation")))}</td>',
        ]
        for name in series:
            cells.extend(
                [
                    f'<td>{hc.esc(hc.fraction_pct(row.get(f"series::{name}::return")))}</td>',
                    f'<td>{hc.esc(hc.money(row.get(f"series::{name}::balance"), currency))}</td>',
                ]
            )
        for ticker in tickers:
            cells.append(
                f'<td>{hc.esc(hc.fraction_pct(row.get(f"asset::{ticker}::return")))}</td>'
            )
        rows.append(f'<tr>{"".join(cells)}</tr>')
    note = ""
    if not monthly_detail.empty and "date" in monthly_detail:
        dates = pd.to_datetime(monthly_detail["date"], errors="coerce").dropna()
        if not dates.empty:
            last = dates.max()
            if last.month < 12:
                note = (
                    f'<p class="muted">Annual return for {last.year} is from '
                    f'01/01/{last.year} to {last.strftime("%m/%d/%Y")}</p>'
                )
    return (
        '<p class="panel-subtitle">Annual returns for the configured portfolios</p>'
        '<div class="table-wrap"><table id="annual-returns-detail" class="pv-grouped-table wide-detail-table">'
        f'<thead><tr>{top}</tr><tr>{second}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>{note}'
    )


def _monthly_detail_table(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    asset_names: dict[str, str],
    currency: str,
) -> str:
    if frame.empty or not {"year", "month"}.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    series, tickers = _detail_structure(frame, portfolio_order, asset_names)
    top, second = _detail_header(
        series, tickers, benchmark_label, asset_names, monthly=True
    )
    rows: list[str] = []
    rendered = frame.sort_values(["year", "month"], ascending=[False, False])
    for _, row in rendered.iterrows():
        cells = [
            f'<td class="identity-cell">{int(row["year"])}</td>',
            f'<td>{int(row["month"])}</td>',
        ]
        for name in series:
            cells.extend(
                [
                    f'<td>{hc.esc(hc.fraction_pct(row.get(f"series::{name}::return")))}</td>',
                    f'<td>{hc.esc(hc.money(row.get(f"series::{name}::balance"), currency))}</td>',
                ]
            )
        for ticker in tickers:
            cells.append(
                f'<td>{hc.esc(hc.fraction_pct(row.get(f"asset::{ticker}::return")))}</td>'
            )
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return (
        '<p class="panel-subtitle">Monthly returns for the configured portfolios</p>'
        '<div class="table-wrap"><table id="monthly-returns-detail" class="pv-grouped-table wide-detail-table">'
        f'<thead><tr>{top}</tr><tr>{second}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _combined_drawdowns(
    series_frame: pd.DataFrame,
    episodes_frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    if series_frame.empty:
        return '<p class="muted">N/A</p>'
    series: list[tuple[str, str]] = []
    targets: list[tuple[str, str]] = []
    for name in portfolio_order:
        column = f"{name}_drawdown_pct"
        if column in series_frame:
            series.append((column, name))
            targets.append((name, name))
    if "benchmark_drawdown_pct" in series_frame:
        series.append(("benchmark_drawdown_pct", benchmark_label or "Benchmark"))
        targets.append(("benchmark", benchmark_label or "Benchmark"))
    chart = pv.time_line_chart(
        series_frame,
        series,
        chart_id="drawdown-combined",
        y_title="Drawdown %",
        value_scale=1.0,
    )
    tables: list[str] = []
    for key, label in targets:
        part = (
            episodes_frame[episodes_frame["portfolio"].astype(str) == key].copy()
            if not episodes_frame.empty and "portfolio" in episodes_frame
            else pd.DataFrame()
        )
        tables.append(
            f'<div class="analysis-panel drawdown-episodes-panel" data-portfolio="{hc.esc(key)}">'
            f'<h3>Drawdowns for {hc.esc(label)}</h3>{pv._drawdown_episode_table(part)}</div>'
        )
    return chart + "".join(tables)


def _assets_section(
    root: Path,
    result: dict[str, Any],
    portfolio_order: list[str],
    benchmark_label: str | None,
    asset_names: dict[str, str],
    currency: str,
) -> str:
    asset_performance = _artifact(root, "portfolio_asset_performance.csv")
    annual_assets = _artifact(root, "annual_asset_returns.csv", raw_first=True)
    correlations = _artifact(root, "correlations.csv", raw_first=True)
    returns_decomp = _artifact(root, "return_decomposition.csv")
    risk_decomp = _artifact(root, "risk_decomposition.csv")
    coverage = (result.get("data_coverage", {}) or {}).get("backtest_monthly_returns", {}) or {}
    annual_chart = pv.annual_asset_returns_chart(annual_assets, asset_names).replace(
        'class="analysis-chart grouped-bar-chart"',
        'class="analysis-chart grouped-bar-chart" style="min-width:0;width:100%"',
    )
    return (
        '<section id="assets" class="result-section"><h2>Assets</h2>'
        f'<h3>Portfolio Assets</h3>{br._portfolio_assets_table(asset_performance)}'
        f'<h3>Portfolio Asset Performance</h3>{br._portfolio_asset_trailing_table(asset_performance)}{br._as_of_note(coverage, "Trailing returns")}'
        f'<h3>Monthly Correlations</h3>{br._correlations_table(correlations, benchmark_label, asset_names, portfolio_order)}'
        f'<h3>Portfolio Return Decomposition</h3>{pv.return_decomposition_table(returns_decomp, portfolio_order, asset_names, currency)}'
        f'<h3>Portfolio Risk Decomposition</h3>{pv.risk_decomposition_table(risk_decomp, portfolio_order, asset_names)}'
        f'<h3>Annual Asset Returns</h3><div class="asset-annual-responsive">{annual_chart}</div></section>'
    )


def _replace_section(html: str, section_id: str, replacement: str) -> str:
    pattern = re.compile(
        rf'<section id="{re.escape(section_id)}"\s+class="result-section[^>]*>.*?</section>',
        re.S,
    )
    return pattern.sub(replacement, html, count=1)


def _move_chart_legend_after(html: str, chart_id: str) -> str:
    pattern = re.compile(
        rf'(<div class="legend">.*?</div>)(<div class="chart-wrap[^>]*data-chart="{re.escape(chart_id)}"[^>]*>.*?</svg></div>)',
        re.S,
    )
    return pattern.sub(r'\2\1', html)


def _fix_tooltip_positioning(html: str) -> str:
    old = '''tooltip.style.left = `${Math.max(6, clientX - hostRect.left + host.scrollLeft + 12)}px`;
    tooltip.style.top = `${Math.max(6, clientY - hostRect.top + host.scrollTop - 44)}px`;'''
    new = '''const tipWidth = tooltip.offsetWidth || 180; const tipHeight = tooltip.offsetHeight || 80;
    const pointerX = clientX - hostRect.left + host.scrollLeft;
    const pointerY = clientY - hostRect.top + host.scrollTop;
    const visibleLeft = host.scrollLeft + 6; const visibleRight = host.scrollLeft + host.clientWidth - 6;
    let left = pointerX + 12;
    if (left + tipWidth > visibleRight) left = pointerX - tipWidth - 12;
    left = Math.max(visibleLeft, Math.min(left, Math.max(visibleLeft, visibleRight - tipWidth)));
    let top = pointerY - 44;
    const visibleTop = host.scrollTop + 6; const visibleBottom = host.scrollTop + host.clientHeight - 6;
    if (top + tipHeight > visibleBottom) top = pointerY - tipHeight - 12;
    top = Math.max(visibleTop, top);
    tooltip.style.left = `${left}px`;
    tooltip.style.top = `${top}px`;'''
    return html.replace(old, new)


def _active_fixes(html: str, benchmark_label: str | None) -> str:
    match = re.search(
        r'<section id="activeReturns"\s+class="result-section[^>]*>.*?</section>',
        html,
        flags=re.S,
    )
    if not match:
        return html
    section = match.group(0)
    section = re.sub(
        r'<h3>Benchmark Summary</h3>.*?(?=<h3>Annualized Active Return</h3>)',
        '',
        section,
        flags=re.S,
    )
    section = section.replace(
        '<h3>Cumulative Active Return</h3>',
        '<h3>Active Return Contribution</h3>',
    )
    if benchmark_label:
        section = section.replace(
            ' vs Benchmark</p>',
            f' vs. {hc.esc(benchmark_label)}</p>',
        )
    return html[: match.start()] + section + html[match.end() :]


def apply_backtest_round1_overlay(
    run_dir: str | Path,
    output_path: str | Path,
) -> Path:
    root = Path(run_dir)
    target = Path(output_path)
    result_path = root / "result.json"
    if not result_path.is_file() or not target.is_file():
        return target
    result = json.loads(result_path.read_text(encoding="utf-8"))
    configuration = result.get("configuration") or {}
    if not isinstance(configuration, dict) or configuration.get("product_mode") != "backtest":
        return target
    html = target.read_text(encoding="utf-8")
    if _MARKER in html:
        return target

    portfolio_order = _portfolio_order(result)
    benchmark_label = _benchmark_label(configuration)
    asset_names = _asset_names(configuration)
    currency = _currency(configuration)

    performance = _artifact(root, "performance_summary.csv")
    performance_html = _performance_summary(
        performance, portfolio_order, benchmark_label, currency
    )
    html = re.sub(
        r'<div id="performance" class="summary-block">.*?(?=<div id="growth" class="summary-block">)',
        f'<div id="performance" class="summary-block"><h3>Performance Summary</h3>{performance_html}</div>\n',
        html,
        count=1,
        flags=re.S,
    )

    metrics = _artifact(root, "risk_and_return_metrics.csv", raw_first=True)
    html = _replace_section(
        html,
        "metrics",
        '<section id="metrics" class="result-section"><h2>Risk and Return Metrics</h2>'
        f'{_risk_metrics_table(metrics, portfolio_order, benchmark_label)}</section>',
    )
    html = html.replace(
        'href="#metrics">Metrics</a>',
        'href="#metrics">Risk and Return Metrics</a>',
    )

    annual = _artifact(root, "annual_returns.csv")
    annual_detail = _artifact(root, "annual_returns_detail.csv", raw_first=True)
    monthly_detail = _artifact(root, "monthly_returns_detail.csv", raw_first=True)
    html = _replace_section(
        html,
        "annualReturns",
        '<section id="annualReturns" class="result-section"><h2>Annual Returns</h2>'
        f'{pv.annual_returns_chart(annual, portfolio_order, benchmark_label)}'
        f'{_annual_detail_table(annual_detail, monthly_detail, portfolio_order, benchmark_label, asset_names, currency)}'
        '</section>',
    )
    html = _replace_section(
        html,
        "monthlyReturns",
        '<section id="monthlyReturns" class="result-section"><h2>Monthly Returns</h2>'
        f'{_monthly_detail_table(monthly_detail, portfolio_order, benchmark_label, asset_names, currency)}'
        '</section>',
    )

    html = _replace_section(
        html,
        "drawdowns",
        '<section id="drawdowns" class="result-section"><h2>Drawdowns</h2>'
        f'{_combined_drawdowns(_artifact(root, "drawdown_series.csv"), _artifact(root, "drawdowns.csv"), portfolio_order, benchmark_label)}'
        '</section>',
    )
    html = _replace_section(
        html,
        "assets",
        _assets_section(
            root,
            result,
            portfolio_order,
            benchmark_label,
            asset_names,
            currency,
        ),
    )
    html = _active_fixes(html, benchmark_label)
    html = _move_chart_legend_after(html, "annual-returns-chart")
    html = _move_chart_legend_after(html, "drawdown-combined")
    html = _fix_tooltip_positioning(html)
    html = html.replace(
        "</head>",
        _MARKER + "\n<style>.wide-detail-table{min-width:1850px}.asset-annual-responsive .chart-wrap{overflow-x:hidden}#risk-and-return-metrics td:first-child{white-space:nowrap}</style>\n</head>",
        1,
    )
    target.write_text(html, encoding="utf-8")
    return target
