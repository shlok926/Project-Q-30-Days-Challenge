"""Shared validator utilities for checking bits, bases, and circuit properties.

References:
    Docs/05_PRODUCT_REQUIREMENTS.md §7
    Docs/10_API_SPECIFICATION.md §6
"""

from typing import Any, Sequence

from qst.exceptions.validation import ValidationError
from qst.utils.validation import validate_qubit_count


def validate_bit_values(bits: Sequence[int]) -> None:
    """Verify all bit values in a sequence are 0 or 1.

    Args:
        bits: Sequence of bit integers.

    Raises:
        ValidationError: If any bit value is not 0 or 1.
    """
    for idx, bit in enumerate(bits):
        # Enforce type check to reject boolean subclasses
        if not isinstance(bit, int) or isinstance(bit, bool) or bit not in (0, 1):
            raise ValidationError(
                f"Invalid bit value at index {idx}: {bit}. Must be 0 or 1.",
                code="QST-VAL-601",
            )


def validate_basis_values(bases: Sequence[str], allowed_bases: Sequence[str]) -> None:
    """Verify all bases belong to the allowed basis set.

    Args:
        bases: Sequence of basis strings.
        allowed_bases: Set or sequence of supported basis strings.

    Raises:
        ValidationError: If any basis value is not supported.
    """
    for idx, basis in enumerate(bases):
        if basis not in allowed_bases:
            raise ValidationError(
                f"Invalid basis value at index {idx}: '{basis}'. "
                f"Must be one of {allowed_bases}",
                code="QST-VAL-602",
            )


def validate_matching_lengths(bits: Sequence[Any], bases: Sequence[Any]) -> None:
    """Verify that bit and basis sequences are of equal length.

    Args:
        bits: A sequence of bits.
        bases: A sequence of bases.

    Raises:
        ValidationError: If the lengths do not match.
    """
    if len(bits) != len(bases):
        raise ValidationError(
            f"Bit sequence length ({len(bits)}) does not match "
            f"basis sequence length ({len(bases)}).",
            code="QST-VAL-603",
        )


def validate_circuit_registers(
    circuit: Any, expected_qubits: int, expected_clbits: int
) -> None:
    """Verify register allocations in a Qiskit circuit match expectations.

    Args:
        circuit: A Qiskit QuantumCircuit.
        expected_qubits: Expected number of qubits.
        expected_clbits: Expected number of classical registers.

    Raises:
        ValidationError: If allocated sizes differ from expected parameters.
    """
    try:
        num_qubits = circuit.num_qubits
        num_clbits = circuit.num_clbits
    except AttributeError as e:
        raise ValidationError(
            f"Invalid circuit object type. Reason: {e}", code="QST-VAL-604"
        ) from e

    if num_qubits != expected_qubits:
        raise ValidationError(
            f"Circuit qubit allocation mismatch. Expected {expected_qubits}, "
            f"allocated {num_qubits}.",
            code="QST-VAL-605",
        )

    if num_clbits != expected_clbits:
        raise ValidationError(
            f"Circuit classical register allocation mismatch. Expected {expected_clbits}, "
            f"allocated {num_clbits}.",
            code="QST-VAL-606",
        )
