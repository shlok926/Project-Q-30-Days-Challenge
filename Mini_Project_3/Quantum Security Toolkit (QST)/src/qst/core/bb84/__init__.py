"""Explicit exports for BB84 Protocol Engine components.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md §5
"""

from qst.core.bb84.constants import BASIS_X, BASIS_Z, SUPPORTED_BASES, SUPPORTED_BITS
from qst.core.bb84.validators import (
    validate_bb84_bits,
    validate_bb84_bases,
    validate_bb84_inputs,
)
from qst.core.bb84.state_preparation import AliceStatePreparer
from qst.core.bb84.circuit_builder import (
    CircuitBuilder,
    GateApplier,
    RegisterAllocator,
    StateEncoder,
)
from qst.core.bb84.measurement import MeasurementBasisGenerator, MeasurementBuilder
from qst.core.bb84.protocol import BB84Protocol

__all__ = [
    "BASIS_X",
    "BASIS_Z",
    "SUPPORTED_BASES",
    "SUPPORTED_BITS",
    "validate_bb84_bits",
    "validate_bb84_bases",
    "validate_bb84_inputs",
    "AliceStatePreparer",
    "CircuitBuilder",
    "GateApplier",
    "RegisterAllocator",
    "StateEncoder",
    "MeasurementBasisGenerator",
    "MeasurementBuilder",
    "BB84Protocol",
]
