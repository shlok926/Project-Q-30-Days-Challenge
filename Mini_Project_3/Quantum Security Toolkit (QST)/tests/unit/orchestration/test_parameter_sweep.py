"""Unit tests for the ParameterSweepGenerator and orchestrator sweep execution.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.exceptions.validation import ValidationError
from qst.models.config import ProtocolType, SecurityThresholds
from qst.models.results import ParameterSweepResult, SweepDimensions
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.orchestration.sweep_generator import ParameterSweepGenerator
from tests.unit.orchestration.test_orchestrator import FakeProtocol


@pytest.mark.unit
def test_sweep_generator_valid() -> None:
    """Verify ParameterSweepGenerator generates correct Cartesian product configs."""
    qubit_counts = [10, 20]
    interception_probabilities = [0.0, 0.5]
    seeds = [123, None]

    configs = ParameterSweepGenerator.generate_configs(
        qubit_counts=qubit_counts,
        interception_probabilities=interception_probabilities,
        seeds=seeds,
        repetitions=2,
    )

    # Cartesian product size: 2 * 2 * 2 = 8 configs
    assert len(configs) == 8
    for cfg in configs:
        assert cfg.repetitions == 2
        assert cfg.n_qubits in qubit_counts
        assert cfg.interception_probability in interception_probabilities
        assert cfg.seed in seeds


@pytest.mark.unit
def test_sweep_generator_validation_failures() -> None:
    """Verify sweep inputs validate dimensions and boundary limits."""
    # Zero repetitions
    with pytest.raises(ValidationError) as exc:
        ParameterSweepGenerator.generate_configs([10], [0.0], [123], repetitions=0)
    assert "QST-VAL-303" in str(exc.value)

    # Empty inputs lists
    with pytest.raises(ValidationError) as exc:
        ParameterSweepGenerator.generate_configs([], [0.0], [123])
    assert "QST-VAL-304" in str(exc.value)

    # Out of range probability
    with pytest.raises(ValidationError) as exc:
        ParameterSweepGenerator.generate_configs([10], [1.5], [123])
    assert "QST-VAL-202" in str(exc.value)


@pytest.mark.unit
def test_orchestrator_execute_parameter_sweep() -> None:
    """Verify SimulationOrchestrator executes configurations sweeps and returns ParameterSweepResult."""
    orchestrator = SimulationOrchestrator(
        protocol_factory=lambda p_type: FakeProtocol()
    )

    qubit_counts = (10, 20)
    interception_probabilities = (0.0, 1.0)
    seeds = (123,)

    configs = ParameterSweepGenerator.generate_configs(
        qubit_counts=qubit_counts,
        interception_probabilities=interception_probabilities,
        seeds=seeds,
        repetitions=2,
    )

    dimensions = SweepDimensions(
        qubit_counts=qubit_counts,
        interception_probabilities=interception_probabilities,
        seeds=seeds,
    )

    sweep_res = orchestrator.run_parameter_sweep(configs, dimensions)
    assert isinstance(sweep_res, ParameterSweepResult)
    assert sweep_res.total_experiments == 4
    assert len(sweep_res.experiments) == 4
    assert sweep_res.sweep_dimensions == dimensions
    assert sweep_res.metadata.protocol == "BB84"
