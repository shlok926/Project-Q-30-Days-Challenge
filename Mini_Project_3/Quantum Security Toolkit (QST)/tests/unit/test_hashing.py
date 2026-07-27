"""Unit tests for PrivacyAmplifier validation rules and boundary checking.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.privacy.exceptions import PrivacyAmplificationError
from qst.privacy.models import PrivacyAmplificationConfiguration
from qst.privacy.amplifier import PrivacyAmplifier


@pytest.mark.unit
def test_amplifier_valid_run() -> None:
    """Verify that a standard amplifier run yields matching sizes and stats."""
    config = PrivacyAmplificationConfiguration(compression_ratio=0.6, seed=42)
    amplifier = PrivacyAmplifier(config)

    key = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]
    res = amplifier.amplify(key)

    assert len(res.final_secret_key.key_bits) == 6
    assert res.input_key_length == 10
    assert res.output_key_length == 6
    assert res.compression_ratio == 0.6
    assert res.statistics.discarded_bits == 4
    assert res.statistics.compression_percentage == 60.0
    assert res.statistics.effective_key_rate == 0.6


@pytest.mark.unit
def test_amplifier_empty_key() -> None:
    """Verify error raised for empty key input."""
    amplifier = PrivacyAmplifier(PrivacyAmplificationConfiguration())
    with pytest.raises(PrivacyAmplificationError) as exc:
        amplifier.amplify([])
    assert "QST-PRIV-701" in str(exc.value)


@pytest.mark.unit
def test_amplifier_non_binary_key() -> None:
    """Verify error raised if input key contains non-binary values."""
    amplifier = PrivacyAmplifier(PrivacyAmplificationConfiguration())
    with pytest.raises(PrivacyAmplificationError) as exc:
        amplifier.amplify([1, 2, 0])
    assert "QST-PRIV-701" in str(exc.value)


@pytest.mark.unit
def test_amplifier_invalid_compression_ratio() -> None:
    """Verify error raised for invalid compression ratios."""
    with pytest.raises(PrivacyAmplificationError) as exc:
        PrivacyAmplifier(PrivacyAmplificationConfiguration(compression_ratio=-0.1))
    assert "QST-PRIV-702" in str(exc.value)

    with pytest.raises(PrivacyAmplificationError) as exc:
        PrivacyAmplifier(PrivacyAmplificationConfiguration(compression_ratio=1.5))
    assert "QST-PRIV-702" in str(exc.value)


@pytest.mark.unit
def test_amplifier_invalid_algorithm() -> None:
    """Verify error raised for unsupported hashing algorithms."""
    with pytest.raises(PrivacyAmplificationError) as exc:
        PrivacyAmplifier(
            PrivacyAmplificationConfiguration(hash_algorithm="invalid_hash")
        )
    assert "QST-PRIV-704" in str(exc.value)
