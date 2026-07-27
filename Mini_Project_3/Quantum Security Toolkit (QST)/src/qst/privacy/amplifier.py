"""Privacy Amplifier executor coordinating key hashing and metrics calculations.

References:
    Docs/10_API_SPECIFICATION.md
"""

import time
import math
from typing import Sequence
from qst.privacy.exceptions import PrivacyAmplificationError
from qst.privacy.validators import (
    validate_key,
    validate_privacy_config,
    validate_dimensions,
)
from qst.privacy.models import (
    PrivacyAmplificationConfiguration,
    FinalSecretKey,
    PrivacyStatistics,
    PrivacyAmplificationResult,
)
from qst.privacy.algorithms.toeplitz import ToeplitzHasher


class PrivacyAmplifier:
    """Orchestrates privacy amplification steps on corrected or sifted keys."""

    def __init__(self, config: PrivacyAmplificationConfiguration) -> None:
        """Initialize the amplifier with configuration settings.

        Args:
            config: PrivacyAmplificationConfiguration object.
        """
        validate_privacy_config(config)
        self.config = config

    def amplify(
        self,
        key: Sequence[int],
        initial_qber: float = 0.0,
    ) -> PrivacyAmplificationResult:
        """Apply privacy amplification to compress the input key.

        Args:
            key: Input binary sequence (sifted or corrected key).
            initial_qber: Estimated raw QBER used to bound Eve's information.

        Returns:
            PrivacyAmplificationResult containing the final key and metrics.

        Raises:
            PrivacyAmplificationError: If validation fails.
        """
        validate_key(key)

        input_key_length = len(key)
        # Compute target output size from compression ratio
        output_key_length = max(
            1, int(input_key_length * self.config.compression_ratio)
        )

        validate_dimensions(input_key_length, output_key_length)

        t_start = time.perf_counter()

        # Instantiate algorithm
        if self.config.hash_algorithm.lower() == "toeplitz":
            hasher = ToeplitzHasher(seed=self.config.seed)
        else:
            raise PrivacyAmplificationError(
                f"Unsupported hash algorithm '{self.config.hash_algorithm}'.",
                code="QST-PRIV-704",
            )

        # Hash key
        secret_bits = hasher.hash_key(key, output_key_length)

        t_elapsed = time.perf_counter() - t_start

        # Calculate metrics
        discarded_bits = input_key_length - output_key_length
        compression_percentage = (output_key_length / input_key_length) * 100.0
        effective_key_rate = output_key_length / input_key_length

        # Estimate Eve's information using Shannon binary entropy on QBER
        e = initial_qber
        if e <= 0.0 or e >= 1.0:
            h_e = 0.0
        else:
            h_e = -e * math.log2(e) - (1 - e) * math.log2(1 - e)

        estimated_eve_information = input_key_length * h_e
        # Security parameter s = discarded_bits - estimated_eve_information
        estimated_security_parameter = max(
            0.0, discarded_bits - estimated_eve_information
        )

        final_key = FinalSecretKey(key_bits=secret_bits)

        stats = PrivacyStatistics(
            input_key_length=input_key_length,
            output_key_length=output_key_length,
            discarded_bits=discarded_bits,
            compression_percentage=compression_percentage,
            effective_key_rate=effective_key_rate,
            estimated_security_parameter=estimated_security_parameter,
            execution_time=t_elapsed,
        )

        return PrivacyAmplificationResult(
            final_secret_key=final_key,
            input_key_length=input_key_length,
            output_key_length=output_key_length,
            compression_ratio=self.config.compression_ratio,
            hash_algorithm=self.config.hash_algorithm,
            estimated_eve_information=estimated_eve_information,
            execution_time=t_elapsed,
            statistics=stats,
        )
