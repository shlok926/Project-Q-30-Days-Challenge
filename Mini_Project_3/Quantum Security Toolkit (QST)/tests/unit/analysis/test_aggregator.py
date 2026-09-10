"""Unit tests for the ExperimentAggregator.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.analysis.aggregators.aggregator import (
    AggregationResult,
    ExperimentAggregator,
)
from qst.models.results import (
    ExecutionMetrics,
    ExperimentMetadata,
    ExperimentResult,
    ParameterSweepResult,
    SecurityMetrics,
    SecurityStatus,
    SimulationResult,
    SweepDimensions,
)


@pytest.fixture
def sample_sweep_result() -> ParameterSweepResult:
    sim1 = SimulationResult(
        qber=0.0,
        final_key_length=10,
        key_rate=0.5,
        sifted_key=[1] * 10,
        n_qubits=20,
        seed=1,
        eve_intercept_probability=0.0,
        security_metrics=SecurityMetrics(
            key_rate=0.5, discard_rate=0.5, error_rate=0.0, status=SecurityStatus.SECURE
        ),
    )
    sim2 = SimulationResult(
        qber=0.1,
        final_key_length=8,
        key_rate=0.4,
        sifted_key=[0] * 8,
        n_qubits=20,
        seed=2,
        eve_intercept_probability=0.0,
        security_metrics=SecurityMetrics(
            key_rate=0.4,
            discard_rate=0.6,
            error_rate=0.1,
            status=SecurityStatus.WARNING,
        ),
    )

    metrics = ExecutionMetrics(
        execution_time=1.0,
        average_simulation_time=0.5,
        throughput=20.0,
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
        simulations=(sim1, sim2),
        average_qber=0.05,
        average_key_rate=0.45,
        secure_runs=1,
        warning_runs=1,
        compromised_runs=0,
        metrics=metrics,
        metadata=metadata,
    )

    dims = SweepDimensions(
        qubit_counts=(20,),
        interception_probabilities=(0.0,),
        seeds=(42,),
    )

    return ParameterSweepResult(
        experiments=(exp,),
        total_experiments=1,
        sweep_dimensions=dims,
        metadata=metadata,
    )


@pytest.mark.unit
def test_aggregator_success(sample_sweep_result: ParameterSweepResult) -> None:
    """Verify ExperimentAggregator computes averages and success ratio correctly."""
    aggregator = ExperimentAggregator()
    res = aggregator.aggregate(sample_sweep_result)

    assert isinstance(res, AggregationResult)
    assert res.average_qber == pytest.approx(0.05)
    assert res.average_key_rate == pytest.approx(0.45)
    assert res.average_throughput == pytest.approx(20.0)
    assert res.success_ratio == pytest.approx(0.5)  # 1 secure run / 2 total runs
    assert res.total_simulations == 2


@pytest.mark.unit
def test_aggregator_empty() -> None:
    """Verify ExperimentAggregator handles empty experiments lists cleanly."""
    metadata = ExperimentMetadata(
        protocol="BB84",
        timestamp="2026-07-23",
        qiskit_version="1.0",
        repetitions=1,
        seed_strategy="none",
    )
    sweep_empty = ParameterSweepResult(
        experiments=(),
        total_experiments=0,
        sweep_dimensions=SweepDimensions((), (), ()),
        metadata=metadata,
    )

    aggregator = ExperimentAggregator()
    res = aggregator.aggregate(sweep_empty)

    assert res.average_qber == 0.0
    assert res.average_key_rate == 0.0
    assert res.average_throughput == 0.0
    assert res.success_ratio == 0.0
    assert res.total_simulations == 0
