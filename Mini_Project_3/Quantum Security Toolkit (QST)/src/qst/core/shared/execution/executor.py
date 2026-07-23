"""Execution interface and Aer executor implementation.

Isolates all Qiskit-specific backend execution behind generic abstractions.

References:
    Docs/06_TECHNICAL_REQUIREMENTS.md §2
    Docs/07_SYSTEM_ARCHITECTURE.md §11
    Docs/SIMULATION_SPEC.md §1
"""

import abc
from typing import Any, Optional

from qiskit import transpile
from qiskit_aer import AerSimulator

from qst.exceptions.simulation import SimulationError


class ExecutorInterface(abc.ABC):
    """Abstract interface defining the QKD circuit execution pipeline.

    Decouples protocol algorithms from backend quantum execution frameworks.
    """

    @abc.abstractmethod
    def execute(self, circuit: Any, seed: Optional[int] = None) -> dict[str, int]:
        """Execute a quantum circuit and return raw measurement counts.

        Args:
            circuit: A quantum circuit object (e.g. Qiskit QuantumCircuit).
            seed: Optional random seed for simulator execution.

        Returns:
            A dictionary mapping binary outcome strings to counts.

        Raises:
            SimulationError: If execution on the backend fails.
        """
        pass

    @abc.abstractmethod
    def validate_transpilation(self, circuit: Any) -> bool:
        """Verify that the circuit is transpilation-compatible with the backend.

        Args:
            circuit: A quantum circuit object.

        Returns:
            True if compilation succeeds.

        Raises:
            SimulationError: If transpilation fails.
        """
        pass


class AerExecutor(ExecutorInterface):
    """Concrete execution wrapper targeting the Qiskit Aer simulator."""

    def __init__(self) -> None:
        """Initialize the Aer execution backend."""
        self._simulator = AerSimulator()

    def execute(self, circuit: Any, seed: Optional[int] = None) -> dict[str, int]:
        """Execute the circuit on AerSimulator with a single shot.

        Args:
            circuit: The Qiskit QuantumCircuit to simulate.
            seed: Optional simulator seed.

        Returns:
            A dictionary of outcome counts (e.g. {'1': 1}).

        Raises:
            SimulationError: If Qiskit Aer simulator execution fails.
        """
        try:
            transpiled_circuit = transpile(circuit, self._simulator)
            job = self._simulator.run(transpiled_circuit, shots=1, seed_simulator=seed)
            result = job.result()
            counts = result.get_counts(transpiled_circuit)
            if not isinstance(counts, dict):
                raise ValueError("Simulator did not return a counts dictionary.")
            return counts
        except Exception as e:
            raise SimulationError(
                f"Failed to execute quantum circuit on AerSimulator. Reason: {e}",
                code="QST-SIM-101",
            ) from e

    def validate_transpilation(self, circuit: Any) -> bool:
        """Verify the Qiskit transpiler accepts the circuit on AerSimulator.

        Args:
            circuit: The Qiskit QuantumCircuit to compile.

        Returns:
            True if transpilation compiles successfully.

        Raises:
            SimulationError: If compilation fails.
        """
        try:
            transpile(circuit, self._simulator)
            return True
        except Exception as e:
            raise SimulationError(
                f"Transpilation check failed for circuit. Reason: {e}",
                code="QST-SIM-102",
            ) from e
