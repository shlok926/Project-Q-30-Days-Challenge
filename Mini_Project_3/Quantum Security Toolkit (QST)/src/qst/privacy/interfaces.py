"""Hash Algorithm interface for extensible Privacy Amplification hashing families.

References:
    Docs/10_API_SPECIFICATION.md
"""

from abc import ABC, abstractmethod
from typing import Sequence


class HashAlgorithm(ABC):
    """Abstract base interface representing a family of hash functions used for Privacy Amplification."""

    @abstractmethod
    def hash_key(self, key: Sequence[int], output_length: int) -> tuple[int, ...]:
        """Compress the input key into a secure output key of the specified length.

        Args:
            key: The input binary sequence to hash (sifted or corrected key).
            output_length: The target output length for the compressed key.

        Returns:
            A tuple of binary bits (0 or 1) representing the final secret key.
        """
        pass
