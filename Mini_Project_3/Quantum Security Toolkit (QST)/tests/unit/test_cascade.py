"""Unit tests for CascadeErrorCorrection reconciler and validators.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.correction.exceptions import CorrectionError
from qst.correction.models import CascadeConfiguration
from qst.correction.cascade import CascadeReconciler


@pytest.mark.unit
def test_cascade_reconciliation_zero_errors() -> None:
    """Verify that identical keys require no correction and terminate early."""
    alice_key = [1, 0, 1, 0, 1, 1, 0, 0]
    bob_key = [1, 0, 1, 0, 1, 1, 0, 0]

    config = CascadeConfiguration(num_passes=4, block_sizes=(4, 8))
    reconciler = CascadeReconciler(config)

    res = reconciler.reconcile(alice_key, bob_key)

    assert res.corrected_error_count == 0
    assert res.estimated_qber_after_correction == 0.0
    # Because of early termination check on pass 1 (before block checks),
    # messages, rounds, and disclosed bits should be 0.
    assert res.parity_messages_exchanged == 0
    assert res.communication_rounds == 0
    assert res.bits_disclosed == 0
    assert res.passes_completed == 0
    assert list(res.corrected_key.key_bits) == alice_key


@pytest.mark.unit
def test_cascade_reconciliation_single_error() -> None:
    """Verify Cascade corrects a single-bit mismatch successfully."""
    alice_key = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1]
    bob_key = [1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1]  # error at index 5

    config = CascadeConfiguration(num_passes=2, block_sizes=(4, 8))
    reconciler = CascadeReconciler(config)

    res = reconciler.reconcile(alice_key, bob_key)

    assert res.corrected_error_count == 1
    assert res.corrected_bit_positions == (5,)
    assert res.estimated_qber_after_correction == 0.0
    assert list(res.corrected_key.key_bits) == alice_key


@pytest.mark.unit
def test_cascade_reconciliation_multi_errors() -> None:
    """Verify Cascade corrects multiple distributed errors successfully."""
    alice_key = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1]
    bob_key = [1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1]  # errors at 1, 5, 12

    config = CascadeConfiguration(num_passes=4, block_sizes=(4, 8, 16))
    reconciler = CascadeReconciler(config)

    res = reconciler.reconcile(alice_key, bob_key)

    assert res.corrected_error_count == 3
    assert set(res.corrected_bit_positions) == {1, 5, 12}
    assert res.estimated_qber_after_correction == 0.0
    assert list(res.corrected_key.key_bits) == alice_key


@pytest.mark.unit
def test_cascade_validators_exceptions() -> None:
    """Verify validator checking empty keys, mismatched length, and configurations."""
    reconciler = CascadeReconciler(CascadeConfiguration())

    # Empty keys check
    with pytest.raises(CorrectionError) as exc:
        reconciler.reconcile([], [1])
    assert "QST-CORR-701" in str(exc.value)

    # Length mismatch check
    with pytest.raises(CorrectionError) as exc:
        reconciler.reconcile([1, 0], [1])
    assert "QST-CORR-702" in str(exc.value)

    # Mismatched bits check
    with pytest.raises(CorrectionError) as exc:
        reconciler.reconcile([2, 0], [1, 0])
    assert "QST-CORR-703" in str(exc.value)

    # Config mismatch check
    with pytest.raises(CorrectionError) as exc:
        CascadeReconciler(CascadeConfiguration(num_passes=-1))
    assert "QST-CORR-703" in str(exc.value)

    with pytest.raises(CorrectionError) as exc:
        CascadeReconciler(CascadeConfiguration(block_sizes=()))
    assert "QST-CORR-703" in str(exc.value)
