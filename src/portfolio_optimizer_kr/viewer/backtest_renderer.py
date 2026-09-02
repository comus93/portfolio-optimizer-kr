from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


_DEF_WIDTH = 1060
_DEF_HEIGHT = 500

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


def _portfolio_order(frame: pd.DataFrame, requested: list[str]) -> list[str]:
    available: set[str] = set()
    if "portfolio" in frame.columns:
        available.update(str(value) for value in frame["portfolio"].dropna())
    else:
        available.update(str(column) for column in frame.columns)
    ordered = [name for name in requested if name in available]
    for name in available:
        if name not in ordered and name != "benchmark":
            ordered.append(name)
    return ordered


def _display_portfolio(value: Any, benchmark_label: str | None) -> str:
    text = str(value)
    return (benchmark_label or "Benchmark") if text == "benchmark" else text


def _human_column(column: str, benchmark_label: str | None = None) -> str:
    if column == "benchmark":
        return benchmark_label or "Benchmark"
    if column == "date":
        return "Date"
    if column == "year":
        return "Year"
    if column == "portfolio":
        return "Portfolio"
    if column == "ticker":
        return "Ticker"
    if column == "rank":
        return "Rank"
    if column == "start":
        return "Start"
    if column == "bottom":
        return "Bottom"
    if column == "recovery":
        return "Recovery"
    if column == "duration_months":
        return "Duration (Months)"
    label = column
    if label.endswith("_pct"):
        label = label[:-4]
    label = label.replace("_", " ").strip()
    return " ".join(word.capitalize() for word in label.split())


def _friendly_table(
    frame: pd.DataFrame,
    *,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
    fraction_columns: set[str] | None = None,
    table_id: str | None = None,
) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    rendered = frame.copy()
    fraction_columns = fraction_columns or set()
    if "portfolio" in rendered.columns:
        order = portfolio_order or []
        ranking = {name: index for index, name in enumerate(order)}
        benchmark_rank = len(order)
        rendered["_order"] = rendered["portfolio"].map(
            lambda value: benchmark_rank
            if str(value) == "benchmark"
            else ranking.get(str(value), benchmark_rank + 1)
        )
        sort_columns = ["_order"] + (["date"] if "date" in rendered.columns else [])
        rendered = rendered.sort_values(sort_columns).drop(columns=["_order"])
        rendered["portfolio"] = rendered["portfolio"].map(
            lambda value: _display_portfolio(value, benchmark_label)
        )
    for column in rendered.columns:
        if column in fraction_columns:
            rendered[column] = rendered[column].map(_fraction_pct)
        elif column.endswith("_pct"):
            rendered[column] = rendered[column].map(_pct)
        elif column == "date":
            rendered[column] = pd.to_datetime(rendered[column], errors="coerce").map(
                lambda value: value.date().isoformat() if not pd.isna(value) else "N/A"
            )
    rendered = rendered.rename(
        columns={column: _human_column(column, benchmark_label) for column in rendered.columns}
    )
    return _table(rendered, table_id=table_id)


def _allocation_matrix(frame: pd.DataFrame, portfolio_order: list[str] | None = None) -> str:
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
        if column == "asset":
            continue
        pivot[column] = pivot[column].map(_pct)
    pivot = pivot.rename(columns={"asset": "Asset"})
    return _table(pivot, table_id="allocation-matrix")


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
    start = pd.Timestamp(dates.iloc[0])
    end = pd.Timestamp(dates.iloc[-1])
    months = max(1, (end.year - start.year) * 12 + end.month - start.month)
    if months <= 120:
        anchor_months = {1, 7}
        year_step = 1
    elif months <= 240:
        anchor_months = {1}
        year_step = 1
    elif months <= 480:
        anchor_months = {1}
        year_step = 2
    else:
        anchor_months = {1}
        year_step = 5
    base_year = start.year
    selected = [
        pd.Timestamp(value)
        for value in dates
        if pd.Timestamp(value).month in anchor_months
        and (pd.Timestamp(value).year - base_year) % year_step == 0
    ]
    if len(selected) < 2:
        selected = [pd.Timestamp(dates.iloc[0]), pd.Timestamp(dates.iloc[-1])]
    return selected


def _growth_svg(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    series_labels: dict[str, str] | None = None,
) -> str:
    if frame.empty or "date" not in frame:
        return '<p class="muted">N/A</p>'
    series_labels = series_labels or {}
    all_series = [column for column in frame.columns if column.endswith("_balance")]
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

    values = pd.to_numeric(shaped[series_columns].stack(), errors="coerce").dropna()
    if values.empty:
        return '<p class="muted">N/A</p>'
    data_min = float(values.min())
    data_max = float(values.max())
    if math.isclose(data_min, data_max):
        padding = max(abs(data_max) * 0.05, 1.0)
        data_min -= padding
        data_max += padding

    step = _nice_step(data_max - data_min, target_ticks=6)
    y_min = math.floor(data_min / step) * step
    y_max = math.ceil(data_max / step) * step
    if math.isclose(y_min, y_max):
        y_max = y_min + step
    y_ticks: list[float] = []
    value = y_min
    while value <= y_max + step * 0.25 and len(y_ticks) < 12:
        y_ticks.append(value)
        value += step

    margin_left, margin_right, margin_top, margin_bottom = 88, 24, 20, 74
    plot_w = _DEF_WIDTH - margin_left - margin_right
    plot_h = _DEF_HEIGHT - margin_top - margin_bottom
    denom = max(y_max - y_min, 1e-12)

    date_min = pd.Timestamp(shaped["date"].iloc[0])
    date_max = pd.Timestamp(shaped["date"].iloc[-1])
    date_span = max((date_max - date_min).total_seconds(), 1.0)

    def x_for(date: pd.Timestamp) -> float:
        return margin_left + plot_w * (pd.Timestamp(date) - date_min).total_seconds() / date_span

    grid: list[str] = []
    y_labels: list[str] = []
    for tick in y_ticks:
        y = margin_top + plot_h * (y_max - tick) / denom
        grid.append(
            f'<line x1="{margin_left}" y1="{y:.2f}" x2="{margin_left + plot_w}" '
            f'y2="{y:.2f}" class="grid-line" />'
        )
        y_labels.append(
            f'<text x="{margin_left - 12}" y="{y + 4:.2f}" text-anchor="end" '
            f'class="axis-label y-tick-label">{_esc(_money(tick))}</text>'
        )

    x_ticks: list[str] = []
    for date in _calendar_ticks(shaped["date"]):
        x = x_for(date)
        label = date.strftime("%b %Y")
        x_ticks.append(
            f'<line x1="{x:.2f}" y1="{margin_top + plot_h}" x2="{x:.2f}" '
            f'y2="{margin_top + plot_h + 8}" class="axis" />'
            f'<text x="{x:.2f}" y="{margin_top + plot_h + 26}" text-anchor="middle" '
            f'class="axis-label x-tick-label">{_esc(label)}</text>'
        )

    palette = ["#1200FF", "#50E2B0", "#85ACD0", "#2D7186"]
    paths: list[str] = []
    points: list[str] = []
    legend: list[str] = []
    for idx, column in enumerate(series_columns):
        key = column[: -len("_balance")]
        label = series_labels.get(key, key)
        color = palette[idx % len(palette)]
        coords: list[tuple[float, float, str, float]] = []
        for _, row in shaped.iterrows():
            raw_value = row[column]
            if not _finite(raw_value):
                continue
            date = pd.Timestamp(row["date"])
            x = x_for(date)
            y = margin_top + plot_h * (y_max - float(raw_value)) / denom
            coords.append((x, y, str(date.date()), float(raw_value)))
        if coords:
            polyline = " ".join(f"{x:.2f},{y:.2f}" for x, y, _, _ in coords)
            paths.append(
                f'<polyline fill="none" stroke="{color}" stroke-width="2.2" '
                f'points="{polyline}" class="growth-series" data-series="{_esc(label)}" />'
            )
            for x, y, date, raw_value in coords:
                title = _esc(f"{date} | {label}: ${raw_value:,.0f}")
                points.append(
                    f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5" fill="{color}" '
                    f'class="growth-point" tabindex="0" aria-label="{title}" '
                    f'data-date="{_esc(date)}" data-series="{_esc(label)}" '
                    f'data-balance="{raw_value:.10f}"><title>{title}</title></circle>'
                )
        legend.append(
            f'<span class="legend-item"><i style="background:{color}"></i>{_esc(label)}</span>'
        )

    return f"""
    <div class="legend" aria-label="Portfolio series legend">{''.join(legend)}</div>
    <div class="chart-wrap growth-chart-wrap">
      <div id="growth-tooltip" class="chart-tooltip" role="status" aria-live="polite"></div>
      <svg class="growth-chart" viewBox="0 0 {_DEF_WIDTH} {_DEF_HEIGHT}" role="img" aria-label="Portfolio balance growth over time">
        {''.join(grid)}
        <line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" class="axis" />
        <line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" class="axis" />
        {''.join(y_labels)}
        {''.join(x_ticks)}
        <text x="{margin_left + plot_w / 2:.2f}" y="{_DEF_HEIGHT - 14}" text-anchor="middle" class="axis-title">Year</text>
        <text x="22" y="{margin_top + plot_h / 2:.2f}" text-anchor="middle" class="axis-title" transform="rotate(-90 22 {margin_top + plot_h / 2:.2f})">Portfolio Balance ($)</text>
        {''.join(paths)}
        {''.join(points)}
      </svg>
    </div>
    <p class="muted">Hover 또는 keyboard focus로 날짜, portfolio identity, balance를 확인할 수 있다.</p>
    """


def _performance_summary(
    frame: pd.DataFrame,
    benchmark: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
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
        for idx, value in rendered[column].items():
            kind = unit.loc[idx] if idx in unit.index else None
            if kind == "pct":
                formatted.append(_pct(value))
            elif kind == "balance":
                formatted.append(_money(value))
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
                if column == "benchmark" or column not in lookup.index or key not in lookup.columns:
                    row[column] = "N/A"
                    continue
                raw_value = lookup.loc[column, key]
                row[column] = _pct(raw_value) if unit_name == "pct" else _ratio(raw_value)
            extra_rows.append(row)
        rendered = pd.concat(
            [rendered.drop(columns=["unit"], errors="ignore"), pd.DataFrame(extra_rows)],
            ignore_index=True,
        )
    else:
        rendered = rendered.drop(columns=["unit"], errors="ignore")

    rendered = rendered[["metric", *value_columns]]
    rendered = rendered.rename(
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
    columns = [column for column, _ in _TRAILING_COLUMNS if column in frame.columns]
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
    rename = {column: label for column, label in _TRAILING_COLUMNS}
    rendered = rendered.rename(columns=rename)
    return _table(rendered, table_id="trailing-returns")


def _metrics_matrix(
    frame: pd.DataFrame,
    portfolio_order: list[str] | None = None,
    benchmark_label: str | None = None,
) -> str:
    if frame.empty or not {"portfolio", "metric", "value"}.issubset(frame.columns):
        return _friendly_table(
            frame,
            portfolio_order=portfolio_order,
            benchmark_label=benchmark_label,
        )
    pivot = frame.pivot_table(index="metric", columns="portfolio", values="value", aggfunc="first")
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
            _fraction_pct(value) if metric in _METRIC_PERCENT_FRACTION else _ratio(value)
            for metric, value in pivot[column].items()
        ]
    formatted.insert(
        0,
        "Metric",
        [_METRIC_LABELS.get(metric, _human_column(metric)) for metric in pivot.index],
    )
    formatted = formatted.reset_index(drop=True)
    formatted = formatted.rename(columns={"benchmark": benchmark_label or "Benchmark"})
    return _table(formatted, table_id="portfolio-metrics")


def _benchmark_summary_table(frame: pd.DataFrame, portfolio_order: list[str]) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    columns = ["portfolio", "active_return_pct", "tracking_error_pct", "information_ratio"]
    rendered = frame[[column for column in columns if column in frame.columns]].copy()
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
    rendered = rendered.rename(
        columns={
            "portfolio": "Portfolio",
            "active_return_pct": "Active Return",
            "tracking_error_pct": "Tracking Error",
            "information_ratio": "Information Ratio",
        }
    )
    return _table(rendered)


def _annual_active_return_table(frame: pd.DataFrame, portfolio_order: list[str]) -> str:
    required = {"portfolio", "date", "annual_active_return"}
    if frame.empty or not required.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    shaped = frame[["portfolio", "date", "annual_active_return"]].copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"])
    shaped["Year"] = shaped["date"].dt.year
    latest = shaped.sort_values("date").groupby(["Year", "portfolio"], as_index=False).tail(1)
    pivot = latest.pivot(index="Year", columns="portfolio", values="annual_active_return")
    columns = [name for name in portfolio_order if name in pivot.columns]
    columns.extend(column for column in pivot.columns if column not in columns)
    pivot = pivot.reindex(columns=columns).reset_index()
    for column in columns:
        pivot[column] = pivot[column].map(_fraction_pct)
    return _table(pivot)


def _active_contribution_latest(frame: pd.DataFrame, portfolio_order: list[str]) -> str:
    required = {"date", "portfolio", "ticker", "cumulative_active_contribution_pct"}
    if frame.empty or not required.issubset(frame.columns):
        return '<p class="muted">N/A</p>'
    shaped = frame[["date", "portfolio", "ticker", "cumulative_active_contribution_pct"]].copy()
    shaped["date"] = pd.to_datetime(shaped["date"], errors="coerce")
    shaped = shaped.dropna(subset=["date"])
    latest = (
        shaped.sort_values("date")
        .groupby(["portfolio", "ticker"], as_index=False)
        .tail(1)
        .copy()
    )
    ranking = {name: index for index, name in enumerate(portfolio_order)}
    latest["_order"] = latest["portfolio"].map(
        lambda value: ranking.get(str(value), len(ranking))
    )
    latest = latest.sort_values(["_order", "portfolio", "ticker"]).drop(
        columns=["_order", "date"]
    )
    latest["cumulative_active_contribution_pct"] = latest[
        "cumulative_active_contribution_pct"
    ].map(_pct)
    latest = latest.rename(
        columns={
            "portfolio": "Portfolio",
            "ticker": "Asset",
            "cumulative_active_contribution_pct": "Cumulative Active Contribution",
        }
    )
    return _table(latest)


def _up_down_table(frame: pd.DataFrame, portfolio_order: list[str]) -> str:
    if frame.empty:
        return '<p class="muted">N/A</p>'
    columns = [
        "portfolio",
        "market_type",
        "portfolio_return",
        "benchmark_return",
        "active_return",
        "occurrences",
    ]
    rendered = frame[[column for column in columns if column in frame.columns]].copy()
    ranking = {name: index for index, name in enumerate(portfolio_order)}
    rendered["_order"] = rendered["portfolio"].map(
        lambda value: ranking.get(str(value), len(ranking))
    )
    market_rank = {"up": 0, "down": 1}
    rendered["_market_order"] = rendered["market_type"].map(
        lambda value: market_rank.get(str(value).lower(), 2)
    )
    rendered = rendered.sort_values(["_order", "_market_order"]).drop(
        columns=["_order", "_market_order"]
    )
    if "market_type" in rendered:
        rendered["market_type"] = rendered["market_type"].map(lambda value: str(value).title())
    for column in {"portfolio_return", "benchmark_return", "active_return"} & set(
        rendered.columns
    ):
        rendered[column] = rendered[column].map(_fraction_pct)
    rendered = rendered.rename(
        columns={
            "portfolio": "Portfolio",
            "market_type": "Market Type",
            "portfolio_return": "Portfolio Return",
            "benchmark_return": "Benchmark Return",
            "active_return": "Active Return",
            "occurrences": "Occurrences",
        }
    )
    return _table(rendered)


def _active_returns_presentation(
    active_returns: pd.DataFrame,
    active_contribution: pd.DataFrame,
    benchmark: pd.DataFrame,
    up_down: pd.DataFrame,
    portfolio_order: list[str],
    benchmark_label: str | None,
) -> str:
    return f"""
      <h3>Benchmark Summary</h3>{_benchmark_summary_table(benchmark, portfolio_order)}
      <h3>Annual Active Return</h3>{_annual_active_return_table(active_returns, portfolio_order)}
      <h3>Active Return Contribution</h3>
      <p class="muted">Latest cumulative contribution by portfolio and asset.</p>
      {_active_contribution_latest(active_contribution, portfolio_order)}
      <h3>Up / Down Market Performance</h3>{_up_down_table(up_down, portfolio_order)}
    """


def _period_note(configuration: dict[str, Any], coverage: dict[str, Any]) -> str:
    period = configuration.get("analysis_period", {}) or {}
    requested_start = str(period.get("start") or "")
    requested_end = str(period.get("end") or "")
    effective_start = str(coverage.get("start") or "")
    effective_end = str(coverage.get("end") or "")
    if requested_start and requested_end and (
        requested_start[:7] != effective_start[:7] or requested_end[:7] != effective_end[:7]
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
    portfolio_metrics = _read_csv(review / "portfolio_metrics.csv")
    annual_assets = _read_csv(review / "annual_asset_returns.csv")
    active_returns = _read_csv(review / "active_returns.csv")
    active_contribution = _read_csv(review / "active_return_contribution.csv")
    up_down = _read_csv(review / "up_down_market_performance.csv")

    period = configuration.get("analysis_period", {}) or {}
    benchmark_cfg = configuration.get("benchmark")
    benchmark_label = (
        benchmark_cfg.get("name") or benchmark_cfg.get("symbol")
        if isinstance(benchmark_cfg, dict)
        else None
    )
    portfolio_order = list((result.get("portfolio_definitions") or {}).keys())
    coverage = result.get("data_coverage", {}).get("backtest_monthly_returns", {}) or {}
    alignment = "Yes" if configuration.get("calendar_aligned") else "No"
    effective_label = f"{coverage.get('start')} - {coverage.get('end')}"
    series_labels = {"benchmark": benchmark_label or "Benchmark"}

    nav_sections = [("overview", "Summary")]
    if not benchmark.empty:
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
    nav = "".join(f'<a href="#{section}">{_esc(label)}</a>' for section, label in nav_sections)

    active_section = ""
    if not benchmark.empty:
        active_section = f"""
        <section id="activeReturns" class="result-section benchmark-relative">
          <h2>Active Returns</h2>
          {_active_returns_presentation(
              active_returns,
              active_contribution,
              benchmark,
              up_down,
              portfolio_order,
              benchmark_label,
          )}
        </section>
        """

    document = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Portfolio Backtest Report</title>
<style>
:root {{ color-scheme: light; font-family: Roboto, "Work Sans", "Helvetica Neue", Arial, sans-serif; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#fff; color:#333; }}
.topbar {{ border-bottom:1px solid #d8dee8; background:#fff; padding:14px 24px; font-weight:600; font-size:20px; }}
.shell {{ display:grid; grid-template-columns:190px minmax(0,1fr); max-width:1320px; margin:0 auto; }}
.sidebar {{ border-right:1px solid #e2e8f0; padding:22px 14px; min-height:100vh; position:sticky; top:0; align-self:start; }}
.sidebar a {{ display:block; color:#374151; text-decoration:none; padding:10px 9px; border-radius:5px; font-size:14px; }}
.sidebar a:hover, .sidebar a:focus {{ background:#eef4ff; color:#184f9d; outline:none; }}
main {{ min-width:0; padding:26px 32px 72px; }}
.result-header {{ margin:0 0 12px; color:#1f2937; font-size:25px; font-weight:500; }}
.coverage-note {{ border-left:3px solid #316db5; padding:8px 12px; margin:0 0 20px; background:#f8fbff; font-size:13px; }}
.result-section {{ border:1px solid #e0e5ec; padding:22px; margin:0 0 24px; background:#fff; }}
.result-section h2 {{ margin:0 0 18px; font-size:21px; color:#1d5c9b; font-weight:500; }}
.result-section h3 {{ margin:26px 0 10px; font-size:16px; font-weight:500; color:#374151; }}
.meta {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:1px; background:#e5e7eb; border:1px solid #e5e7eb; margin-bottom:20px; }}
.meta div {{ background:#fff; padding:10px 12px; font-size:13px; }}
.meta b {{ display:block; font-size:11px; color:#6b7280; margin-bottom:4px; text-transform:uppercase; letter-spacing:.02em; }}
.table-wrap {{ overflow-x:auto; border:1px solid #e2e8f0; }}
table {{ border-collapse:collapse; width:100%; min-width:640px; }}
th,td {{ padding:8px 10px; border-bottom:1px solid #e8ecf1; text-align:right; font-size:13px; }}
th:first-child,td:first-child {{ text-align:left; }}
th {{ background:#f5f7fa; color:#374151; font-weight:600; }}
tbody tr:nth-child(even) {{ background:#fafbfc; }}
.legend {{ display:flex; flex-wrap:wrap; gap:18px; justify-content:center; margin:8px 0 10px; }}
.legend-item {{ display:inline-flex; align-items:center; gap:6px; font-size:12px; }}
.legend-item i {{ width:18px; height:3px; display:inline-block; }}
.chart-wrap {{ overflow-x:auto; position:relative; }}
.growth-chart {{ width:100%; min-width:900px; height:auto; display:block; }}
.axis {{ stroke:#ccd6eb; stroke-width:1; }}
.grid-line {{ stroke:#e6e6e6; stroke-width:1; }}
.axis-label {{ font-size:11px; fill:#333; }}
.axis-title {{ font-size:12px; fill:#333; }}
.growth-point {{ opacity:0; cursor:crosshair; }}
.growth-point:hover, .growth-point:focus {{ opacity:1; stroke:#fff; stroke-width:2; outline:none; }}
.chart-tooltip {{ display:none; position:absolute; z-index:4; pointer-events:none; background:rgba(255,255,255,.98); border:1px solid #9ca3af; box-shadow:0 3px 12px rgba(0,0,0,.12); padding:8px 10px; font-size:12px; border-radius:3px; white-space:nowrap; }}
.muted {{ color:#6b7280; font-size:12px; }}
.summary-block {{ margin-top:24px; }}
.summary-block > h3 {{ color:#1d5c9b; font-size:17px; }}
@media (max-width:800px) {{
  .shell {{ display:block; }}
  .sidebar {{ min-height:0; position:sticky; top:0; z-index:5; display:flex; gap:4px; overflow-x:auto; border-right:0; border-bottom:1px solid #e2e8f0; background:#fff; padding:8px 10px; }}
  .sidebar a {{ white-space:nowrap; padding:7px 9px; }}
  main {{ padding:18px 12px 50px; }}
  .result-section {{ padding:14px; }}
}}
</style>
</head>
<body>
<div class="topbar">Portfolio Research · Backtest</div>
<div class="shell">
<nav class="sidebar" aria-label="Backtest result sections">{nav}</nav>
<main>
<h1 class="result-header">Portfolio Analysis Results ({_esc(effective_label)})</h1>
{_period_note(configuration, coverage)}
<section id="overview" class="result-section">
  <h2>Summary</h2>
  <div class="meta">
    <div><b>Run ID</b>{_esc(configuration.get('run_id'))}</div>
    <div><b>Time Period</b>{_esc(configuration.get('time_period_mode'))}</div>
    <div><b>Requested</b>{_esc(period.get('start'))} → {_esc(period.get('end'))}</div>
    <div><b>Effective</b>{_esc(coverage.get('start'))} → {_esc(coverage.get('end'))} ({_esc(coverage.get('observations'))} months)</div>
    <div><b>Initial Amount</b>{_money(configuration.get('initial_balance'))}</div>
    <div><b>Benchmark</b>{_esc(benchmark_label or 'None')}</div>
    <div><b>Rebalancing</b>{_esc(configuration.get('rebalancing_period'))}</div>
    <div><b>Calendar Aligned</b>{alignment}</div>
    <div><b>Return Semantics</b>{_esc(configuration.get('return_semantics'))}</div>
  </div>
  <div id="allocation" class="summary-block"><h3>Target Allocation</h3>{_allocation_matrix(allocations, portfolio_order)}</div>
  <div id="performance" class="summary-block"><h3>Performance Summary</h3>{_performance_summary(performance, benchmark, portfolio_order, benchmark_label)}</div>
  <div id="growth" class="summary-block"><h3>Portfolio Growth</h3>{_growth_svg(growth, portfolio_order, series_labels)}</div>
  <div id="trailing" class="summary-block"><h3>Trailing Returns</h3>{_trailing_returns_table(trailing, portfolio_order, benchmark_label)}</div>
</section>
{active_section}
<section id="metrics" class="result-section"><h2>Metrics</h2>{_metrics_matrix(portfolio_metrics, portfolio_order, benchmark_label)}</section>
<section id="annualReturns" class="result-section"><h2>Annual Returns</h2>{_friendly_table(annual, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
<section id="monthlyReturns" class="result-section"><h2>Monthly Returns</h2>{_friendly_table(monthly, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
<section id="drawdowns" class="result-section"><h2>Drawdowns</h2>{_friendly_table(drawdowns, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
<section id="assets" class="result-section">
  <h2>Assets</h2>
  <h3>Annual Asset Returns</h3>{_friendly_table(annual_assets, benchmark_label=benchmark_label)}
  <h3>Correlations</h3>{_friendly_table(correlations, benchmark_label=benchmark_label)}
  <h3>Return Decomposition</h3>{_friendly_table(returns_decomp, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}
  <h3>Risk Decomposition</h3>{_friendly_table(risk_decomp, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}
</section>
<section id="rollingReturns" class="result-section"><h2>Rolling Returns</h2><h3>3 Year</h3>{_friendly_table(rolling3, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}<h3>5 Year</h3>{_friendly_table(rolling5, portfolio_order=portfolio_order, benchmark_label=benchmark_label)}</section>
</main>
</div>
<script>
(() => {{
  const tooltip = document.getElementById('growth-tooltip');
  const host = document.querySelector('.growth-chart-wrap');
  if (!tooltip || !host) return;
  const formatMoney = value => Number(value).toLocaleString(undefined, {{style:'currency', currency:'USD', maximumFractionDigits:0}});
  const show = (point, event) => {{
    const date = point.dataset.date || '';
    const series = point.dataset.series || '';
    const value = point.dataset.balance;
    tooltip.innerHTML = `<b>${{date}}</b><br>${{series}}: ${{formatMoney(value)}}`;
    tooltip.style.display = 'block';
    const hostRect = host.getBoundingClientRect();
    const pointRect = point.getBoundingClientRect();
    const clientX = event?.clientX || (pointRect.left + pointRect.width / 2);
    const clientY = event?.clientY || pointRect.top;
    tooltip.style.left = `${{Math.max(6, clientX - hostRect.left + host.scrollLeft + 12)}}px`;
    tooltip.style.top = `${{Math.max(6, clientY - hostRect.top + host.scrollTop - 44)}}px`;
  }};
  const hide = () => {{ tooltip.style.display = 'none'; }};
  document.querySelectorAll('.growth-point').forEach(point => {{
    point.addEventListener('mouseenter', event => show(point, event));
    point.addEventListener('mousemove', event => show(point, event));
    point.addEventListener('mouseleave', hide);
    point.addEventListener('focus', event => show(point, event));
    point.addEventListener('blur', hide);
  }});
}})();
</script>
</body>
</html>
"""
    target = Path(output_path) if output_path is not None else root / "report.html"
    target.write_text(document, encoding="utf-8")
    return target
