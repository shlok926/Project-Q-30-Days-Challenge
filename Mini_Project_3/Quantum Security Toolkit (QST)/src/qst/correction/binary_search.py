"""Binary search implementation for localizing single-bit errors in odd-parity blocks.

References:
    Docs/10_API_SPECIFICATION.md
"""

from typing import Sequence
from qst.correction.parity import calculate_parity
from qst.correction.block import KeyBlock


def perform_binary_search(
    block: KeyBlock,
    alice_key: Sequence[int],
    bob_key: Sequence[int],
) -> tuple[int, int, int, int]:
    """Execute BINARY search to localize a single-bit discrepancy between Alice and Bob.

    Args:
        block: The KeyBlock containing the mismatch.
        alice_key: Alice's sifted key bits.
        bob_key: Bob's sifted key bits.

    Returns:
        A tuple containing:
          - The original index of the localized error (int).
          - Parity messages exchanged during search (int).
          - Communication rounds used (int).
          - Bits of parity information disclosed (int).
    """
    indices = block.indices
    low = 0
    high = len(indices) - 1

    messages = 0
    rounds = 0
    disclosed = 0

    while low < high:
        mid = (low + high) // 2
        # Partition left sub-segment
        left_sub = indices[low : mid + 1]

        # Calculate parities
        a_parity = calculate_parity([alice_key[idx] for idx in left_sub])
        b_parity = calculate_parity([bob_key[idx] for idx in left_sub])

        messages += 1
        rounds += 1
        disclosed += 1

        if a_parity != b_parity:
            # Mismatch exists in the left half
            high = mid
        else:
            # Mismatch exists in the right half
            low = mid + 1

    return indices[low], messages, rounds, disclosed
