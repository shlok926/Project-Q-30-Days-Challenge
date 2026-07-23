"""Abstract and concrete random provider implementations for QKD simulations.

References:
    Docs/06_TECHNICAL_REQUIREMENTS.md §2
    Docs/07_SYSTEM_ARCHITECTURE.md §8
    Docs/BB84_SPEC.md §4
"""

import abc
from typing import Optional, Sequence

import numpy as np


class RandomProvider(abc.ABC):
    """Abstract interface defining the requirements for QKD random generation.

    Decouples protocol logic from specific random source generators (NumPy,
    cryptographic hardware, quantum RNGs, etc.).
    """

    @abc.abstractmethod
    def generate_bits(self, length: int) -> tuple[int, ...]:
        """Generate a sequence of random classical bits (0 or 1).

        Args:
            length: Number of bits to generate.

        Returns:
            An immutable tuple of integers (0 or 1).
        """
        pass

    @abc.abstractmethod
    def generate_bases(
        self, length: int, allowed_bases: Sequence[str]
    ) -> tuple[str, ...]:
        """Generate a sequence of random measurement bases.

        Args:
            length: Number of bases to generate.
            allowed_bases: Sequence of valid basis identifiers (e.g. ('Z', 'X')).

        Returns:
            An immutable tuple of basis strings.
        """
        pass


class NumpyRandomProvider(RandomProvider):
    """Concrete implementation of RandomProvider using NumPy.

    Ensures reproducible and deterministic generation using a seeded Generator.
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """Initialize the NumPy random provider.

        Args:
            seed: Optional integer seed for generator initialization.
        """
        self._rng = np.random.default_rng(seed)

    def generate_bits(self, length: int) -> tuple[int, ...]:
        """Generate a sequence of random classical bits (0 or 1).

        Args:
            length: Number of bits to generate.

        Returns:
            An immutable tuple of integers (0 or 1).
        """
        if length <= 0:
            return ()
        bits = self._rng.integers(0, 2, size=length)
        return tuple(int(b) for b in bits)

    def generate_bases(
        self, length: int, allowed_bases: Sequence[str]
    ) -> tuple[str, ...]:
        """Generate a sequence of random measurement bases.

        Args:
            length: Number of bases to generate.
            allowed_bases: Sequence of valid basis identifiers (e.g. ('Z', 'X')).

        Returns:
            An immutable tuple of basis strings.
        """
        if length <= 0 or not allowed_bases:
            return ()
        bases = self._rng.choice(allowed_bases, size=length)
        return tuple(str(b) for b in bases)
