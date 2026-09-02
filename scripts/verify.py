from __future__ import annotations

import argparse
import shlex
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "verification" / "profile.yaml"


def _run(command: str) -> None:
    print(f"+ {command}", flush=True)
    subprocess.run(shlex.split(command), cwd=ROOT, check=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the repository's minimal agent verification stages")
    parser.add_argument("--openspec", action="store_true", help="run strict OpenSpec validation first")
    parser.add_argument("--full", action="store_true", help="run full pytest completion suite after targeted/regression tests")
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

    print("verification command stages completed; real-run/browser stages remain explicit agent steps")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
