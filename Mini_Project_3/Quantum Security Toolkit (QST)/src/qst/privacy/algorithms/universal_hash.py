"""Universal Hashing algorithm implementation for privacy amplification.

References:
    Docs/10_API_SPECIFICATION.md §4
    Carter, J. L., & Wegman, M. N. (1979). Universal classes of hash functions.
"""

from typing import Sequence

import numpy as np

from qst.privacy.exceptions import PrivacyAmplificationError
from qst.privacy.interfaces import HashAlgorithm


class UniversalHash(HashAlgorithm):
    """Strongly 2-universal hash family over GF(2) via affine randomized matrix mapping.

    Implements the Carter-Wegman linear congruence hash family:
        h_{A, b}(x) = (A @ x + b) mod 2

    where:
        - x in {0, 1}^n is the input key vector of length n (input_length).
        - A in {0, 1}^{m x n} is a binary matrix drawn uniformly at random.
        - b in {0, 1}^m is a binary affine bias vector drawn uniformly at random.
        - m is the target output length (output_length <= n).

    Properties:
        - Pairwise Independence (Strongly 2-Universal):
          For any distinct x1 != x2 in {0, 1}^n and any y1, y2 in {0, 1}^m,
          Pr_{A, b}[h_{A, b}(x1) = y1 and h_{A, b}(x2) = y2] = 2^{-2m},
          which implies collision probability Pr_{A, b}[h(x1) = h(x2)] = 2^{-m}.
        - Deterministic: Identical seed produces identical matrix A and vector b.

    Security Notice:
        This universal hash family is strictly designed for information-theoretic
        privacy amplification against eavesdroppers with bounded collision/min-entropy.
        It does NOT provide computational preimage resistance or cryptographic collision
        resistance in the sense of SHA-256 or SHA-3.
    """

    def __init__(self, seed: int = 42) -> None:
        """Initialize the Universal Hash algorithm with a deterministic seed.

        Args:
            seed: Pseudo-random generator seed for parameter generation.
        """
        self.seed = seed

    def generate_parameters(
        self, input_length: int, output_length: int
    ) -> tuple[np.ndarray, np.ndarray]:
        """Construct deterministic binary matrix A and affine vector b.

        Args:
            input_length: Dimension n of the input vector.
            output_length: Dimension m of the compressed output vector.

        Returns:
            Tuple of (matrix A with shape (m, n), vector b with shape (m,)).
        """
        rng = np.random.default_rng(self.seed)
        matrix_a = rng.integers(0, 2, size=(output_length, input_length), dtype=np.int8)
        vector_b = rng.integers(0, 2, size=output_length, dtype=np.int8)
        return matrix_a, vector_b

    def hash_key(self, key: Sequence[int], output_length: int) -> tuple[int, ...]:
        """Compress the key using affine matrix multiplication modulo 2.

        Args:
            key: Input binary key sequence of length n.
            output_length: Target compressed key length m (m <= n).

        Returns:
            Tuple of compressed binary bits of length m.

        Raises:
            PrivacyAmplificationError: If key is invalid or output_length exceeds input length.
        """
        input_length = len(key)
        if input_length == 0:
            raise PrivacyAmplificationError(
                "Input key cannot be empty.", code="QST-PRIV-701"
            )
        if output_length <= 0 or output_length > input_length:
            raise PrivacyAmplificationError(
                f"Output length ({output_length}) must be between 1 and input length ({input_length}).",
                code="QST-PRIV-703",
            )

        matrix_a, vector_b = self.generate_parameters(input_length, output_length)
        key_vector = np.array(key, dtype=np.int8)

        # Affine transform over GF(2): (A @ x + b) % 2
        hashed = (np.dot(matrix_a, key_vector) + vector_b) % 2
        return tuple(int(bit) for bit in hashed)

