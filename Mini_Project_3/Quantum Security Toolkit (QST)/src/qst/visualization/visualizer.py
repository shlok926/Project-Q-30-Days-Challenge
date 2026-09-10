"""Visualizer dispatcher class.

References:
    Docs/VISUALIZATION_SPEC.md §1-§5
    Docs/07_SYSTEM_ARCHITECTURE.md §5, §11
"""

from typing import Optional

from qst.models.results import SimulationResult
from qst.visualization.backend import VisualizationBackend, VisualizationResult
from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)
from qst.visualization.styles import LightTheme, Theme


class Visualizer:
    """Dispatches dataset render requests onto a configured plotting backend."""

    def __init__(
        self,
        backend: VisualizationBackend,
        theme: Optional[Theme] = None,
    ) -> None:
        """Initialize Visualizer.

        Args:
            backend: A concrete subclass of VisualizationBackend.
            theme: Styling variables to apply. Defaults to LightTheme.
        """
        self.backend = backend
        self.theme = theme or LightTheme()

    def line_chart(
        self,
        series: LineSeries,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Plot a line chart series.

        Args:
            series: The LineSeries dataset.
            filepath: Destination file save path.

        Returns:
            A VisualizationResult payload wrapper.
        """
        return self.backend.line_chart(series, self.theme, filepath)

    def scatter_chart(
        self,
        series: ScatterSeries,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Plot a scatter chart series.

        Args:
            series: The ScatterSeries dataset.
            filepath: Destination file save path.

        Returns:
            A VisualizationResult payload wrapper.
        """
        return self.backend.scatter_chart(series, self.theme, filepath)

    def histogram(
        self,
        series: HistogramSeries,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Plot a histogram.

        Args:
            series: The HistogramSeries dataset.
            filepath: Destination file save path.

        Returns:
            A VisualizationResult payload wrapper.
        """
        return self.backend.histogram(series, self.theme, filepath)

    def heatmap(
        self,
        matrix: HeatmapMatrix,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Plot a heatmap matrix.

        Args:
            matrix: The HeatmapMatrix dataset.
            filepath: Destination file save path.

        Returns:
            A VisualizationResult payload wrapper.
        """
        return self.backend.heatmap(matrix, self.theme, filepath)

    @staticmethod
    def render_basis_table(result: SimulationResult) -> str:
        """Render a text-based table showing qubit state matching.

        Args:
            result: The SimulationResult output to represent.

        Returns:
            A formatted string containing the basis reconciliation table.
        """
        if result.alice_bases is None or result.bob_bases is None:
            return "No bases to compare."

        lines = [
            "Basis Reconciliation Table:",
            f"Alice Bases: {' '.join(result.alice_bases)}",
            f"Bob Bases:   {' '.join(result.bob_bases)}",
        ]

        match_str = []
        for a, b in zip(result.alice_bases, result.bob_bases):
            match_str.append("✔" if a == b else "✘")

        lines.append(f"Matches:     {' '.join(match_str)}")
        return "\n".join(lines)
