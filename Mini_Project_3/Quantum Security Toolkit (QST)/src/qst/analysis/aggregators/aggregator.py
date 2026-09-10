"""Experiment metrics aggregator.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

from dataclasses import dataclass

from qst.models.results import ParameterSweepResult, SecurityStatus, SimulationResult


@dataclass(frozen=True)
class AggregationResult:
    """Immutable representation of aggregated sweep result metrics.

    Attributes:
        average_qber: Mean QBER rate across all simulations.
        average_key_rate: Mean key rate across all simulations.
        average_throughput: Mean throughput processed.
        success_ratio: Ratio of secure runs over total runs.
        total_simulations: Total number of execution loops aggregated.
    """

    average_qber: float
    average_key_rate: float
    average_throughput: float
    success_ratio: float
    total_simulations: int


class ExperimentAggregator:
    """Aggregates metrics across parameter sweep results."""

    def aggregate(self, sweep_result: ParameterSweepResult) -> AggregationResult:
        """Aggregate all trials contained within a parameter sweep result.

        Args:
            sweep_result: ParameterSweepResult object.

        Returns:
            An AggregationResult holding combined values.
        """
        all_sims: list[SimulationResult] = []
        throughputs: list[float] = []

        for exp in sweep_result.experiments:
            all_sims.extend(exp.simulations)
            throughputs.append(exp.metrics.throughput)

        if not all_sims:
            return AggregationResult(
                average_qber=0.0,
                average_key_rate=0.0,
                average_throughput=0.0,
                success_ratio=0.0,
                total_simulations=0,
            )

        qbers = [s.qber for s in all_sims if s.qber is not None]
        key_rates = [s.key_rate for s in all_sims if s.key_rate is not None]

        avg_qber = float(sum(qbers) / len(qbers)) if qbers else 0.0
        avg_key_rate = float(sum(key_rates) / len(key_rates)) if key_rates else 0.0
        avg_throughput = (
            float(sum(throughputs) / len(throughputs)) if throughputs else 0.0
        )

        # Success ratio: secure runs / total simulations count
        secure_count = len([
            s
            for s in all_sims
            if s.security_metrics and s.security_metrics.status == SecurityStatus.SECURE
        ])
        success_ratio = float(secure_count / len(all_sims))

        return AggregationResult(
            average_qber=avg_qber,
            average_key_rate=avg_key_rate,
            average_throughput=avg_throughput,
            success_ratio=success_ratio,
            total_simulations=len(all_sims),
        )
