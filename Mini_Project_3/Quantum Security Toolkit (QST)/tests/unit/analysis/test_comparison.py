"""Unit tests for the ComparisonService and visualization dataset models validation.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.analysis.comparisons.comparison import (
    ComparisonResult,
    ComparisonService,
)
from qst.exceptions.validation import ValidationError
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
from qst.models.visualization import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)


@pytest.fixture
def base_experiment() -> ExperimentResult:
    return ExperimentResult(
        simulations=(),
        average_qber=0.1,
        average_key_rate=0.4,
        secure_runs=5,
        warning_runs=2,
        compromised_runs=1,
        metrics=ExecutionMetrics(1.0, 1.0, 100.0, 1.0),
        metadata=ExperimentMetadata("BB84", "t", "v", 2, "s"),
    )


@pytest.mark.unit
def test_compare_experiments_improvement(base_experiment: ExperimentResult) -> None:
    """Verify comparison highlights improvements (lower QBER, higher key rate, higher throughput)."""
    better_exp = ExperimentResult(
        simulations=(),
        average_qber=0.05,  # Better
        average_key_rate=0.5,  # Better
        secure_runs=6,
        warning_runs=1,
        compromised_runs=1,
        metrics=ExecutionMetrics(1.0, 1.0, 150.0, 1.0),  # Better
        metadata=base_experiment.metadata,
    )

    service = ComparisonService()
    res = service.compare_experiments(base_experiment, better_exp)

    assert isinstance(res, ComparisonResult)
    assert len(res.improvements) == 3
    assert any("QBER decreased" in imp for imp in res.improvements)
    assert any("Key rate increased" in imp for imp in res.improvements)
    assert any("Throughput increased" in imp for imp in res.improvements)
    assert not res.regressions


@pytest.mark.unit
def test_compare_experiments_regression(base_experiment: ExperimentResult) -> None:
    """Verify comparison highlights regressions (higher QBER, lower key rate, lower throughput)."""
    worse_exp = ExperimentResult(
        simulations=(),
        average_qber=0.15,  # Worse
        average_key_rate=0.3,  # Worse
        secure_runs=4,
        warning_runs=2,
        compromised_runs=2,
        metrics=ExecutionMetrics(1.0, 1.0, 50.0, 1.0),  # Worse
        metadata=base_experiment.metadata,
    )

    service = ComparisonService()
    res = service.compare_experiments(base_experiment, worse_exp)

    assert len(res.regressions) == 3
    assert any("QBER increased" in reg for reg in res.regressions)
    assert any("Key rate decreased" in reg for reg in res.regressions)
    assert any("Throughput decreased" in reg for reg in res.regressions)
    assert not res.improvements


@pytest.mark.unit
def test_compare_sweeps_differential() -> None:
    """Verify sweep comparison aggregates details and tracks relative shifts."""
    metadata = ExperimentMetadata("BB84", "t", "v", 2, "s")
    sec_metrics = SecurityMetrics(0.5, 0.5, 0.0, SecurityStatus.SECURE)
    warn_metrics = SecurityMetrics(0.35, 0.65, 0.15, SecurityStatus.WARNING)

    sim1 = SimulationResult(
        qber=0.05,
        final_key_length=10,
        key_rate=0.45,
        sifted_key=[],
        n_qubits=20,
        seed=1,
        eve_intercept_probability=0.0,
        security_metrics=sec_metrics,
    )
    sim2 = SimulationResult(
        qber=0.15,
        final_key_length=8,
        key_rate=0.35,
        sifted_key=[],
        n_qubits=20,
        seed=2,
        eve_intercept_probability=0.5,
        security_metrics=warn_metrics,
    )

    # Sweep 1
    exp1 = ExperimentResult(
        (sim1,), 0.05, 0.45, 1, 0, 0, ExecutionMetrics(1.0, 1.0, 100.0, 1.0), metadata
    )
    sweep1 = ParameterSweepResult((exp1,), 1, SweepDimensions((), (), ()), metadata)

    # Sweep 2 (Worse)
    exp2 = ExperimentResult(
        (sim2,), 0.15, 0.35, 0, 1, 0, ExecutionMetrics(1.0, 1.0, 50.0, 1.0), metadata
    )
    sweep2 = ParameterSweepResult((exp2,), 1, SweepDimensions((), (), ()), metadata)

    service = ComparisonService()
    res = service.compare_sweeps(sweep1, sweep2)

    assert len(res.regressions) == 4  # QBER, key rate, throughput, success ratio
    assert any("QBER increased" in reg for reg in res.regressions)
    assert any("success ratio decreased" in reg for reg in res.regressions)


@pytest.mark.unit
def test_dataset_models_validations() -> None:
    """Verify LineSeries, ScatterSeries, HistogramSeries, HeatmapMatrix dimensions validation."""
    # LineSeries dimensions mismatch
    with pytest.raises(ValidationError) as exc:
        LineSeries("Label", (1.0, 2.0), (1.0,))
    assert "QST-VAL-701" in str(exc.value)

    # ScatterSeries dimensions mismatch
    with pytest.raises(ValidationError) as exc:
        ScatterSeries("Label", (1.0,), (1.0, 2.0))
    assert "QST-VAL-701" in str(exc.value)

    # HistogramSeries bin matching error
    with pytest.raises(ValidationError) as exc:
        HistogramSeries("Label", (1.0,), (0.0, 1.0), (1, 2))
    assert "QST-VAL-702" in str(exc.value)

    # HeatmapMatrix row dimension error
    with pytest.raises(ValidationError) as exc:
        HeatmapMatrix("Label", ("X1",), ("Y1", "Y2"), ((1.0,),))
    assert "QST-VAL-703" in str(exc.value)

    # HeatmapMatrix column dimension error
    with pytest.raises(ValidationError) as exc:
        HeatmapMatrix("Label", ("X1", "X2"), ("Y1",), ((1.0,),))
    assert "QST-VAL-704" in str(exc.value)


@pytest.mark.unit
def test_compare_sweeps_improvements() -> None:
    """Verify sweep comparison highlights improvements (lower QBER, higher key rate/throughput/ratio)."""
    metadata = ExperimentMetadata("BB84", "t", "v", 2, "s")
    sec_metrics = SecurityMetrics(0.5, 0.5, 0.0, SecurityStatus.SECURE)
    warn_metrics = SecurityMetrics(0.35, 0.65, 0.15, SecurityStatus.WARNING)

    sim1 = SimulationResult(
        0.15, 8, 0.35, [], 20, 1, 0.5, security_metrics=warn_metrics
    )
    sim2 = SimulationResult(
        0.05, 10, 0.45, [], 20, 2, 0.0, security_metrics=sec_metrics
    )

    # Sweep 1 (Worse)
    exp1 = ExperimentResult(
        (sim1,), 0.15, 0.35, 0, 1, 0, ExecutionMetrics(1.0, 1.0, 50.0, 1.0), metadata
    )
    sweep1 = ParameterSweepResult((exp1,), 1, SweepDimensions((), (), ()), metadata)

    # Sweep 2 (Better)
    exp2 = ExperimentResult(
        (sim2,), 0.05, 0.45, 1, 0, 0, ExecutionMetrics(1.0, 1.0, 100.0, 1.0), metadata
    )
    sweep2 = ParameterSweepResult((exp2,), 1, SweepDimensions((), (), ()), metadata)

    service = ComparisonService()
    res = service.compare_sweeps(sweep1, sweep2)

    assert len(res.improvements) == 4  # QBER, key rate, throughput, success ratio
    assert any("QBER decreased" in imp for imp in res.improvements)
    assert any("success ratio increased" in imp for imp in res.improvements)
    assert not res.regressions


@pytest.mark.unit
def test_compare_experiments_equal(base_experiment: ExperimentResult) -> None:
    """Verify comparison yields empty changes when experiment results are identical."""
    service = ComparisonService()
    res = service.compare_experiments(base_experiment, base_experiment)
    assert not res.improvements
    assert not res.regressions
