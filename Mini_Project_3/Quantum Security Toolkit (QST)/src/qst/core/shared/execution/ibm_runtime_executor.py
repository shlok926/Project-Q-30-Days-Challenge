"""IBM Quantum Runtime concrete executor implementation.

Isolates IBM Quantum hardware and runtime services execution behind generic abstractions.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md §11
    Docs/TECHNICAL_REQUIREMENTS.md
"""

import logging
from typing import Any, Optional, Union

from qiskit import transpile
from qst.exceptions.simulation import SimulationError
from qst.core.shared.execution.executor import ExecutorInterface

logger = logging.getLogger("qst.execution.ibm")


class IBMRuntimeExecutor(ExecutorInterface):
    """Concrete execution wrapper targeting IBM Quantum Runtime services and hardware QPUs."""

    def __init__(
        self,
        backend_name: Optional[str] = None,
        token: Optional[str] = None,
        noise_aware_local: bool = False,
    ) -> None:
        """Initialize the IBM Quantum Runtime execution backend.

        Args:
            backend_name: Explicit name of backend or 'best' / 'simulator'.
            token: IBM Quantum API token. If omitted, attempts to load saved account.
            noise_aware_local: If True, builds a local AerSimulator noise model from QPU.

        Raises:
            SimulationError: If import, auth, or backend selection fails.
        """
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
        except ImportError as e:
            raise SimulationError(
                f"The 'qiskit-ibm-runtime' package is not installed. Reason: {e}",
                code="QST-SIM-300",
            ) from e

        # 1. Authenticate with IBM Quantum
        try:
            try:
                if token:
                    self._service = QiskitRuntimeService(
                        channel="ibm_quantum", token=token
                    )
                else:
                    self._service = QiskitRuntimeService(channel="ibm_quantum")
            except Exception:
                if token:
                    self._service = QiskitRuntimeService(
                        channel="ibm_quantum_platform", token=token
                    )
                else:
                    self._service = QiskitRuntimeService(channel="ibm_quantum_platform")
        except Exception as e:
            raise SimulationError(
                f"IBM Quantum authentication failed. Reason: {e}",
                code="QST-SIM-301",
            ) from e

        # 2. Select backend
        try:
            if backend_name == "best" or not backend_name:
                self._backend = self._service.least_busy(
                    simulator=False, operational=True
                )
            elif backend_name == "simulator":
                self._backend = self._service.least_busy(
                    simulator=True, operational=True
                )
            else:
                self._backend = self._service.backend(backend_name)
        except Exception as e:
            raise SimulationError(
                f"Failed to select IBM Quantum backend '{backend_name}'. Reason: {e}",
                code="QST-SIM-303",
            ) from e

        # 3. Setup Noise-aware local simulation if configured
        self._noise_aware_local = noise_aware_local
        self._local_simulator = None
        if self._noise_aware_local:
            try:
                from qiskit_aer import AerSimulator

                self._local_simulator = AerSimulator.from_backend(self._backend)
                logger.info(
                    f"Initialized local noise-aware simulator from QPU: {self._backend.name}"
                )
            except Exception as e:
                logger.warning(
                    f"Could not build local noise-aware simulator. Executing on real QPU. Reason: {e}"
                )

    @property
    def backend(self) -> Any:
        """Access the selected IBM backend instance."""
        return self._backend

    @staticmethod
    def discover_backends(token: Optional[str] = None) -> list[dict[str, Any]]:
        """List all available IBM Quantum backends with operational status.

        Args:
            token: Optional IBM Quantum API token.

        Returns:
            A list of dictionaries with backend properties.
        """
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService

            try:
                if token:
                    service = QiskitRuntimeService(channel="ibm_quantum", token=token)
                else:
                    service = QiskitRuntimeService(channel="ibm_quantum")
            except Exception:
                if token:
                    service = QiskitRuntimeService(
                        channel="ibm_quantum_platform", token=token
                    )
                else:
                    service = QiskitRuntimeService(channel="ibm_quantum_platform")

            backends_info = []
            for b in service.backends():
                try:
                    status = b.status()
                    operational = getattr(status, "operational", True)
                    pending_jobs = getattr(status, "pending_jobs", 0)
                except Exception:
                    operational = True
                    pending_jobs = 0

                backends_info.append(
                    {
                        "backend_name": b.name,
                        "num_qubits": b.num_qubits,
                        "operational_status": operational,
                        "simulator_vs_hardware": (
                            "simulator" if b.simulator else "hardware"
                        ),
                        "queue_information": f"{pending_jobs} jobs pending",
                    }
                )
            return backends_info
        except Exception as e:
            raise SimulationError(
                f"Failed to discover IBM Quantum backends. Reason: {e}",
                code="QST-SIM-302",
            ) from e

    def execute(
        self,
        circuit: Any,
        seed: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> dict[str, int]:
        """Execute a quantum circuit on the selected QPU backend or noise-aware simulator.

        Args:
            circuit: A Qiskit QuantumCircuit.
            seed: Optional simulator seed.
            timeout: Optional execution timeout in seconds.

        Returns:
            A counts dictionary mapping binary outcomes to frequency count.

        Raises:
            SimulationError: If execution on QPU fails or times out.
        """
        try:
            if self._noise_aware_local and self._local_simulator is not None:
                transpiled = transpile(circuit, self._local_simulator)
                job = self._local_simulator.run(
                    transpiled, shots=1, seed_simulator=seed
                )
            else:
                transpiled = transpile(circuit, self._backend)
                job = self._backend.run(transpiled, shots=1, seed_simulator=seed)

            # Retrieve results with optional timeout
            result = job.result(timeout=timeout)
            counts = result.get_counts(transpiled)
            if not isinstance(counts, dict):
                raise ValueError(
                    "Backend execution did not return a counts dictionary."
                )
            return counts
        except Exception as e:
            target = (
                "local noise-aware simulator"
                if self._noise_aware_local
                else f"IBM backend {self._backend.name}"
            )
            raise SimulationError(
                f"Failed to execute quantum circuit on {target}. Reason: {e}",
                code="QST-SIM-304",
            ) from e

    def validate_transpilation(self, circuit: Any) -> bool:
        """Verify the transpiler accepts the circuit for the IBM QPU backend.

        Args:
            circuit: The Qiskit QuantumCircuit to compile.

        Returns:
            True if transpilation compiles successfully.

        Raises:
            SimulationError: If compilation fails.
        """
        try:
            target = (
                self._local_simulator
                if (self._noise_aware_local and self._local_simulator is not None)
                else self._backend
            )
            transpile(circuit, target)
            return True
        except Exception as e:
            raise SimulationError(
                f"Transpilation check failed for IBM backend. Reason: {e}",
                code="QST-SIM-305",
            ) from e
