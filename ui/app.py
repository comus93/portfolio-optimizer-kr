from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
import yaml

from portfolio_optimizer_kr.catalog import load_catalog, search_catalog
from portfolio_optimizer_kr.config import write_user_config
from portfolio_optimizer_kr.runner import run_yaml
from portfolio_optimizer_kr.viewer import load_run_artifacts

ROOT = Path(__file__).parents[1]
CONFIG_DIR = ROOT / "configs" / "ui"
RUNS_DIR = ROOT / "runs"
CATALOG_PATH = (
    ROOT / "data" / "asset_catalog.csv"
    if (ROOT / "data" / "asset_catalog.csv").is_file()
    else ROOT / "data" / "asset_catalog.example.csv"
)

ASSET_COLUMNS = [
    "symbol",
    "name",
    "currency",
    "provided_weight_pct",
    "min_weight_pct",
    "max_weight_pct",
]


def _empty_assets() -> pd.DataFrame:
    return pd.DataFrame(columns=ASSET_COLUMNS)


def _init_state() -> None:
    if "selected_assets" not in st.session_state:
        st.session_state.selected_assets = _empty_assets()
    if "last_run_dir" not in st.session_state:
        st.session_state.last_run_dir = ""


def _add_catalog_asset(row: pd.Series) -> None:
    assets = st.session_state.selected_assets
    symbol = str(row["symbol"])
    if symbol in set(assets["symbol"].astype(str)):
        return
    new_row = pd.DataFrame(
        [
            {
                "symbol": symbol,
                "name": row.get("name", ""),
                "currency": row.get("currency", "KRW") or "KRW",
                "provided_weight_pct": 0.0,
                "min_weight_pct": 0.0,
                "max_weight_pct": 100.0,
            }
        ]
    )
    st.session_state.selected_assets = pd.concat([assets, new_row], ignore_index=True)


def _build_config(
    run_id: str,
    start,
    end,
    assets: pd.DataFrame,
    benchmark_symbol: str,
    benchmark_currency: str,
    objective: str,
    target_volatility_pct: float | None,
    frontier_points: int,
    rebalancing_period: str,
    risk_free_mode: str,
    annual_rate_pct: float | None,
    usdkrw_symbol: str,
) -> dict:
    asset_rows = []
    for row in assets.fillna("").to_dict(orient="records"):
        if not str(row.get("symbol", "")).strip():
            continue
        asset_rows.append(
            {
                "symbol": str(row["symbol"]).strip(),
                "name": str(row.get("name") or "").strip() or None,
                "currency": str(row.get("currency") or "KRW").upper(),
                "provided_weight_pct": float(row.get("provided_weight_pct") or 0),
                "min_weight_pct": float(row.get("min_weight_pct") or 0),
                "max_weight_pct": float(row.get("max_weight_pct") or 100),
            }
        )
    config = {
        "run_id": run_id.strip(),
        "analysis_period": {"start": start.isoformat(), "end": end.isoformat()},
        "assets": asset_rows,
        "optimization": {
            "objective": objective,
            "frontier_points": int(frontier_points),
        },
        "portfolio": {"rebalancing_period": rebalancing_period},
        "risk_free": {"mode": risk_free_mode},
        "fx": {},
    }
    if benchmark_symbol.strip():
        config["benchmark"] = {
            "symbol": benchmark_symbol.strip(),
            "currency": benchmark_currency.upper(),
        }
    if objective == "target_volatility":
        config["optimization"]["target_volatility_pct"] = float(target_volatility_pct or 0)
    if risk_free_mode == "fixed":
        config["risk_free"]["annual_rate_pct"] = float(annual_rate_pct or 0)
    if usdkrw_symbol.strip():
        config["fx"]["usdkrw_symbol"] = usdkrw_symbol.strip()
    return config


def input_page() -> None:
    st.header("Portfolio input")
    catalog = load_catalog(CATALOG_PATH)
    query = st.text_input("Search assets", placeholder="Ticker or name")
    matches = search_catalog(catalog, query, limit=20) if query.strip() else catalog.head(10)
    if not matches.empty:
        labels = [f"{row.symbol} | {row.name}" for row in matches.itertuples()]
        selected = st.selectbox("Search results", labels)
        if st.button("Add selected asset"):
            _add_catalog_asset(matches.iloc[labels.index(selected)])
            st.rerun()
    else:
        st.caption("No catalog result. You can add/edit rows manually below.")

    edited = st.data_editor(
        st.session_state.selected_assets,
        num_rows="dynamic",
        use_container_width=True,
        key="asset_editor",
    )
    st.session_state.selected_assets = edited[ASSET_COLUMNS].copy()

    left, right = st.columns(2)
    with left:
        run_id = st.text_input("Run ID", value="ui-run-001")
        start = st.date_input("Start")
        benchmark_symbol = st.text_input("Benchmark", value="SPY")
        objective = st.selectbox("Objective", ["max_sharpe", "target_volatility"])
        rebalancing = st.selectbox("Rebalancing", ["monthly", "yearly"])
    with right:
        end = st.date_input("End")
        benchmark_currency = st.selectbox("Benchmark currency", ["USD", "KRW"])
        target_volatility = (
            st.number_input("Target volatility (%)", min_value=0.0, value=13.0)
            if objective == "target_volatility"
            else None
        )
        frontier_points = st.number_input("Frontier points", min_value=2, value=100)
        risk_free_mode = st.selectbox("Risk-free mode", ["us_3m_tbill", "fixed"])
        annual_rate = (
            st.number_input("Annual risk-free rate (%)", value=2.0)
            if risk_free_mode == "fixed"
            else None
        )
        usdkrw_symbol = st.text_input("FDR USD/KRW symbol (mixed-currency only)")

    config = _build_config(
        run_id,
        start,
        end,
        st.session_state.selected_assets,
        benchmark_symbol,
        benchmark_currency,
        objective,
        target_volatility,
        int(frontier_points),
        rebalancing,
        risk_free_mode,
        annual_rate,
        usdkrw_symbol,
    )
    st.subheader("Generated YAML")
    st.code(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), language="yaml")

    save_col, run_col = st.columns(2)
    config_path = CONFIG_DIR / f"{run_id.strip() or 'unnamed'}.yaml"
    if save_col.button("Save YAML"):
        write_user_config(config, config_path)
        st.success(f"Saved {config_path.relative_to(ROOT)}")
    if run_col.button("Run optimization", type="primary"):
        write_user_config(config, config_path)
        output = run_yaml(config_path, RUNS_DIR)
        st.session_state.last_run_dir = str(output)
        st.success(f"Completed {output.name}")


def results_page() -> None:
    st.header("Run results")
    default = st.session_state.last_run_dir
    run_dir_text = st.text_input("Run directory", value=default)
    if not run_dir_text:
        st.info("Run an optimization or enter an existing runs/<run_id> directory.")
        return
    run_dir = Path(run_dir_text)
    if not run_dir.is_absolute():
        run_dir = ROOT / run_dir
    try:
        artifacts = load_run_artifacts(run_dir)
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    configuration = artifacts.result.get("configuration", {})
    st.caption(
        f"{configuration.get('run_id', run_dir.name)} | "
        f"{configuration.get('objective', '')}"
    )
    if artifacts.review:
        table_name = st.selectbox("Review table", sorted(artifacts.review))
        st.dataframe(artifacts.review[table_name], use_container_width=True)
    else:
        st.warning("No review CSV layer found for this run yet.")

    frontier = artifacts.review.get("efficient_frontier")
    if frontier is not None:
        x_candidates = [c for c in frontier.columns if "volatility" in c or "standard_deviation" in c]
        y_candidates = [c for c in frontier.columns if "expected_return" in c]
        if x_candidates and y_candidates:
            st.subheader("Efficient frontier")
            st.scatter_chart(frontier, x=x_candidates[0], y=y_candidates[0])

    rolling = artifacts.review.get("rolling_returns_3y")
    if rolling is not None and "date" in rolling.columns:
        value_columns = [c for c in rolling.columns if c != "date"]
        if value_columns:
            st.subheader("Rolling 3Y returns")
            chart = rolling.copy()
            chart["date"] = pd.to_datetime(chart["date"])
            st.line_chart(chart.set_index("date")[value_columns])


def main() -> None:
    st.set_page_config(page_title="Portfolio Optimizer KR", layout="wide")
    _init_state()
    st.title("Portfolio Optimizer KR")
    page = st.sidebar.radio("Page", ["Input", "Results"])
    input_page() if page == "Input" else results_page()


if __name__ == "__main__":
    main()
