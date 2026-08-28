"""Small parsers for the checked-in Portfolio Visualizer golden references."""
from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

import pandas as pd


TARGET_VOL_SYMBOLS = ("QQQ", "SPMO", "GDX", "GLD", "SLV", "AIA", "XLE", "PTF", "QLD")


@dataclass(frozen=True)
class TargetVolGolden:
    symbols: tuple[str, ...]
    expected_returns: pd.Series
    volatilities: pd.Series
    correlation: pd.DataFrame
    bounds: dict[str, tuple[float, float]]
    provided_weights: pd.Series
    published_weights: pd.Series
    target_volatility: float
    period: dict[str, str]
    published_metrics: dict[str, float]


def _cells(line: str) -> list[str]:
    return [cell.strip().replace("\\-", "-") for cell in line.split("|")[1:-1]]


def _percentage(value: str) -> float:
    return float(value.rstrip("%").replace("\\-", "-")) / 100


def _portfolio_weights(text: str, heading: str, symbols: tuple[str, ...]) -> pd.Series:
    section = text.split(heading, 1)[1].split("####", 1)[0]
    weights = pd.Series(0.0, index=symbols)
    for line in section.splitlines():
        cells = _cells(line)
        if len(cells) == 3 and cells[0] in symbols and cells[2].endswith("%"):
            weights[cells[0]] = _percentage(cells[2])
    return weights


def load_target_vol_golden(path: str | Path) -> TargetVolGolden:
    """Parse the rounded PV target-volatility values used for parity diagnostics."""
    text = Path(path).read_text(encoding="utf-8")
    symbols = TARGET_VOL_SYMBOLS

    assets = text.split("#### Efficient Frontier Assets", 1)[1].split("#### Asset Correlations", 1)[0]
    rows = []
    for line in assets.splitlines():
        cells = _cells(line)
        if len(cells) == 7 and cells[0].isdigit() and cells[2].endswith("%"):
            rows.append(cells)
    if len(rows) < len(symbols):
        raise ValueError("could not parse all PV target-volatility asset rows")
    rows = rows[: len(symbols)]
    expected_returns = pd.Series([_percentage(row[2]) for row in rows], index=symbols)
    volatilities = pd.Series([_percentage(row[3]) for row in rows], index=symbols)
    bounds = {
        symbol: (_percentage(row[5]), _percentage(row[6]))
        for symbol, row in zip(symbols, rows)
    }

    correlation_section = text.split("#### Asset Correlations", 1)[1].split("#### Efficient Frontier", 1)[0]
    correlation_rows = []
    for line in correlation_section.splitlines():
        cells = _cells(line)
        if len(cells) == 11 and cells[1] in symbols:
            correlation_rows.append([float(value) for value in cells[2:]])
    if len(correlation_rows) != len(symbols):
        raise ValueError("could not parse PV target-volatility correlation matrix")
    correlation = pd.DataFrame(correlation_rows, index=symbols, columns=symbols)

    target_match = re.search(r"targeted annual volatility\. The possible", text)
    target_heading = re.search(r"#### Maximum Return at ([\d.]+)% Volatility", text)
    period_match = re.search(r"Portfolio Optimization Results \(([A-Za-z]{3}) (\d{4}) - ([A-Za-z]{3}) (\d{4})\)", text)
    if target_match is None or target_heading is None or period_match is None:
        raise ValueError("could not identify PV target-volatility metadata")
    months = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}
    period = {
        "start": f"{period_match.group(2)}-{months[period_match.group(1)]}",
        "end": f"{period_match.group(4)}-{months[period_match.group(3)]}",
    }
    published_metrics = {}
    for field, key in (("Annualized Return (CAGR)", "cagr"), ("Maximum Drawdown", "max_drawdown"), ("Expected Return", "expected_return"), ("Standard Deviation", "volatility"), ("Sharpe Ratio (ex-ante)", "sharpe")):
        match = re.search(rf"\| {re.escape(field)} \| .*? \| (\\?[-\d.]+)%? \|", text)
        if match is None:
            raise ValueError(f"could not parse PV target-volatility {field}")
        value = float(match.group(1).replace("\\-", "-"))
        published_metrics[key] = value / 100 if field not in {"Sharpe Ratio (ex-ante)"} else value

    return TargetVolGolden(
        symbols=symbols,
        expected_returns=expected_returns,
        volatilities=volatilities,
        correlation=correlation,
        bounds=bounds,
        provided_weights=_portfolio_weights(text, "#### Provided Portfolio", symbols),
        published_weights=_portfolio_weights(text, "#### Maximum Return at", symbols),
        target_volatility=_percentage(target_heading.group(1) + "%"),
        period=period,
        published_metrics=published_metrics,
    )
