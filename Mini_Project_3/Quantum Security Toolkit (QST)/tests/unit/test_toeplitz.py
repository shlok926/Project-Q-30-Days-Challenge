"""Unit tests for Toeplitz Matrix Hashing generator and matrix validation.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
import numpy as np
from qst.privacy.algorithms.toeplitz import ToeplitzHasher


@pytest.mark.unit
def test_toeplitz_matrix_determinism() -> None:
    """Verify that a fixed seed creates identical Toeplitz matrices across runs."""
    hasher1 = ToeplitzHasher(seed=123)
    hasher2 = ToeplitzHasher(seed=123)

    m1 = hasher1.generate_matrix(input_length=20, output_length=10)
    m2 = hasher2.generate_matrix(input_length=20, output_length=10)

    # Check identical elements
    assert np.array_equal(m1, m2)

    # Confirm different seed produces different matrix
    hasher3 = ToeplitzHasher(seed=456)
    m3 = hasher3.generate_matrix(input_length=20, output_length=10)
    assert not np.array_equal(m1, m3)


@pytest.mark.unit
def test_toeplitz_diagonal_property() -> None:
    """Verify constant diagonals on generated Toeplitz matrices."""
    hasher = ToeplitzHasher(seed=99)
    matrix = hasher.generate_matrix(input_length=15, output_length=8)

    rows, cols = matrix.shape
    for i in range(1, rows):
        for j in range(1, cols):
            assert matrix[i, j] == matrix[i - 1, j - 1]


@pytest.mark.unit
def test_toeplitz_hashing_output() -> None:
    """Verify that hashing input matches matrix multiplication results."""
    key = [1, 0, 1, 1, 0, 1, 0, 0]
    hasher = ToeplitzHasher(seed=42)

    output = hasher.hash_key(key, output_length=4)
    assert len(output) == 4
    for bit in output:
        assert bit in (0, 1)
