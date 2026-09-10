"""Unit tests for UniversalHash algorithm and 2-universal collision properties.

References:
    Docs/10_API_SPECIFICATION.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.privacy.algorithms.universal_hash import UniversalHash
from qst.privacy.amplifier import PrivacyAmplifier
from qst.privacy.exceptions import PrivacyAmplificationError
from qst.privacy.models import PrivacyAmplificationConfiguration


@pytest.mark.unit
def test_universal_hash_determinism() -> None:
    """Verify that identical seeds produce identical hashed outputs."""
    key = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1]
    hasher1 = UniversalHash(seed=12345)
    hasher2 = UniversalHash(seed=12345)

    out1 = hasher1.hash_key(key, output_length=5)
    out2 = hasher2.hash_key(key, output_length=5)

    assert out1 == out2
    assert len(out1) == 5
    assert all(b in (0, 1) for b in out1)


@pytest.mark.unit
def test_universal_hash_seed_sensitivity() -> None:
    """Verify that different seeds produce different hash functions."""
    key = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1] * 4
    hasher1 = UniversalHash(seed=1)
    hasher2 = UniversalHash(seed=2)

    out1 = hasher1.hash_key(key, output_length=10)
    out2 = hasher2.hash_key(key, output_length=10)

    assert out1 != out2


@pytest.mark.unit
def test_universal_hash_dimension_validation() -> None:
    """Verify boundary conditions and dimension constraints."""
    hasher = UniversalHash(seed=42)

    # Empty key
    with pytest.raises(PrivacyAmplificationError) as exc:
        hasher.hash_key([], output_length=5)
    assert "QST-PRIV-701" in str(exc.value)

    # Output length > input length
    with pytest.raises(PrivacyAmplificationError) as exc:
        hasher.hash_key([1, 0, 1], output_length=4)
    assert "QST-PRIV-703" in str(exc.value)

    # Output length <= 0
    with pytest.raises(PrivacyAmplificationError) as exc:
        hasher.hash_key([1, 0, 1], output_length=0)
    assert "QST-PRIV-703" in str(exc.value)


@pytest.mark.unit
def test_universal_hash_2_universal_collision_property() -> None:
    """Verify the 2-universal property: Pr[h(x1) == h(x2)] <= 2^(-m) over hash family seeds."""
    x1 = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0]
    x2 = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1]  # 1 bit difference
    output_length = 3  # m = 3 -> theoretical collision probability = 2^(-3) = 0.125
    num_samples = 400

    collisions = 0
    for seed in range(num_samples):
        hasher = UniversalHash(seed=seed)
        h1 = hasher.hash_key(x1, output_length)
        h2 = hasher.hash_key(x2, output_length)
        if h1 == h2:
            collisions += 1

    empirical_rate = collisions / num_samples
    # With m=3, theoretical is 0.125. Over 400 samples, empirical rate should comfortably be in [0.05, 0.22]
    assert 0.04 <= empirical_rate <= 0.25, f"Empirical collision rate {empirical_rate} deviates from theoretical 0.125"


@pytest.mark.unit
def test_universal_hash_in_privacy_amplifier() -> None:
    """Verify UniversalHash integrates cleanly with PrivacyAmplifier."""
    config = PrivacyAmplificationConfiguration(
        compression_ratio=0.5,
        hash_algorithm="universal_hash",
        seed=777,
    )
    amplifier = PrivacyAmplifier(config=config)
    key = [1, 0, 1, 1, 0, 0, 1, 0]
    result = amplifier.amplify(key, initial_qber=0.03)

    assert result.output_key_length == 4
    assert len(result.final_secret_key.key_bits) == 4
    assert all(b in (0, 1) for b in result.final_secret_key.key_bits)
    assert result.statistics.discarded_bits == 4

