"""Unit tests for QST results serializers.

References:
    Docs/EXPORT_SPEC.md §3
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.models.results import (
    EveSimulationResult,
    ExecutionMetrics,
    ExperimentMetadata,
    ExperimentResult,
    ParameterSweepResult,
    QBERResult,
    ReconciliationResult,
    SecurityMetrics,
    SecurityStatus,
    SiftedKeyResult,
    SimulationResult,
    SweepDimensions,
)
from qst.reporting.serializers.serializers import (
    ExperimentSerializer,
    ParameterSweepSerializer,
    SimulationSerializer,
)


@pytest.fixture
def sample_simulation_result() -> SimulationResult:
    recon = ReconciliationResult(
        matching_indices=(0, 2),
        discarded_indices=(1,),
        matching_bases=("Z", "Z"),
        total_bits=3,
        matching_count=2,
        match_rate=0.66,
    )
    sifted = SiftedKeyResult(
        alice_key=(1, 0),
        bob_key=(1, 0),
        key_length=2,
    )
    eve = EveSimulationResult(
        intercepted_mask=(False, True, False),
        eve_bases=("X", "Z", "X"),
        eve_measurements=(0, 0, 1),
        reconstructed_bits=(0, 0, 1),
        reconstructed_bases=("X", "Z", "X"),
    )
    qber = QBERResult(
        error_count=0,
        sifted_key_length=2,
        qber=0.0,
        confidence_notes="High confidence",
    )
    metrics = SecurityMetrics(
        key_rate=0.66,
        discard_rate=0.33,
        error_rate=0.0,
        status=SecurityStatus.SECURE,
    )

    return SimulationResult(
        qber=0.0,
        final_key_length=2,
        key_rate=0.66,
        sifted_key=[1, 0],
        n_qubits=3,
        seed=123,
        eve_intercept_probability=0.0,
        warnings=[],
        metadata={},
        alice_bits=(1, 0, 1),
        bob_bits=(1, 1, 1),
        alice_bases=("Z", "X", "Z"),
        bob_bases=("Z", "Z", "Z"),
        reconciliation=recon,
        sifted_keys=sifted,
        eve_simulation=eve,
        qber_result=qber,
        security_metrics=metrics,
    )


@pytest.mark.unit
def test_simulation_serializer_valid(
    sample_simulation_result: SimulationResult,
) -> None:
    """Verify SimulationSerializer converts SimulationResult to nested dictionary."""
    serializer = SimulationSerializer()
    serialized = serializer.serialize(sample_simulation_result)

    assert isinstance(serialized, dict)
    assert serialized["qber"] == 0.0
    assert serialized["n_qubits"] == 3
    assert serialized["reconciliation"]["matching_count"] == 2
    assert serialized["sifted_keys"]["key_length"] == 2
    assert serialized["eve_simulation"]["reconstructed_bits"] == (0, 0, 1)
    assert serialized["qber_result"]["confidence_notes"] == "High confidence"
    assert serialized["security_metrics"]["status"] == "SECURE"


@pytest.mark.unit
def test_simulation_serializer_invalid() -> None:
    """Verify SimulationSerializer type assertions."""
    serializer = SimulationSerializer()
    with pytest.raises(TypeError):
        serializer.serialize("not-a-simulation-result")


@pytest.mark.unit
def test_experiment_serializer_valid(
    sample_simulation_result: SimulationResult,
) -> None:
    """Verify ExperimentSerializer converts ExperimentResult to nested dictionary."""
    metrics = ExecutionMetrics(
        execution_time=1.2,
        average_simulation_time=0.6,
        throughput=10.0,
        simulations_per_second=2.0,
    )
    metadata = ExperimentMetadata(
        protocol="BB84",
        timestamp="2026-07-23T22:00:00Z",
        qiskit_version="1.0.0",
        repetitions=2,
        seed_strategy="seeded",
    )
    exp = ExperimentResult(
        simulations=(sample_simulation_result,),
        average_qber=0.0,
        average_key_rate=0.66,
        secure_runs=1,
        warning_runs=0,
        compromised_runs=0,
        metrics=metrics,
        metadata=metadata,
    )

    serializer = ExperimentSerializer()
    serialized = serializer.serialize(exp)

    assert isinstance(serialized, dict)
    assert len(serialized["simulations"]) == 1
    assert serialized["average_qber"] == 0.0
    assert serialized["metrics"]["execution_time"] == 1.2
    assert serialized["metadata"]["protocol"] == "BB84"


@pytest.mark.unit
def test_experiment_serializer_invalid() -> None:
    """Verify ExperimentSerializer type assertions."""
    serializer = ExperimentSerializer()
    with pytest.raises(TypeError):
        serializer.serialize("not-an-experiment-result")


@pytest.mark.unit
def test_parameter_sweep_serializer_valid(
    sample_simulation_result: SimulationResult,
) -> None:
    """Verify ParameterSweepSerializer converts ParameterSweepResult to nested dictionary."""
    metrics = ExecutionMetrics(
        execution_time=1.2,
        average_simulation_time=0.6,
        throughput=10.0,
        simulations_per_second=2.0,
    )
    metadata = ExperimentMetadata(
        protocol="BB84",
        timestamp="2026-07-23T22:00:00Z",
        qiskit_version="1.0.0",
        repetitions=2,
        seed_strategy="seeded",
    )
    exp = ExperimentResult(
        simulations=(sample_simulation_result,),
        average_qber=0.0,
        average_key_rate=0.66,
        secure_runs=1,
        warning_runs=0,
        compromised_runs=0,
        metrics=metrics,
        metadata=metadata,
    )
    dims = SweepDimensions(
        qubit_counts=(10, 20),
        interception_probabilities=(0.0, 0.5),
        seeds=(123, None),
    )
    sweep = ParameterSweepResult(
        experiments=(exp,),
        total_experiments=1,
        sweep_dimensions=dims,
        metadata=metadata,
    )

    serializer = ParameterSweepSerializer()
    serialized = serializer.serialize(sweep)

    assert isinstance(serialized, dict)
    assert len(serialized["experiments"]) == 1
    assert serialized["sweep_dimensions"]["qubit_counts"] == (10, 20)
    assert serialized["metadata"]["protocol"] == "BB84"


@pytest.mark.unit
def test_parameter_sweep_serializer_invalid() -> None:
    """Verify ParameterSweepSerializer type assertions."""
    serializer = ParameterSweepSerializer()
    with pytest.raises(TypeError):
        serializer.serialize("not-a-sweep-result")


@pytest.mark.unit
def test_simulation_serializer_nones() -> None:
    """Verify SimulationSerializer handles None values in optional properties cleanly."""
    res = SimulationResult(
        qber=None,
        final_key_length=0,
        key_rate=0.0,
        sifted_key=[],
        n_qubits=10,
        seed=None,
        eve_intercept_probability=0.0,
        reconciliation=None,
        sifted_keys=None,
        eve_simulation=None,
        qber_result=None,
        security_metrics=None,
    )
    serializer = SimulationSerializer()
    serialized = serializer.serialize(res)
    assert serialized["reconciliation"] is None
    assert serialized["sifted_keys"] is None
    assert serialized["eve_simulation"] is None
    assert serialized["qber_result"] is None
    assert serialized["security_metrics"] is None


@pytest.mark.unit
def test_abstract_serializer_pass() -> None:
    """Verify Serializer base abstract class serialize method coverage."""
    from qst.reporting.serializers.serializers import Serializer

    assert Serializer.serialize(None, None) is None
