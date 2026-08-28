from __future__ import annotations

import argparse
from pathlib import Path

from portfolio_optimizer_kr.config import load_run_config
from portfolio_optimizer_kr.research import execute_controlled_experiment
from portfolio_optimizer_kr.runner import run_yaml


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="portfolio-optimizer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a run YAML without executing it")
    validate.add_argument("config", type=Path)

    run = subparsers.add_parser("run", help="execute a run YAML")
    run.add_argument("config", type=Path)
    run.add_argument("--output-root", type=Path, default=Path("runs"))
    run.add_argument(
        "--annual-rf-pct",
        type=float,
        default=None,
        help="temporary annual risk-free override in percentage points for external RF mode",
    )

    execute = subparsers.add_parser(
        "execute", help="execute the research experiment selected by control/execute.yaml"
    )
    execute.add_argument("--repo-root", type=Path, default=Path("."))
    execute.add_argument("--control", type=Path, default=Path("control/execute.yaml"))
    execute.add_argument("--output-root", type=Path, default=Path("runs"))
    execute.add_argument(
        "--annual-rf-pct",
        type=float,
        default=None,
        help="temporary annual risk-free override in percentage points for external RF mode",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "validate":
        spec = load_run_config(args.config)
        print(f"valid: {spec.request.run_id}")
        return 0

    annual_rf = args.annual_rf_pct / 100.0 if args.annual_rf_pct is not None else None
    if args.command == "execute":
        output = execute_controlled_experiment(
            repo_root=args.repo_root,
            control_path=args.control,
            output_root=args.output_root,
            annual_rf=annual_rf,
        )
    else:
        output = run_yaml(args.config, args.output_root, annual_rf=annual_rf)
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
