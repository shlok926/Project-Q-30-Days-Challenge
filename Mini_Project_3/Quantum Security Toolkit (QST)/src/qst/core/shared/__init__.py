"""Shared package initialization for reusable QKD simulation blocks.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md
"""

from qst.core.shared.execution.executor import AerExecutor, ExecutorInterface
from qst.core.shared.random.random_provider import NumpyRandomProvider, RandomProvider
from qst.core.shared.validation.validators import (
    validate_basis_values,
    validate_bit_values,
    validate_circuit_registers,
    validate_matching_lengths,
    validate_qubit_count,
)

__all__ = [
    "RandomProvider",
    "NumpyRandomProvider",
    "ExecutorInterface",
    "AerExecutor",
    "validate_qubit_count",
    "validate_bit_values",
    "validate_basis_values",
    "validate_matching_lengths",
    "validate_circuit_registers",
]
