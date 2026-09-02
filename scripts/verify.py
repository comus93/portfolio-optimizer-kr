from __future__ import annotations

import argparse
import os
import shlex
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "verification" / "profile.yaml"


def _run(command: str, *, extra_env: dict[str, str] | None = None) -> None:
    print(f"+ {command}", flush=True)
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    subprocess.run(shlex.split(command), cwd=ROOT, check=True, env=env)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the repository's agent verification stages"
    )
    parser.add_argument(
        "--openspec", action="store_true", help="run strict OpenSpec validation first"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="run full pytest completion suite after targeted/regression tests",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="run deterministic Playwright browser acceptance after command tests",
    )
    parser.add_argument(
        "--browser-report",
        type=str,
        default=None,
        help="verify an existing generated Backtest report.html with Playwright; path must be inside the repository",
    )
    args = parser.parse_args(argv)

    profile = yaml.safe_load(PROFILE.read_text(encoding="utf-8"))
    if args.openspec:
        for command in profile.get("openspec", []):
            _run(command)

    tests = profile.get("tests", {})
    for command in tests.get("targeted", []):
        _run(command)
    for command in tests.get("affected_regression", []):
        _run(command)
    if args.full:
        for command in tests.get("completion", []):
            _run(command)

    browser = profile.get("browser", {})
    if args.browser_report:
        command = str(browser.get("real_report_command") or "npx playwright test")
        env_name = str(browser.get("real_report_env") or "BACKTEST_REPORT_PATH")
        _run(command, extra_env={env_name: args.browser_report})
    elif args.browser:
        command = str(browser.get("fixture_command") or "npm run verify:browser")
        _run(command)

    if not args.browser and not args.browser_report:
        print(
            "verification command stages completed; real-run/browser stages remain explicit agent steps"
        )
    else:
        print("verification command + browser stages completed; real-run remains an explicit agent step")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
