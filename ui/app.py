from __future__ import annotations

from datetime import date
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

BASE_ASSET_COLUMNS = ["symbol", "name", "currency"]
OPTIMIZATION_COLUMNS = [
    *BASE_ASSET_COLUMNS,
    "provided_weight_pct",
    "min_weight_pct",
    "max_weight_pct",
]
BACKTEST_WEIGHT_COLUMNS = ["portfolio_1_pct", "portfolio_2_pct", "portfolio_3_pct"]
ALL_ASSET_COLUMNS = [*OPTIMIZATION_COLUMNS, *BACKTEST_WEIGHT_COLUMNS]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _empty_assets() -> pd.DataFrame:
    return pd.DataFrame(columns=ALL_ASSET_COLUMNS)


def _ensure_asset_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    defaults = {
        "symbol": "",
        "name": "",
        "currency": "KRW",
        "provided_weight_pct": 0.0,
        "min_weight_pct": 0.0,
        "max_weight_pct": 100.0,
        "portfolio_1_pct": 0.0,
        "portfolio_2_pct": 0.0,
        "portfolio_3_pct": 0.0,
    }
    for column, default in defaults.items():
        if column not in out:
            out[column] = default
    return out[ALL_ASSET_COLUMNS]


def _init_state() -> None:
    if "selected_assets" not in st.session_state:
        st.session_state.selected_assets = _empty_assets()
    else:
        st.session_state.selected_assets = _ensure_asset_columns(st.session_state.selected_assets)
    if "last_run_dir" not in st.session_state:
        st.session_state.last_run_dir = ""


def _add_catalog_asset(row: pd.Series) -> None:
    assets = _ensure_asset_columns(st.session_state.selected_assets)
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
                "portfolio_1_pct": 0.0,
                "portfolio_2_pct": 0.0,
                "portfolio_3_pct": 0.0,
            }
        ]
    )
    st.session_state.selected_assets = pd.concat([assets, new_row], ignore_index=True)


def _asset_rows(assets: pd.DataFrame, *, optimization: bool) -> list[dict]:
    rows: list[dict] = []
    for row in assets.fillna("").to_dict(orient="records"):
        symbol = str(row.get("symbol", "")).strip()
        if not symbol:
            continue
        item = {
            "symbol": symbol,
            "name": str(row.get("name") or "").strip() or None,
            "currency": str(row.get("currency") or "KRW").upper(),
        }
        if optimization:
            item.update(
                {
                    "provided_weight_pct": float(row.get("provided_weight_pct") or 0),
                    "min_weight_pct": float(row.get("min_weight_pct") or 0),
                    "max_weight_pct": float(row.get("max_weight_pct") or 100),
                }
            )
        rows.append(item)
    return rows


def _shared_tail(
    config: dict,
    *,
    risk_free_mode: str,
    annual_rate_pct: float | None,
    usdkrw_symbol: str,
) -> dict:
    config["risk_free"] = {"mode": risk_free_mode}
    if risk_free_mode == "fixed":
        config["risk_free"]["annual_rate_pct"] = float(annual_rate_pct or 0)
    config["fx"] = {}
    if usdkrw_symbol.strip():
        config["fx"]["usdkrw_symbol"] = usdkrw_symbol.strip()
    return config


def _build_optimization_config(
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
    config = {
        "product_mode": "optimization",
        "run_id": run_id.strip(),
        "analysis_period": {"start": start.isoformat(), "end": end.isoformat()},
        "assets": _asset_rows(assets, optimization=True),
        "optimization": {
            "objective": objective,
            "frontier_points": int(frontier_points),
        },
        "portfolio": {"rebalancing_period": rebalancing_period},
    }
    if benchmark_symbol.strip():
        config["benchmark"] = {
            "symbol": benchmark_symbol.strip(),
            "currency": benchmark_currency.upper(),
        }
    if objective == "target_volatility":
        config["optimization"]["target_volatility_pct"] = float(target_volatility_pct or 0)
    return _shared_tail(
        config,
        risk_free_mode=risk_free_mode,
        annual_rate_pct=annual_rate_pct,
        usdkrw_symbol=usdkrw_symbol,
    )


def _build_backtest_config(
    *,
    run_id: str,
    assets: pd.DataFrame,
    portfolio_names: list[str],
    time_period_mode: str,
    use_full_common_period: bool,
    start_year: int,
    first_month: str,
    end_year: int,
    last_month: str,
    initial_balance: float,
    benchmark_symbol: str,
    benchmark_currency: str,
    rebalancing_period: str,
    calendar_aligned: bool,
    risk_free_mode: str,
    annual_rate_pct: float | None,
    usdkrw_symbol: str,
) -> dict:
    config: dict = {
        "product_mode": "backtest",
        "run_id": run_id.strip(),
        "time_period": {"mode": time_period_mode},
        "assets": _asset_rows(assets, optimization=False),
        "portfolios": [],
        "initial_balance": float(initial_balance),
        "rebalancing": {
            "period": rebalancing_period,
            "calendar_aligned": bool(calendar_aligned),
        },
    }
    if not use_full_common_period:
        config["time_period"].update(
            {
                "start_year": int(start_year),
                "end_year": int(end_year),
            }
        )
        if time_period_mode == "month_to_month":
            config["time_period"]["first_month"] = first_month
            config["time_period"]["last_month"] = last_month

    for idx, name in enumerate(portfolio_names, start=1):
        weight_column = f"portfolio_{idx}_pct"
        weights = {
            str(row["symbol"]).strip(): float(row.get(weight_column) or 0)
            for row in assets.fillna("").to_dict(orient="records")
            if str(row.get("symbol") or "").strip()
        }
        config["portfolios"].append(
            {
                "name": name.strip() or f"Portfolio {idx}",
                "weights_pct": weights,
            }
        )

    if benchmark_symbol.strip():
        config["benchmark"] = {
            "symbol": benchmark_symbol.strip(),
            "currency": benchmark_currency.upper(),
        }
    else:
        config["benchmark"] = None
    return _shared_tail(
        config,
        risk_free_mode=risk_free_mode,
        annual_rate_pct=annual_rate_pct,
        usdkrw_symbol=usdkrw_symbol,
    )


def _asset_picker(catalog: pd.DataFrame) -> None:
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


def _shared_market_inputs():
    left, right = st.columns(2)
    with left:
        benchmark_symbol = st.text_input("Benchmark", value="SPY")
        risk_free_mode = st.selectbox("Risk-free mode", ["us_3m_tbill", "fixed"])
    with right:
        benchmark_currency = st.selectbox("Benchmark currency", ["USD", "KRW"])
        annual_rate = (
            st.number_input("Annual risk-free rate (%)", value=2.0)
            if risk_free_mode == "fixed"
            else None
        )
        usdkrw_symbol = st.text_input("FDR USD/KRW symbol (mixed-currency only)")
    return benchmark_symbol, benchmark_currency, risk_free_mode, annual_rate, usdkrw_symbol


def _optimization_input() -> tuple[dict, str]:
    edited = st.data_editor(
        st.session_state.selected_assets[OPTIMIZATION_COLUMNS],
        num_rows="dynamic",
        use_container_width=True,
        key="optimization_asset_editor",
    )
    for column in OPTIMIZATION_COLUMNS:
        st.session_state.selected_assets[column] = edited[column]

    left, right = st.columns(2)
    with left:
        run_id = st.text_input("Run ID", value="ui-run-001", key="opt_run_id")
        start = st.date_input("Start", key="opt_start")
        objective = st.selectbox("Objective", ["max_sharpe", "target_volatility"])
        rebalancing = st.selectbox("Rebalancing", ["monthly", "yearly"], key="opt_rebalance")
    with right:
        end = st.date_input("End", key="opt_end")
        target_volatility = (
            st.number_input("Target volatility (%)", min_value=0.0, value=13.0)
            if objective == "target_volatility"
            else None
        )
        frontier_points = st.number_input("Frontier points", min_value=2, value=100)

    benchmark_symbol, benchmark_currency, risk_free_mode, annual_rate, usdkrw_symbol = _shared_market_inputs()
    return (
        _build_optimization_config(
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
        ),
        run_id,
    )


def _backtest_input() -> tuple[dict, str]:
    st.subheader("Portfolio Assets")
    portfolio_count = st.number_input("Portfolios", min_value=1, max_value=3, value=1, step=1)
    portfolio_names = [
        st.text_input(f"Portfolio {idx} name", value=f"Portfolio {idx}", key=f"bt_name_{idx}")
        for idx in range(1, int(portfolio_count) + 1)
    ]
    columns = [*BASE_ASSET_COLUMNS, *BACKTEST_WEIGHT_COLUMNS[: int(portfolio_count)]]
    edited = st.data_editor(
        st.session_state.selected_assets[columns],
        num_rows="dynamic",
        use_container_width=True,
        key="backtest_asset_editor",
    )
    for column in columns:
        st.session_state.selected_assets[column] = edited[column]

    st.subheader("Settings")
    run_id = st.text_input("Run ID", value="backtest-ui-001", key="bt_run_id")
    time_period_mode = st.selectbox(
        "Time Period", ["month_to_month", "year_to_year"], format_func=lambda value: "Month-to-Month" if value == "month_to_month" else "Year-to-Year"
    )
    use_full_common_period = st.checkbox("Use full common effective period", value=True)
    current_year = date.today().year
    period_left, period_right = st.columns(2)
    with period_left:
        start_year = int(st.number_input("Start Year", min_value=1900, max_value=current_year, value=max(1900, current_year - 10), disabled=use_full_common_period))
        first_month = st.selectbox("First Month", MONTHS, disabled=use_full_common_period or time_period_mode != "month_to_month")
    with period_right:
        end_year = int(st.number_input("End Year", min_value=1900, max_value=current_year, value=current_year, disabled=use_full_common_period))
        last_month = st.selectbox("Last Month", MONTHS, index=11, disabled=use_full_common_period or time_period_mode != "month_to_month")

    settings_left, settings_right = st.columns(2)
    with settings_left:
        initial_balance = st.number_input("Initial Amount", min_value=0.01, value=10000.0)
        rebalancing = st.selectbox(
            "Rebalancing",
            ["none", "yearly", "semiannual", "quarterly", "monthly"],
            index=4,
        )
    with settings_right:
        calendar_aligned = st.selectbox("Calendar Aligned", [True, False], format_func=lambda value: "Yes" if value else "No")

    benchmark_symbol, benchmark_currency, risk_free_mode, annual_rate, usdkrw_symbol = _shared_market_inputs()
    config = _build_backtest_config(
        run_id=run_id,
        assets=st.session_state.selected_assets,
        portfolio_names=portfolio_names,
        time_period_mode=time_period_mode,
        use_full_common_period=use_full_common_period,
        start_year=start_year,
        first_month=first_month,
        end_year=end_year,
        last_month=last_month,
        initial_balance=initial_balance,
        benchmark_symbol=benchmark_symbol,
        benchmark_currency=benchmark_currency,
        rebalancing_period=rebalancing,
        calendar_aligned=calendar_aligned,
        risk_free_mode=risk_free_mode,
        annual_rate_pct=annual_rate,
        usdkrw_symbol=usdkrw_symbol,
    )
    return config, run_id


def input_page() -> None:
    st.header("Portfolio research input")
    product_mode = st.radio("Product", ["Optimization", "Backtest"], horizontal=True)
    catalog = load_catalog(CATALOG_PATH)
    _asset_picker(catalog)

    if product_mode == "Backtest":
        config, run_id = _backtest_input()
        run_label = "Run backtest"
    else:
        config, run_id = _optimization_input()
        run_label = "Run optimization"

    st.subheader("Generated YAML")
    st.code(yaml.safe_dump(config, sort_keys=False, allow_unicode=True), language="yaml")

    save_col, run_col = st.columns(2)
    config_path = CONFIG_DIR / f"{run_id.strip() or 'unnamed'}.yaml"
    if save_col.button("Save YAML"):
        write_user_config(config, config_path)
        st.success(f"Saved {config_path.relative_to(ROOT)}")
    if run_col.button(run_label, type="primary"):
        write_user_config(config, config_path)
        output = run_yaml(config_path, RUNS_DIR)
        st.session_state.last_run_dir = str(output)
        st.success(f"Completed {output.name}")


def results_page() -> None:
    st.header("Run results")
    default = st.session_state.last_run_dir
    run_dir_text = st.text_input("Run directory", value=default)
    if not run_dir_text:
        st.info("Run a portfolio study or enter an existing runs/<run_id> directory.")
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
    product_mode = configuration.get("product_mode", "optimization")
    identity = (
        configuration.get("objective", "")
        if product_mode != "backtest"
        else f"{configuration.get('time_period_mode', '')} | {configuration.get('rebalancing_period', '')}"
    )
    st.caption(f"{configuration.get('run_id', run_dir.name)} | {product_mode} | {identity}")
    if artifacts.review:
        table_name = st.selectbox("Review table", sorted(artifacts.review))
        st.dataframe(artifacts.review[table_name], use_container_width=True)
    else:
        st.warning("No review CSV layer found for this run yet.")

    if product_mode == "backtest":
        growth = artifacts.raw.get("portfolio_growth")
        if growth is not None and "date" in growth.columns:
            value_columns = [c for c in growth.columns if c.endswith("_balance")]
            if value_columns:
                chart = growth.copy()
                chart["date"] = pd.to_datetime(chart["date"])
                st.subheader("Portfolio growth")
                st.line_chart(chart.set_index("date")[value_columns])
    else:
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
