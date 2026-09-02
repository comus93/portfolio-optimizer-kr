from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


_DEF_WIDTH = 1060
_DEF_HEIGHT = 420
_PALETTE = ["#1200FF", "#50E2B0", "#85ACD0", "#2D7186", "#A45EE5", "#E59F3A", "#D45050", "#6F8F3D"]

_METRIC_LABELS = {
    "beta": "Beta",
    "alpha": "Alpha",
    "r_squared": "R-squared",
    "treynor_ratio": "Treynor Ratio",
    "calmar_ratio": "Calmar Ratio",
    "modigliani_modigliani": "Modigliani-Modigliani",
    "skewness": "Skewness",
    "excess_kurtosis": "Excess Kurtosis",
    "historical_var_95": "Historical VaR 95",
}
_METRIC_PERCENT_FRACTION = {"alpha", "modigliani_modigliani", "historical_var_95"}

_TRAILING_COLUMNS = [
    ("portfolio", "Portfolio"),
    ("3m_pct", "3 Month"),
    ("ytd_pct", "YTD"),
    ("1y_pct", "1 Year"),
    ("3y_pct", "3 Year Annualized Return"),
    ("5y_pct", "5 Year Annualized Return"),
    ("10y_pct", "10 Year Annualized Return"),
    ("full_period_pct", "Full Period CAGR"),
    ("3y_annualized_volatility_pct", "3 Year Annualized Standard Deviation"),
    ("5y_annualized_volatility_pct", "5 Year Annualized Standard Deviation"),
]

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


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _pct(value: Any) -> str:
    return f"{float(value):,.2f}%" if _finite(value) else "N/A"


def _fraction_pct(value: Any) -> str:
    return f"{float(value) * 100:,.2f}%" if _finite(value) else "N/A"


def _currency_label(currency: str) -> str:
    code = str(currency or "USD").upper()
    return {"USD": "$", "KRW": "₩"}.get(code, code)


def _money(value: Any, currency: str = "USD") -> str:
    if not _finite(value):
        return "N/A"
    code = str(currency or "USD").upper()
    symbol = {"USD": "$", "KRW": "₩"}.get(code)
    return f"{symbol}{float(value):,.0f}" if symbol else f"{code} {float(value):,.0f}"


def _ratio(value: Any) -> str:
    return f"{float(value):,.3f}" if _finite(value) else "N/A"


def _correlation(value: Any) -> str:
    return f"{float(value):,.2f}" if _finite(value) else "N/A"


def _display_option(value: Any) -> str:
    text = str(value or "")
    return _OPTION_LABELS.get(text, _human_column(text))


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


def _table(
    frame: pd.DataFrame,
    *,
    table_id: str | None = None,
    table_class: str = "",
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    identifier = f' id="{_esc(table_id)}"' if table_id else ""
    cls = f' class="{_esc(table_class)}"' if table_class else ""
    headers = "".join(f"<th>{_esc(column)}</th>" for column in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = "".join(
            f"<td>{_esc('N/A' if pd.isna(value) else value)}</td>" for value in row
        )
        rows.append(f"<tr>{cells}</tr>")
    return (
        f'<div class="table-wrap"><table{identifier}{cls}><thead><tr>{headers}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


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


def _display_portfolio(value: Any, benchmark_label: str | None) -> str:
    text = str(value)
    return (benchmark_label or "Benchmark") if text == "benchmark" else text


def _human_column(column: str, benchmark_label: str | None = None) -> str:
    labels = {
        "benchmark": benchmark_label or "Benchmark",
        "date": "Date",
        "year": "Year",
        "portfolio": "Portfolio",
        "ticker": "Ticker",
        "rank": "Rank",
        "start": "Start",
        "bottom": "Bottom",
        "recovery": "Recovery",
        "duration_months": "Duration (Months)",
    }
    if column in labels:
        return labels[column]
    label = column[:-4] if column.endswith("_pct") else column
    return " ".join(
        word.capitalize() for word in label.replace("_", " ").strip().split()
    )


def _friendly_table(
    frame: pd.DataFrame,
    *,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
    fraction_columns: set[str] | None = None,
    money_columns: set[str] | None = None,
    ratio_columns: set[str] | None = None,
    column_labels: dict[str, str] | None = None,
    currency: str = "USD",
    table_id: str | None = None,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    fraction_columns = fraction_columns or set()
    money_columns = money_columns or set()
    ratio_columns = ratio_columns or set()
    column_labels = column_labels or {}
    if "portfolio" in rendered.columns:
        order = portfolio_order or []
        ranking = {name: index for index, name in enumerate(order)}
        benchmark_rank = len(order)
        rendered["_order"] = rendered["portfolio"].map(
            lambda value: benchmark_rank
            if str(value) == "benchmark"
            else ranking.get(str(value), benchmark_rank + 1)
        )
        sort_columns = ["_order"] + (
            ["date"] if "date" in rendered.columns else []
        )
        rendered = rendered.sort_values(sort_columns).drop(columns=["_order"])
        rendered["portfolio"] = rendered["portfolio"].map(
            lambda value: _display_portfolio(value, benchmark_label)
        )
    if "series" in rendered.columns:
        rendered["series"] = rendered["series"].map(
            lambda value: _display_portfolio(value, benchmark_label)
        )
    for column in rendered.columns:
        if column in fraction_columns:
            rendered[column] = rendered[column].map(_fraction_pct)
        elif column in money_columns:
            rendered[column] = rendered[column].map(
                lambda value: _money(value, currency)
            )
        elif column in ratio_columns:
            rendered[column] = rendered[column].map(_correlation)
        elif column.endswith("_pct"):
            rendered[column] = rendered[column].map(_pct)
        elif column == "date":
            rendered[column] = pd.to_datetime(
                rendered[column], errors="coerce"
            ).map(
                lambda value: value.date().isoformat()
                if not pd.isna(value)
                else "N/A"
            )
    rendered = rendered.rename(
        columns={
            column: column_labels.get(
                column, _human_column(column, benchmark_label)
            )
            for column in rendered.columns
        }
    )
    return _table(rendered, table_id=table_id)


def _annual_asset_returns_table(frame: pd.DataFrame) -> str:
    return _friendly_table(
        frame,
        fraction_columns={"return"},
        table_id="annual-asset-returns-table",
    )


def _correlations_table(
    frame: pd.DataFrame,
    benchmark_label: str | None,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    if "series" in rendered:
        rendered["series"] = rendered["series"].map(
            lambda value: _display_portfolio(value, benchmark_label)
        )
    headers = []
    for column in rendered.columns:
        label = (
            benchmark_label or "Benchmark"
            if column == "benchmark"
            else column
        )
        headers.append(f"<th>{_esc(label)}</th>")
    rows: list[str] = []
    for _, row in rendered.iterrows():
        cells: list[str] = []
        for column in rendered.columns:
            value = row[column]
            if column == "series":
                cells.append(f'<td class="identity-cell">{_esc(value)}</td>')
            else:
                text = _correlation(value)
                if _finite(value):
                    strength = min(abs(float(value)), 1.0)
                    tone = "49,109,181" if float(value) >= 0 else "196,74,74"
                    cells.append(
                        f'<td class="heatmap-cell" '
                        f'data-correlation="{float(value):.8f}" '
                        f'style="background:rgba({tone},{0.08 + strength * 0.30:.3f})">'
                        f'{_esc(text)}</td>'
                    )
                else:
                    cells.append(
                        f'<td class="heatmap-cell">{_esc(text)}</td>'
                    )
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        '<div class="table-wrap"><table id="correlations-heatmap" '
        f'class="heatmap"><thead><tr>{"".join(headers)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div>'
    )


def _decomposition_table(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None,
    *,
    currency: str,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    if "asset" in rendered.columns:
        rendered["asset"] = rendered["asset"].map(
            lambda value: str(value).removeprefix("contribution_")
        )
    value_columns = [column for column in rendered.columns if column != "asset"]
    requested = portfolio_order or []
    suffixes = ("_contribution_balance", "_risk_contribution_pct")

    def identity(column: str) -> str:
        for suffix in suffixes:
            if column.endswith(suffix):
                return column[: -len(suffix)]
        return column

    ranking = {name: index for index, name in enumerate(requested)}
    value_columns.sort(
        key=lambda column: ranking.get(identity(column), len(ranking))
    )
    rendered = rendered[
        [column for column in ["asset", *value_columns] if column in rendered]
    ]
    labels = {column: identity(column) for column in value_columns}
    money_columns = {
        column for column in value_columns if column.endswith("_balance")
    }
    return _friendly_table(
        rendered,
        portfolio_order=portfolio_order,
        money_columns=money_columns,
        column_labels=labels,
        currency=currency,
    )


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


def _nice_step(span: float, target_ticks: int = 6) -> float:
    if not math.isfinite(span) or span <= 0:
        return 1.0
    rough = span / max(target_ticks, 1)
    exponent = math.floor(math.log10(rough))
    fraction = rough / (10**exponent)
    if fraction <= 1:
        nice = 1.0
    elif fraction <= 2:
        nice = 2.0
    elif fraction <= 2.5:
        nice = 2.5
    elif fraction <= 5:
        nice = 5.0
    else:
        nice = 10.0
    return nice * (10**exponent)


def _calendar_ticks(dates: pd.Series) -> list[pd.Timestamp]:
    normalized = [pd.Timestamp(value) for value in dates if not pd.isna(value)]
    if not normalized:
        return []
    start, end = normalized[0], normalized[-1]
    months = max(1, (end.year - start.year) * 12 + end.month - start.month)
    if months <= 120:
        anchor_months, year_step = {1, 7}, 1
    elif months <= 240:
        anchor_months, year_step = {1}, 1
    elif months <= 480:
        anchor_months, year_step = {1}, 2
    else:
        anchor_months, year_step = {1}, 5
    base_year = start.year
    selected: list[pd.Timestamp] = []
    seen: set[tuple[int, int]] = set()
    for value in normalized:
        key = (value.year, value.month)
        if key in seen:
            continue
        if (
            value.month in anchor_months
            and (value.year - base_year) % year_step == 0
        ):
            selected.append(value)
            seen.add(key)
    if len(selected) < 2:
        selected = []
        seen.clear()
        for value in (normalized[0], normalized[-1]):
            key = (value.year, value.month)
            if key not in seen:
                selected.append(value)
                seen.add(key)
    return selected


def _chart_shell(
    chart_id: str,
    svg: str,
    legend: str = "",
    note: str = "",
) -> str:
    note_html = f'<p class="muted">{_esc(note)}</p>' if note else ""
    return (
        f'{legend}<div class="chart-wrap analysis-chart-wrap" '
        f'data-chart="{_esc(chart_id)}">'
        '<div class="chart-tooltip generic-tooltip" role="status" '
        f'aria-live="polite"></div>{svg}</div>{note_html}'
    )


def _legend(items: Iterable[tuple[str, str]]) -> str:
    spans = [
        f'<span class="legend-item"><i style="background:{color}"></i>'
        f'{_esc(label)}</span>'
        for label, color in items
    ]
    return f'<div class="legend">{"".join(spans)}</div>'


def _grouped_bar_chart(
    categories: list[str],
    series: list[tuple[str, list[float | None]]],
    *,
    chart_id: str,
    y_title: str,
    tooltip_rows: list[str] | None = None,
    x_title: str = "Year",
) -> str:
    if not categories or not series:
        return '<p class="muted">N/A</p>'
    values = [
        float(value)
        for _, series_values in series
        for value in series_values
        if _finite(value)
    ]
    if not values:
        return '<p class="muted">N/A</p>'
    min_value = min(min(values), 0.0)
    max_value = max(max(values), 0.0)
    if math.isclose(min_value, max_value):
        max_value = min_value + 1.0
    span = max_value - min_value
    padding = max(span * 0.08, 1.0)
    y_min, y_max = min_value - padding, max_value + padding
    margin_left, margin_right, margin_top, margin_bottom = 78, 24, 24, 72
    width, height = _DEF_WIDTH, _DEF_HEIGHT
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    denominator = y_max - y_min

    def y_for(value: float) -> float:
        return margin_top + plot_height * (y_max - value) / denominator

    zero_y = y_for(0.0)
    step = _nice_step(denominator, 6)
    tick = math.ceil(y_min / step) * step
    grid: list[str] = []
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" '
            'class="grid-line" />'
        )
        grid.append(
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" '
            f'text-anchor="end" class="axis-label y-tick-label">'
            f'{_esc(_pct(tick))}</text>'
        )
        tick += step

    group_width = plot_width / max(len(categories), 1)
    inner_width = group_width * 0.76
    bar_width = inner_width / max(len(series), 1)
    marks: list[str] = []
    labels: list[str] = []
    for category_index, category in enumerate(categories):
        center = margin_left + group_width * (category_index + 0.5)
        if (
            len(categories) <= 16
            or category_index % max(1, len(categories) // 10) == 0
            or category_index == len(categories) - 1
        ):
            labels.append(
                f'<text x="{center:.2f}" y="{margin_top + plot_height + 24}" '
                f'text-anchor="middle" class="axis-label x-tick-label">'
                f'{_esc(category)}</text>'
            )
        tooltip = (
            tooltip_rows[category_index]
            if tooltip_rows and category_index < len(tooltip_rows)
            else category
        )
        for series_index, (name, series_values) in enumerate(series):
            if (
                category_index >= len(series_values)
                or not _finite(series_values[category_index])
            ):
                continue
            value = float(series_values[category_index])
            x = (
                center
                - inner_width / 2
                + series_index * bar_width
                + bar_width * 0.08
            )
            rendered_width = bar_width * 0.84
            y_value = y_for(value)
            y = min(zero_y, y_value)
            rendered_height = max(abs(zero_y - y_value), 1.0)
            marks.append(
                f'<rect x="{x:.2f}" y="{y:.2f}" '
                f'width="{rendered_width:.2f}" height="{rendered_height:.2f}" '
                f'fill="{_PALETTE[series_index % len(_PALETTE)]}" '
                'class="chart-mark grouped-bar" tabindex="0" '
                f'data-category="{_esc(category)}" data-series="{_esc(name)}" '
                f'data-value="{value:.10f}" data-tooltip="{_esc(tooltip)}" '
                f'aria-label="{_esc(category + " | " + name + ": " + _pct(value))}" />'
            )
    legend = _legend(
        (name, _PALETTE[index % len(_PALETTE)])
        for index, (name, _) in enumerate(series)
    )
    svg = f'''<svg class="analysis-chart grouped-bar-chart" viewBox="0 0 {width} {height}" role="img" aria-label="{_esc(chart_id)}">
      {''.join(grid)}
      <line x1="{margin_left}" y1="{zero_y:.2f}" x2="{margin_left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(marks)}{''.join(labels)}
      <text x="{margin_left + plot_width / 2:.2f}" y="{height - 14}" text-anchor="middle" class="axis-title">{_esc(x_title)}</text>
      <text x="20" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {margin_top + plot_height / 2:.2f})">{_esc(y_title)}</text>
    </svg>'''
    return _chart_shell(chart_id, svg, legend)


def _time_line_chart(
    frame: pd.DataFrame,
    series: list[tuple[str, str]],
    *,
    chart_id: str,
    y_title: str,
    value_scale: float = 1.0,
    note: str = "",
) -> str:
    if frame.empty or "date" not in frame.columns:
        return '<p class="muted">N/A</p>'
    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    existing = [(column, label) for column, label in series if column in shaped]
    if shaped.empty or not existing:
        return '<p class="muted">N/A</p>'
    values: list[float] = []
    for column, _ in existing:
        values.extend(
            [
                float(value) * value_scale
                for value in pd.to_numeric(
                    shaped[column], errors="coerce"
                ).dropna()
            ]
        )
    if not values:
        return '<p class="muted">N/A</p>'
    y_min, y_max = min(values), max(values)
    if y_title.endswith("%"):
        y_min = min(0.0, y_min)
        y_max = max(0.0, y_max)
    if math.isclose(y_min, y_max):
        y_min -= 1.0
        y_max += 1.0
    padding = max((y_max - y_min) * 0.08, 0.5)
    y_min, y_max = y_min - padding, y_max + padding
    margin_left, margin_right, margin_top, margin_bottom = 78, 24, 24, 70
    width, height = _DEF_WIDTH, _DEF_HEIGHT
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    denominator = y_max - y_min
    date_min, date_max = shaped["date"].iloc[0], shaped["date"].iloc[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return (
            margin_left
            + plot_width * (date - date_min).total_seconds() / date_span
        )

    def y_for(value: float) -> float:
        return margin_top + plot_height * (y_max - value) / denominator

    step = _nice_step(denominator, 6)
    tick = math.ceil(y_min / step) * step
    grid: list[str] = []
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" '
            'class="grid-line" />'
        )
        grid.append(
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" '
            f'text-anchor="end" class="axis-label y-tick-label">'
            f'{_esc(_pct(tick))}</text>'
        )
        tick += step
    x_ticks: list[str] = []
    for date in _calendar_ticks(shaped["date"]):
        x = x_for(date)
        x_ticks.append(
            f'<text x="{x:.2f}" y="{margin_top + plot_height + 24}" '
            f'text-anchor="middle" class="axis-label x-tick-label">'
            f'{_esc(date.strftime("%b %Y"))}</text>'
        )

    paths: list[str] = []
    points: list[str] = []
    for series_index, (column, label) in enumerate(existing):
        color = _PALETTE[series_index % len(_PALETTE)]
        coordinates: list[tuple[float, float]] = []
        for _, row in shaped.iterrows():
            if not _finite(row[column]):
                continue
            date = pd.Timestamp(row["date"])
            value = float(row[column]) * value_scale
            x, y = x_for(date), y_for(value)
            coordinates.append((x, y))
            tooltip_parts = [date.strftime("%Y-%m-%d")]
            for peer_column, peer_label in existing:
                peer = row.get(peer_column)
                if _finite(peer):
                    tooltip_parts.append(
                        f"{peer_label}: {_pct(float(peer) * value_scale)}"
                    )
            tooltip = " | ".join(tooltip_parts)
            points.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" '
                f'fill="{color}" class="chart-mark line-point" tabindex="0" '
                f'data-date="{date.date()}" data-series="{_esc(label)}" '
                f'data-value="{value:.10f}" data-tooltip="{_esc(tooltip)}" '
                f'aria-label="{_esc(date.strftime("%Y-%m-%d") + " | " + label + ": " + _pct(value))}" />'
            )
        if coordinates:
            paths.append(
                f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in coordinates)}" '
                f'fill="none" stroke="{color}" stroke-width="2.2" '
                f'class="line-series" data-series="{_esc(label)}" />'
            )
    legend = _legend(
        (label, _PALETTE[index % len(_PALETTE)])
        for index, (_, label) in enumerate(existing)
    )
    svg = f'''<svg class="analysis-chart line-chart" viewBox="0 0 {width} {height}" role="img" aria-label="{_esc(chart_id)}">
      {''.join(grid)}
      <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" class="axis" />
      {''.join(x_ticks)}{''.join(paths)}{''.join(points)}
      <text x="{margin_left + plot_width / 2:.2f}" y="{height - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {margin_top + plot_height / 2:.2f})">{_esc(y_title)}</text>
    </svg>'''
    return _chart_shell(chart_id, svg, legend, note)


def _growth_svg(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    series_labels: dict[str, str] | None = None,
    currency: str = "USD",
) -> str:
    if frame.empty or "date" not in frame:
        return '<p class="muted">N/A</p>'
    series_labels = series_labels or {}
    all_series = [
        column for column in frame.columns if column.endswith("_balance")
    ]
    if not all_series:
        return '<p class="muted">N/A</p>'
    keys = [column[: -len("_balance")] for column in all_series]
    requested = portfolio_order or []
    ordered_keys = [name for name in requested if name in keys]
    if "benchmark" in keys:
        ordered_keys.append("benchmark")
    ordered_keys.extend(key for key in keys if key not in ordered_keys)
    series_columns = [f"{key}_balance" for key in ordered_keys]
    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    if shaped.empty:
        return '<p class="muted">N/A</p>'
    values = pd.to_numeric(
        shaped[series_columns].stack(), errors="coerce"
    ).dropna()
    if values.empty:
        return '<p class="muted">N/A</p>'
    data_min, data_max = float(values.min()), float(values.max())
    if math.isclose(data_min, data_max):
        padding = max(abs(data_max) * 0.05, 1.0)
        data_min, data_max = data_min - padding, data_max + padding
    step = _nice_step(data_max - data_min, 6)
    y_min = math.floor(data_min / step) * step
    y_max = math.ceil(data_max / step) * step
    if math.isclose(y_min, y_max):
        y_max = y_min + step
    margin_left, margin_right, margin_top, margin_bottom = 88, 24, 20, 74
    plot_width = _DEF_WIDTH - margin_left - margin_right
    plot_height = _DEF_HEIGHT - margin_top - margin_bottom
    denominator = max(y_max - y_min, 1e-12)
    date_min = pd.Timestamp(shaped["date"].iloc[0])
    date_max = pd.Timestamp(shaped["date"].iloc[-1])
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return (
            margin_left
            + plot_width
            * (pd.Timestamp(date) - date_min).total_seconds()
            / date_span
        )

    grid: list[str] = []
    y_labels: list[str] = []
    tick = y_min
    while tick <= y_max + step * 0.25 and len(y_labels) < 12:
        y = margin_top + plot_height * (y_max - tick) / denominator
        grid.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" '
            'class="grid-line" />'
        )
        y_labels.append(
            f'<text x="{margin_left - 12}" y="{y + 4:.2f}" '
            f'text-anchor="end" class="axis-label y-tick-label">'
            f'{_esc(_money(tick, currency))}</text>'
        )
        tick += step
    x_ticks: list[str] = []
    for date in _calendar_ticks(shaped["date"]):
        x = x_for(date)
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{margin_top + plot_height}" '
            f'x2="{x:.2f}" y2="{margin_top + plot_height + 8}" '
            'class="axis" />'
            f'<text x="{x:.2f}" y="{margin_top + plot_height + 26}" '
            f'text-anchor="middle" class="axis-label x-tick-label">'
            f'{_esc(date.strftime("%b %Y"))}</text>'
        )
    paths: list[str] = []
    points: list[str] = []
    legend_items: list[tuple[str, str]] = []
    for index, column in enumerate(series_columns):
        key = column[: -len("_balance")]
        label = series_labels.get(key, key)
        color = _PALETTE[index % len(_PALETTE)]
        coordinates: list[tuple[float, float]] = []
        for _, row in shaped.iterrows():
            if not _finite(row[column]):
                continue
            date = pd.Timestamp(row["date"])
            raw_value = float(row[column])
            x = x_for(date)
            y = margin_top + plot_height * (y_max - raw_value) / denominator
            coordinates.append((x, y))
            title = f"{date.date()} | {label}: {_money(raw_value, currency)}"
            points.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" '
                f'fill="{color}" class="growth-point chart-mark" tabindex="0" '
                f'aria-label="{_esc(title)}" data-date="{date.date()}" '
                f'data-series="{_esc(label)}" data-balance="{raw_value:.10f}" '
                f'data-tooltip="{_esc(title)}" />'
            )
        if coordinates:
            paths.append(
                f'<polyline fill="none" stroke="{color}" stroke-width="2.2" '
                f'points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in coordinates)}" '
                f'class="growth-series" data-series="{_esc(label)}" />'
            )
        legend_items.append((label, color))
    legend = _legend(legend_items)
    svg = f'''<svg class="growth-chart analysis-chart" viewBox="0 0 {_DEF_WIDTH} {_DEF_HEIGHT}" role="img" aria-label="Portfolio balance growth over time">
      {''.join(grid)}
      <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" class="axis" />
      <line x1="{margin_left}" y1="{margin_top + plot_height}" x2="{margin_left + plot_width}" y2="{margin_top + plot_height}" class="axis" />
      {''.join(y_labels)}{''.join(x_ticks)}
      <text x="{margin_left + plot_width / 2:.2f}" y="{_DEF_HEIGHT - 14}" text-anchor="middle" class="axis-title">Year</text>
      <text x="22" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 22 {margin_top + plot_height / 2:.2f})">Portfolio Balance ({_esc(_currency_label(currency))})</text>
      {''.join(paths)}{''.join(points)}
    </svg>'''
    return _chart_shell(
        "portfolio-growth",
        svg,
        legend,
        "Hover 또는 keyboard focus로 날짜, portfolio identity, balance를 확인할 수 있다.",
    ).replace(
        '<div class="chart-tooltip generic-tooltip"',
        '<div id="growth-tooltip" class="chart-tooltip generic-tooltip"',
        1,
    )


def _performance_summary(
    frame: pd.DataFrame,
    benchmark: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
    currency: str = "USD",
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    unit = rendered.get("unit", pd.Series(index=rendered.index, dtype=object))
    requested = portfolio_order or []
    value_columns = [name for name in requested if name in rendered.columns]
    if "benchmark" in rendered.columns:
        value_columns.append("benchmark")
    value_columns.extend(
        column
        for column in rendered.columns
        if column not in {"metric", "unit"} and column not in value_columns
    )
    for column in value_columns:
        formatted = []
        for index, value in rendered[column].items():
            kind = unit.loc[index] if index in unit.index else None
            if kind == "pct":
                formatted.append(_pct(value))
            elif kind == "balance":
                formatted.append(_money(value, currency))
            else:
                formatted.append(_ratio(value))
        rendered[column] = formatted
    if not benchmark.empty and "portfolio" in benchmark.columns:
        extra_rows: list[dict[str, Any]] = []
        lookup = benchmark.set_index("portfolio")
        for label, key, unit_name in (
            ("Active Return", "active_return_pct", "pct"),
            ("Tracking Error", "tracking_error_pct", "pct"),
            ("Information Ratio", "information_ratio", "ratio"),
        ):
            row: dict[str, Any] = {"metric": label}
            for column in value_columns:
                if (
                    column == "benchmark"
                    or column not in lookup.index
                    or key not in lookup.columns
                ):
                    row[column] = "N/A"
                else:
                    raw_value = lookup.loc[column, key]
                    row[column] = (
                        _pct(raw_value)
                        if unit_name == "pct"
                        else _ratio(raw_value)
                    )
            extra_rows.append(row)
        rendered = pd.concat(
            [
                rendered.drop(columns=["unit"], errors="ignore"),
                pd.DataFrame(extra_rows),
            ],
            ignore_index=True,
        )
    else:
        rendered = rendered.drop(columns=["unit"], errors="ignore")
    rendered = rendered[["metric", *value_columns]].rename(
        columns={
            "metric": "Metric",
            "benchmark": benchmark_label or "Benchmark",
        }
    )
    return _table(rendered, table_id="performance-summary")


def _trailing_returns_table(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    columns = [column for column, _ in _TRAILING_COLUMNS if column in frame]
    rendered = frame[columns].copy()
    requested = portfolio_order or []
    ranking = {name: index for index, name in enumerate(requested)}
    rendered["_order"] = rendered["portfolio"].map(
        lambda value: len(requested)
        if str(value) == "benchmark"
        else ranking.get(str(value), len(requested) + 1)
    )
    rendered = rendered.sort_values("_order").drop(columns="_order")
    rendered["portfolio"] = rendered["portfolio"].map(
        lambda value: _display_portfolio(value, benchmark_label)
    )
    for column in columns:
        if column != "portfolio":
            rendered[column] = rendered[column].map(_pct)
    return _table(
        rendered.rename(
            columns={column: label for column, label in _TRAILING_COLUMNS}
        ),
        table_id="trailing-returns",
    )


def _metrics_matrix(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
    fallback_performance: pd.DataFrame | None = None,
    currency: str = "USD",
) -> str:
    if frame.empty or not {"portfolio", "metric", "value"}.issubset(frame.columns):
        if (
            fallback_performance is not None
            and not fallback_performance.empty
            and "metric" in fallback_performance
        ):
            requested = portfolio_order or []
            columns = [
                name for name in requested if name in fallback_performance.columns
            ]
            columns.extend(
                column
                for column in fallback_performance.columns
                if column not in {"metric", "unit"} and column not in columns
            )
            formatted = pd.DataFrame({"Metric": fallback_performance["metric"]})
            for column in columns:
                values = fallback_performance[column]
                if "unit" in fallback_performance:
                    values = [
                        _pct(value)
                        if unit_name == "pct"
                        else _money(value, currency)
                        if unit_name == "balance"
                        else _ratio(value)
                        for value, unit_name in zip(
                            values, fallback_performance["unit"]
                        )
                    ]
                formatted[_display_portfolio(column, benchmark_label)] = values
            return _table(
                formatted.reset_index(drop=True),
                table_id="portfolio-metrics",
            )
        return _friendly_table(
            frame,
            portfolio_order=portfolio_order,
            benchmark_label=benchmark_label,
        )
    pivot = frame.pivot_table(
        index="metric",
        columns="portfolio",
        values="value",
        aggfunc="first",
    )
    known = [metric for metric in _METRIC_LABELS if metric in pivot.index]
    known.extend(metric for metric in pivot.index if metric not in known)
    pivot = pivot.reindex(index=known)
    requested = portfolio_order or []
    columns = [name for name in requested if name in pivot.columns]
    if "benchmark" in pivot.columns:
        columns.append("benchmark")
    columns.extend(column for column in pivot.columns if column not in columns)
    pivot = pivot.reindex(columns=columns)
    formatted = pd.DataFrame(index=pivot.index)
    for column in pivot.columns:
        formatted[column] = [
            _fraction_pct(value)
            if metric in _METRIC_PERCENT_FRACTION
            else _ratio(value)
            for metric, value in pivot[column].items()
        ]
    formatted.insert(
        0,
        "Metric",
        [
            _METRIC_LABELS.get(metric, _human_column(metric))
            for metric in pivot.index
        ],
    )
    return _table(
        formatted.reset_index(drop=True).rename(
            columns={"benchmark": benchmark_label or "Benchmark"}
        ),
        table_id="portfolio-metrics",
    )


def _benchmark_summary_table(
    frame: pd.DataFrame,
    portfolio_order: list[str],
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    columns = [
        "portfolio",
        "active_return_pct",
        "tracking_error_pct",
        "information_ratio",
    ]
    rendered = frame[[column for column in columns if column in frame]].copy()
    ranking = {name: index for index, name in enumerate(portfolio_order)}
    rendered["_order"] = rendered["portfolio"].map(
        lambda value: ranking.get(str(value), len(ranking))
    )
    rendered = rendered.sort_values("_order").drop(columns="_order")
    if "active_return_pct" in rendered:
        rendered["active_return_pct"] = rendered["active_return_pct"].map(_pct)
    if "tracking_error_pct" in rendered:
        rendered["tracking_error_pct"] = rendered["tracking_error_pct"].map(_pct)
    if "information_ratio" in rendered:
        rendered["information_ratio"] = rendered["information_ratio"].map(_ratio)
    return _table(
        rendered.rename(
            columns={
                "portfolio": "Portfolio",
                "active_return_pct": "Active Return",
                "tracking_error_pct": "Tracking Error",
                "information_ratio": "Information Ratio",
            }
        )
    )


def _annual_returns_chart(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    if frame.empty or "year" not in frame:
        return '<p class="muted">N/A</p>'
    series: list[tuple[str, list[float | None]]] = []
    for name in portfolio_order:
        column = f"{name}_return_pct"
        if column in frame:
            series.append(
                (
                    name,
                    [float(value) if _finite(value) else None for value in frame[column]],
                )
            )
    if "benchmark_return_pct" in frame:
        series.append(
            (
                benchmark_label or "Benchmark",
                [
                    float(value) if _finite(value) else None
                    for value in frame["benchmark_return_pct"]
                ],
            )
        )
    categories = [str(int(value)) for value in frame["year"]]
    tooltips = []
    for index, year in enumerate(categories):
        parts = [year]
        for name, values in series:
            if index < len(values) and _finite(values[index]):
                parts.append(f"{name}: {_pct(values[index])}")
        tooltips.append(" | ".join(parts))
    return _grouped_bar_chart(
        categories,
        series,
        chart_id="annual-returns-chart",
        y_title="Annual Return %",
        tooltip_rows=tooltips,
    )


def _annual_active_frame(
    frame: pd.DataFrame,
    portfolio_order: list[str],
) -> pd.DataFrame:
    required = {"portfolio", "date", "annual_active_return"}
    if frame.empty or not required.issubset(frame.columns):
        return pd.DataFrame()
    shaped = frame[["portfolio", "date", "annual_active_return"]].copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"])
    shaped["year"] = shaped["date"].dt.year
    latest = (
        shaped.sort_values("date")
        .groupby(["year", "portfolio"], as_index=False)
        .tail(1)
    )
    pivot = latest.pivot(
        index="year",
        columns="portfolio",
        values="annual_active_return",
    ).sort_index()
    columns = [name for name in portfolio_order if name in pivot.columns]
    columns.extend(column for column in pivot.columns if column not in columns)
    return pivot.reindex(columns=columns).reset_index()


def _annual_active_return_table(
    frame: pd.DataFrame,
    portfolio_order: list[str],
) -> str:
    pivot = _annual_active_frame(frame, portfolio_order)
    if pivot.empty:
        return '<p class="muted">N/A</p>'
    rendered = pivot.copy()
    for column in rendered.columns:
        if column != "year":
            rendered[column] = rendered[column].map(_fraction_pct)
    return _table(rendered.rename(columns={"year": "Year"}))


def _annual_active_return_chart(
    frame: pd.DataFrame,
    portfolio_order: list[str],
) -> str:
    pivot = _annual_active_frame(frame, portfolio_order)
    if pivot.empty:
        return '<p class="muted">N/A</p>'
    categories = [str(int(value)) for value in pivot["year"]]
    series = [
        (
            name,
            [
                float(value) * 100 if _finite(value) else None
                for value in pivot[name]
            ],
        )
        for name in pivot.columns
        if name != "year"
    ]
    tooltips = []
    for index, year in enumerate(categories):
        parts = [year]
        for name, values in series:
            if index < len(values) and _finite(values[index]):
                parts.append(f"{name}: {_pct(values[index])}")
        tooltips.append(" | ".join(parts))
    return _grouped_bar_chart(
        categories,
        series,
        chart_id="annual-active-return-chart",
        y_title="Active Return %",
        tooltip_rows=tooltips,
    )


def _annual_asset_returns_chart(
    frame: pd.DataFrame,
    asset_names: dict[str, str] | None = None,
) -> str:
    required = {"year", "ticker", "return"}
    if frame.empty or not required.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    asset_names = asset_names or {}
    pivot = frame.pivot(
        index="year", columns="ticker", values="return"
    ).sort_index()
    categories = [str(int(value)) for value in pivot.index]
    ordered_tickers = [ticker for ticker in asset_names if ticker in pivot.columns]
    ordered_tickers.extend(
        ticker for ticker in pivot.columns if ticker not in ordered_tickers
    )
    series = []
    for ticker in ordered_tickers:
        name = asset_names.get(str(ticker), "").strip()
        label = f"{name} ({ticker})" if name else str(ticker)
        series.append(
            (
                label,
                [
                    float(value) * 100 if _finite(value) else None
                    for value in pivot[ticker]
                ],
            )
        )
    tooltips = []
    for index, year in enumerate(categories):
        parts = [year]
        for name, values in series:
            if index < len(values) and _finite(values[index]):
                parts.append(f"{name}: {_pct(values[index])}")
        tooltips.append(" | ".join(parts))
    return _grouped_bar_chart(
        categories,
        series,
        chart_id="annual-asset-returns-chart",
        y_title="Asset Return %",
        tooltip_rows=tooltips,
    )


def _drawdown_presentation(
    drawdown_series: pd.DataFrame,
    episodes: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    if drawdown_series.empty:
        return _friendly_table(
            episodes,
            portfolio_order=portfolio_order,
            benchmark_label=benchmark_label,
        )
    blocks = []
    identities = [
        (name, f"{name}_drawdown_pct", name) for name in portfolio_order
    ]
    if "benchmark_drawdown_pct" in drawdown_series:
        identities.append(
            ("benchmark", "benchmark_drawdown_pct", benchmark_label or "Benchmark")
        )
    for key, column, label in identities:
        if column not in drawdown_series:
            continue
        chart = _time_line_chart(
            drawdown_series[["date", column]],
            [(column, label)],
            chart_id=f"drawdown-{key}",
            y_title="Drawdown %",
        )
        episode = (
            episodes[episodes["portfolio"].astype(str) == key].copy()
            if "portfolio" in episodes
            else pd.DataFrame()
        )
        table = (
            _friendly_table(episode, benchmark_label=benchmark_label)
            if not episode.empty
            else '<p class="muted">No drawdown episode.</p>'
        )
        blocks.append(
            f'<div class="analysis-panel drawdown-panel" '
            f'data-portfolio="{_esc(label)}"><h3>{_esc(label)}</h3>'
            f'{chart}<h4>Drawdown Episodes</h4>{table}</div>'
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def _active_contribution_presentation(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    asset_names: dict[str, str] | None = None,
) -> str:
    required = {
        "date",
        "portfolio",
        "ticker",
        "cumulative_active_contribution_pct",
    }
    if frame.empty or not required.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    asset_names = asset_names or {}
    blocks = []
    for portfolio in portfolio_order:
        part = frame[frame["portfolio"].astype(str) == portfolio].copy()
        if part.empty:
            continue
        pivot = part.pivot(
            index="date",
            columns="ticker",
            values="cumulative_active_contribution_pct",
        ).reset_index()
        series: list[tuple[str, str]] = []
        for ticker in pivot.columns:
            if ticker == "date":
                continue
            name = asset_names.get(str(ticker), "").strip()
            label = f"{name} ({ticker})" if name else str(ticker)
            series.append((ticker, label))
        blocks.append(
            f'<div class="analysis-panel active-contribution-panel" '
            f'data-portfolio="{_esc(portfolio)}"><h4>{_esc(portfolio)}</h4>'
            f'{_time_line_chart(pivot, series, chart_id=f"active-contribution-{portfolio}", y_title="Cumulative Active Contribution %")}'
            '</div>'
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def _rolling_active_risk_panel(
    frame: pd.DataFrame,
    portfolio: str,
    benchmark_label: str | None,
) -> str:
    part = (
        frame[frame["portfolio"].astype(str) == portfolio].copy()
        if "portfolio" in frame
        else pd.DataFrame()
    )
    required = {"date", "rolling_active_return", "rolling_tracking_error_pct"}
    if part.empty or not required.issubset(part.columns):
        return '<p class="muted">N/A</p>'
    part["date"] = pd.to_datetime(part["date"], errors="coerce")
    part = part.dropna(
        subset=["date", "rolling_active_return", "rolling_tracking_error_pct"]
    ).sort_values("date")
    if part.empty:
        return '<p class="muted">N/A</p>'
    active = pd.to_numeric(part["rolling_active_return"], errors="coerce") * 100
    tracking = pd.to_numeric(
        part["rolling_tracking_error_pct"], errors="coerce"
    )
    left_min, left_max = min(float(active.min()), 0.0), max(float(active.max()), 0.0)
    right_min, right_max = 0.0, max(float(tracking.max()), 0.1)
    left_padding = max((left_max - left_min) * 0.08, 0.5)
    right_padding = max((right_max - right_min) * 0.08, 0.5)
    left_min, left_max = left_min - left_padding, left_max + left_padding
    right_max += right_padding
    margin_left, margin_right, margin_top, margin_bottom = 78, 78, 24, 72
    width, height = _DEF_WIDTH, _DEF_HEIGHT
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom
    dates = list(part["date"])
    date_min, date_max = dates[0], dates[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return (
            margin_left
            + plot_width * (date - date_min).total_seconds() / date_span
        )

    def y_left(value: float) -> float:
        return (
            margin_top
            + plot_height
            * (left_max - value)
            / max(left_max - left_min, 1e-12)
        )

    def y_right(value: float) -> float:
        return (
            margin_top
            + plot_height
            * (right_max - value)
            / max(right_max - right_min, 1e-12)
        )

    zero_y = y_left(0.0)
    bar_width = max(3.0, min(14.0, plot_width / max(len(part), 1) * 0.65))
    bars: list[str] = []
    line_coordinates: list[tuple[float, float]] = []
    points: list[str] = []
    for _, row in part.iterrows():
        date = pd.Timestamp(row["date"])
        active_value = float(row["rolling_active_return"]) * 100
        tracking_error = float(row["rolling_tracking_error_pct"])
        x = x_for(date)
        active_y = y_left(active_value)
        tooltip = (
            f"{date.strftime('%Y-%m-%d')} | Active Return: {_pct(active_value)} | "
            f"Tracking Error: {_pct(tracking_error)}"
        )
        bars.append(
            f'<rect x="{x - bar_width / 2:.2f}" '
            f'y="{min(active_y, zero_y):.2f}" width="{bar_width:.2f}" '
            f'height="{max(abs(zero_y - active_y), 1):.2f}" '
            f'fill="{_PALETTE[0]}" class="chart-mark active-return-bar" '
            f'tabindex="0" data-tooltip="{_esc(tooltip)}" '
            f'aria-label="{_esc(tooltip)}" />'
        )
        tracking_y = y_right(tracking_error)
        line_coordinates.append((x, tracking_y))
        points.append(
            f'<circle cx="{x:.2f}" cy="{tracking_y:.2f}" r="4.5" '
            f'fill="{_PALETTE[1]}" '
            'class="chart-mark tracking-error-point" tabindex="0" '
            f'data-tooltip="{_esc(tooltip)}" aria-label="{_esc(tooltip)}" />'
        )
    x_ticks = []
    for date in _calendar_ticks(part["date"]):
        x = x_for(date)
        x_ticks.append(
            f'<text x="{x:.2f}" y="{margin_top + plot_height + 24}" '
            f'text-anchor="middle" class="axis-label x-tick-label">'
            f'{_esc(date.strftime("%b %Y"))}</text>'
        )
    axes: list[str] = []
    left_step = _nice_step(left_max - left_min, 5)
    tick = math.ceil(left_min / left_step) * left_step
    while tick <= left_max + left_step * 0.1 and len(axes) < 20:
        y = y_left(tick)
        axes.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" '
            f'x2="{margin_left + plot_width}" y2="{y:.2f}" '
            'class="grid-line" />'
        )
        axes.append(
            f'<text x="{margin_left - 10}" y="{y + 4:.2f}" '
            f'text-anchor="end" class="axis-label left-axis-label">'
            f'{_esc(_pct(tick))}</text>'
        )
        tick += left_step
    right_step = _nice_step(right_max - right_min, 5)
    tick = right_min
    while tick <= right_max + right_step * 0.1 and len(axes) < 40:
        y = y_right(tick)
        axes.append(
            f'<text x="{margin_left + plot_width + 10}" y="{y + 4:.2f}" '
            f'text-anchor="start" class="axis-label right-axis-label">'
            f'{_esc(_pct(tick))}</text>'
        )
        tick += right_step
    svg = f'''<svg class="analysis-chart rolling-active-risk-chart" viewBox="0 0 {width} {height}" role="img" aria-label="Rolling Active Return and Risk 36 months">
      {''.join(axes)}
      <line x1="{margin_left}" y1="{zero_y:.2f}" x2="{margin_left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(bars)}
      <polyline points="{' '.join(f'{x:.2f},{y:.2f}' for x, y in line_coordinates)}" fill="none" stroke="{_PALETTE[1]}" stroke-width="2.4" class="tracking-error-line" />
      {''.join(points)}{''.join(x_ticks)}
      <text x="{margin_left + plot_width / 2:.2f}" y="{height - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {margin_top + plot_height / 2:.2f})">Active Return %</text>
      <text x="{width - 20}" y="{margin_top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(90 {width - 20} {margin_top + plot_height / 2:.2f})">Tracking Error %</text>
    </svg>'''
    legend = _legend(
        [("Active Return", _PALETTE[0]), ("Tracking Error", _PALETTE[1])]
    )
    subtitle = f"{portfolio} vs. {benchmark_label or 'Benchmark'}"
    return (
        f'<div class="analysis-panel rolling-active-risk-panel" '
        f'data-portfolio="{_esc(portfolio)}">'
        '<h4>Rolling Active Return and Risk (36 months)</h4>'
        f'<p class="panel-subtitle">{_esc(subtitle)}</p>'
        f'{_chart_shell(f"rolling-active-risk-{portfolio}", svg, legend)}</div>'
    )


def _up_down_statistics(
    active_returns: pd.DataFrame,
    portfolio: str,
) -> pd.DataFrame:
    part = (
        active_returns[
            active_returns["portfolio"].astype(str) == portfolio
        ].copy()
        if "portfolio" in active_returns
        else pd.DataFrame()
    )
    required = {"benchmark_return", "active_return"}
    if part.empty or not required.issubset(part.columns):
        return pd.DataFrame()
    part["market_type"] = np.where(
        pd.to_numeric(part["benchmark_return"], errors="coerce") >= 0,
        "Up",
        "Down",
    )
    rows = []
    for market_type in ["Up", "Down"]:
        group = part[part["market_type"] == market_type]
        if group.empty:
            continue
        active = pd.to_numeric(group["active_return"], errors="coerce").dropna()
        above = active[active > 0]
        below = active[active < 0]
        total = len(active)
        rows.append(
            {
                "Market Type": market_type,
                "Above Benchmark Count": len(above),
                "Below Benchmark Count": len(below),
                "Total": total,
                "% Above Benchmark": _pct(
                    100 * len(above) / total if total else np.nan
                ),
                "Average Active Return Above": (
                    _fraction_pct(above.mean()) if len(above) else "N/A"
                ),
                "Average Active Return Below": (
                    _fraction_pct(below.mean()) if len(below) else "N/A"
                ),
                "Average Active Return Total": (
                    _fraction_pct(active.mean()) if total else "N/A"
                ),
            }
        )
    return pd.DataFrame(rows)


def _up_down_paired_chart(
    active_returns: pd.DataFrame,
    portfolio: str,
) -> str:
    part = (
        active_returns[
            active_returns["portfolio"].astype(str) == portfolio
        ].copy()
        if "portfolio" in active_returns
        else pd.DataFrame()
    )
    required = {"benchmark_return", "portfolio_return"}
    if part.empty or not required.issubset(part.columns):
        return '<p class="muted">N/A</p>'
    part = part.dropna(
        subset=["benchmark_return", "portfolio_return"]
    ).sort_values("benchmark_return")
    if part.empty:
        return '<p class="muted">N/A</p>'
    group_count = min(20, len(part))
    group_indices = np.array_split(np.arange(len(part)), group_count)
    categories: list[str] = []
    portfolio_values: list[float] = []
    benchmark_values: list[float] = []
    tooltips: list[str] = []
    for index, indices in enumerate(group_indices, start=1):
        group = part.iloc[indices]
        benchmark_return = float(group["benchmark_return"].mean()) * 100
        portfolio_return = float(group["portfolio_return"].mean()) * 100
        categories.append(f"{benchmark_return:.1f}%")
        portfolio_values.append(portfolio_return)
        benchmark_values.append(benchmark_return)
        tooltips.append(
            f"Group {index} | {portfolio}: {_pct(portfolio_return)} | "
            f"Benchmark: {_pct(benchmark_return)} | Observations: {len(group)}"
        )
    return _grouped_bar_chart(
        categories,
        [(portfolio, portfolio_values), ("Benchmark", benchmark_values)],
        chart_id=f"return-vs-benchmark-{portfolio}",
        y_title="Return %",
        tooltip_rows=tooltips,
        x_title="Group Mean Benchmark Return %",
    )


def _up_down_presentation(
    active_returns: pd.DataFrame,
    portfolio_order: list[str],
) -> str:
    blocks = []
    for portfolio in portfolio_order:
        statistics = _up_down_statistics(active_returns, portfolio)
        if statistics.empty:
            continue
        blocks.append(
            f'<div class="analysis-panel up-down-panel" '
            f'data-portfolio="{_esc(portfolio)}"><h4>{_esc(portfolio)}</h4>'
            f'{_table(statistics, table_class="up-down-statistics")}'
            f'<h5>Return vs. Benchmark</h5>'
            f'{_up_down_paired_chart(active_returns, portfolio)}</div>'
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def _active_returns_presentation(
    active_returns: pd.DataFrame,
    active_contribution: pd.DataFrame,
    benchmark: pd.DataFrame,
    up_down: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    asset_names: dict[str, str] | None = None,
) -> str:
    del up_down
    rolling_panels = "".join(
        _rolling_active_risk_panel(
            active_returns,
            portfolio,
            benchmark_label,
        )
        for portfolio in portfolio_order
    )
    return f'''
      <h3>Benchmark Summary</h3>{_benchmark_summary_table(benchmark, portfolio_order)}
      <h3>Annual Active Return</h3>{_annual_active_return_chart(active_returns, portfolio_order)}{_annual_active_return_table(active_returns, portfolio_order)}
      <h3>Active Return Contribution</h3>{_active_contribution_presentation(active_contribution, portfolio_order, asset_names)}
      <h3>Rolling Active Return and Risk</h3>{rolling_panels}
      <h3>Up / Down Market Performance</h3>{_up_down_presentation(active_returns, portfolio_order)}
    '''


def _rolling_returns_chart(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    years: int,
) -> str:
    series: list[tuple[str, str]] = []
    for name in portfolio_order:
        column = f"{name}_annualized_return_pct"
        if column in frame:
            series.append((column, name))
    if "benchmark_annualized_return_pct" in frame:
        series.append(
            (
                "benchmark_annualized_return_pct",
                benchmark_label or "Benchmark",
            )
        )
    return _time_line_chart(
        frame,
        series,
        chart_id=f"rolling-{years}y-annualized-return",
        y_title="Annualized Return %",
    )


def _asset_performance_from_monthly_returns(
    frame: pd.DataFrame,
    configuration: dict[str, Any],
) -> pd.DataFrame:
    if frame.empty or "date" not in frame:
        return pd.DataFrame()
    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    rf_annual = float(
        (configuration.get("risk_free") or {}).get("effective_annual_rate")
        or 0.0
    )
    assets = {
        str(asset.get("symbol")): str(asset.get("name") or "")
        for asset in configuration.get("assets", [])
        if isinstance(asset, dict)
    }
    rows = []
    for column in shaped.columns:
        if not str(column).startswith("asset_"):
            continue
        ticker = str(column)[len("asset_") :]
        returns = pd.to_numeric(shaped[column], errors="coerce")
        valid = pd.DataFrame(
            {"date": shaped["date"], "return": returns}
        ).dropna()
        if valid.empty:
            continue
        series = valid["return"]
        observation_count = len(series)
        compounded = float((1.0 + series).prod())
        cagr = (
            compounded ** (12.0 / observation_count) - 1.0
            if compounded > 0
            else np.nan
        )
        annualized_return = float(series.mean() * 12.0)
        annualized_std = (
            float(series.std(ddof=1) * math.sqrt(12))
            if observation_count > 1
            else np.nan
        )
        sharpe = (
            (annualized_return - rf_annual) / annualized_std
            if _finite(annualized_std) and annualized_std > 0
            else np.nan
        )
        rf_month = (
            (1.0 + rf_annual) ** (1.0 / 12.0) - 1.0
            if rf_annual > -1
            else 0.0
        )
        downside = np.minimum(series.to_numpy(dtype=float) - rf_month, 0.0)
        downside_deviation = (
            float(np.sqrt(np.mean(downside**2)) * math.sqrt(12))
            if observation_count
            else np.nan
        )
        sortino = (
            (annualized_return - rf_annual) / downside_deviation
            if _finite(downside_deviation) and downside_deviation > 0
            else np.nan
        )
        wealth = (1.0 + series).cumprod()
        max_drawdown = float((wealth / wealth.cummax() - 1.0).min())
        yearly = (
            valid.assign(year=valid["date"].dt.year)
            .groupby("year")["return"]
            .apply(lambda values: float((1.0 + values).prod() - 1.0))
        )
        best_year = float(yearly.max()) if not yearly.empty else np.nan
        worst_year = float(yearly.min()) if not yearly.empty else np.nan
        last_date = valid["date"].iloc[-1]

        def trailing(months: int, annualize: bool = False) -> float:
            if len(series) < months:
                return np.nan
            chunk = series.iloc[-months:]
            total = float((1.0 + chunk).prod() - 1.0)
            if annualize:
                return (1.0 + total) ** (12.0 / months) - 1.0
            return total

        ytd_chunk = valid[valid["date"].dt.year == last_date.year]["return"]
        ytd = (
            float((1.0 + ytd_chunk).prod() - 1.0)
            if not ytd_chunk.empty
            else np.nan
        )
        trailing_3m = trailing(3)
        trailing_1y = trailing(12)
        trailing_3y = trailing(36, True)
        trailing_5y = trailing(60, True)
        trailing_10y = trailing(120, True)
        rows.append(
            {
                "ticker": ticker,
                "name": assets.get(ticker, ""),
                "cagr_pct": cagr * 100,
                "annualized_return_pct": annualized_return * 100,
                "annualized_volatility_pct": (
                    annualized_std * 100 if _finite(annualized_std) else np.nan
                ),
                "best_year_pct": best_year * 100,
                "worst_year_pct": worst_year * 100,
                "max_drawdown_pct": max_drawdown * 100,
                "sharpe_ratio": sharpe,
                "sortino_ratio": sortino,
                "3m_pct": (
                    trailing_3m * 100 if _finite(trailing_3m) else np.nan
                ),
                "ytd_pct": ytd * 100,
                "1y_pct": (
                    trailing_1y * 100 if _finite(trailing_1y) else np.nan
                ),
                "3y_pct": (
                    trailing_3y * 100 if _finite(trailing_3y) else np.nan
                ),
                "5y_pct": (
                    trailing_5y * 100 if _finite(trailing_5y) else np.nan
                ),
                "10y_pct": (
                    trailing_10y * 100 if _finite(trailing_10y) else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def _asset_performance_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    columns = [
        "ticker",
        "name",
        "cagr_pct",
        "annualized_return_pct",
        "annualized_volatility_pct",
        "best_year_pct",
        "worst_year_pct",
        "max_drawdown_pct",
        "sharpe_ratio",
        "sortino_ratio",
        "3m_pct",
        "ytd_pct",
        "1y_pct",
        "3y_pct",
        "5y_pct",
        "10y_pct",
    ]
    rendered = frame[[column for column in columns if column in frame]].copy()
    for column in rendered.columns:
        if column.endswith("_pct"):
            rendered[column] = rendered[column].map(_pct)
        elif column.endswith("_ratio"):
            rendered[column] = rendered[column].map(_ratio)
    labels = {
        "ticker": "Ticker",
        "name": "Name",
        "cagr_pct": "CAGR",
        "annualized_return_pct": "Annualized Return",
        "annualized_volatility_pct": "Standard Deviation",
        "best_year_pct": "Best Year",
        "worst_year_pct": "Worst Year",
        "max_drawdown_pct": "Maximum Drawdown",
        "sharpe_ratio": "Sharpe Ratio",
        "sortino_ratio": "Sortino Ratio",
        "3m_pct": "3M",
        "ytd_pct": "YTD",
        "1y_pct": "1Y",
        "3y_pct": "3Y Annualized",
        "5y_pct": "5Y Annualized",
        "10y_pct": "10Y Annualized",
    }
    return _table(
        rendered.rename(columns=labels),
        table_id="portfolio-asset-performance",
    )


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
        frame = _read_csv(review / name)
        return frame if not frame.empty else _read_csv(raw / name)

    allocations = artifact("target_allocations.csv")
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
    correlations = artifact("correlations.csv")
    returns_decomp = artifact("return_decomposition.csv")
    risk_decomp = artifact("risk_decomposition.csv")
    portfolio_metrics = artifact("portfolio_metrics.csv")
    annual_assets = artifact("annual_asset_returns.csv")
    active_returns = artifact("active_returns.csv")
    active_contribution = artifact("active_return_contribution.csv")
    up_down = artifact("up_down_market_performance.csv")
    monthly_series = artifact("monthly_return_series.csv")
    asset_performance = artifact("portfolio_asset_performance.csv")
    if asset_performance.empty:
        asset_performance = _asset_performance_from_monthly_returns(
            monthly_series, configuration
        )
        if not asset_performance.empty:
            review.mkdir(parents=True, exist_ok=True)
            asset_performance.to_csv(
                review / "portfolio_asset_performance.csv", index=False
            )

    period = configuration.get("analysis_period", {}) or {}
    benchmark_configuration = configuration.get("benchmark")
    benchmark_label = (
        benchmark_configuration.get("name")
        or benchmark_configuration.get("symbol")
        if isinstance(benchmark_configuration, dict)
        else None
    )
    currency = _base_currency(configuration)
    portfolio_order = _portfolio_order(allocations, [])
    if not portfolio_order:
        portfolio_order = list((result.get("portfolio_definitions") or {}).keys())
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
        active_section = f'''<section id="activeReturns" class="result-section benchmark-relative"><h2>Active Returns</h2>
        {_active_returns_presentation(active_returns, active_contribution, benchmark, up_down, portfolio_order, benchmark_label, asset_names)}</section>'''

    document = f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Portfolio Backtest Report</title>
<style>
:root {{ color-scheme: light; font-family: Roboto, "Work Sans", "Helvetica Neue", Arial, sans-serif; }}
* {{ box-sizing:border-box; }} body {{ margin:0; background:#fff; color:#333; }}
.topbar {{ border-bottom:1px solid #d8dee8; background:#fff; padding:14px 24px; font-weight:600; font-size:20px; }}
.shell {{ display:grid; grid-template-columns:190px minmax(0,1fr); max-width:1400px; margin:0 auto; }}
.sidebar {{ border-right:1px solid #e2e8f0; padding:22px 14px; min-height:100vh; position:sticky; top:0; align-self:start; }}
.sidebar a {{ display:block; color:#374151; text-decoration:none; padding:10px 9px; border-radius:5px; font-size:14px; }}
.sidebar a:hover,.sidebar a:focus {{ background:#eef4ff; color:#184f9d; outline:none; }}
main {{ min-width:0; padding:26px 32px 72px; }} .result-header {{ margin:0 0 12px; color:#1f2937; font-size:25px; font-weight:500; }}
.coverage-note {{ border-left:3px solid #316db5; padding:8px 12px; margin:0 0 20px; background:#f8fbff; font-size:13px; }}
.result-section {{ border:1px solid #e0e5ec; padding:22px; margin:0 0 24px; background:#fff; }}
.result-section h2 {{ margin:0 0 18px; font-size:21px; color:#1d5c9b; font-weight:500; }}
.result-section h3 {{ margin:28px 0 10px; font-size:17px; font-weight:500; color:#1d5c9b; }}
.result-section h4 {{ margin:20px 0 8px; font-size:15px; color:#374151; }} .result-section h5 {{ margin:18px 0 8px; font-size:14px; }}
.meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1px; background:#e5e7eb; border:1px solid #e5e7eb; margin-bottom:20px; }}
.meta div {{ background:#fff; padding:10px 12px; font-size:13px; }} .meta b {{ display:block; font-size:11px; color:#6b7280; margin-bottom:4px; text-transform:uppercase; letter-spacing:.02em; }}
.table-wrap {{ overflow-x:auto; border:1px solid #e2e8f0; margin-bottom:12px; }} table {{ border-collapse:collapse; width:100%; min-width:640px; }}
th,td {{ padding:8px 10px; border-bottom:1px solid #e8ecf1; text-align:right; font-size:13px; }} th:first-child,td:first-child {{ text-align:left; }}
th {{ background:#f5f7fa; color:#374151; font-weight:600; }} tbody tr:nth-child(even) {{ background:#fafbfc; }}
.heatmap td {{ font-variant-numeric:tabular-nums; }} .identity-cell {{ font-weight:500; }}
.legend {{ display:flex; flex-wrap:wrap; gap:18px; justify-content:center; margin:8px 0 10px; }} .legend-item {{ display:inline-flex; align-items:center; gap:6px; font-size:12px; }} .legend-item i {{ width:18px; height:3px; display:inline-block; }}
.chart-wrap {{ overflow-x:auto; position:relative; margin-bottom:12px; }} .analysis-chart {{ width:100%; min-width:900px; height:auto; display:block; }}
.axis {{ stroke:#ccd6eb; stroke-width:1; }} .zero-axis {{ stroke:#9ca3af; }} .grid-line {{ stroke:#e6e6e6; stroke-width:1; }}
.axis-label {{ font-size:11px; fill:#333; }} .axis-title {{ font-size:12px; fill:#333; }}
.chart-mark {{ cursor:crosshair; }} .line-point,.growth-point,.tracking-error-point {{ opacity:0; }}
.line-point:hover,.line-point:focus,.growth-point:hover,.growth-point:focus,.tracking-error-point:hover,.tracking-error-point:focus {{ opacity:1; stroke:#fff; stroke-width:2; outline:none; }}
.chart-tooltip {{ display:none; position:absolute; z-index:4; pointer-events:none; background:rgba(255,255,255,.98); border:1px solid #9ca3af; box-shadow:0 3px 12px rgba(0,0,0,.12); padding:8px 10px; font-size:12px; border-radius:3px; white-space:normal; max-width:min(520px,80vw); }}
.muted,.panel-subtitle {{ color:#6b7280; font-size:12px; }} .summary-block {{ margin-top:24px; }} .summary-block > h3 {{ color:#1d5c9b; font-size:17px; }}
.analysis-panel {{ border-top:1px solid #eef1f5; padding-top:8px; margin-top:18px; }}
@media (max-width:800px) {{ .shell {{ display:block; }} .sidebar {{ min-height:0; position:sticky; top:0; z-index:5; display:flex; gap:4px; overflow-x:auto; border-right:0; border-bottom:1px solid #e2e8f0; background:#fff; padding:8px 10px; }} .sidebar a {{ white-space:nowrap; padding:7px 9px; }} main {{ padding:18px 12px 50px; }} .result-section {{ padding:14px; }} }}
</style></head><body>
<div class="topbar">Portfolio Research · Backtest</div><div class="shell"><nav class="sidebar" aria-label="Backtest result sections">{nav}</nav><main>
<h1 class="result-header">Portfolio Analysis Results ({_esc(effective_label)})</h1>{_period_note(configuration, coverage)}
<section id="overview" class="result-section"><h2>Summary</h2><div class="meta">
<div><b>Run ID</b>{_esc(configuration.get('run_id'))}</div><div><b>Time Period</b>{_esc(_display_option(configuration.get('time_period_mode')))}</div>
<div><b>Requested</b>{_esc(period.get('start'))} → {_esc(period.get('end'))}</div><div><b>Effective</b>{_esc(coverage.get('start'))} → {_esc(coverage.get('end'))} ({_esc(coverage.get('observations'))} months)</div>
<div><b>Initial Amount</b>{_money(configuration.get('initial_balance'), currency)}</div><div><b>Benchmark</b>{_esc(benchmark_label or 'None')}</div>
<div><b>Rebalancing</b>{_esc(_display_option(configuration.get('rebalancing_period')))}</div><div><b>Calendar Aligned</b>{alignment}</div><div><b>Return Semantics</b>{_esc(_display_option(configuration.get('return_semantics')))}</div></div>
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
<section id="rollingReturns" class="result-section"><h2>Rolling Returns</h2><h3>Rolling 3 Year Annualized Return</h3>{_rolling_returns_chart(rolling3, portfolio_order, benchmark_label, 3)}{_friendly_table(rolling3, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}<h3>Rolling 5 Year Annualized Return</h3>{_rolling_returns_chart(rolling5, portfolio_order, benchmark_label, 5)}{_friendly_table(rolling5, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
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
    const clientX = event?.clientX || (markRect.left + markRect.width / 2); const clientY = event?.clientY || markRect.top;
    tooltip.style.left = `${{Math.max(6, clientX - hostRect.left + host.scrollLeft + 12)}}px`;
    tooltip.style.top = `${{Math.max(6, clientY - hostRect.top + host.scrollTop - 44)}}px`;
  }};
  const hide = mark => {{ const tooltip = mark.closest('.chart-wrap')?.querySelector('.chart-tooltip'); if (tooltip) tooltip.style.display = 'none'; }};
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
