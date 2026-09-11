from __future__ import annotations

import pandas as pd
import pytest

from portfolio_optimizer_kr.analytics import normalized_underwater_duration
from portfolio_optimizer_kr.viewer.pv_visual import drawdown_presentation


def test_normalized_underwater_duration_uses_recovered_worst10_median() -> None:
    episodes = pd.DataFrame([
        {"rank": 1, "recovery": "2021-05-31", "underwater_months": 4, "maximum_drawdown": -0.10},
        {"rank": 2, "recovery": "2022-06-30", "underwater_months": 6, "maximum_drawdown": -0.20},
        {"rank": 3, "recovery": None, "underwater_months": 12, "maximum_drawdown": -0.30},
        {"rank": 11, "recovery": "2023-01-31", "underwater_months": 1, "maximum_drawdown": -0.10},
    ])
    summary = normalized_underwater_duration(episodes)
    assert summary["completed_episode_count"] == 2
    assert summary["episode_limit"] == 10
    assert summary["normalized_underwater_duration_months_per_10pct"] == pytest.approx(3.5)


def test_drawdown_presentation_displays_canonical_elasticity_kpi() -> None:
    dates = pd.to_datetime(["2020-01-31", "2020-02-29", "2020-03-31"])
    series = pd.DataFrame({"date": dates, "Portfolio A_drawdown_pct": [0.0, -10.0, 0.0]})
    episodes = pd.DataFrame([{
        "portfolio": "Portfolio A", "rank": 1, "start": dates[1], "bottom": dates[1],
        "recovery": dates[2], "maximum_drawdown_pct": -10.0, "decline_months": 1,
        "recovery_months": 1, "underwater_months": 2, "annualized_recovery_rate_pct": 213.8,
    }])
    resilience = pd.DataFrame([{
        "portfolio": "Portfolio A",
        "normalized_underwater_duration_months_per_10pct": 3.14,
        "completed_episode_count": 7,
        "episode_limit": 10,
    }])
    rendered = drawdown_presentation(series, episodes, ["Portfolio A"], None, resilience)
    assert "탄성회복도" in rendered
    assert "3.1개월 / 10% DD" in rendered
    assert "낮을수록 좋음" in rendered
    assert 'class="drawdown-resilience-table"' in rendered
    assert "Completed Episodes" in rendered
    assert ">7/10</td>" in rendered
