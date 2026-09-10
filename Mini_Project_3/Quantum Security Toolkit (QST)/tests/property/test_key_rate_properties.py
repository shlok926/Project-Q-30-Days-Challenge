"""Property-based invariant testing for final secret key rate sizes.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from qst.secret.validators import validate_key_lengths


@pytest.mark.property
@given(
    raw=st.integers(min_value=50, max_value=2000),
    r1=st.floats(min_value=0.1, max_value=0.99),
    r2=st.floats(min_value=0.1, max_value=0.99),
    r3=st.floats(min_value=0.1, max_value=0.99),
)
def test_key_lengths_monotonically_decreasing(
    raw: int, r1: float, r2: float, r3: float
) -> None:
    """Verify Raw >= Sifted >= Corrected >= Final holds across generated sizes."""
    sifted = max(1, int(raw * r1))
    corrected = max(1, int(sifted * r2))
    final = max(1, int(corrected * r3))

    validate_key_lengths(
        raw=raw,
        sifted=sifted,
        corrected=corrected,
        final=final,
    )


@pytest.mark.property
@given(
    smaller=st.integers(min_value=10, max_value=500),
    larger=st.integers(min_value=501, max_value=1000),
)
def test_invalid_key_length_ordering_raises(smaller: int, larger: int) -> None:
    """Verify out-of-order key lengths always fail validation."""
    with pytest.raises(Exception):
        validate_key_lengths(
            raw=smaller,
            sifted=larger,
            corrected=smaller,
            final=smaller,
        )

