"""Unit tests for BINARY search error localization logic.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.correction.block import KeyBlock
from qst.correction.binary_search import perform_binary_search


@pytest.mark.unit
def test_binary_search_single_error() -> None:
    """Verify that perform_binary_search localizes a single error accurately."""
    alice_key = [1, 0, 1, 1, 0, 1, 0, 0]
    bob_key = [1, 0, 1, 0, 0, 1, 0, 0]  # Error at index 3

    # Check whole block search
    block = KeyBlock(original_indices=list(range(8)), pass_index=1, block_index=0)
    err_idx, messages, rounds, disclosed = perform_binary_search(
        block, alice_key, bob_key
    )

    assert err_idx == 3
    assert messages == 3  # log2(8) steps
    assert rounds == 3
    assert disclosed == 3


@pytest.mark.unit
def test_binary_search_multiple_errors_picks_one() -> None:
    """Verify that perform_binary_search returns one mismatch index even with multiple errors."""
    alice_key = [1, 0, 1, 1, 0, 1, 0, 0]
    bob_key = [0, 0, 1, 0, 0, 1, 0, 0]  # Errors at 0 and 3 (even count, parity matches)
    # But if we search a sub-segment with odd errors, it resolves one
    block = KeyBlock(original_indices=[0, 1, 2, 3], pass_index=1, block_index=0)

    err_idx, messages, rounds, disclosed = perform_binary_search(
        block, alice_key, bob_key
    )
    # Errors are at 0 and 3. Left half [0, 1] has error at 0. Right half [2, 3] has error at 3.
    # It should locate index 0 since left half has odd parities (alice [1, 0]=1, bob [0, 0]=0)
    assert err_idx == 0
