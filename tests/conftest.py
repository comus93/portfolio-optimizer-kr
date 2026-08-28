import pandas as pd
import pytest


@pytest.fixture
def simple_monthly_returns():
    index = pd.date_range("2024-01-31", periods=6, freq="ME")
    return pd.DataFrame(
        {
            "A": [0.02, 0.01, -0.01, 0.03, 0.00, 0.02],
            "B": [0.01, 0.00, 0.01, 0.01, 0.02, -0.01],
        },
        index=index,
    )


@pytest.fixture
def diagonal_moments():
    mu = pd.Series({"A": 0.12, "B": 0.08})
    covariance = pd.DataFrame([[0.01, 0.0], [0.0, 0.004]], index=mu.index, columns=mu.index)
    return mu, covariance
