"""Property-based invariant testing for final secret key rate sizes.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
import numpy as np
from qst.secret.validators import validate_key_lengths


@pytest.mark.property
def test_key_lengths_monotonically_decreasing() -> None:
    """Verify Raw >= Sifted >= Corrected >= Final holds for varying sizes."""
    rng = np.random.default_rng(12345)

    for _ in range(50):
        # Generate random ordered sizes
        raw = rng.integers(50, 1000)
        sifted = rng.integers(10, raw + 1)
        corrected = rng.integers(5, sifted + 1)
        final = rng.integers(1, corrected + 1)

        # Validator should pass without raising exceptions
        validate_key_lengths(
            raw=raw,
            sifted=sifted,
            corrected=corrected,
            final=final,
        )

        # Invalid cases should raise ValidationError / SecretKeyError
        with pytest.raises(Exception):
            validate_key_lengths(
                raw=raw,
                sifted=corrected,  # invalid order
                corrected=sifted,
                final=final,
            )
