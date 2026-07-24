"""Unit tests for error correction parity calculations.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.correction.parity import calculate_parity


@pytest.mark.unit
def test_parity_even_count() -> None:
    """Verify calculate_parity returns 0 for even counts of ones."""
    assert calculate_parity([0, 0, 0]) == 0
    assert calculate_parity([1, 1, 0, 0]) == 0
    assert calculate_parity([1, 1, 1, 1, 0, 1, 1]) == 0
    assert calculate_parity([]) == 0


@pytest.mark.unit
def test_parity_odd_count() -> None:
    """Verify calculate_parity returns 1 for odd counts of ones."""
    assert calculate_parity([1]) == 1
    assert calculate_parity([1, 0, 0]) == 1
    assert calculate_parity([1, 1, 1]) == 1
    assert calculate_parity([1, 0, 1, 0, 1]) == 1
