"""Unit tests for the QST KeySiftingService.

References:
    Docs/BB84_SPEC.md §1 Step 8
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.core.bb84.sifting import KeySiftingService
from qst.exceptions.validation import ValidationError
from qst.models.results import ReconciliationResult


@pytest.mark.unit
def test_sifting_valid() -> None:
    """Verify sifting correctly selects matches and preserves bit ordering."""
    service = KeySiftingService()
    alice_bits = (1, 0, 1, 1, 0)
    bob_bits = (1, 1, 1, 0, 0)

    recon = ReconciliationResult(
        matching_indices=(0, 2, 4),
        discarded_indices=(1, 3),
        matching_bases=("Z", "X", "Z"),
        total_bits=5,
        matching_count=3,
        match_rate=0.6,
    )

    res = service.sift_keys(alice_bits, bob_bits, recon)
    assert res.alice_key == (1, 1, 0)
    assert res.bob_key == (1, 1, 0)
    assert res.key_length == 3


@pytest.mark.unit
def test_sifting_empty() -> None:
    """Verify sifting works when no matching indices are reconciliated."""
    service = KeySiftingService()
    alice_bits = (1, 0)
    bob_bits = (1, 1)

    recon = ReconciliationResult(
        matching_indices=(),
        discarded_indices=(0, 1),
        matching_bases=(),
        total_bits=2,
        matching_count=0,
        match_rate=0.0,
    )

    res = service.sift_keys(alice_bits, bob_bits, recon)
    assert res.alice_key == ()
    assert res.bob_key == ()
    assert res.key_length == 0


@pytest.mark.unit
def test_sifting_invalid_inputs() -> None:
    """Verify sifting flags incorrect key lengths or total bit mismatches."""
    service = KeySiftingService()

    recon = ReconciliationResult(
        matching_indices=(0,),
        discarded_indices=(),
        matching_bases=("Z",),
        total_bits=1,
        matching_count=1,
        match_rate=1.0,
    )

    # Key lengths mismatch
    with pytest.raises(ValidationError) as exc:
        service.sift_keys((1, 0), (1,), recon)
    assert "QST-VAL-802" in str(exc.value)

    # Key length does not match reconciliation total bits
    with pytest.raises(ValidationError) as exc:
        service.sift_keys((1, 0), (1, 0), recon)
    assert "QST-VAL-803" in str(exc.value)


@pytest.mark.unit
def test_reconciliation_result_validation_unsorted() -> None:
    """Verify ReconciliationResult validates sorted matching indices."""
    with pytest.raises(ValidationError) as exc:
        ReconciliationResult(
            matching_indices=(1, 0),
            discarded_indices=(),
            matching_bases=("Z", "X"),
            total_bits=2,
            matching_count=2,
            match_rate=1.0,
        )
    assert "QST-VAL-505" in str(exc.value)


@pytest.mark.unit
def test_reconciliation_result_validation_non_unique() -> None:
    """Verify ReconciliationResult validates unique matching indices."""
    with pytest.raises(ValidationError) as exc:
        ReconciliationResult(
            matching_indices=(0, 0),
            discarded_indices=(),
            matching_bases=("Z", "Z"),
            total_bits=2,
            matching_count=2,
            match_rate=1.0,
        )
    assert "QST-VAL-506" in str(exc.value)


@pytest.mark.unit
def test_reconciliation_result_validation_out_of_bounds() -> None:
    """Verify ReconciliationResult validates index bounds checks."""
    with pytest.raises(ValidationError) as exc:
        ReconciliationResult(
            matching_indices=(0, 2),
            discarded_indices=(),
            matching_bases=("Z", "Z"),
            total_bits=2,
            matching_count=2,
            match_rate=1.0,
        )
    assert "QST-VAL-507" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        ReconciliationResult(
            matching_indices=(0,),
            discarded_indices=(2,),
            matching_bases=("Z",),
            total_bits=2,
            matching_count=1,
            match_rate=0.5,
        )
    assert "QST-VAL-508" in str(exc.value)


@pytest.mark.unit
def test_new_domain_models_validation_failures() -> None:
    """Verify validation boundaries check on ReconciliationResult and SiftedKeyResult."""
    from qst.models.results import SiftedKeyResult

    # ReconciliationResult negative total bits
    with pytest.raises(ValidationError) as exc:
        ReconciliationResult(
            matching_indices=(),
            discarded_indices=(),
            matching_bases=(),
            total_bits=-1,
            matching_count=0,
            match_rate=0.0,
        )
    assert "QST-VAL-513" in str(exc.value)

    # ReconciliationResult matching count mismatch
    with pytest.raises(ValidationError) as exc:
        ReconciliationResult(
            matching_indices=(0,),
            discarded_indices=(),
            matching_bases=("Z",),
            total_bits=1,
            matching_count=5,
            match_rate=1.0,
        )
    assert "QST-VAL-509" in str(exc.value)

    # ReconciliationResult match rate out of bounds
    with pytest.raises(ValidationError) as exc:
        ReconciliationResult(
            matching_indices=(0,),
            discarded_indices=(),
            matching_bases=("Z",),
            total_bits=1,
            matching_count=1,
            match_rate=1.5,
        )
    assert "QST-VAL-510" in str(exc.value)

    # SiftedKeyResult key lengths mismatch
    with pytest.raises(ValidationError) as exc:
        SiftedKeyResult(alice_key=(1, 0), bob_key=(1,), key_length=2)
    assert "QST-VAL-511" in str(exc.value)

    # SiftedKeyResult key length mismatch
    with pytest.raises(ValidationError) as exc:
        SiftedKeyResult(alice_key=(1, 0), bob_key=(1, 0), key_length=5)
    assert "QST-VAL-512" in str(exc.value)
