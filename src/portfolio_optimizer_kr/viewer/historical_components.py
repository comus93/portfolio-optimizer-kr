from __future__ import annotations

import html
import math
from typing import Any, Iterable

import numpy as np
import pandas as pd


WIDTH = 1060
HEIGHT = 420
PALETTE = [
    "#1200FF",
    "#50E2B0",
    "#85ACD0",
    "#2D7186",
    "#A45EE5",
    "#E59F3A",
    "#D45050",
    "#6F8F3D",
]

METRIC_LABELS = {
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
METRIC_PERCENT_FRACTION = {
    "alpha",
    "modigliani_modigliani",
    "historical_var_95",
}
TRAILING_COLUMNS = [
    ("portfolio", "Portfolio"),
    ("return_3m_pct", "3 Month"),
    ("3m_pct", "3 Month"),
    ("ytd_pct", "YTD"),
    ("return_1y_pct", "1 Year"),
    ("1y_pct", "1 Year"),
    ("annualized_3y_pct", "3 Year Annualized Return"),
    ("3y_pct", "3 Year Annualized Return"),
    ("annualized_5y_pct", "5 Year Annualized Return"),
    ("5y_pct", "5 Year Annualized Return"),
    ("annualized_10y_pct", "10 Year Annualized Return"),
    ("10y_pct", "10 Year Annualized Return"),
    ("full_period_cagr_pct", "Full Period CAGR"),
    ("full_period_pct", "Full Period CAGR"),
    ("volatility_3y_pct", "3 Year Annualized Standard Deviation"),
    ("3y_annualized_volatility_pct", "3 Year Annualized Standard Deviation"),
    ("volatility_5y_pct", "5 Year Annualized Standard Deviation"),
    ("5y_annualized_volatility_pct", "5 Year Annualized Standard Deviation"),
]


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def pct(value: Any) -> str:
    return f"{float(value):,.2f}%" if finite(value) else "N/A"


def fraction_pct(value: Any) -> str:
    return f"{float(value) * 100:,.2f}%" if finite(value) else "N/A"


def money(value: Any, currency: str = "USD") -> str:
    if not finite(value):
        return "N/A"
    code = str(currency or "USD").upper()
    symbol = {"USD": "$", "KRW": "₩"}.get(code)
    return (
        f"{symbol}{float(value):,.0f}"
        if symbol
        else f"{code} {float(value):,.0f}"
    )


def currency_label(currency: str) -> str:
    code = str(currency or "USD").upper()
    return {"USD": "$", "KRW": "₩"}.get(code, code)


def ratio(value: Any) -> str:
    return f"{float(value):,.3f}" if finite(value) else "N/A"


def correlation(value: Any) -> str:
    return f"{float(value):,.2f}" if finite(value) else "N/A"


def display_portfolio(value: Any, benchmark_label: str | None) -> str:
    text = str(value)
    return (benchmark_label or "Benchmark") if text == "benchmark" else text


def human_column(column: str, benchmark_label: str | None = None) -> str:
    labels = {
        "benchmark": benchmark_label or "Benchmark",
        "date": "Date",
        "year": "Year",
        "portfolio": "Portfolio",
        "ticker": "Ticker",
        "name": "Name",
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
        word.capitalize()
        for word in label.replace("_", " ").strip().split()
    )


def table(
    frame: pd.DataFrame,
    *,
    table_id: str | None = None,
    table_class: str = "",
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    identifier = f' id="{esc(table_id)}"' if table_id else ""
    cls = f' class="{esc(table_class)}"' if table_class else ""
    headers = "".join(f"<th>{esc(column)}</th>" for column in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = "".join(
            f"<td>{esc('N/A' if pd.isna(value) else value)}</td>"
            for value in row
        )
        rows.append(f"<tr>{cells}</tr>")
    return (
        f'<div class="table-wrap"><table{identifier}{cls}><thead><tr>'
        f'{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    )


def friendly_table(
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
    if "portfolio" in rendered:
        requested = portfolio_order or []
        ranking = {name: index for index, name in enumerate(requested)}
        rendered["_order"] = rendered["portfolio"].map(
            lambda value: len(requested)
            if str(value) == "benchmark"
            else ranking.get(str(value), len(requested) + 1)
        )
        sort_columns = ["_order"] + (
            ["date"] if "date" in rendered else []
        )
        rendered = rendered.sort_values(sort_columns).drop(columns="_order")
        rendered["portfolio"] = rendered["portfolio"].map(
            lambda value: display_portfolio(value, benchmark_label)
        )
    if "series" in rendered:
        rendered["series"] = rendered["series"].map(
            lambda value: display_portfolio(value, benchmark_label)
        )
    for column in rendered.columns:
        if column in fraction_columns:
            rendered[column] = rendered[column].map(fraction_pct)
        elif column in money_columns:
            rendered[column] = rendered[column].map(
                lambda value: money(value, currency)
            )
        elif column in ratio_columns:
            rendered[column] = rendered[column].map(correlation)
        elif str(column).endswith("_pct"):
            rendered[column] = rendered[column].map(pct)
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
                column, human_column(str(column), benchmark_label)
            )
            for column in rendered.columns
        }
    )
    return table(rendered, table_id=table_id)


def calendar_ticks(dates: pd.Series) -> list[pd.Timestamp]:
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
    selected: list[pd.Timestamp] = []
    seen: set[tuple[int, int]] = set()
    for value in normalized:
        key = (value.year, value.month)
        if key in seen:
            continue
        if value.month in anchor_months and (value.year - start.year) % year_step == 0:
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


def nice_step(span: float, target_ticks: int = 6) -> float:
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


def legend(items: Iterable[tuple[str, str]]) -> str:
    def label_html(value: Any) -> str:
        return esc(value).replace("\n", "<br>")

    return '<div class="legend">' + "".join(
        f'<span class="legend-item"><i style="background:{color}"></i>'
        f'<span class="legend-label">{label_html(label)}</span></span>'
        for label, color in items
    ) + "</div>"


def chart_shell(
    chart_id: str,
    svg: str,
    legend_html: str = "",
    note: str = "",
) -> str:
    note_html = f'<p class="muted">{esc(note)}</p>' if note else ""
    return (
        f'{legend_html}<div class="chart-wrap analysis-chart-wrap" '
        f'data-chart="{esc(chart_id)}">'
        '<div class="chart-tooltip generic-tooltip" role="status" '
        f'aria-live="polite"></div>{svg}</div>{note_html}'
    )


def grouped_bar_chart(
    categories: list[str],
    series: list[tuple[str, list[float | None]]],
    *,
    chart_id: str,
    y_title: str,
    tooltip_rows: list[str] | None = None,
    x_title: str = "Year",
) -> str:
    values = [
        float(value)
        for _, row in series
        for value in row
        if finite(value)
    ]
    if not categories or not series or not values:
        return '<p class="muted">N/A</p>'
    y_min, y_max = min(min(values), 0.0), max(max(values), 0.0)
    if math.isclose(y_min, y_max):
        y_max = y_min + 1.0
    padding = max((y_max - y_min) * 0.08, 1.0)
    y_min, y_max = y_min - padding, y_max + padding
    left, right, top, bottom = 78, 24, 24, 72
    plot_width, plot_height = WIDTH - left - right, HEIGHT - top - bottom

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    zero_y = y_for(0.0)
    step = nice_step(y_max - y_min, 6)
    tick = math.ceil(y_min / step) * step
    grid: list[str] = []
    while tick <= y_max + step * 0.1 and len(grid) < 24:
        y = y_for(tick)
        grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" '
            f'y2="{y:.2f}" class="grid-line" />'
            f'<text x="{left - 10}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-tick-label">{esc(pct(tick))}</text>'
        )
        tick += step
    group_width = plot_width / max(len(categories), 1)
    inner_width = group_width * 0.76
    bar_width = inner_width / max(len(series), 1)
    marks: list[str] = []
    labels: list[str] = []
    for category_index, category in enumerate(categories):
        center = left + group_width * (category_index + 0.5)
        if len(categories) <= 16 or category_index % max(1, len(categories) // 10) == 0 or category_index == len(categories) - 1:
            labels.append(
                f'<text x="{center:.2f}" y="{top + plot_height + 24}" '
                f'text-anchor="middle" class="axis-label x-tick-label">{esc(category)}</text>'
            )
        tooltip = tooltip_rows[category_index] if tooltip_rows and category_index < len(tooltip_rows) else category
        for series_index, (name, values_row) in enumerate(series):
            if category_index >= len(values_row) or not finite(values_row[category_index]):
                continue
            value = float(values_row[category_index])
            x = center - inner_width / 2 + series_index * bar_width + bar_width * 0.08
            y_value = y_for(value)
            marks.append(
                f'<rect x="{x:.2f}" y="{min(zero_y, y_value):.2f}" '
                f'width="{bar_width * 0.84:.2f}" height="{max(abs(zero_y - y_value), 1):.2f}" '
                f'fill="{PALETTE[series_index % len(PALETTE)]}" '
                'class="chart-mark grouped-bar" tabindex="0" '
                f'data-tooltip="{esc(tooltip)}" aria-label="{esc(category + " | " + name + ": " + pct(value))}" />'
            )
    svg = f'''<svg class="analysis-chart grouped-bar-chart" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{esc(chart_id)}">
      {''.join(grid)}
      <line x1="{left}" y1="{zero_y:.2f}" x2="{left + plot_width}" y2="{zero_y:.2f}" class="axis zero-axis" />
      {''.join(marks)}{''.join(labels)}
      <text x="{left + plot_width / 2:.2f}" y="{HEIGHT - 14}" text-anchor="middle" class="axis-title">{esc(x_title)}</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">{esc(y_title)}</text>
    </svg>'''
    return chart_shell(
        chart_id,
        svg,
        legend(
            (name, PALETTE[index % len(PALETTE)])
            for index, (name, _) in enumerate(series)
        ),
    )


def time_line_chart(
    frame: pd.DataFrame,
    series: list[tuple[str, str]],
    *,
    chart_id: str,
    y_title: str,
    value_scale: float = 1.0,
) -> str:
    if frame.empty or "date" not in frame:
        return '<p class="muted">N/A</p>'
    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    existing = [(column, label) for column, label in series if column in shaped]
    values = [
        float(value) * value_scale
        for column, _ in existing
        for value in pd.to_numeric(shaped[column], errors="coerce").dropna()
    ]
    if shaped.empty or not existing or not values:
        return '<p class="muted">N/A</p>'
    y_min, y_max = min(values), max(values)
    if y_title.endswith("%"):
        y_min, y_max = min(0.0, y_min), max(0.0, y_max)
    if math.isclose(y_min, y_max):
        y_min -= 1
        y_max += 1
    padding = max((y_max - y_min) * 0.08, 0.5)
    y_min, y_max = y_min - padding, y_max + padding
    left, right, top, bottom = 78, 24, 24, 70
    plot_width, plot_height = WIDTH - left - right, HEIGHT - top - bottom
    date_min, date_max = shaped["date"].iloc[0], shaped["date"].iloc[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return left + plot_width * (date - date_min).total_seconds() / date_span

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    paths: list[str] = []
    points: list[str] = []
    for series_index, (column, label) in enumerate(existing):
        color = PALETTE[series_index % len(PALETTE)]
        coords: list[tuple[float, float]] = []
        for _, row in shaped.iterrows():
            if not finite(row[column]):
                continue
            date = pd.Timestamp(row["date"])
            value = float(row[column]) * value_scale
            x, y = x_for(date), y_for(value)
            coords.append((x, y))
            tooltip = " | ".join(
                [date.strftime("%Y-%m-%d")]
                + [
                    f"{peer_label}: {pct(float(row[peer_column]) * value_scale)}"
                    for peer_column, peer_label in existing
                    if finite(row.get(peer_column))
                ]
            )
            points.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="{color}" '
                f'class="chart-mark line-point" tabindex="0" data-tooltip="{esc(tooltip)}" '
                f'aria-label="{esc(date.strftime("%Y-%m-%d") + " | " + label + ": " + pct(value))}" />'
            )
        if coords:
            paths.append(
                f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in coords)}" '
                f'fill="none" stroke="{color}" stroke-width="2.2" class="line-series" />'
            )
    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" y="{top + plot_height + 24}" '
        f'text-anchor="middle" class="axis-label x-tick-label">{esc(date.strftime("%b %Y"))}</text>'
        for date in calendar_ticks(shaped["date"])
    )
    svg = f'''<svg class="analysis-chart line-chart" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{esc(chart_id)}">
      {x_ticks}{''.join(paths)}{''.join(points)}
      <text x="{left + plot_width / 2:.2f}" y="{HEIGHT - 14}" text-anchor="middle" class="axis-title">Month / Year</text>
      <text x="20" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 20 {top + plot_height / 2:.2f})">{esc(y_title)}</text>
    </svg>'''
    return chart_shell(
        chart_id,
        svg,
        legend(
            (label, PALETTE[index % len(PALETTE)])
            for index, (_, label) in enumerate(existing)
        ),
    )


def growth_svg(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    series_labels: dict[str, str] | None = None,
    currency: str = "USD",
) -> str:
    if frame.empty or "date" not in frame:
        return '<p class="muted">N/A</p>'
    labels = series_labels or {}
    columns = [column for column in frame if str(column).endswith("_balance")]
    keys = [column[: -len("_balance")] for column in columns]
    order = [name for name in (portfolio_order or []) if name in keys]
    if "benchmark" in keys:
        order.append("benchmark")
    order.extend(key for key in keys if key not in order)
    shaped = frame.copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"]).sort_values("date")
    series = [
        (f"{key}_balance", labels.get(key, key)) for key in order
    ]
    values = [
        float(value)
        for column, _ in series
        for value in pd.to_numeric(shaped[column], errors="coerce").dropna()
    ]
    if not values:
        return '<p class="muted">N/A</p>'
    y_min, y_max = min(values), max(values)
    step = nice_step(max(y_max - y_min, 1), 6)
    y_min = math.floor(y_min / step) * step
    y_max = math.ceil(y_max / step) * step
    if math.isclose(y_min, y_max):
        y_max += step
    left, right, top, bottom = 88, 24, 20, 74
    plot_width, plot_height = WIDTH - left - right, HEIGHT - top - bottom
    date_min, date_max = shaped["date"].iloc[0], shaped["date"].iloc[-1]
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return left + plot_width * (date - date_min).total_seconds() / date_span

    def y_for(value: float) -> float:
        return top + plot_height * (y_max - value) / max(y_max - y_min, 1e-12)

    y_grid: list[str] = []
    tick = y_min
    while tick <= y_max + step * 0.1 and len(y_grid) < 20:
        y = y_for(tick)
        y_grid.append(
            f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_width}" y2="{y:.2f}" class="grid-line" />'
            f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" class="axis-label y-tick-label">{esc(money(tick, currency))}</text>'
        )
        tick += step
    x_ticks = "".join(
        f'<text x="{x_for(date):.2f}" y="{top + plot_height + 26}" text-anchor="middle" '
        f'class="axis-label x-tick-label">{esc(date.strftime("%b %Y"))}</text>'
        for date in calendar_ticks(shaped["date"])
    )
    paths: list[str] = []
    points: list[str] = []
    for index, (column, label) in enumerate(series):
        color = PALETTE[index % len(PALETTE)]
        coords: list[tuple[float, float]] = []
        for _, row in shaped.iterrows():
            if not finite(row[column]):
                continue
            date, value = pd.Timestamp(row["date"]), float(row[column])
            coords.append((x_for(date), y_for(value)))
            tooltip = f"{date.date()} | {label}: {money(value, currency)}"
            points.append(
                f'<circle cx="{x_for(date):.2f}" cy="{y_for(value):.2f}" r="5" fill="{color}" '
                f'class="growth-point chart-mark" tabindex="0" data-tooltip="{esc(tooltip)}" aria-label="{esc(tooltip)}" />'
            )
        if coords:
            paths.append(
                f'<polyline fill="none" stroke="{color}" stroke-width="2.2" '
                f'points="{" ".join(f"{x:.2f},{y:.2f}" for x, y in coords)}" class="growth-series" />'
            )
    svg = f'''<svg class="growth-chart analysis-chart" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Portfolio balance growth over time">
      {''.join(y_grid)}{x_ticks}{''.join(paths)}{''.join(points)}
      <text x="{left + plot_width / 2:.2f}" y="{HEIGHT - 14}" text-anchor="middle" class="axis-title">Year</text>
      <text x="22" y="{top + plot_height / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 22 {top + plot_height / 2:.2f})">Portfolio Balance ({esc(currency_label(currency))})</text>
    </svg>'''
    return chart_shell(
        "portfolio-growth",
        svg,
        legend(
            (label, PALETTE[index % len(PALETTE)])
            for index, (_, label) in enumerate(series)
        ),
    ).replace(
        '<div class="chart-tooltip generic-tooltip"',
        '<div id="growth-tooltip" class="chart-tooltip generic-tooltip"',
        1,
    )


def performance_summary(
    frame: pd.DataFrame,
    benchmark: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
    currency: str = "USD",
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    units = rendered.get("unit", pd.Series(index=rendered.index, dtype=object))
    requested = portfolio_order or []
    value_columns = [name for name in requested if name in rendered]
    if "benchmark" in rendered:
        value_columns.append("benchmark")
    value_columns.extend(
        column for column in rendered.columns
        if column not in {"metric", "unit"} and column not in value_columns
    )
    for column in value_columns:
        rendered[column] = [
            pct(value) if units.loc[index] == "pct"
            else money(value, currency) if units.loc[index] == "balance"
            else ratio(value)
            for index, value in rendered[column].items()
        ]
    if not benchmark.empty and "portfolio" in benchmark:
        lookup = benchmark.set_index("portfolio")
        extra = []
        for label, key, kind in (
            ("Active Return", "active_return_pct", "pct"),
            ("Tracking Error", "tracking_error_pct", "pct"),
            ("Information Ratio", "information_ratio", "ratio"),
        ):
            row: dict[str, Any] = {"metric": label}
            for column in value_columns:
                value = lookup.loc[column, key] if column in lookup.index and key in lookup else None
                row[column] = "N/A" if column == "benchmark" or not finite(value) else pct(value) if kind == "pct" else ratio(value)
            extra.append(row)
        rendered = pd.concat(
            [rendered.drop(columns=["unit"], errors="ignore"), pd.DataFrame(extra)],
            ignore_index=True,
        )
    else:
        rendered = rendered.drop(columns=["unit"], errors="ignore")
    return table(
        rendered[["metric", *value_columns]].rename(
            columns={"metric": "Metric", "benchmark": benchmark_label or "Benchmark"}
        ),
        table_id="performance-summary",
    )


def trailing_returns_table(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
) -> str:
    if frame.empty or "portfolio" not in frame:
        return '<p class="muted">N/A</p>'
    selected: list[tuple[str, str]] = [("portfolio", "Portfolio")]
    used_labels = {"Portfolio"}
    for column, label in TRAILING_COLUMNS:
        if column in frame and label not in used_labels:
            selected.append((column, label))
            used_labels.add(label)
    rendered = frame[[column for column, _ in selected]].copy()
    ranking = {name: index for index, name in enumerate(portfolio_order or [])}
    rendered["_order"] = rendered["portfolio"].map(
        lambda value: len(ranking) if str(value) == "benchmark" else ranking.get(str(value), len(ranking) + 1)
    )
    rendered = rendered.sort_values("_order").drop(columns="_order")
    rendered["portfolio"] = rendered["portfolio"].map(
        lambda value: display_portfolio(value, benchmark_label)
    )
    for column, _ in selected:
        if column != "portfolio":
            rendered[column] = rendered[column].map(pct)
    return table(
        rendered.rename(columns={column: label for column, label in selected}),
        table_id="trailing-returns",
    )


def metrics_matrix(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
    fallback_performance: pd.DataFrame | None = None,
    currency: str = "USD",
) -> str:
    if not frame.empty and {"portfolio", "metric", "value"}.issubset(frame.columns):
        pivot = frame.pivot_table(index="metric", columns="portfolio", values="value", aggfunc="first")
    elif not frame.empty and "metric" in frame:
        pivot = frame.set_index("metric").drop(columns=["unit"], errors="ignore")
    elif fallback_performance is not None:
        return performance_summary(fallback_performance, pd.DataFrame(), portfolio_order, benchmark_label, currency)
    else:
        return '<p class="muted">N/A</p>'
    known = [metric for metric in METRIC_LABELS if metric in pivot.index]
    known.extend(metric for metric in pivot.index if metric not in known)
    pivot = pivot.reindex(known)
    requested = portfolio_order or []
    columns = [name for name in requested if name in pivot]
    if "benchmark" in pivot:
        columns.append("benchmark")
    columns.extend(column for column in pivot if column not in columns)
    formatted = pd.DataFrame({
        "Metric": [METRIC_LABELS.get(metric, human_column(str(metric))) for metric in pivot.index]
    })
    for column in columns:
        formatted[display_portfolio(column, benchmark_label)] = [
            fraction_pct(value) if metric in METRIC_PERCENT_FRACTION else ratio(value)
            for metric, value in pivot[column].items()
        ]
    return table(formatted, table_id="portfolio-metrics")


def annual_returns_chart(
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
            series.append((name, [float(v) if finite(v) else None for v in frame[column]]))
    if "benchmark_return_pct" in frame:
        series.append((benchmark_label or "Benchmark", [float(v) if finite(v) else None for v in frame["benchmark_return_pct"]]))
    categories = [str(int(value)) for value in frame["year"]]
    tooltips = [
        " | ".join(
            [categories[index]]
            + [f"{name}: {pct(values[index])}" for name, values in series if index < len(values) and finite(values[index])]
        )
        for index in range(len(categories))
    ]
    return grouped_bar_chart(categories, series, chart_id="annual-returns-chart", y_title="Annual Return %", tooltip_rows=tooltips)


def annual_asset_returns_table(frame: pd.DataFrame) -> str:
    return friendly_table(frame, fraction_columns={"return"}, table_id="annual-asset-returns-table")


def annual_asset_returns_chart(
    frame: pd.DataFrame,
    asset_names: dict[str, str] | None = None,
) -> str:
    if frame.empty or not {"year", "ticker", "return"}.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    asset_names = asset_names or {}
    pivot = frame.pivot(index="year", columns="ticker", values="return").sort_index()
    categories = [str(int(value)) for value in pivot.index]
    tickers = [ticker for ticker in asset_names if ticker in pivot.columns]
    tickers.extend(ticker for ticker in pivot.columns if ticker not in tickers)
    series = []
    for ticker in tickers:
        label = f"{asset_names.get(str(ticker), '')} ({ticker})" if asset_names.get(str(ticker), "").strip() else str(ticker)
        series.append((label, [float(v) * 100 if finite(v) else None for v in pivot[ticker]]))
    tooltips = [
        " | ".join(
            [categories[index]]
            + [f"{name}: {pct(values[index])}" for name, values in series if index < len(values) and finite(values[index])]
        )
        for index in range(len(categories))
    ]
    return grouped_bar_chart(categories, series, chart_id="annual-asset-returns-chart", y_title="Asset Return %", tooltip_rows=tooltips)


def correlations_table(frame: pd.DataFrame, benchmark_label: str | None) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    if "series" in rendered:
        rendered["series"] = rendered["series"].map(lambda value: display_portfolio(value, benchmark_label))
    headers = "".join(
        f'<th>{esc(benchmark_label or "Benchmark" if column == "benchmark" else column)}</th>'
        for column in rendered.columns
    )
    rows = []
    for _, row in rendered.iterrows():
        cells = []
        for column in rendered.columns:
            value = row[column]
            if column == "series":
                cells.append(f'<td class="identity-cell">{esc(value)}</td>')
            else:
                tone = "49,109,181" if finite(value) and float(value) >= 0 else "196,74,74"
                strength = min(abs(float(value)), 1.0) if finite(value) else 0
                cells.append(
                    f'<td class="heatmap-cell" data-correlation="{float(value):.8f}" '
                    f'style="background:rgba({tone},{0.08 + strength * 0.30:.3f})">{esc(correlation(value))}</td>'
                    if finite(value)
                    else '<td class="heatmap-cell">N/A</td>'
                )
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return f'<div class="table-wrap"><table id="correlations-heatmap" class="heatmap"><thead><tr>{headers}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def decomposition_table(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None,
    *,
    currency: str,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    identity_column = "asset" if "asset" in rendered else "ticker" if "ticker" in rendered else None
    if identity_column:
        rendered[identity_column] = rendered[identity_column].astype(str).str.removeprefix("contribution_")
    value_columns = [column for column in rendered if column != identity_column and column != "unit"]
    suffixes = ("_contribution_balance", "_risk_contribution_pct", "_contribution", "_risk_contribution")
    def identity(column: str) -> str:
        for suffix in suffixes:
            if str(column).endswith(suffix):
                return str(column)[: -len(suffix)]
        return str(column)
    ranking = {name: index for index, name in enumerate(portfolio_order or [])}
    value_columns.sort(key=lambda column: ranking.get(identity(str(column)), len(ranking)))
    selected = [column for column in [identity_column, *value_columns] if column]
    rendered = rendered[selected]
    labels = {column: identity(str(column)) for column in value_columns}
    money_columns = {column for column in value_columns if str(column).endswith(("_balance", "_contribution")) and not str(column).endswith("_pct")}
    return friendly_table(rendered, money_columns=money_columns, column_labels=labels, currency=currency)


def asset_performance_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    aliases = {
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
    raw_fraction_aliases = {
        "annualized_return": "Annualized Return",
        "annualized_volatility": "Standard Deviation",
        "best_year": "Best Year",
        "worst_year": "Worst Year",
        "max_drawdown": "Maximum Drawdown",
        "3m": "3M", "ytd": "YTD", "1y": "1Y", "3y": "3Y Annualized",
        "5y": "5Y Annualized", "10y": "10Y Annualized",
    }
    rendered = pd.DataFrame(index=frame.index)
    for column, label in aliases.items():
        if column in frame:
            values = frame[column]
            if column.endswith("_pct"):
                values = values.map(pct)
            elif column in {"sharpe_ratio", "sortino_ratio"}:
                values = values.map(ratio)
            rendered[label] = values
    for column, label in raw_fraction_aliases.items():
        if label not in rendered and column in frame:
            rendered[label] = frame[column].map(fraction_pct)
    ordered = list(aliases.values())
    rendered = rendered[[label for label in ordered if label in rendered]]
    return table(rendered, table_id="portfolio-asset-performance")


def drawdown_presentation(
    drawdown_series: pd.DataFrame,
    episodes: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    if drawdown_series.empty:
        return friendly_table(episodes, portfolio_order=portfolio_order, benchmark_label=benchmark_label)
    identities = [(name, f"{name}_drawdown_pct", name) for name in portfolio_order]
    if "benchmark_drawdown_pct" in drawdown_series:
        identities.append(("benchmark", "benchmark_drawdown_pct", benchmark_label or "Benchmark"))
    blocks = []
    for key, column, label in identities:
        if column not in drawdown_series:
            continue
        chart = time_line_chart(drawdown_series[["date", column]], [(column, label)], chart_id=f"drawdown-{key}", y_title="Drawdown %")
        episode = episodes[episodes["portfolio"].astype(str) == key].copy() if "portfolio" in episodes else pd.DataFrame()
        blocks.append(
            f'<div class="analysis-panel drawdown-panel" data-portfolio="{esc(label)}"><h3>{esc(label)}</h3>{chart}<h4>Drawdown Episodes</h4>{friendly_table(episode, benchmark_label=benchmark_label)}</div>'
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def rolling_returns_chart(
    frame: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    years: int,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    series: list[tuple[str, str]] = []
    for name in portfolio_order:
        column = f"{name}_annualized_return_pct"
        if column in frame:
            series.append((column, name))
    if "benchmark_annualized_return_pct" in frame:
        series.append(("benchmark_annualized_return_pct", benchmark_label or "Benchmark"))
    return time_line_chart(frame, series, chart_id=f"rolling-{years}y-annualized-return", y_title="Annualized Return %")


def _annual_active_frame(frame: pd.DataFrame, portfolio_order: list[str]) -> pd.DataFrame:
    if frame.empty or not {"portfolio", "date", "annual_active_return"}.issubset(frame):
        return pd.DataFrame()
    shaped = frame[["portfolio", "date", "annual_active_return"]].copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"])
    shaped["year"] = shaped["date"].dt.year
    latest = shaped.sort_values("date").groupby(["year", "portfolio"], as_index=False).tail(1)
    pivot = latest.pivot(index="year", columns="portfolio", values="annual_active_return").sort_index()
    columns = [name for name in portfolio_order if name in pivot]
    columns.extend(column for column in pivot if column not in columns)
    return pivot.reindex(columns=columns).reset_index()


def _active_contribution(frame: pd.DataFrame, portfolio_order: list[str], asset_names: dict[str, str]) -> str:
    required = {"date", "portfolio", "ticker", "cumulative_active_contribution_pct"}
    if frame.empty or not required.issubset(frame):
        return '<p class="muted">N/A</p>'
    blocks = []
    for portfolio in portfolio_order:
        part = frame[frame["portfolio"].astype(str) == portfolio]
        if part.empty:
            continue
        pivot = part.pivot(index="date", columns="ticker", values="cumulative_active_contribution_pct").reset_index()
        series = []
        for ticker in pivot.columns:
            if ticker == "date":
                continue
            label = f"{asset_names.get(str(ticker), '')} ({ticker})" if asset_names.get(str(ticker), "").strip() else str(ticker)
            series.append((ticker, label))
        blocks.append(
            f'<div class="analysis-panel active-contribution-panel" data-portfolio="{esc(portfolio)}"><h4>{esc(portfolio)}</h4>{time_line_chart(pivot, series, chart_id=f"active-contribution-{portfolio}", y_title="Cumulative Active Contribution %")}</div>'
        )
    return "".join(blocks) if blocks else '<p class="muted">N/A</p>'


def _rolling_active_risk(frame: pd.DataFrame, portfolio: str) -> str:
    if frame.empty or "portfolio" not in frame:
        return '<p class="muted">N/A</p>'
    part = frame[frame["portfolio"].astype(str) == portfolio].copy()
    if part.empty or not {"date", "rolling_active_return_pct", "rolling_tracking_error_pct"}.issubset(part):
        return '<p class="muted">N/A</p>'
    part["date"] = pd.to_datetime(part["date"], errors="coerce")
    part = part.dropna(subset=["date", "rolling_active_return_pct", "rolling_tracking_error_pct"]).sort_values("date")
    if part.empty:
        return '<p class="muted">N/A</p>'
    dates = [date.strftime("%Y-%m") for date in part["date"]]
    active = [float(value) for value in part["rolling_active_return_pct"]]
    tracking = [float(value) for value in part["rolling_tracking_error_pct"]]
    # Presentation-only combo chart: canonical active/tracking series are already persisted.
    categories = dates
    bars = grouped_bar_chart(
        categories,
        [("Active Return", active)],
        chart_id=f"rolling-active-bars-{portfolio}",
        y_title="Active Return %",
        x_title="Month / Year",
    )
    line_frame = pd.DataFrame({"date": part["date"], "tracking": tracking})
    line = time_line_chart(line_frame, [("tracking", "Tracking Error")], chart_id=f"rolling-active-risk-{portfolio}", y_title="Tracking Error %")
    return f'<div class="analysis-panel rolling-active-risk-panel" data-portfolio="{esc(portfolio)}"><h4>Rolling Active Return / Risk · 36 months</h4><p class="muted">Active Return % · Tracking Error %</p>{bars}{line}</div>'


def _up_down_table(frame: pd.DataFrame, portfolio: str) -> str:
    part = frame[frame["portfolio"].astype(str) == portfolio].copy() if "portfolio" in frame else pd.DataFrame()
    if part.empty:
        return '<p class="muted">N/A</p>'
    aliases = {
        "market_type": "Market Type",
        "above_benchmark_count": "Above Benchmark Count",
        "below_benchmark_count": "Below Benchmark Count",
        "total_count": "Total",
        "occurrences": "Total",
        "pct_above_benchmark": "% Above Benchmark",
        "above_active_return_pct": "Average Active Return Above",
        "below_active_return_pct": "Average Active Return Below",
        "overall_active_return_pct": "Average Active Return Total",
        "active_return_pct": "Average Active Return Total",
    }
    selected = []
    used = set()
    for column, label in aliases.items():
        if column in part and label not in used:
            selected.append(column)
            used.add(label)
    rendered = part[selected].copy()
    for column in rendered:
        if column.endswith("_pct") or column == "pct_above_benchmark":
            rendered[column] = rendered[column].map(pct)
    return table(rendered.rename(columns=aliases))


def _up_down_chart(observations: pd.DataFrame, portfolio: str) -> str:
    part = observations[observations["portfolio"].astype(str) == portfolio].copy() if "portfolio" in observations else pd.DataFrame()
    if part.empty or not {"benchmark_return_pct", "portfolio_return_pct"}.issubset(part):
        return '<p class="muted">N/A</p>'
    part = part.sort_values("benchmark_return_pct").reset_index(drop=True)
    group_count = min(20, len(part))
    groups = np.array_split(np.arange(len(part)), group_count)
    labels: list[str] = []
    benchmark_values: list[float] = []
    portfolio_values: list[float] = []
    for index, group in enumerate(groups, start=1):
        if len(group) == 0:
            continue
        selected = part.iloc[group]
        labels.append(str(index))
        benchmark_values.append(float(selected["benchmark_return_pct"].mean()))
        portfolio_values.append(float(selected["portfolio_return_pct"].mean()))
    return grouped_bar_chart(
        labels,
        [("Portfolio", portfolio_values), ("Benchmark", benchmark_values)],
        chart_id=f"return-vs-benchmark-{portfolio}",
        y_title="Average Monthly Return %",
        x_title="Benchmark Return Quantile Group",
    )


def active_returns_presentation(
    active_returns: pd.DataFrame,
    active_contribution: pd.DataFrame,
    benchmark_summary: pd.DataFrame,
    up_down: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
    asset_names: dict[str, str] | None = None,
    up_down_observations: pd.DataFrame | None = None,
) -> str:
    asset_names = asset_names or {}
    annual = _annual_active_frame(active_returns, portfolio_order)
    annual_chart = '<p class="muted">N/A</p>'
    annual_table = '<p class="muted">N/A</p>'
    if not annual.empty:
        categories = [str(int(value)) for value in annual["year"]]
        series = [
            (name, [float(value) * 100 if finite(value) else None for value in annual[name]])
            for name in annual.columns if name != "year"
        ]
        annual_chart = grouped_bar_chart(categories, series, chart_id="annual-active-return-chart", y_title="Active Return %")
        rendered = annual.copy()
        for column in rendered:
            if column != "year":
                rendered[column] = rendered[column].map(fraction_pct)
        annual_table = table(rendered.rename(columns={"year": "Year"}))
    summary = friendly_table(
        benchmark_summary,
        portfolio_order=portfolio_order,
        column_labels={
            "active_return_pct": "Active Return",
            "tracking_error_pct": "Tracking Error",
            "information_ratio": "Information Ratio",
        },
    )
    contribution = _active_contribution(active_contribution, portfolio_order, asset_names)
    rolling = "".join(_rolling_active_risk(active_returns, portfolio) for portfolio in portfolio_order)
    observations = up_down_observations if up_down_observations is not None else pd.DataFrame()
    up_down_blocks = []
    for portfolio in portfolio_order:
        up_down_blocks.append(
            f'<div class="analysis-panel up-down-panel" data-portfolio="{esc(portfolio)}"><h4>{esc(portfolio)}</h4>{_up_down_table(up_down, portfolio)}<h5>Return vs. Benchmark</h5>{_up_down_chart(observations, portfolio)}</div>'
        )
    return (
        '<h3>Benchmark Summary</h3>' + summary
        + '<h3>Annual Active Return</h3>' + annual_chart + annual_table
        + '<h3>Active Return Contribution</h3>' + contribution
        + '<h3>Rolling Active Return / Risk</h3>' + rolling
        + '<h3>Up / Down Market Performance</h3>' + "".join(up_down_blocks)
    )
