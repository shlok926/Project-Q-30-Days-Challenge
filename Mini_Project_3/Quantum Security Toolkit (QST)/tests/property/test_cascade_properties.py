"""Property-based and mathematical invariants tests for Cascade Error Correction.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from qst.correction.cascade import CascadeReconciler
from qst.correction.models import CascadeConfiguration


@pytest.mark.property
@given(
    seed=st.integers(min_value=0, max_value=10000),
    num_passes=st.integers(min_value=1, max_value=4),
)
def test_cascade_determinism(seed: int, num_passes: int) -> None:
    """Verify that execution is fully deterministic given identical inputs and configurations."""
    rng = np.random.default_rng(seed)
    alice_key = list(rng.integers(0, 2, size=100))
    bob_key = list(alice_key)
    err_indices = rng.choice(100, size=4, replace=False)
    for idx in err_indices:
        bob_key[idx] = 1 - bob_key[idx]

    config = CascadeConfiguration(seed=seed, num_passes=num_passes, block_sizes=(8, 16))
    reconciler = CascadeReconciler(config)

    # Run multiple times
    res1 = reconciler.reconcile(alice_key, bob_key)
    res2 = reconciler.reconcile(alice_key, bob_key)

    # Verify exact equivalences
    assert res1.corrected_key.key_bits == res2.corrected_key.key_bits
    assert res1.corrected_bit_positions == res2.corrected_bit_positions
    assert res1.parity_messages_exchanged == res2.parity_messages_exchanged
    assert res1.communication_rounds == res2.communication_rounds
    assert res1.correction_efficiency == res2.correction_efficiency
    assert res1.estimated_qber_after_correction == res2.estimated_qber_after_correction


@pytest.mark.property
@given(
    key=st.lists(st.integers(min_value=0, max_value=1), min_size=16, max_size=64),
    seed=st.integers(min_value=0, max_value=10000),
)
def test_cascade_identity_reconciliation(key: list[int], seed: int) -> None:
    """When Alice and Bob share identical keys, Cascade reconciles without modifying bits."""
    config = CascadeConfiguration(seed=seed, num_passes=2, block_sizes=(4, 8))
    reconciler = CascadeReconciler(config)
    res = reconciler.reconcile(key, list(key))
    assert list(res.corrected_key.key_bits) == key
    assert res.estimated_qber_after_correction == 0.0
    assert res.corrected_error_count == 0



@pytest.mark.property
def test_cascade_invariants_efficiency_bound() -> None:
    """Verify Shannon efficiency bounds and error correction success invariants."""
    rng = np.random.default_rng(100)
    # Generate keys across different lengths and error counts
    for length in [50, 100, 200]:
        alice_key = list(rng.integers(0, 2, size=length))
        bob_key = list(alice_key)

        # Introduce approx 5% errors
        n_errors = max(1, int(length * 0.05))
        err_indices = rng.choice(length, size=n_errors, replace=False)
        for idx in err_indices:
            bob_key[idx] = 1 - bob_key[idx]

        config = CascadeConfiguration(seed=1234, num_passes=4, block_sizes=(2, 4, 8))
        reconciler = CascadeReconciler(config)
        res = reconciler.reconcile(alice_key, bob_key)

        # 1. Verification of correct key resolution
        assert list(res.corrected_key.key_bits) == alice_key
        assert res.estimated_qber_after_correction == 0.0
        assert res.corrected_error_count == n_errors

        # 2. Shannon limit bounds verification
        # The number of bits disclosed must be positive and efficiency > 0
        assert res.bits_disclosed > 0
        assert res.correction_efficiency > 0.0
