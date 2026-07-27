"""Universal Hashing algorithm placeholder.

References:
    Docs/10_API_SPECIFICATION.md
"""

from typing import Sequence
from qst.privacy.interfaces import HashAlgorithm


class UniversalHash(HashAlgorithm):
    """Stub implementation for future 2-universal hash family extensions."""

    def __init__(self, seed: int = 42) -> None:
        """Initialize the Universal Hash algorithm.

        Args:
            seed: Configured seed.
        """
        self.seed = seed

    def hash_key(self, key: Sequence[int], output_length: int) -> tuple[int, ...]:
        """Hashing execution placeholder.

        Args:
            key: Input key.
            output_length: Output length.
        """
        raise NotImplementedError(
            "Alternative Universal Hash algorithm is not yet supported in this version."
        )
