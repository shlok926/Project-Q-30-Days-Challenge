"""Integration tests for the analysis layer.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md
"""

import pytest

from qst.analysis.aggregators.aggregator import ExperimentAggregator
from qst.analysis.comparisons.comparison import ComparisonService
from qst.analysis.trends.trends import TrendAnalysisService
from qst.models.results import SweepDimensions
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.orchestration.sweep_generator import ParameterSweepGenerator


@pytest.mark.integration
def test_analysis_pipeline_sweeps_aggregates_trends_comparisons() -> None:
    """Verify entire analysis subsystem pipeline works end to end."""
    # 1. Generate configs and execute sweeps
    qubit_counts = [10, 20]
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
    sweep_res_1 = orchestrator.run_parameter_sweep(configs, sweep_dims)
    sweep_res_2 = orchestrator.run_parameter_sweep(configs, sweep_dims)

    # Validate output dimensions
    assert sweep_res_1.total_experiments == 4
    assert len(sweep_res_1.experiments) == 4

    # Validate determinism
    for exp1, exp2 in zip(sweep_res_1.experiments, sweep_res_2.experiments):
        assert exp1.average_qber == exp2.average_qber
        assert exp1.average_key_rate == exp2.average_key_rate
        assert exp1.secure_runs == exp2.secure_runs
        for sim1, sim2 in zip(exp1.simulations, exp2.simulations):
            assert sim1.qber == sim2.qber
            assert sim1.final_key_length == sim2.final_key_length

    # 2. Run Aggregator
    aggregator = ExperimentAggregator()
    agg_res_1 = aggregator.aggregate(sweep_res_1)
    agg_res_2 = aggregator.aggregate(sweep_res_2)

    assert agg_res_1.total_simulations == 8
    assert agg_res_1.average_qber == agg_res_2.average_qber
    assert agg_res_1.average_key_rate == agg_res_2.average_key_rate
    assert agg_res_1.success_ratio == agg_res_2.success_ratio

    # 3. Run Trend Analysis
    trend_service = TrendAnalysisService()
    line_qber = trend_service.analyze_qber_vs_interception(sweep_res_1)
    line_key = trend_service.analyze_key_rate_vs_qubits(sweep_res_1)
    line_through = trend_service.analyze_throughput_vs_repetitions(sweep_res_1)

    assert len(line_qber.x_values) == 2
    assert line_qber.x_values == (0.0, 0.5)
    assert len(line_key.x_values) == 2
    assert line_key.x_values == (10.0, 20.0)
    assert len(line_through.x_values) == 1
    assert line_through.x_values == (2.0,)

    # 4. Run Comparison Service
    comparison_service = ComparisonService()
    comp_res = comparison_service.compare_sweeps(sweep_res_1, sweep_res_2)

    # Only check that non-volatile comparison metrics like QBER, Key Rate, and Success Ratio have no improvements/regressions
    for imp in comp_res.improvements:
        assert "throughput" in imp or "time" in imp
    for reg in comp_res.regressions:
        assert "throughput" in reg or "time" in reg
    assert "Total simulations count shift: 8 -> 8" in comp_res.statistical_differences
