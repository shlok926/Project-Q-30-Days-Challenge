"""Trend analysis service generating LineSeries datasets.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

from qst.models.results import ParameterSweepResult
from qst.visualization.datasets import LineSeries


class TrendAnalysisService:
    """Generates visualization-ready dataset series representing parameter trends."""

    def analyze_qber_vs_interception(
        self, sweep_result: ParameterSweepResult
    ) -> LineSeries:
        """Examine changes in QBER as interception probability varies.

        Args:
            sweep_result: ParameterSweepResult sweep observations.

        Returns:
            A LineSeries ready for plotting.
        """
        groups: dict[float, list[float]] = {}
        for exp in sweep_result.experiments:
            if not exp.simulations:
                continue
            prob = exp.simulations[0].interception_probability
            groups.setdefault(prob, []).append(exp.average_qber)

        sorted_probs = sorted(groups.keys())
        avg_qbers = [float(sum(groups[p]) / len(groups[p])) for p in sorted_probs]

        return LineSeries(
            label="QBER vs Interception Probability",
            x_values=tuple(sorted_probs),
            y_values=tuple(avg_qbers),
        )

    def analyze_key_rate_vs_qubits(
        self, sweep_result: ParameterSweepResult
    ) -> LineSeries:
        """Examine changes in key rate as qubit count varies.

        Args:
            sweep_result: ParameterSweepResult sweep observations.

        Returns:
            A LineSeries ready for plotting.
        """
        groups: dict[int, list[float]] = {}
        for exp in sweep_result.experiments:
            if not exp.simulations:
                continue
            qubits = exp.simulations[0].n_qubits
            groups.setdefault(qubits, []).append(exp.average_key_rate)

        sorted_qubits = sorted(groups.keys())
        avg_key_rates = [float(sum(groups[q]) / len(groups[q])) for q in sorted_qubits]

        return LineSeries(
            label="Key Rate vs Qubit Count",
            x_values=tuple(float(q) for q in sorted_qubits),
            y_values=tuple(avg_key_rates),
        )

    def analyze_throughput_vs_repetitions(
        self, sweep_result: ParameterSweepResult
    ) -> LineSeries:
        """Examine changes in throughput as repetition count varies.

        Args:
            sweep_result: ParameterSweepResult sweep observations.

        Returns:
            A LineSeries ready for plotting.
        """
        groups: dict[int, list[float]] = {}
        for exp in sweep_result.experiments:
            rep = exp.metadata.repetitions
            groups.setdefault(rep, []).append(exp.metrics.throughput)

        sorted_reps = sorted(groups.keys())
        avg_throughputs = [float(sum(groups[r]) / len(groups[r])) for r in sorted_reps]

        return LineSeries(
            label="Throughput vs Repetitions",
            x_values=tuple(float(r) for r in sorted_reps),
            y_values=tuple(avg_throughputs),
        )
