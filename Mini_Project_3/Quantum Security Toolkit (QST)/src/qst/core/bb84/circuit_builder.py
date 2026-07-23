"""Single Responsibility circuit components for compiling Alice's BB84 circuits.

References:
    Docs/BB84_SPEC.md §3
    Docs/07_SYSTEM_ARCHITECTURE.md §5
"""

from typing import Any, Sequence

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from qst.core.bb84.constants import BASIS_X, BASIS_Z
from qst.core.bb84.validators import validate_bb84_circuit, validate_bb84_inputs


class RegisterAllocator:
    """Allocates Qiskit quantum and classical registers."""

    def allocate(self, n_qubits: int) -> tuple[QuantumRegister, ClassicalRegister]:
        """Allocate registers for the specified qubit count.

        Args:
            n_qubits: Number of registers to allocate.

        Returns:
            A tuple of (QuantumRegister, ClassicalRegister).
        """
        qr = QuantumRegister(n_qubits, name="q")
        cr = ClassicalRegister(n_qubits, name="c")
        return qr, cr


class GateApplier:
    """Encapsulates execution of quantum gate placements on a circuit."""

    def apply_x(self, circuit: QuantumCircuit, qubit_idx: int) -> None:
        """Apply an X (NOT) gate to a specific qubit.

        Args:
            circuit: The Qiskit QuantumCircuit.
            qubit_idx: Index of the target qubit.
        """
        circuit.x(qubit_idx)

    def apply_h(self, circuit: QuantumCircuit, qubit_idx: int) -> None:
        """Apply a Hadamard (H) gate to a specific qubit.

        Args:
            circuit: The Qiskit QuantumCircuit.
            qubit_idx: Index of the target qubit.
        """
        circuit.h(qubit_idx)


class StateEncoder:
    """Encodes classical bits into specific bases on qubits."""

    def __init__(self, gate_applier: GateApplier) -> None:
        """Initialize the StateEncoder.

        Args:
            gate_applier: The gate applier utility.
        """
        self._gate_applier = gate_applier

    def encode(
        self, circuit: QuantumCircuit, qubit_idx: int, bit: int, basis: str
    ) -> None:
        """Encode a bit in a basis onto a target qubit.

        Args:
            circuit: The Qiskit QuantumCircuit.
            qubit_idx: Index of the qubit.
            bit: Bit value (0 or 1).
            basis: Basis identifier (Z or X).
        """
        if bit == 1:
            self._gate_applier.apply_x(circuit, qubit_idx)
        if basis == BASIS_X:
            self._gate_applier.apply_h(circuit, qubit_idx)


class CircuitBuilder:
    """Composes complete Alice state preparation circuits."""

    def __init__(self, allocator: RegisterAllocator, encoder: StateEncoder) -> None:
        """Initialize the CircuitBuilder.

        Args:
            allocator: The register allocator.
            encoder: The state encoder.
        """
        self._allocator = allocator
        self._encoder = encoder

    def build_circuit(
        self, bits: Sequence[int], bases: Sequence[str]
    ) -> QuantumCircuit:
        """Build and validate Alice's quantum state preparation circuit.

        Args:
            bits: Sequence of bit values (0 or 1).
            bases: Sequence of basis values (Z or X).

        Returns:
            The compiled Qiskit QuantumCircuit.

        Raises:
            ValidationError: If inputs are invalid or circuit bounds are violated.
        """
        validate_bb84_inputs(bits, bases)
        length = len(bits)

        qr, cr = self._allocator.allocate(length)
        qc = QuantumCircuit(qr, cr)

        for i in range(length):
            self._encoder.encode(qc, i, bits[i], bases[i])

        validate_bb84_circuit(qc, expected_qubits=length, expected_clbits=length)
        return qc
