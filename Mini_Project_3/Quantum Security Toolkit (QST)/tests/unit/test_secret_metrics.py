"""Unit tests for SecretMetricsCalculator, validators, and security levels.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.secret.exceptions import SecretKeyError
from qst.secret.models import SecurityClassificationConfig, SecurityLevel
from qst.secret.metrics import SecretMetricsCalculator


@pytest.mark.unit
def test_calculator_rates_and_losses() -> None:
    """Verify metrics calculation and QKD rate formulas."""
    calculator = SecretMetricsCalculator()

    # Raw=100, Sifted=50, Corrected=45, Final=30
    metrics = calculator.calculate_metrics(
        raw_len=100,
        sifted_len=50,
        corrected_len=45,
        final_len=30,
        security_parameter=6.0,
    )

    assert metrics.raw_key_rate == 1.0
    assert metrics.sifted_key_rate == 0.5
    assert metrics.corrected_key_rate == 0.45
    assert metrics.final_secret_key_rate == 0.3
    assert metrics.compression_ratio == pytest.approx(30 / 45)
    assert metrics.overall_efficiency == 0.3

    # Loss checks
    assert metrics.error_correction_loss == 0.05
    assert metrics.privacy_amplification_loss == 0.15
    assert metrics.total_protocol_loss == 0.7


@pytest.mark.unit
def test_calculator_validation_exceptions() -> None:
    """Verify validator checking non-monotonically decreasing key sizes."""
    calculator = SecretMetricsCalculator()

    # Raw < Sifted
    with pytest.raises(SecretKeyError) as exc:
        calculator.calculate_metrics(
            raw_len=50,
            sifted_len=100,
            corrected_len=45,
            final_len=30,
            security_parameter=1.0,
        )
    assert "QST-SEC-701" in str(exc.value)

    # Sifted < Corrected
    with pytest.raises(SecretKeyError) as exc:
        calculator.calculate_metrics(
            raw_len=100,
            sifted_len=40,
            corrected_len=45,
            final_len=30,
            security_parameter=1.0,
        )
    assert "QST-SEC-701" in str(exc.value)

    # Corrected < Final
    with pytest.raises(SecretKeyError) as exc:
        calculator.calculate_metrics(
            raw_len=100,
            sifted_len=50,
            corrected_len=20,
            final_len=30,
            security_parameter=1.0,
        )
    assert "QST-SEC-701" in str(exc.value)


@pytest.mark.unit
def test_security_level_classification() -> None:
    """Verify configurable thresholds map correctly to SecurityLevel."""
    # Use default thresholds: high=10.0, medium=4.0
    calc_default = SecretMetricsCalculator()
    assert calc_default.classify_security_level(12.0) == SecurityLevel.HIGH
    assert calc_default.classify_security_level(5.0) == SecurityLevel.MEDIUM
    assert calc_default.classify_security_level(2.0) == SecurityLevel.LOW

    # Custom thresholds config: high=15.0, medium=8.0
    config = SecurityClassificationConfig(high_threshold=15.0, medium_threshold=8.0)
    calc_custom = SecretMetricsCalculator(config)
    assert calc_custom.classify_security_level(12.0) == SecurityLevel.MEDIUM
    assert calc_custom.classify_security_level(9.0) == SecurityLevel.MEDIUM
    assert calc_custom.classify_security_level(7.0) == SecurityLevel.LOW
    assert calc_custom.classify_security_level(16.0) == SecurityLevel.HIGH
