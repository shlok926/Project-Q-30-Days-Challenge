"""Unit tests for SecurityAnalytics calculations.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.analytics.security import SecurityAnalytics


@pytest.mark.unit
def test_compute_qber() -> None:
    """Verify error rates calculations over samples."""
    alice = [1, 0, 1, 0, 1]
    bob = [1, 1, 1, 0, 0]

    # No sample indices
    assert SecurityAnalytics.compute_qber(alice, bob, []) is None

    # Normal sample
    assert SecurityAnalytics.compute_qber(alice, bob, [0, 1, 2]) == pytest.approx(1 / 3)
    assert SecurityAnalytics.compute_qber(alice, bob, [0, 2, 3]) == 0.0


@pytest.mark.unit
def test_compute_key_rate() -> None:
    """Verify simple key rate divisions."""
    assert SecurityAnalytics.compute_key_rate(10, 20) == 0.5
    assert SecurityAnalytics.compute_key_rate(0, 50) == 0.0
    assert SecurityAnalytics.compute_key_rate(10, 0) == 0.0


@pytest.mark.unit
def test_detection_probability() -> None:
    """Verify statistical detection probabilities values."""
    assert SecurityAnalytics.detection_probability(0.0, 10) == 0.0
    assert SecurityAnalytics.detection_probability(0.25, 0) == 0.0
    assert SecurityAnalytics.detection_probability(0.25, 10) > 0.0
