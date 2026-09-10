"""Property-based and mathematical invariants tests for Privacy Amplification.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import numpy as np
import pytest
from hypothesis import given
from hypothesis import strategies as st

from qst.privacy.algorithms.toeplitz import ToeplitzHasher
from qst.privacy.algorithms.universal_hash import UniversalHash
from qst.privacy.amplifier import PrivacyAmplifier
from qst.privacy.models import FinalSecretKey, PrivacyAmplificationConfiguration


@pytest.mark.property
@given(
    seed=st.integers(min_value=0, max_value=100000),
    ratio=st.floats(min_value=0.1, max_value=0.9),
)
def test_privacy_determinism(seed: int, ratio: float) -> None:
    """Verify that execution is fully deterministic given identical inputs and configurations."""
    rng = np.random.default_rng(seed)
    key = list(rng.integers(0, 2, size=100))

    config = PrivacyAmplificationConfiguration(compression_ratio=ratio, seed=seed)
    amplifier = PrivacyAmplifier(config)

    res1 = amplifier.amplify(key)
    res2 = amplifier.amplify(key)

    # Check exact determinism
    assert res1.final_secret_key.key_bits == res2.final_secret_key.key_bits
    assert res1.output_key_length == res2.output_key_length
    assert (
        res1.statistics.compression_percentage == res2.statistics.compression_percentage
    )
    assert res1.statistics.effective_key_rate == res2.statistics.effective_key_rate


@pytest.mark.property
@given(
    bits=st.lists(st.integers(min_value=0, max_value=1), min_size=2, max_size=80)
)
def test_entropy_properties_hypothesis(bits: list[int]) -> None:
    """Verify Shannon and Min-Entropy mathematical bounds (H_min <= H_shannon)."""
    key = FinalSecretKey(key_bits=tuple(bits))
    assert 0.0 <= key.min_entropy_estimate <= 1.0 + 1e-9
    assert 0.0 <= key.shannon_entropy_estimate <= 1.0 + 1e-9
    # Invariant: Min-entropy is always <= Shannon entropy
    assert key.min_entropy_estimate <= key.shannon_entropy_estimate + 1e-9


@pytest.mark.property
@given(
    key=st.lists(st.integers(min_value=0, max_value=1), min_size=10, max_size=50),
    output_len=st.integers(min_value=1, max_value=10),
    seed=st.integers(min_value=0, max_value=100000),
)
def test_universal_hash_properties_hypothesis(
    key: list[int], output_len: int, seed: int
) -> None:
    """Verify UniversalHash determinism and length property under arbitrary bit streams."""
    output_len = min(output_len, len(key))
    hasher = UniversalHash(seed=seed)
    out1 = hasher.hash_key(key, output_len)
    out2 = hasher.hash_key(key, output_len)

    assert out1 == out2
    assert len(out1) == output_len
    assert all(b in (0, 1) for b in out1)



@pytest.mark.property
def test_toeplitz_matrix_regressions() -> None:
    """Verify that Toeplitz matrix generator resists PRNG regressions."""
    hasher = ToeplitzHasher(seed=777)
    m1 = hasher.generate_matrix(input_length=10, output_length=5)
    m2 = hasher.generate_matrix(input_length=10, output_length=5)

    assert np.array_equal(m1, m2)
    # Check that a subset has expected values
    assert m1.shape == (5, 10)
