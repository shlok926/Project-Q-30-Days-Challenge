"""Unit tests for the QST Executor layer.

References:
    Docs/06_TECHNICAL_REQUIREMENTS.md §2
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest
from qiskit import QuantumCircuit

from qst.core.shared.execution.executor import AerExecutor, ExecutorInterface
from qst.exceptions.simulation import SimulationError


@pytest.mark.unit
def test_executor_interface() -> None:
    """Verify that ExecutorInterface is an abstract base class."""
    with pytest.raises(TypeError):
        ExecutorInterface()  # type: ignore[abstract]


@pytest.mark.unit
def test_aer_executor_valid() -> None:
    """Verify AerExecutor compiles and runs a QuantumCircuit successfully."""
    executor = AerExecutor()

    # Simple 2-qubit circuit with measurement
    qc = QuantumCircuit(2, 2)
    qc.x(0)  # qubit 0 set to 1
    qc.measure(0, 0)
    qc.measure(1, 1)

    # Validate transpilation
    assert executor.validate_transpilation(qc) is True

    # Execute
    counts = executor.execute(qc, seed=42)
    assert isinstance(counts, dict)
    assert (
        counts.get("01") == 1
    )  # qubit 0 is 1, qubit 1 is 0 (little endian string "01")


@pytest.mark.unit
def test_aer_executor_invalid() -> None:
    """Verify AerExecutor raises SimulationError when transpilation or execution fails."""
    executor = AerExecutor()

    # Invalid circuit with unallocated register access
    # We construct a custom incorrect object to force failure
    with pytest.raises(SimulationError) as exc:
        executor.execute(None, seed=42)
    assert "QST-SIM-101" in str(exc.value)

    with pytest.raises(SimulationError) as exc:
        executor.validate_transpilation(None)
    assert "QST-SIM-102" in str(exc.value)


@pytest.mark.unit
def test_abstract_executor() -> None:
    """Verify abstract methods can be compiled and called using super()."""
    from typing import Any

    class MockExecutor(ExecutorInterface):
        def execute(self, circuit: Any, seed: Optional[int] = None) -> dict[str, int]:
            return super().execute(circuit, seed)  # type: ignore[return-value]

        def validate_transpilation(self, circuit: Any) -> bool:
            return super().validate_transpilation(circuit)

    executor = MockExecutor()
    assert executor.execute(None) is None
    assert executor.validate_transpilation(None) is None


@pytest.mark.unit
def test_aer_executor_non_dict_counts() -> None:
    """Verify AerExecutor raises SimulationError when backend returns non-dict counts."""
    from unittest import mock

    executor = AerExecutor()
    qc = QuantumCircuit(1, 1)
    qc.measure(0, 0)

    mock_result = mock.MagicMock()
    mock_result.get_counts.return_value = ["not_a_dict"]

    mock_job = mock.MagicMock()
    mock_job.result.return_value = mock_result

    with mock.patch.object(executor._simulator, "run", return_value=mock_job):
        with pytest.raises(SimulationError) as exc:
            executor.execute(qc)
        assert "QST-SIM-101" in str(exc.value)
        assert "did not return a counts dictionary" in str(exc.value)
