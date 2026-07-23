"""Validation checks mapped to BB84 specific parameter specifications.

References:
    Docs/BB84_SPEC.md §6
    Docs/05_PRODUCT_REQUIREMENTS.md §7
"""

from typing import Any, Sequence

from qst.core.bb84.constants import SUPPORTED_BASES, SUPPORTED_BITS
from qst.core.shared.validation.validators import (
    validate_basis_values,
    validate_bit_values,
    validate_circuit_registers,
    validate_matching_lengths,
    validate_qubit_count,
)


def validate_bb84_bits(bits: Sequence[int]) -> None:
    """Verify sequence consists of valid BB84 bits (0 or 1).

    Args:
        bits: A sequence of bit values.
    """
    validate_bit_values(bits)


def validate_bb84_bases(bases: Sequence[str]) -> None:
    """Verify sequence consists of valid BB84 bases (Z or X).

    Args:
        bases: A sequence of basis values.
    """
    validate_basis_values(bases, SUPPORTED_BASES)


def validate_bb84_inputs(bits: Sequence[int], bases: Sequence[str]) -> None:
    """Validate bits and bases parameters for BB84 execution consistency.

    Args:
        bits: Sequence of bit values.
        bases: Sequence of basis values.
    """
    validate_matching_lengths(bits, bases)
    validate_bb84_bits(bits)
    validate_bb84_bases(bases)


def validate_bb84_circuit(
    circuit: Any, expected_qubits: int, expected_clbits: int
) -> None:
    """Validate BB84 compiled QuantumCircuit size properties.

    Args:
        circuit: A Qiskit QuantumCircuit.
        expected_qubits: Expected number of qubits.
        expected_clbits: Expected number of classical registers.
    """
    validate_circuit_registers(circuit, expected_qubits, expected_clbits)
