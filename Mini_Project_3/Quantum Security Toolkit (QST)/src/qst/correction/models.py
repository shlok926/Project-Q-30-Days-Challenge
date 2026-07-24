"""Cascade Error Correction immutable domain models.

References:
    Docs/10_API_SPECIFICATION.md §5
"""

import math
from dataclasses import dataclass, field
from typing import Optional, Sequence


@dataclass(frozen=True)
class CorrectedKey:
    """Immutable model representing the reconciled key after Cascade error correction."""

    key_bits: tuple[int, ...]
    length: int = field(init=False)

    def __post_init__(self) -> None:
        """Populate secondary read-only properties."""
        object.__setattr__(self, "length", len(self.key_bits))


@dataclass(frozen=True)
class CascadeConfiguration:
    """Configuration parameters for the Cascade error correction protocol."""

    block_sizes: tuple[int, ...] = (8, 16, 32, 64)
    num_passes: int = 4
    seed: int = 42


@dataclass(frozen=True)
class CorrectionStatistics:
    """Raw telemetry captured during Cascade execution."""

    initial_discrepancies: int
    corrected_bit_positions: tuple[int, ...]
    parity_exchanges: int
    communication_rounds: int
    bits_disclosed: int
    execution_time: float


@dataclass(frozen=True)
class CorrectionResult:
    """Consolidated immutable container storing the reconciled key and protocol metrics."""

    corrected_key: CorrectedKey
    corrected_error_count: int
    corrected_bit_positions: tuple[int, ...]
    initial_qber: float
    estimated_qber_after_correction: float
    correction_efficiency: float
    parity_messages_exchanged: int
    communication_rounds: int
    bits_disclosed: int
    passes_completed: int
    execution_time: float
    statistics: CorrectionStatistics
