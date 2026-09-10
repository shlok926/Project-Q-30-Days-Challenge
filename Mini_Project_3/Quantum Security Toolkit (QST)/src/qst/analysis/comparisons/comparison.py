"""Comparison service identifying differences between experiment results.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

from dataclasses import dataclass

from qst.analysis.aggregators.aggregator import ExperimentAggregator
from qst.models.results import ExperimentResult, ParameterSweepResult


@dataclass(frozen=True)
class ComparisonResult:
    """Immutable representation of differences between two executions.

    Attributes:
        improvements: List of metrics that improved in the second run.
        regressions: List of metrics that degraded in the second run.
        statistical_differences: Description of shifts in security distributions.
    """

    improvements: tuple[str, ...]
    regressions: tuple[str, ...]
    statistical_differences: tuple[str, ...]


class ComparisonService:
    """Compares experiments and parameter sweeps to highlight performance shifts."""

    def compare_experiments(
        self, exp1: ExperimentResult, exp2: ExperimentResult
    ) -> ComparisonResult:
        """Compare two individual ExperimentResult results.

        Args:
            exp1: Baseline ExperimentResult.
            exp2: Target ExperimentResult to compare.

        Returns:
            A ComparisonResult object detailing changes.
        """
        improvements = []
        regressions = []
        stats_diffs = []

        # QBER comparison (lower QBER is better)
        if exp2.average_qber < exp1.average_qber:
            improvements.append(
                f"QBER decreased from {exp1.average_qber} to {exp2.average_qber}"
            )
        elif exp2.average_qber > exp1.average_qber:
            regressions.append(
                f"QBER increased from {exp1.average_qber} to {exp2.average_qber}"
            )

        # Key rate comparison (higher key rate is better)
        if exp2.average_key_rate > exp1.average_key_rate:
            improvements.append(
                f"Key rate increased from {exp1.average_key_rate} to {exp2.average_key_rate}"
            )
        elif exp2.average_key_rate < exp1.average_key_rate:
            regressions.append(
                f"Key rate decreased from {exp1.average_key_rate} to {exp2.average_key_rate}"
            )

        # Throughput comparison (higher is better)
        t1 = exp1.metrics.throughput
        t2 = exp2.metrics.throughput
        if t2 > t1:
            improvements.append(f"Throughput increased from {t1} to {t2}")
        elif t2 < t1:
            regressions.append(f"Throughput decreased from {t1} to {t2}")

        # Distribution shift description
        stats_diffs.append(
            f"Secure runs shift: {exp1.secure_runs} -> {exp2.secure_runs}"
        )
        stats_diffs.append(
            f"Warning runs shift: {exp1.warning_runs} -> {exp2.warning_runs}"
        )
        stats_diffs.append(
            f"Compromised runs shift: {exp1.compromised_runs} -> {exp2.compromised_runs}"
        )

        return ComparisonResult(
            improvements=tuple(improvements),
            regressions=tuple(regressions),
            statistical_differences=tuple(stats_diffs),
        )

    def compare_sweeps(
        self, sweep1: ParameterSweepResult, sweep2: ParameterSweepResult
    ) -> ComparisonResult:
        """Compare two ParameterSweepResult sweeps by aggregating their metrics.

        Args:
            sweep1: Baseline ParameterSweepResult.
            sweep2: Target ParameterSweepResult to compare.

        Returns:
            A ComparisonResult object detailing changes.
        """
        aggregator = ExperimentAggregator()
        agg1 = aggregator.aggregate(sweep1)
        agg2 = aggregator.aggregate(sweep2)

        improvements = []
        regressions = []
        stats_diffs = []

        # QBER comparison
        if agg2.average_qber < agg1.average_qber:
            improvements.append(
                f"Aggregated QBER decreased from {agg1.average_qber} to {agg2.average_qber}"
            )
        elif agg2.average_qber > agg1.average_qber:
            regressions.append(
                f"Aggregated QBER increased from {agg1.average_qber} to {agg2.average_qber}"
            )

        # Key rate comparison
        if agg2.average_key_rate > agg1.average_key_rate:
            improvements.append(
                f"Aggregated key rate increased from {agg1.average_key_rate} to {agg2.average_key_rate}"
            )
        elif agg2.average_key_rate < agg1.average_key_rate:
            regressions.append(
                f"Aggregated key rate decreased from {agg1.average_key_rate} to {agg2.average_key_rate}"
            )

        # Throughput comparison
        if agg2.average_throughput > agg1.average_throughput:
            improvements.append(
                f"Aggregated throughput increased from {agg1.average_throughput} to {agg2.average_throughput}"
            )
        elif agg2.average_throughput < agg1.average_throughput:
            regressions.append(
                f"Aggregated throughput decreased from {agg1.average_throughput} to {agg2.average_throughput}"
            )

        # Success ratio comparison
        if agg2.success_ratio > agg1.success_ratio:
            improvements.append(
                f"Aggregated success ratio increased from {agg1.success_ratio} to {agg2.success_ratio}"
            )
        elif agg2.success_ratio < agg1.success_ratio:
            regressions.append(
                f"Aggregated success ratio decreased from {agg1.success_ratio} to {agg2.success_ratio}"
            )

        stats_diffs.append(
            f"Total simulations count shift: {agg1.total_simulations} -> {agg2.total_simulations}"
        )

        return ComparisonResult(
            improvements=tuple(improvements),
            regressions=tuple(regressions),
            statistical_differences=tuple(stats_diffs),
        )
