"""Measurement components for Bob's basis choices and measurement rotations.

References:
    Docs/BB84_SPEC.md §1 Steps 5-6
    Docs/07_SYSTEM_ARCHITECTURE.md §5
"""

from typing import Any, Sequence

from qiskit import QuantumCircuit

from qst.core.bb84.constants import BASIS_X, SUPPORTED_BASES
from qst.core.bb84.validators import validate_bb84_bases, validate_bb84_circuit
from qst.core.bb84.circuit_builder import GateApplier
from qst.core.shared.random.random_provider import RandomProvider
from qst.core.shared.validation.validators import validate_qubit_count


class MeasurementBasisGenerator:
    """Generates Bob's random measurement bases."""

    def __init__(self, random_provider: RandomProvider) -> None:
        """Initialize the MeasurementBasisGenerator.

        Args:
            random_provider: The random source instance.
        """
        self._random_provider = random_provider

    def generate_bases(self, length: int) -> tuple[str, ...]:
        """Generate and validate Bob's random bases.

        Args:
            length: Number of bases to generate.

        Returns:
            An immutable tuple of basis strings.

        Raises:
            ValidationError: If length is invalid.
        """
        validate_qubit_count(length)
        bases = self._random_provider.generate_bases(length, SUPPORTED_BASES)
        validate_bb84_bases(bases)
        return bases


class MeasurementBuilder:
    """Configures measurement rotations and registers measurements on a circuit."""

    def __init__(self, gate_applier: GateApplier) -> None:
        """Initialize the MeasurementBuilder.

        Args:
            gate_applier: The gate applier utility.
        """
        self._gate_applier = gate_applier

    def apply_measurement(
        self, circuit: QuantumCircuit, bob_bases: Sequence[str]
    ) -> QuantumCircuit:
        """Apply basis rotations and measurements to the quantum circuit.

        Args:
            circuit: The Qiskit QuantumCircuit containing prepared states.
            bob_bases: Sequence of Bob's measurement bases.

        Returns:
            The modified Qiskit QuantumCircuit with measurements attached.

        Raises:
            ValidationError: If bases or circuit bounds are invalid.
        """
        validate_bb84_bases(bob_bases)
        length = len(bob_bases)
        validate_bb84_circuit(circuit, expected_qubits=length, expected_clbits=length)

        # Clone circuit to avoid mutating Alice's prepared circuit directly
        measured_qc = circuit.copy()

        for i in range(length):
            if bob_bases[i] == BASIS_X:
                self._gate_applier.apply_h(measured_qc, i)
            measured_qc.measure(i, i)

        return measured_qc
