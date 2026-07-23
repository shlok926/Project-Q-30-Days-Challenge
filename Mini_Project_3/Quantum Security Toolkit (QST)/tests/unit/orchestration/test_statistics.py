"""Unit tests for the ExperimentStatisticsService, DescriptiveStatistics, and ConfidenceIntervalCalculator.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import math
import pytest

from qst.orchestration.statistics import (
    ConfidenceIntervalCalculator,
    DescriptiveStatistics,
    ExperimentStatisticsService,
)
from qst.models.results import StatisticsResult


@pytest.mark.unit
def test_statistics_empty_and_single() -> None:
    """Verify statistics handle empty or single-item lists gracefully without errors."""
    service = ExperimentStatisticsService()

    # Empty check
    res_empty = service.calculate_statistics([])
    assert isinstance(res_empty, StatisticsResult)
    assert res_empty.mean == 0.0
    assert res_empty.median == 0.0
    assert res_empty.variance == 0.0
    assert res_empty.standard_deviation == 0.0
    assert res_empty.confidence_interval == (0.0, 0.0)

    # Direct helper empty checks
    assert DescriptiveStatistics.mean([]) == 0.0
    assert DescriptiveStatistics.median([]) == 0.0

    # Single check
    res_single = service.calculate_statistics([5.5])
    assert res_single.mean == 5.5
    assert res_single.median == 5.5
    assert res_single.variance == 0.0
    assert res_single.standard_deviation == 0.0
    assert res_single.confidence_interval == (5.5, 5.5)


@pytest.mark.unit
def test_descriptive_statistics_calculations() -> None:
    """Verify correct calculation of mean, median, variance, and standard deviation."""
    values = [1.0, 2.0, 3.0, 4.0, 5.0]

    # Mean: 15 / 5 = 3.0
    assert DescriptiveStatistics.mean(values) == 3.0

    # Median: 3.0 (odd length)
    assert DescriptiveStatistics.median(values) == 3.0

    # Median: even length
    assert DescriptiveStatistics.median([1.0, 2.0, 3.0, 4.0]) == 2.5

    # Variance: ddof=1 sample variance
    # mean=3.0, deviations = [-2, -1, 0, 1, 2] -> squared sum = 4 + 1 + 0 + 1 + 4 = 10
    # var = 10 / (5 - 1) = 2.5
    assert DescriptiveStatistics.variance(values) == 2.5

    # Std dev: sqrt(2.5) ≈ 1.5811388
    assert DescriptiveStatistics.standard_deviation(values) == pytest.approx(
        math.sqrt(2.5)
    )


@pytest.mark.unit
def test_confidence_interval_calculator() -> None:
    """Verify basic 95% confidence interval outputs calculations."""
    values = [10.0, 12.0, 11.0, 13.0, 9.0]
    # mean = 11.0
    # var = (1 + 1 + 0 + 4 + 4) / 4 = 2.5
    # std_dev = sqrt(2.5) ≈ 1.5811
    # margin = 1.96 * (1.5811 / sqrt(5)) ≈ 1.96 * 0.7071 ≈ 1.3859
    # CI = (11.0 - 1.3859, 11.0 + 1.3859) = (9.614, 12.386)
    ci = ConfidenceIntervalCalculator.calculate_ci_95(values)
    assert ci[0] == pytest.approx(9.614, abs=1e-3)
    assert ci[1] == pytest.approx(12.386, abs=1e-3)


@pytest.mark.unit
def test_statistics_service_orchestrated() -> None:
    """Verify the ExperimentStatisticsService calculates values in unified StatisticsResult."""
    service = ExperimentStatisticsService()
    res = service.calculate_statistics([1.0, 2.0, 3.0, 4.0, 5.0])
    assert res.mean == 3.0
    assert res.median == 3.0
    assert res.variance == 2.5
    assert res.standard_deviation == pytest.approx(math.sqrt(2.5))
    assert res.confidence_interval[0] < 3.0
    assert res.confidence_interval[1] > 3.0
