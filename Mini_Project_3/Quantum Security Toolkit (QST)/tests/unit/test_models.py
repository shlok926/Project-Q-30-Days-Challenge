"""Unit tests for QST domain models and their built-in validations.

References:
    Docs/10_API_SPECIFICATION.md §5
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.exceptions.validation import ValidationError
from qst.models.config import SimulationConfig
from qst.models.results import BatchResult, SimulationResult


@pytest.mark.unit
def test_simulation_config_valid() -> None:
    """Verify SimulationConfig instantiates correctly with valid parameters."""
    cfg = SimulationConfig(n_qubits=100, seed=42, eve_intercept_probability=0.5)
    assert cfg.n_qubits == 100
    assert cfg.seed == 42
    assert cfg.eve_intercept_probability == 0.5


@pytest.mark.unit
def test_simulation_config_invalid() -> None:
    """Verify SimulationConfig validation flags incorrect configuration parameters."""
    with pytest.raises(ValidationError):
        SimulationConfig(n_qubits=-50)

    with pytest.raises(ValidationError):
        SimulationConfig(n_qubits=100, eve_intercept_probability=1.5)

    with pytest.raises(ValidationError) as exc:
        SimulationConfig(n_qubits=100, repetitions=0)
    assert "QST-VAL-303" in str(exc.value)


@pytest.mark.unit
def test_simulation_result_valid() -> None:
    """Verify SimulationResult accepts valid inputs."""
    res = SimulationResult(
        qber=0.25,
        final_key_length=50,
        key_rate=0.5,
        sifted_key=[0, 1, 0, 1],
        n_qubits=100,
        seed=42,
        eve_intercept_probability=0.5,
    )
    assert res.qber == 0.25
    assert res.key_rate == 0.5
    assert res.final_key_length == 50


@pytest.mark.unit
def test_simulation_result_invalid() -> None:
    """Verify SimulationResult rejects out-of-bound ranges."""
    with pytest.raises(ValidationError):
        SimulationResult(
            qber=1.2,
            final_key_length=50,
            key_rate=0.5,
            sifted_key=[0, 1],
            n_qubits=100,
            seed=42,
            eve_intercept_probability=0.5,
        )

    with pytest.raises(ValidationError):
        SimulationResult(
            qber=0.2,
            final_key_length=-5,
            key_rate=0.5,
            sifted_key=[0, 1],
            n_qubits=100,
            seed=42,
            eve_intercept_probability=0.5,
        )

    with pytest.raises(ValidationError):
        SimulationResult(
            qber=0.2,
            final_key_length=50,
            key_rate=-0.1,
            sifted_key=[0, 1],
            n_qubits=100,
            seed=42,
            eve_intercept_probability=0.5,
        )
    with pytest.raises(ValidationError):
        SimulationResult(
            qber=0.2,
            final_key_length=50,
            key_rate=0.5,
            sifted_key=[0, 1],
            n_qubits=100,
            seed=42,
            eve_intercept_probability=0.5,
            interception_probability=1.5,
        )


@pytest.mark.unit
def test_batch_result_valid() -> None:
    """Verify BatchResult matches run count checks."""
    res = SimulationResult(
        qber=0.25,
        final_key_length=50,
        key_rate=0.5,
        sifted_key=[0, 1, 0, 1],
        n_qubits=100,
        seed=42,
        eve_intercept_probability=0.5,
    )
    batch = BatchResult(run_count=1, results=[res])
    assert batch.run_count == 1
    assert len(batch.results) == 1


@pytest.mark.unit
def test_batch_result_invalid() -> None:
    """Verify BatchResult validation flags mismatched count properties."""
    res = SimulationResult(
        qber=0.25,
        final_key_length=50,
        key_rate=0.5,
        sifted_key=[0, 1, 0, 1],
        n_qubits=100,
        seed=42,
        eve_intercept_probability=0.5,
    )
    with pytest.raises(ValidationError):
        BatchResult(run_count=2, results=[res])
