"""Toeplitz Matrix Hashing implementation for privacy amplification.

References:
    Docs/10_API_SPECIFICATION.md
"""

from typing import Sequence
import numpy as np
from qst.privacy.interfaces import HashAlgorithm


class ToeplitzHasher(HashAlgorithm):
    """Universal hash family utilizing Toeplitz matrix multiplication modulo 2."""

    def __init__(self, seed: int = 42) -> None:
        """Initialize the Toeplitz hasher with a deterministic seed.

        Args:
            seed: Pseudo-random generator seed for matrix construction.
        """
        self.seed = seed

    def generate_matrix(self, input_length: int, output_length: int) -> np.ndarray:
        """Construct a deterministic (output_length x input_length) Toeplitz matrix.

        Args:
            input_length: Number of columns (M).
            output_length: Number of rows (N).

        Returns:
            A 2D numpy array representing the Toeplitz matrix.
        """
        rng = np.random.default_rng(self.seed)
        total_bits = output_length + input_length - 1
        random_bits = rng.integers(0, 2, size=total_bits)

        matrix = np.zeros((output_length, input_length), dtype=int)
        for i in range(output_length):
            for j in range(input_length):
                matrix[i, j] = random_bits[i - j + (input_length - 1)]

        return matrix

    def hash_key(self, key: Sequence[int], output_length: int) -> tuple[int, ...]:
        """Compress the key using the generated Toeplitz matrix modulo 2.

        Args:
            key: The input binary sequence to compress.
            output_length: The target output length.

        Returns:
            A tuple of compressed secret key bits.
        """
        input_length = len(key)
        matrix = self.generate_matrix(input_length, output_length)
        key_vector = np.array(key, dtype=int)

        # Vector-matrix multiplication modulo 2
        output_vector = np.dot(matrix, key_vector) % 2
        return tuple(output_vector.tolist())
