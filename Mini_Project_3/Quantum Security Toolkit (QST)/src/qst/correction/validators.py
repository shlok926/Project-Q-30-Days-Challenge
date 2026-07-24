"""Input and configuration validators for Cascade Error Correction.

References:
    Docs/10_API_SPECIFICATION.md §4
"""

from typing import Sequence
from qst.correction.exceptions import CorrectionError
from qst.correction.models import CascadeConfiguration


def validate_keys(alice_key: Sequence[int], bob_key: Sequence[int]) -> None:
    """Validate that Alice's and Bob's keys are compatible and non-empty.

    Args:
        alice_key: Alice's sifted key bits.
        bob_key: Bob's sifted key bits.

    Raises:
        CorrectionError: If keys are empty, have mismatched lengths, or contain invalid bits.
    """
    if not alice_key or not bob_key:
        raise CorrectionError(
            "Keys for error correction cannot be empty.",
            code="QST-CORR-701",
        )

    if len(alice_key) != len(bob_key):
        raise CorrectionError(
            f"Key lengths do not match: Alice has {len(alice_key)} bits, Bob has {len(bob_key)} bits.",
            code="QST-CORR-702",
        )

    for i, bit in enumerate(alice_key):
        if bit not in (0, 1):
            raise CorrectionError(
                f"Alice's key contains invalid bit '{bit}' at index {i}.",
                code="QST-CORR-703",
            )

    for i, bit in enumerate(bob_key):
        if bit not in (0, 1):
            raise CorrectionError(
                f"Bob's key contains invalid bit '{bit}' at index {i}.",
                code="QST-CORR-703",
            )


def validate_cascade_config(config: CascadeConfiguration) -> None:
    """Validate configuration parameters for the Cascade reconciler.

    Args:
        config: The CascadeConfiguration instance.

    Raises:
        CorrectionError: If configuration contains invalid passes, block sizes, or seed.
    """
    if config.num_passes <= 0:
        raise CorrectionError(
            f"Number of passes must be greater than zero, got {config.num_passes}.",
            code="QST-CORR-703",
        )

    if not config.block_sizes:
        raise CorrectionError(
            "Block sizes tuple cannot be empty.",
            code="QST-CORR-703",
        )

    for i, size in enumerate(config.block_sizes):
        if size <= 0:
            raise CorrectionError(
                f"Block size at index {i} must be greater than zero, got {size}.",
                code="QST-CORR-703",
            )
