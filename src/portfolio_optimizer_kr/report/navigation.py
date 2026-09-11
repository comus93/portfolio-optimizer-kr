from __future__ import annotations

import csv
import json
import re
import warnings
from pathlib import Path
from typing import Any, Mapping

import yaml


_MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}

_BACKTEST_METRICS = (
    "CAGR",
    "Annualized Return",
    "Standard Deviation",
    "Maximum Drawdown",
    "Sharpe Ratio (ex-post)",
    "Sortino Ratio",
)

_OPTIMIZATION_METRICS = (
    "CAGR",
    "Annualized Return",
    "Expected Return",
    "Standard Deviation",
    "Maximum Drawdown",
    "Sharpe Ratio (ex-post)",
    "Sortino Ratio",
)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError):
        return {}
    return dict(loaded) if isinstance(loaded, Mapping) else {}


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    return dict(loaded) if isinstance(loaded, Mapping) else {}


def _escape(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _fmt_number(value: Any, unit: str | None = None) -> str:
    if value in (None, ""):
        return "N/A"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return _escape(value)
    if unit in {"pct", "percent"}:
        return f"{number:.2f}%"
    if unit == "balance":
        return f"{number:,.2f}"
    return f"{number:.3f}".rstrip("0").rstrip(".")


def _month_number(value: Any) -> int | None:
    if isinstance(value, int) and 1 <= value <= 12:
        return value
    return _MONTHS.get(str(value or "").strip().lower()[:3])


def _period(input_data: Mapping[str, Any], configuration: Mapping[str, Any]) -> str:
    raw = input_data.get("time_period")
    if isinstance(raw, Mapping):
        mode = str(raw.get("mode") or "").lower()
        start_year = raw.get("start_year")
        end_year = raw.get("end_year")
        if start_year and end_year:
            if "year_to_year" in mode or "year-to-year" in mode:
                return f"{start_year} ~ {end_year}"
            first = _month_number(raw.get("first_month"))
            last = _month_number(raw.get("last_month"))
            if first and last:
                return f"{int(start_year):04d}-{first:02d} ~ {int(end_year):04d}-{last:02d}"

    analysis_period = input_data.get("analysis_period")
    if not isinstance(analysis_period, Mapping):
        analysis_period = configuration.get("analysis_period")
    if isinstance(analysis_period, Mapping):
        start = analysis_period.get("start")
        end = analysis_period.get("end")
        if start or end:
            return f"{start or 'N/A'} ~ {end or 'N/A'}"

    start = input_data.get("start") or configuration.get("start")
    end = input_data.get("end") or configuration.get("end")
    if start or end:
        return f"{start or 'N/A'} ~ {end or 'N/A'}"
    return "N/A"


def _benchmark(input_data: Mapping[str, Any], configuration: Mapping[str, Any]) -> str:
    if "benchmark" in input_data:
        raw = input_data.get("benchmark")
        if raw is None:
            return "None"
    else:
        raw = configuration.get("benchmark")

    if isinstance(raw, Mapping):
        name = raw.get("name")
        symbol = raw.get("symbol")
        preset = raw.get("preset")
        if name and symbol:
            return f"{name} ({symbol})"
        if name:
            return str(name)
        if preset:
            return str(preset)
        if symbol:
            return str(symbol)
    return str(raw) if raw not in (None, "") else "None"


def _rebalancing(input_data: Mapping[str, Any], configuration: Mapping[str, Any]) -> str:
    raw = input_data.get("rebalancing")
    if isinstance(raw, Mapping):
        period = raw.get("period")
        aligned = raw.get("calendar_aligned")
        if period:
            if aligned is None or str(period).lower() in {"monthly", "none"}:
                return str(period)
            return f"{period} (calendar aligned: {'Yes' if aligned else 'No'})"

    portfolio = input_data.get("portfolio")
    if isinstance(portfolio, Mapping) and portfolio.get("rebalancing_period"):
        return str(portfolio["rebalancing_period"])

    value = configuration.get("rebalancing") or configuration.get("rebalancing_period")
    return str(value) if value not in (None, "") else "N/A"


def _currency(input_data: Mapping[str, Any], configuration: Mapping[str, Any]) -> str:
    raw_assets = input_data.get("assets") or configuration.get("assets") or []
    currencies = {
        str(row.get("currency")).upper()
        for row in raw_assets
        if isinstance(row, Mapping) and row.get("currency")
    }
    if not currencies:
        return "N/A"
    if currencies == {"KRW", "USD"}:
        fx = input_data.get("fx") or configuration.get("fx")
        if isinstance(fx, Mapping) and fx.get("usdkrw_symbol"):
            return "KRW (USD/KRW normalized)"
    return "/".join(sorted(currencies))


def _context_name(path_value: Any, *, kind: str) -> str:
    text = str(path_value or "").strip()
    if not text:
        return "N/A"
    path = Path(text)
    if kind == "study" and "studies" in path.parts:
        index = path.parts.index("studies")
        if index + 1 < len(path.parts):
            return path.parts[index + 1]
    if kind == "experiment":
        return path.stem
    return text


def _created(run_id: str) -> str:
    match = re.match(r"^(\d{4})(\d{2})(\d{2})", run_id)
    return "-".join(match.groups()) if match else "N/A"


def _weights_pct(raw: Mapping[str, Any], *, already_pct: bool) -> str:
    parts: list[str] = []
    for ticker, value in raw.items():
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        pct = number if already_pct else number * 100.0
        rendered = f"{pct:.2f}".rstrip("0").rstrip(".")
        parts.append(f"{ticker} {rendered}%")
    return ", ".join(parts) if parts else "N/A"


def _optimization_provided_weights(input_data: Mapping[str, Any]) -> dict[str, float]:
    weights: dict[str, float] = {}
    raw_assets = input_data.get("assets")
    if not isinstance(raw_assets, list):
        return weights
    for row in raw_assets:
        if not isinstance(row, Mapping) or not row.get("symbol"):
            continue
        value = row.get("provided_weight_pct")
        if value is None:
            continue
        try:
            weights[str(row["symbol"])] = float(value)
        except (TypeError, ValueError):
            continue
    return weights


def _portfolio_rows(
    input_data: Mapping[str, Any], result: Mapping[str, Any]
) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    raw_portfolios = input_data.get("portfolios")
    if isinstance(raw_portfolios, list):
        for index, portfolio in enumerate(raw_portfolios):
            if not isinstance(portfolio, Mapping):
                continue
            name = str(portfolio.get("name") or f"Portfolio {index + 1}")
            weights_pct = portfolio.get("weights_pct")
            if isinstance(weights_pct, Mapping):
                rows.append((name, _weights_pct(weights_pct, already_pct=True)))
                continue
            weights = portfolio.get("weights") or portfolio.get("target_weights")
            if isinstance(weights, Mapping):
                rows.append((name, _weights_pct(weights, already_pct=False)))
        if rows:
            return rows

    definitions = result.get("portfolio_definitions")
    if isinstance(definitions, Mapping):
        for name, definition in definitions.items():
            if not isinstance(definition, Mapping):
                continue
            weights = definition.get("target_weights")
            if isinstance(weights, Mapping):
                rows.append((str(name), _weights_pct(weights, already_pct=False)))
        if rows:
            return rows

    configuration = result.get("configuration")
    if not isinstance(configuration, Mapping):
        configuration = {}
    provided = input_data.get("provided_weights") or configuration.get("provided_weights")
    if isinstance(provided, Mapping) and provided:
        rows.append(("Provided Portfolio", _weights_pct(provided, already_pct=False)))
    else:
        provided_pct = _optimization_provided_weights(input_data)
        if provided_pct:
            rows.append(("Provided Portfolio", _weights_pct(provided_pct, already_pct=True)))

    optimized = result.get("optimization_result")
    if isinstance(optimized, Mapping):
        weights = optimized.get("weights")
        if isinstance(weights, Mapping) and weights:
            rows.append(("Optimized Portfolio", _weights_pct(weights, already_pct=False)))
    return rows


def _performance_rows(run_dir: Path, product_mode: str) -> tuple[list[str], list[dict[str, str]]]:
    path = run_dir / "review" / "performance_summary.csv"
    if not path.is_file():
        return [], []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except (OSError, UnicodeError, csv.Error):
        return [], []
    if not rows:
        return [], []
    portfolios = [key for key in rows[0] if key not in {"metric", "unit"}]
    wanted = _BACKTEST_METRICS if product_mode == "backtest" else _OPTIMIZATION_METRICS
    return portfolios, [row for row in rows if row.get("metric") in wanted]


def _title_and_purpose(
    input_data: Mapping[str, Any],
    context: Mapping[str, Any],
    product_mode: str,
    portfolios: list[tuple[str, str]],
    benchmark: str,
) -> tuple[str, str]:
    explicit_title = input_data.get("title") or input_data.get("run_title")
    explicit_purpose = input_data.get("purpose") or input_data.get("description")
    experiment = _context_name(context.get("experiment"), kind="experiment")
    product_label = product_mode.title()

    if explicit_title:
        title = str(explicit_title)
    elif experiment != "N/A":
        title = experiment
    elif portfolios:
        names = " vs ".join(name for name, _ in portfolios[:3])
        title = f"{product_label} run: {names}"
    else:
        title = f"{product_label} run"

    if explicit_purpose:
        purpose = str(explicit_purpose)
    elif product_mode == "backtest" and portfolios:
        names = ", ".join(name for name, _ in portfolios)
        suffix = "" if benchmark == "None" else f" against {benchmark}"
        purpose = f"Historical comparison of {names}{suffix}."
    elif product_mode == "optimization":
        purpose = "Portfolio optimization and historical evaluation using the persisted run configuration."
    else:
        purpose = f"Persisted {product_mode} research run."
    return title, purpose


def _artifact_lines(run_dir: Path) -> list[str]:
    candidates = [
        ("Report", "report.html"),
        ("Input", "input.yaml"),
        ("Result", "result.json"),
        ("Context", "context.yaml"),
        ("Raw tables", "raw/"),
        ("Review tables", "review/"),
        ("Validation", "validation/"),
    ]
    lines: list[str] = []
    for label, relative in candidates:
        if (run_dir / relative.rstrip("/")).exists():
            lines.append(f"- [{label}]({relative})")
    return lines or ["- No linked artifacts available."]


def build_run_readme(
    run_dir: str | Path,
    *,
    result: Mapping[str, Any] | None = None,
) -> str:
    directory = Path(run_dir)
    persisted_result = (
        dict(result)
        if isinstance(result, Mapping)
        else _read_json(directory / "result.json")
    )
    input_data = _read_yaml(directory / "input.yaml")
    context = _read_yaml(directory / "context.yaml")
    configuration = persisted_result.get("configuration")
    if not isinstance(configuration, Mapping):
        configuration = {}

    run_id = str(
        configuration.get("run_id")
        or input_data.get("run_id")
        or context.get("run_id")
        or directory.name
    )
    product_mode = str(
        configuration.get("product_mode")
        or input_data.get("product_mode")
        or context.get("product_mode")
        or "optimization"
    ).lower()
    benchmark = _benchmark(input_data, configuration)
    portfolios = _portfolio_rows(input_data, persisted_result)
    title, purpose = _title_and_purpose(
        input_data, context, product_mode, portfolios, benchmark
    )

    lines = [
        f"# {_escape(title)}",
        "",
        "## Metadata",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| Run ID | `{_escape(run_id)}` |",
        f"| Product | {_escape(product_mode.title())} |",
        f"| Study | `{_escape(_context_name(context.get('study'), kind='study'))}` |",
        f"| Experiment | `{_escape(_context_name(context.get('experiment'), kind='experiment'))}` |",
        f"| Period | {_escape(_period(input_data, configuration))} |",
        f"| Benchmark | {_escape(benchmark)} |",
        f"| Rebalancing | {_escape(_rebalancing(input_data, configuration))} |",
        f"| Currency | {_escape(_currency(input_data, configuration))} |",
        f"| Created | {_created(run_id)} |",
        "",
        "## Purpose",
        "",
        purpose.strip(),
        "",
        "## Portfolios",
        "",
    ]

    if portfolios:
        lines.extend(["| Portfolio | Allocation |", "|---|---|"])
        lines.extend(
            f"| {_escape(name)} | {_escape(allocation)} |"
            for name, allocation in portfolios
        )
    else:
        lines.append("No portfolio allocation summary is available.")

    lines.extend(["", "## Key Results", ""])
    performance_names, performance_rows = _performance_rows(directory, product_mode)
    if performance_rows and performance_names:
        lines.append(
            "| Portfolio | "
            + " | ".join(_escape(row["metric"]) for row in performance_rows)
            + " |"
        )
        lines.append("|---|" + "---:|" * len(performance_rows))
        for name in performance_names:
            values = [
                _fmt_number(row.get(name), row.get("unit"))
                for row in performance_rows
            ]
            lines.append(f"| {_escape(name)} | " + " | ".join(values) + " |")
    else:
        lines.append("Representative performance summary is not available for this run.")

    raw_notes = input_data.get("notes")
    lines.extend(["", "## Notes", ""])
    if isinstance(raw_notes, str) and raw_notes.strip():
        lines.append(raw_notes.strip())
    elif isinstance(raw_notes, list) and raw_notes:
        lines.extend(f"- {_escape(note)}" for note in raw_notes)
    else:
        lines.append(
            "Generated from persisted run artifacts for human/LLM navigation. "
            "Canonical values remain in `result.json` and `raw/`."
        )

    lines.extend(["", "## Artifacts", ""])
    lines.extend(_artifact_lines(directory))
    return "\n".join(lines).rstrip() + "\n"


def write_run_readme(
    run_dir: str | Path,
    *,
    result: Mapping[str, Any] | None = None,
) -> Path:
    directory = Path(run_dir)
    target = directory / "README.md"
    target.write_text(build_run_readme(directory, result=result), encoding="utf-8")
    return target


def _index_record(run_dir: Path) -> dict[str, str]:
    result = _read_json(run_dir / "result.json")
    input_data = _read_yaml(run_dir / "input.yaml")
    context = _read_yaml(run_dir / "context.yaml")
    configuration = result.get("configuration")
    if not isinstance(configuration, Mapping):
        configuration = {}
    product_mode = str(
        configuration.get("product_mode")
        or input_data.get("product_mode")
        or context.get("product_mode")
        or "optimization"
    ).lower()
    benchmark = _benchmark(input_data, configuration)
    portfolios = _portfolio_rows(input_data, result)
    title, _ = _title_and_purpose(
        input_data, context, product_mode, portfolios, benchmark
    )
    study = _context_name(context.get("study"), kind="study")
    experiment = _context_name(context.get("experiment"), kind="experiment")
    if study == "N/A" and experiment == "N/A":
        study_experiment = "N/A"
    elif study == "N/A":
        study_experiment = experiment
    elif experiment == "N/A":
        study_experiment = study
    else:
        study_experiment = f"{study} / {experiment}"
    return {
        "run": run_dir.name,
        "product": product_mode.title(),
        "study_experiment": study_experiment,
        "period": _period(input_data, configuration),
        "benchmark": benchmark,
        "summary": title,
    }


def build_runs_index(runs_root: str | Path) -> str:
    root = Path(runs_root)
    records = (
        [
            _index_record(path)
            for path in sorted(
                root.iterdir(), key=lambda item: item.name, reverse=True
            )
            if path.is_dir() and (path / "result.json").is_file()
        ]
        if root.is_dir()
        else []
    )

    def run_table(rows: list[dict[str, str]]) -> list[str]:
        out = [
            "| Run | Product | Study / Experiment | Period | Benchmark | Report | Summary |",
            "|---|---|---|---|---|---|---|",
        ]
        for record in rows:
            out.append(
                f"| [{_escape(record['run'])}]({_escape(record['run'])}/) | "
                f"{_escape(record['product'])} | {_escape(record['study_experiment'])} | "
                f"{_escape(record['period'])} | {_escape(record['benchmark'])} | N/A | "
                f"{_escape(record['summary'])} |"
            )
        if not rows:
            out.append("| N/A | N/A | N/A | N/A | N/A | N/A | No persisted runs found |")
        return out

    grouped: dict[tuple[str, str], dict[str, object]] = {}
    for record in records:
        key = (record["product"], record["study_experiment"])
        if key not in grouped:
            grouped[key] = {"latest": record, "count": 0}
        grouped[key]["count"] = int(grouped[key]["count"]) + 1

    lines = [
        "# Run Index",
        "",
        "This is a navigation view of persisted research runs. Canonical values remain inside each run directory.",
        "",
        "## Latest by Experiment",
        "",
        "Use this first to understand the current research surface without opening individual run folders.",
        "",
        "| Product | Study / Experiment | Latest Run | Runs | Period | Summary |",
        "|---|---|---|---:|---|---|",
    ]
    for item in grouped.values():
        record = item["latest"]
        assert isinstance(record, dict)
        lines.append(
            f"| {_escape(record['product'])} | {_escape(record['study_experiment'])} | "
            f"[{_escape(record['run'])}]({_escape(record['run'])}/) | {int(item['count'])} | "
            f"{_escape(record['period'])} | {_escape(record['summary'])} |"
        )
    if not grouped:
        lines.append("| N/A | N/A | N/A | 0 | N/A | No persisted runs found |")

    recent = records[:20]
    lines.extend(["", "## Recent Runs", ""])
    lines.extend(run_table(recent))
    lines.extend([
        "",
        "<details>",
        f"<summary>Full Run History ({len(records)} runs)</summary>",
        "",
    ])
    lines.extend(run_table(records))
    lines.extend(["", "</details>"])
    return "\n".join(lines).rstrip() + "\n"

def write_runs_index(runs_root: str | Path) -> Path:
    root = Path(runs_root)
    root.mkdir(parents=True, exist_ok=True)
    target = root / "README.md"
    target.write_text(build_runs_index(root), encoding="utf-8")
    return target


def refresh_run_navigation(
    run_dir: str | Path,
    *,
    result: Mapping[str, Any] | None = None,
    update_index: bool = True,
) -> None:
    directory = Path(run_dir)
    write_run_readme(directory, result=result)
    if update_index:
        write_runs_index(directory.parent)


def try_refresh_run_navigation(
    run_dir: str | Path,
    *,
    result: Mapping[str, Any] | None = None,
    update_index: bool = True,
) -> bool:
    """Best-effort refresh that cannot invalidate an otherwise completed run."""
    try:
        refresh_run_navigation(
            run_dir,
            result=result,
            update_index=update_index,
        )
    except (OSError, UnicodeError, ValueError, TypeError) as exc:
        warnings.warn(
            f"run navigation refresh failed: {exc}",
            RuntimeWarning,
            stacklevel=2,
        )
        return False
    return True
