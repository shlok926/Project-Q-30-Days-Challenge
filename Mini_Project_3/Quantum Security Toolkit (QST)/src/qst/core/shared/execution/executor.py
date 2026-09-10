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
        self._stabilizer_simulator: Optional[AerSimulator] = None

    def _get_simulator_for_circuit(self, circuit: Any) -> AerSimulator:
        """Return the optimal simulator backend based on circuit width and simulation capability."""
        n_qubits = getattr(circuit, "num_qubits", 0)
        sim_qubits = getattr(self._simulator, "num_qubits", 29)
        if n_qubits > sim_qubits:
            if self._stabilizer_simulator is None:
                self._stabilizer_simulator = AerSimulator(method="stabilizer")
            return self._stabilizer_simulator
        return self._simulator

    def execute(self, circuit: Any, seed: Optional[int] = None) -> dict[str, int]:
        """Execute the circuit on AerSimulator with a single shot.

        Args:
            circuit: The Qiskit QuantumCircuit to simulate.
            seed: Optional simulator seed.

        Returns:
            A dictionary of outcome counts (e.g. {'1': 1}).

        Raises:
            SimulationError: If Qiskit Aer simulator execution fails or qubit count is unsafe.
        """
        n_qubits = getattr(circuit, "num_qubits", 0)
        if n_qubits > 2048:
            raise SimulationError(
                f"Circuit qubit count ({n_qubits}) exceeds AerExecutor safety ceiling of 2048.",
                code="QST-SIM-103",
            )

        sim = self._get_simulator_for_circuit(circuit)
        try:
            transpiled_circuit = transpile(circuit, sim)
            job = sim.run(transpiled_circuit, shots=1, seed_simulator=seed)
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
        sim = self._get_simulator_for_circuit(circuit)
        try:
            transpile(circuit, sim)
            return True
        except Exception as e:
            raise SimulationError(
                f"Transpilation check failed for circuit. Reason: {e}",
                code="QST-SIM-102",
            ) from e

