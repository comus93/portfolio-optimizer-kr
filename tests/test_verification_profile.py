from pathlib import Path
import json

import yaml


def test_agent_verification_profile_has_backtest_and_regression_stages():
    root = Path(__file__).resolve().parents[1]
    profile = yaml.safe_load(
        (root / "verification" / "profile.yaml").read_text(encoding="utf-8")
    )

    assert profile["version"] == 1
    assert "tests/test_backtest.py" in " ".join(profile["tests"]["targeted"])
    assert "tests/test_runner.py" in " ".join(profile["tests"]["affected_regression"])
    assert profile["real_run"]["config"] == "configs/backtest-example.yaml"
    assert profile["browser"]["required_for_report_changes"] is True
    assert profile["browser"]["engine"] == "playwright-chromium"
    assert profile["browser"]["fixture_command"] == "npm run verify:browser"
    assert profile["browser"]["real_report_env"] == "BACKTEST_REPORT_PATH"
    assert "npm install" in profile["browser"]["one_time_setup"]
    assert "npx playwright install chromium" in profile["browser"]["one_time_setup"]
    assert profile["human_visual_review"]["when"] == "material_layout_or_interaction_change"
    assert "human reviewer" in profile["human_visual_review"]["rule"]


def test_playwright_browser_verification_files_are_wired():
    root = Path(__file__).resolve().parents[1]
    package = json.loads((root / "package.json").read_text(encoding="utf-8"))

    assert "@playwright/test" in package["devDependencies"]
    assert package["scripts"]["verify:browser"].startswith(
        "uv run python scripts/prepare_browser_fixture.py"
    )
    assert (root / "playwright.config.mjs").is_file()
    assert (root / "scripts" / "prepare_browser_fixture.py").is_file()
    assert (root / "verification" / "browser" / "backtest-report.spec.mjs").is_file()
