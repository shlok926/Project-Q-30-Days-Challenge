"""Unit tests for the IBM Quantum Runtime executor.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md §11
    Docs/14_TESTING_STRATEGY.md
"""

import sys
from unittest import mock
import pytest
from qiskit.circuit import QuantumCircuit
from qst.exceptions.simulation import SimulationError
from qst.core.shared.execution.ibm_runtime_executor import IBMRuntimeExecutor


# 1. Create Mocks for Qiskit IBM Runtime Service
class MockBackendStatus:
    def __init__(self, operational: bool = True, pending_jobs: int = 2):
        self.operational = operational
        self.pending_jobs = pending_jobs


class MockBackend:
    def __init__(self, name: str, num_qubits: int, simulator: bool = False):
        self.name = name
        self.num_qubits = num_qubits
        self.simulator = simulator
        self._status = MockBackendStatus()
        self.target = mock.MagicMock()

    def status(self):
        return self._status

    def run(self, circuit, shots=1, seed_simulator=None):
        mock_job = mock.MagicMock()
        mock_result = mock.MagicMock()
        mock_result.get_counts.return_value = {"110": 1}
        mock_job.result.return_value = mock_result
        return mock_job


@pytest.fixture(autouse=True)
def mock_transpile():
    """Autouse fixture to mock qiskit's transpile function to bypass BackendV2 checks."""
    with mock.patch("qst.core.shared.execution.ibm_runtime_executor.transpile", side_effect=lambda circ, *args, **kwargs: circ) as m:
        yield m


class MockQiskitRuntimeService:
    def __init__(self, channel=None, token=None):
        self.channel = channel
        self.token = token
        self._backends = [
            MockBackend("ibm_osaka", 127, False),
            MockBackend("ibm_brisbane", 127, False),
            MockBackend("ibmq_qasm_simulator", 32, True),
        ]

    def backends(self):
        return self._backends

    def backend(self, name):
        for b in self._backends:
            if b.name == name:
                return b
        raise ValueError(f"Backend '{name}' not found.")

    def least_busy(self, simulator=False, operational=True):
        candidates = [b for b in self._backends if b.simulator == simulator]
        if candidates:
            return candidates[0]
        raise ValueError("No matching backend found.")


@pytest.fixture
def mock_ibm_runtime():
    """Fixture that patches qiskit_ibm_runtime module with mocks."""
    mock_module = mock.MagicMock()
    mock_module.QiskitRuntimeService = MockQiskitRuntimeService
    with mock.patch.dict(sys.modules, {"qiskit_ibm_runtime": mock_module}):
        yield mock_module


@pytest.mark.unit
def test_discover_backends(mock_ibm_runtime) -> None:
    """Verify discover_backends extracts attributes correctly from QiskitRuntimeService."""
    info = IBMRuntimeExecutor.discover_backends(token="dummy_token")
    assert len(info) == 3
    assert info[0]["backend_name"] == "ibm_osaka"
    assert info[0]["num_qubits"] == 127
    assert info[0]["operational_status"] is True
    assert info[0]["simulator_vs_hardware"] == "hardware"
    assert info[0]["queue_information"] == "2 jobs pending"

    assert info[2]["backend_name"] == "ibmq_qasm_simulator"
    assert info[2]["simulator_vs_hardware"] == "simulator"


@pytest.mark.unit
def test_executor_backend_selection(mock_ibm_runtime) -> None:
    """Verify IBMRuntimeExecutor constructor selects backend variants correctly."""
    # Best selection (should pick first hardware)
    exec_best = IBMRuntimeExecutor(backend_name="best", token="dummy_token")
    assert exec_best.backend.name == "ibm_osaka"

    # Explicit backend
    exec_explicit = IBMRuntimeExecutor(backend_name="ibm_brisbane", token="dummy_token")
    assert exec_explicit.backend.name == "ibm_brisbane"

    # Simulator selection
    exec_sim = IBMRuntimeExecutor(backend_name="simulator", token="dummy_token")
    assert exec_sim.backend.name == "ibmq_qasm_simulator"


@pytest.mark.unit
def test_executor_auth_and_missing_errors(mock_ibm_runtime) -> None:
    """Verify that auth or backend errors trigger SimulationError correctly."""
    # Authentication failure mock
    with mock.patch(
        "qiskit_ibm_runtime.QiskitRuntimeService",
        side_effect=Exception("Mock Auth Failure"),
    ):
        with pytest.raises(SimulationError) as exc:
            IBMRuntimeExecutor(token="bad_token")
        assert "QST-SIM-301" in str(exc.value)

    # Missing backend failure mock
    with pytest.raises(SimulationError) as exc:
        IBMRuntimeExecutor(backend_name="nonexistent_backend", token="dummy")
    assert "QST-SIM-303" in str(exc.value)


@pytest.mark.unit
def test_executor_execute_pipeline(mock_ibm_runtime) -> None:
    """Verify execute and validate_transpilation complete successfully or raise on execution errors."""
    executor = IBMRuntimeExecutor(backend_name="ibm_brisbane", token="dummy")
    circ = QuantumCircuit(2)
    circ.h(0)
    circ.cx(0, 1)

    # Validate execution
    counts = executor.execute(circ)
    assert counts == {"110": 1}

    # Validate transpilation
    assert executor.validate_transpilation(circ) is True

    # Transpilation failure mock
    with mock.patch(
        "qst.core.shared.execution.ibm_runtime_executor.transpile",
        side_effect=Exception("Transpilation failed"),
    ):
        with pytest.raises(SimulationError) as exc:
            executor.validate_transpilation(circ)
        assert "QST-SIM-305" in str(exc.value)

        with pytest.raises(SimulationError) as exc:
            executor.execute(circ)
        assert "QST-SIM-304" in str(exc.value)


@pytest.mark.unit
def test_executor_noise_aware_local(mock_ibm_runtime) -> None:
    """Verify local noise-aware execution constructs AerSimulator locally."""
    # Mock AerSimulator.from_backend
    mock_aer = mock.MagicMock()
    mock_aer_sim = mock.MagicMock()
    mock_aer.AerSimulator.from_backend.return_value = mock_aer_sim

    mock_job = mock.MagicMock()
    mock_result = mock.MagicMock()
    mock_result.get_counts.return_value = {"00": 1}
    mock_job.result.return_value = mock_result
    mock_aer_sim.run.return_value = mock_job

    with mock.patch.dict(sys.modules, {"qiskit_aer": mock_aer}):
        executor = IBMRuntimeExecutor(
            backend_name="ibm_brisbane",
            token="dummy",
            noise_aware_local=True,
        )
        circ = QuantumCircuit(2)
        counts = executor.execute(circ)
        assert counts == {"00": 1}
        mock_aer.AerSimulator.from_backend.assert_called_once_with(executor.backend)
