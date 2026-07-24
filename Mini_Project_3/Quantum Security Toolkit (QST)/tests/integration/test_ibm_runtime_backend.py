"""Integration tests for QST IBM Quantum Runtime backend integration and fallbacks.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md §11
    Docs/14_TESTING_STRATEGY.md
"""

import sys
from unittest import mock
import pytest
from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.exceptions.simulation import SimulationError


class FailingExecutor:
    """Mock executor designed to raise execution exceptions for fallback checks."""

    def execute(self, circuit, seed=None):
        raise SimulationError("QPU Queue Error Mock", code="QST-SIM-304")

    def validate_transpilation(self, circuit):
        return True


@pytest.fixture
def mock_ibm_runtime_failing():
    """Mock module patch returning failing connection service."""
    mock_module = mock.MagicMock()
    mock_module.QiskitRuntimeService.side_effect = Exception("Auth Mock Denied")
    with mock.patch.dict(sys.modules, {"qiskit_ibm_runtime": mock_module}):
        yield mock_module


@pytest.mark.integration
def test_orchestrator_auth_failure_fallback_to_aer(mock_ibm_runtime_failing) -> None:
    """Verify that orchestrator falls back to Aer simulator when IBM auth fails if fallback is active."""
    # 1. Fallback enabled (should run successfully using Aer)
    config_fallback = SimulationConfig(
        n_qubits=10,
        seed=42,
        interception_probability=0.0,
        use_ibm_runtime=True,
        ibm_token="invalid_token_fallback",
        fallback_to_aer=True,
    )
    orchestrator = SimulationOrchestrator()
    res = orchestrator.run_once(config_fallback)
    assert len(res.simulations) == 1
    assert res.average_qber == 0.0

    # 2. Fallback disabled (should propagate auth exception)
    config_no_fallback = SimulationConfig(
        n_qubits=10,
        seed=42,
        interception_probability=0.0,
        use_ibm_runtime=True,
        ibm_token="invalid_token_no_fallback",
        fallback_to_aer=False,
    )
    with pytest.raises(SimulationError) as exc:
        orchestrator.run_once(config_no_fallback)
    assert "QST-SIM-301" in str(exc.value)


@pytest.mark.integration
def test_orchestrator_execution_failure_fallback_to_aer() -> None:
    """Verify that orchestrator falls back to Aer simulator if execution fails mid-run."""
    config = SimulationConfig(
        n_qubits=10,
        seed=42,
        interception_probability=0.0,
        use_ibm_runtime=True,
        fallback_to_aer=True,
    )

    orchestrator = SimulationOrchestrator()

    # Stub the IBMRuntimeExecutor constructor to return our failing executor
    with mock.patch(
        "qst.core.shared.execution.ibm_runtime_executor.IBMRuntimeExecutor",
        return_value=FailingExecutor(),
    ):
        res = orchestrator.run_once(config)
        assert len(res.simulations) == 1
        assert res.average_qber == 0.0  # Successfully ran on Aer fallback
