"""Property-based and mathematical invariants tests for Cascade Error Correction.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
import numpy as np
from qst.correction.models import CascadeConfiguration
from qst.correction.cascade import CascadeReconciler


@pytest.mark.property
def test_cascade_determinism() -> None:
    """Verify that execution is fully deterministic given identical inputs and configurations."""
    rng = np.random.default_rng(42)
    alice_key = list(rng.integers(0, 2, size=200))
    # Introduce 10 random errors
    bob_key = list(alice_key)
    err_indices = rng.choice(200, size=10, replace=False)
    for idx in err_indices:
        bob_key[idx] = 1 - bob_key[idx]

    config = CascadeConfiguration(seed=99, num_passes=4, block_sizes=(8, 16))
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
