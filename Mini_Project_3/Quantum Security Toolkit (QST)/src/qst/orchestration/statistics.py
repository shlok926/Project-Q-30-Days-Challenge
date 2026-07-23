"""Experiment statistics calculation service and internal calculator engines.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

import math
from typing import Sequence

from qst.models.results import StatisticsResult


class DescriptiveStatistics:
    """Computes descriptive statistical metrics (mean, median, variance, std_dev)."""

    @staticmethod
    def mean(values: Sequence[float]) -> float:
        """Calculate the arithmetic mean of a sequence of values."""
        if not values:
            return 0.0
        return float(sum(values) / len(values))

    @staticmethod
    def median(values: Sequence[float]) -> float:
        """Calculate the median of a sequence of values."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        length = len(sorted_vals)
        if length % 2 == 1:
            return float(sorted_vals[length // 2])
        else:
            mid = length // 2
            return float((sorted_vals[mid - 1] + sorted_vals[mid]) / 2.0)

    @staticmethod
    def variance(values: Sequence[float]) -> float:
        """Calculate the sample variance of a sequence of values."""
        length = len(values)
        if length <= 1:
            return 0.0
        mean_val = DescriptiveStatistics.mean(values)
        squared_deltas = sum((x - mean_val) ** 2 for x in values)
        return float(squared_deltas / (length - 1))

    @staticmethod
    def standard_deviation(values: Sequence[float]) -> float:
        """Calculate the sample standard deviation of a sequence of values."""
        return float(math.sqrt(DescriptiveStatistics.variance(values)))


class ConfidenceIntervalCalculator:
    """Computes standard confidence intervals using normal distribution approximation."""

    @staticmethod
    def calculate_ci_95(values: Sequence[float]) -> tuple[float, float]:
        """Calculate a basic 95% confidence interval for the mean."""
        length = len(values)
        mean_val = DescriptiveStatistics.mean(values)
        if length <= 1:
            return (mean_val, mean_val)
        std_dev = DescriptiveStatistics.standard_deviation(values)
        margin = 1.96 * (std_dev / math.sqrt(length))
        return (mean_val - margin, mean_val + margin)


class ExperimentStatisticsService:
    """Public service coordinating calculation of all experiment statistics."""

    def calculate_statistics(self, values: Sequence[float]) -> StatisticsResult:
        """Compute standard statistics summary for a sequence of observations.

        Args:
            values: Sequence of numeric values to analyze.

        Returns:
            A StatisticsResult dataclass containing computed metrics.
        """
        if not values:
            return StatisticsResult(
                mean=0.0,
                median=0.0,
                variance=0.0,
                standard_deviation=0.0,
                confidence_interval=(0.0, 0.0),
            )

        mean_val = DescriptiveStatistics.mean(values)
        median_val = DescriptiveStatistics.median(values)
        var_val = DescriptiveStatistics.variance(values)
        std_val = DescriptiveStatistics.standard_deviation(values)
        ci_val = ConfidenceIntervalCalculator.calculate_ci_95(values)

        return StatisticsResult(
            mean=mean_val,
            median=median_val,
            variance=var_val,
            standard_deviation=std_val,
            confidence_interval=ci_val,
        )
