"""Parity computation functions for error correction block checks.

References:
    Docs/10_API_SPECIFICATION.md
"""

from typing import Sequence


def calculate_parity(bits: Sequence[int]) -> int:
    """Compute the parity of a sequence of bits (0 or 1).

    Parity is defined as:
        0 if the count of '1' bits is even.
        1 if the count of '1' bits is odd.

    Args:
        bits: A sequence of binary bits (0 or 1).

    Returns:
        The parity bit value (0 or 1).
    """
    return sum(bits) % 2
