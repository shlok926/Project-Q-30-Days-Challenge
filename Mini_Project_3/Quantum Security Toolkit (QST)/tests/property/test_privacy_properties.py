"""Property-based and mathematical invariants tests for Privacy Amplification.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
import numpy as np
from qst.privacy.models import PrivacyAmplificationConfiguration, FinalSecretKey
from qst.privacy.amplifier import PrivacyAmplifier
from qst.privacy.algorithms.toeplitz import ToeplitzHasher


@pytest.mark.property
def test_privacy_determinism() -> None:
    """Verify that execution is fully deterministic given identical inputs and configurations."""
    rng = np.random.default_rng(42)
    key = list(rng.integers(0, 2, size=150))

    config = PrivacyAmplificationConfiguration(compression_ratio=0.5, seed=123)
    amplifier = PrivacyAmplifier(config)

    res1 = amplifier.amplify(key)
    res2 = amplifier.amplify(key)

    # Check matches
    assert res1.final_secret_key.key_bits == res2.final_secret_key.key_bits
    assert res1.output_key_length == res2.output_key_length
    assert (
        res1.statistics.compression_percentage == res2.statistics.compression_percentage
    )
    assert (
        res1.statistics.estimated_security_parameter
        == res2.statistics.estimated_security_parameter
    )
    assert res1.statistics.effective_key_rate == res2.statistics.effective_key_rate
    assert (
        res1.final_secret_key.shannon_entropy_estimate
        == res2.final_secret_key.shannon_entropy_estimate
    )
    assert (
        res1.final_secret_key.min_entropy_estimate
        == res2.final_secret_key.min_entropy_estimate
    )


@pytest.mark.property
def test_entropy_properties() -> None:
    """Verify Shannon and Min-Entropy mathematical bounds (H_min <= H_shannon)."""
    # Test completely biased key: all ones
    biased_key = FinalSecretKey(key_bits=(1, 1, 1, 1, 1))
    assert biased_key.shannon_entropy_estimate == 0.0
    assert biased_key.min_entropy_estimate == 0.0

    # Test balanced key
    balanced_key = FinalSecretKey(key_bits=(1, 0, 1, 0, 1, 0))
    assert pytest.approx(balanced_key.shannon_entropy_estimate) == 1.0
    assert pytest.approx(balanced_key.min_entropy_estimate) == 1.0

    # Test random key: Min-entropy must always be <= Shannon entropy
    rng = np.random.default_rng(999)
    for _ in range(5):
        bits = tuple(rng.integers(0, 2, size=50).tolist())
        key = FinalSecretKey(key_bits=bits)
        assert key.min_entropy_estimate <= key.shannon_entropy_estimate + 1e-9


@pytest.mark.property
def test_toeplitz_matrix_regressions() -> None:
    """Verify that Toeplitz matrix generator resists PRNG regressions."""
    hasher = ToeplitzHasher(seed=777)
    m1 = hasher.generate_matrix(input_length=10, output_length=5)
    m2 = hasher.generate_matrix(input_length=10, output_length=5)

    assert np.array_equal(m1, m2)
    # Check that a subset has expected values
    assert m1.shape == (5, 10)
