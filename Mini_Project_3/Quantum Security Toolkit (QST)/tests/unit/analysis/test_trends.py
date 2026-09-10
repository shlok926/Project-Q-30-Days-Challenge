"""Unit tests for the TrendAnalysisService.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.analysis.trends.trends import TrendAnalysisService
from qst.exceptions.validation import ValidationError
from qst.models.results import (
    ExecutionMetrics,
    ExperimentMetadata,
    ExperimentResult,
    ParameterSweepResult,
    SimulationResult,
    SweepDimensions,
)


@pytest.fixture
def trend_sweep_result() -> ParameterSweepResult:
    # Experiment 1: qubits=10, prob=0.0, reps=2, throughput=100.0, qber=0.01, key_rate=0.5
    sim1 = SimulationResult(
        qber=0.01,
        final_key_length=5,
        key_rate=0.5,
        sifted_key=[0, 1],
        n_qubits=10,
        seed=1,
        eve_intercept_probability=0.0,
        interception_probability=0.0,
    )
    exp1 = ExperimentResult(
        simulations=(sim1,),
        average_qber=0.01,
        average_key_rate=0.5,
        secure_runs=1,
        warning_runs=0,
        compromised_runs=0,
        metrics=ExecutionMetrics(1.0, 1.0, 100.0, 1.0),
        metadata=ExperimentMetadata("BB84", "t", "v", 2, "s"),
    )

    # Experiment 2: qubits=20, prob=0.5, reps=4, throughput=200.0, qber=0.15, key_rate=0.3
    sim2 = SimulationResult(
        qber=0.15,
        final_key_length=6,
        key_rate=0.3,
        sifted_key=[0, 0],
        n_qubits=20,
        seed=2,
        eve_intercept_probability=0.5,
        interception_probability=0.5,
    )
    exp2 = ExperimentResult(
        simulations=(sim2,),
        average_qber=0.15,
        average_key_rate=0.3,
        secure_runs=0,
        warning_runs=1,
        compromised_runs=0,
        metrics=ExecutionMetrics(1.0, 1.0, 200.0, 1.0),
        metadata=ExperimentMetadata("BB84", "t", "v", 4, "s"),
    )

    dims = SweepDimensions(
        qubit_counts=(10, 20),
        interception_probabilities=(0.0, 0.5),
        seeds=(1,),
    )
    return ParameterSweepResult(
        experiments=(exp1, exp2),
        total_experiments=2,
        sweep_dimensions=dims,
        metadata=exp1.metadata,
    )


@pytest.mark.unit
def test_trend_analysis_qber_vs_interception(
    trend_sweep_result: ParameterSweepResult,
) -> None:
    """Verify correct grouping and sorting of QBER vs Interception Probability."""
    service = TrendAnalysisService()
    series = service.analyze_qber_vs_interception(trend_sweep_result)

    assert series.label == "QBER vs Interception Probability"
    assert series.x_values == (0.0, 0.5)
    assert series.y_values == (0.01, 0.15)


@pytest.mark.unit
def test_trend_analysis_key_rate_vs_qubits(
    trend_sweep_result: ParameterSweepResult,
) -> None:
    """Verify correct grouping and sorting of Key Rate vs Qubits Count."""
    service = TrendAnalysisService()
    series = service.analyze_key_rate_vs_qubits(trend_sweep_result)

    assert series.label == "Key Rate vs Qubit Count"
    assert series.x_values == (10.0, 20.0)
    assert series.y_values == (0.5, 0.3)


@pytest.mark.unit
def test_trend_analysis_throughput_vs_repetitions(
    trend_sweep_result: ParameterSweepResult,
) -> None:
    """Verify correct grouping and sorting of Throughput vs Repetitions count."""
    service = TrendAnalysisService()
    series = service.analyze_throughput_vs_repetitions(trend_sweep_result)

    assert series.label == "Throughput vs Repetitions"
    assert series.x_values == (2.0, 4.0)
    assert series.y_values == (100.0, 200.0)


@pytest.mark.unit
def test_trend_analysis_empty_simulations() -> None:
    """Verify TrendAnalysisService skips experiments with empty simulation lists."""
    metadata = ExperimentMetadata("BB84", "t", "v", 2, "s")
    exp = ExperimentResult(
        (), 0.0, 0.0, 0, 0, 0, ExecutionMetrics(1.0, 1.0, 100.0, 1.0), metadata
    )
    sweep = ParameterSweepResult((exp,), 1, SweepDimensions((), (), ()), metadata)

    service = TrendAnalysisService()
    # Empty simulations should raise ValidationError because empty LineSeries datasets are invalid
    with pytest.raises(ValidationError) as exc:
        service.analyze_qber_vs_interception(sweep)
    assert "QST-VAL-705" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        service.analyze_key_rate_vs_qubits(sweep)
    assert "QST-VAL-705" in str(exc.value)
