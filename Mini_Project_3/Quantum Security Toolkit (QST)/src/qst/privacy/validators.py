"""Input and configuration validators for Privacy Amplification.

References:
    Docs/10_API_SPECIFICATION.md §4
"""

from typing import Sequence
from qst.privacy.exceptions import PrivacyAmplificationError
from qst.privacy.models import PrivacyAmplificationConfiguration


def validate_key(key: Sequence[int]) -> None:
    """Validate that the input key is non-empty and contains only binary bits.

    Args:
        key: The key bits sequence.

    Raises:
        PrivacyAmplificationError: If key is empty or has non-binary values.
    """
    if not key:
        raise PrivacyAmplificationError(
            "Input key for privacy amplification cannot be empty.",
            code="QST-PRIV-701",
        )

    for i, bit in enumerate(key):
        if bit not in (0, 1):
            raise PrivacyAmplificationError(
                f"Input key contains invalid bit '{bit}' at index {i}.",
                code="QST-PRIV-701",
            )


def validate_privacy_config(config: PrivacyAmplificationConfiguration) -> None:
    """Validate the privacy amplification configuration bounds.

    Args:
        config: The configuration details.

    Raises:
        PrivacyAmplificationError: If configuration values are out of bounds.
    """
    if not (0.0 < config.compression_ratio <= 1.0):
        raise PrivacyAmplificationError(
            f"Compression ratio must be between 0.0 (exclusive) and 1.0 (inclusive), got {config.compression_ratio}.",
            code="QST-PRIV-702",
        )

    valid_algos = ("toeplitz",)
    if config.hash_algorithm.lower() not in valid_algos:
        raise PrivacyAmplificationError(
            f"Unsupported hashing algorithm '{config.hash_algorithm}'. Supported: {valid_algos}.",
            code="QST-PRIV-704",
        )


def validate_dimensions(input_length: int, output_length: int) -> None:
    """Validate matrix dimensions for key hashing.

    Args:
        input_length: The length of the input key.
        output_length: The length of the target output key.

    Raises:
        PrivacyAmplificationError: If dimensions are invalid or try to expand the key.
    """
    if input_length <= 0 or output_length <= 0:
        raise PrivacyAmplificationError(
            f"Key dimensions must be positive integers, got input={input_length}, output={output_length}.",
            code="QST-PRIV-703",
        )

    if output_length > input_length:
        raise PrivacyAmplificationError(
            f"Output key length ({output_length}) cannot be larger than input key length ({input_length}).",
            code="QST-PRIV-703",
        )
