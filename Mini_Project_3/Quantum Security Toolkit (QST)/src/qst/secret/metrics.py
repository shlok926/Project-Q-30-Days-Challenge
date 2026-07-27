"""SecretMetricsCalculator implementing rates, losses, and security level classification.

References:
    Docs/10_API_SPECIFICATION.md
"""

from typing import Optional
from qst.secret.models import (
    SecretKeyMetrics,
    SecurityLevel,
    SecurityClassificationConfig,
)
from qst.secret.validators import validate_key_lengths, validate_rates


class SecretMetricsCalculator:
    """Computes key rates, protocol losses, and security level classification."""

    def __init__(
        self,
        classification_config: Optional[SecurityClassificationConfig] = None,
    ) -> None:
        """Initialize the metrics calculator with classification thresholds.

        Args:
            classification_config: Configurable security classification thresholds.
        """
        self.config = classification_config or SecurityClassificationConfig()

    def calculate_metrics(
        self,
        raw_len: int,
        sifted_len: int,
        corrected_len: Optional[int],
        final_len: int,
        security_parameter: float,
    ) -> SecretKeyMetrics:
        """Calculate QKD key rate and protocol loss metrics.

        Args:
            raw_len: Raw key size.
            sifted_len: Sifted key size.
            corrected_len: Reconciled key size.
            final_len: Compressed final key size.
            security_parameter: Computed trace distance security parameter.

        Returns:
            A SecretKeyMetrics dataclass populated with rates and efficiencies.
        """
        validate_key_lengths(raw_len, sifted_len, corrected_len, final_len)

        # Handle fallback for corrected length if error correction was disabled
        active_corrected_len = (
            corrected_len
            if (corrected_len is not None and corrected_len > 0)
            else sifted_len
        )

        if raw_len > 0:
            denom = float(raw_len)
            raw_key_rate = raw_len / denom
            sifted_key_rate = sifted_len / denom
            corrected_key_rate = (
                (corrected_len / denom)
                if (corrected_len is not None)
                else sifted_key_rate
            )
            final_secret_key_rate = final_len / denom

            privacy_amplification_loss = (active_corrected_len - final_len) / denom
            error_correction_loss = (
                (sifted_len - corrected_len) / denom
                if (corrected_len is not None)
                else 0.0
            )
            total_protocol_loss = (raw_len - final_len) / denom
        else:
            raw_key_rate = 0.0
            sifted_key_rate = 0.0
            corrected_key_rate = 0.0
            final_secret_key_rate = 0.0
            privacy_amplification_loss = 0.0
            error_correction_loss = 0.0
            total_protocol_loss = 0.0

        # Validate rate bounds
        validate_rates(
            {
                "raw_key_rate": raw_key_rate,
                "sifted_key_rate": sifted_key_rate,
                "corrected_key_rate": corrected_key_rate,
                "final_secret_key_rate": final_secret_key_rate,
            }
        )

        compression_ratio = (
            final_len / active_corrected_len if active_corrected_len > 0 else 0.0
        )
        overall_efficiency = final_secret_key_rate

        return SecretKeyMetrics(
            raw_key_rate=raw_key_rate,
            sifted_key_rate=sifted_key_rate,
            corrected_key_rate=corrected_key_rate,
            final_secret_key_rate=final_secret_key_rate,
            compression_ratio=compression_ratio,
            overall_efficiency=overall_efficiency,
            security_parameter_summary=security_parameter,
            privacy_amplification_loss=privacy_amplification_loss,
            error_correction_loss=error_correction_loss,
            total_protocol_loss=total_protocol_loss,
        )

    def classify_security_level(self, security_parameter: float) -> SecurityLevel:
        """Classify key security level based on security parameter thresholds.

        Args:
            security_parameter: Computed trace distance security parameter.

        Returns:
            The SecurityLevel classification enum.
        """
        if security_parameter >= self.config.high_threshold:
            return SecurityLevel.HIGH
        elif security_parameter >= self.config.medium_threshold:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW
