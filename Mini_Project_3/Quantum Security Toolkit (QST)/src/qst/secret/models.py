"""Secret key metrics and final summary models.

References:
    Docs/10_API_SPECIFICATION.md §5
"""

from enum import Enum
from dataclasses import dataclass, field


class SecurityLevel(Enum):
    """Classification of cryptographic key security levels."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass(frozen=True)
class SecurityClassificationConfig:
    """Configurable thresholds for SecurityLevel classification."""

    high_threshold: float = 10.0
    medium_threshold: float = 4.0


@dataclass(frozen=True)
class SecretKeyMetrics:
    """Cryptographic rates, efficiencies, and information loss metrics."""

    raw_key_rate: float
    sifted_key_rate: float
    corrected_key_rate: float
    final_secret_key_rate: float
    compression_ratio: float
    overall_efficiency: float
    security_parameter_summary: float
    privacy_amplification_loss: float
    error_correction_loss: float
    total_protocol_loss: float


@dataclass(frozen=True)
class ProtocolSummary:
    """High-level summary of the entire BB84 protocol execution."""

    raw_key_length: int
    sifted_key_length: int
    corrected_key_length: int
    final_key_length: int
    qber: float
    correction_enabled: bool
    privacy_enabled: bool
    overall_success: bool
    execution_mode: str
    protocol_name: str = "BB84"
