import numpy as np

from portfolio_optimizer_kr.optimize import build_efficient_frontier


def test_frontier_points_are_ordered_and_fully_invested(diagonal_moments):
    mu, covariance = diagonal_moments
    frontier = build_efficient_frontier(mu, covariance, points=8)
    assert len(frontier) == 8
    assert np.all(np.diff(frontier["expected_return"]) >= -1e-6)
    weight_cols = [c for c in frontier.columns if c.startswith("weight_")]
    assert np.allclose(frontier[weight_cols].sum(axis=1), 1.0, atol=5e-5)
    assert (frontier[weight_cols] >= -5e-5).all().all()
