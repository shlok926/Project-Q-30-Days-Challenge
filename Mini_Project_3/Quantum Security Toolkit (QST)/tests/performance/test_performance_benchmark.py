"""Performance benchmarks for detecting QST execution regressions.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md
"""

import time

import pytest

from qst.models.results import SweepDimensions
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.orchestration.sweep_generator import ParameterSweepGenerator


@pytest.mark.performance
def test_performance_benchmark_sweep_threshold() -> None:
    """Execute a controlled parameter sweep and assert execution duration bounds."""
    qubit_counts = [5, 10]
    probabilities = [0.0, 0.5]
    seeds = [42]
    repetitions = 2

    configs = ParameterSweepGenerator.generate_configs(
        qubit_counts=qubit_counts,
        interception_probabilities=probabilities,
        seeds=seeds,
        repetitions=repetitions,
    )
    sweep_dims = SweepDimensions(
        qubit_counts=tuple(qubit_counts),
        interception_probabilities=tuple(probabilities),
        seeds=tuple(seeds),
    )

    orchestrator = SimulationOrchestrator()

    # Measure start time
    t_start = time.perf_counter()
    res = orchestrator.run_parameter_sweep(configs, sweep_dims)
    t_duration = time.perf_counter() - t_start

    # Verify results are valid
    assert res.total_experiments == 4
    assert res.experiments[0].metrics.throughput > 0.0

    # Ensure suite stays extremely fast and checks performance bounds (threshold: 10.0s)
    assert (
        t_duration < 10.0
    ), f"Performance regression detected: sweep took {t_duration:.2f} seconds."
