"""Privacy Amplification domain models.

References:
    Docs/10_API_SPECIFICATION.md §5
"""

import time
import math
from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class PrivacyAmplificationConfiguration:
    """Configuration parameters for the Privacy Amplification protocol."""

    compression_ratio: float = 0.5
    hash_algorithm: str = "toeplitz"
    seed: int = 42


@dataclass(frozen=True)
class FinalSecretKey:
    """Immutable model representing the distilled secret key after Privacy Amplification."""

    key_bits: tuple[int, ...]
    creation_timestamp: float = field(default_factory=time.time)
    shannon_entropy_estimate: float = field(init=False)
    min_entropy_estimate: float = field(init=False)

    def __post_init__(self) -> None:
        """Compute Shannon and Min-Entropy of the key sequence."""
        if not self.key_bits:
            object.__setattr__(self, "shannon_entropy_estimate", 0.0)
            object.__setattr__(self, "min_entropy_estimate", 0.0)
            return

        total = len(self.key_bits)
        count_0 = self.key_bits.count(0)
        count_1 = total - count_0

        p0 = count_0 / total
        p1 = count_1 / total

        # Shannon Entropy
        shannon = 0.0
        if p0 > 0.0:
            shannon -= p0 * math.log2(p0)
        if p1 > 0.0:
            shannon -= p1 * math.log2(p1)
        object.__setattr__(self, "shannon_entropy_estimate", shannon)

        # Min-Entropy
        p_max = max(p0, p1)
        min_entropy = -math.log2(p_max) if p_max > 0.0 else 0.0
        object.__setattr__(self, "min_entropy_estimate", min_entropy)


@dataclass(frozen=True)
class PrivacyStatistics:
    """Detailed benchmark and statistical telemetry for Privacy Amplification."""

    input_key_length: int
    output_key_length: int
    discarded_bits: int
    compression_percentage: float
    effective_key_rate: float
    estimated_security_parameter: float
    execution_time: float


@dataclass(frozen=True)
class PrivacyAmplificationResult:
    """Consolidated immutable container storing the distilled key and privacy metrics."""

    final_secret_key: FinalSecretKey
    input_key_length: int
    output_key_length: int
    compression_ratio: float
    hash_algorithm: str
    estimated_eve_information: float
    execution_time: float
    statistics: PrivacyStatistics
