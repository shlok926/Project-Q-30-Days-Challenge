"""Unit tests for the QST AliceStatePreparer.

References:
    Docs/BB84_SPEC.md §1 Steps 1-2
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.core.shared.random.random_provider import NumpyRandomProvider
from qst.core.bb84.state_preparation import AliceStatePreparer
from qst.exceptions.validation import ValidationError


@pytest.mark.unit
def test_alice_state_preparer_valid() -> None:
    """Verify state preparer configures bits/bases and logs metadata."""
    prov = NumpyRandomProvider(seed=42)
    preparer = AliceStatePreparer(prov)

    # State metadata before prepare
    meta = preparer.metadata
    assert not meta["state_prepared"]
    assert meta["length"] == 0

    # Prepare
    bits, bases = preparer.prepare_state(10)
    assert len(bits) == 10
    assert len(bases) == 10
    assert preparer.bits == bits
    assert preparer.bases == bases

    # State metadata after prepare
    meta = preparer.metadata
    assert meta["state_prepared"]
    assert meta["length"] == 10


@pytest.mark.unit
def test_alice_state_preparer_invalid() -> None:
    """Verify state preparer raises ValidationError on out-of-bounds parameters."""
    prov = NumpyRandomProvider(seed=42)
    preparer = AliceStatePreparer(prov)

    with pytest.raises(ValidationError) as exc:
        preparer.prepare_state(-1)
    assert "QST-VAL-102" in str(exc.value)
