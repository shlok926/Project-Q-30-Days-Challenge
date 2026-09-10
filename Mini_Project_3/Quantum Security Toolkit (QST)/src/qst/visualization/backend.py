"""Abstract base classes for plotting backends and rendering results.

References:
    Docs/VISUALIZATION_SPEC.md §3
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

import abc
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)
from qst.visualization.styles import Theme


class ChartType(Enum):
    """Enumeration representing chart plot categories."""

    LINE = "LINE"
    SCATTER = "SCATTER"
    HISTOGRAM = "HISTOGRAM"
    HEATMAP = "HEATMAP"


@dataclass(frozen=True)
class VisualizationResult:
    """Immutable encapsulation representing a generated chart layout.

    Attributes:
        figure: The generated plot or canvas figure object.
        filepath: Storage destination if plot was saved to disk.
        width: Canvas width coordinate span.
        height: Canvas height coordinate span.
        dpi: Target pixel density configuration.
        format: Exported image format identifier string.
    """

    figure: Any
    filepath: Optional[str]
    width: float
    height: float
    dpi: int
    format: Optional[str]


class VisualizationBackend(abc.ABC):
    """Abstract interface defining the visualizer plotting contract."""

    @abc.abstractmethod
    def render(
        self,
        dataset: Any,
        chart_type: ChartType,
        theme: Theme,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Render a dataset coordinate collection onto a canvas visual.

        Args:
            dataset: Data presentation series object.
            chart_type: Enum ChartType category target.
            theme: Styling variables to apply.
            filepath: Target file destination to write.

        Returns:
            A VisualizationResult wrapper model.
        """
        pass

    def line_chart(
        self,
        series: LineSeries,
        theme: Theme,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Convenience method rendering a line graph series.

        Args:
            series: Data presentation series object.
            theme: Styling variables to apply.
            filepath: Target file destination to write.

        Returns:
            A VisualizationResult wrapper model.
        """
        return self.render(series, ChartType.LINE, theme, filepath)

    def scatter_chart(
        self,
        series: ScatterSeries,
        theme: Theme,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Convenience method rendering a scatter graph series.

        Args:
            series: Data presentation series object.
            theme: Styling variables to apply.
            filepath: Target file destination to write.

        Returns:
            A VisualizationResult wrapper model.
        """
        return self.render(series, ChartType.SCATTER, theme, filepath)

    def histogram(
        self,
        series: HistogramSeries,
        theme: Theme,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Convenience method rendering a histogram.

        Args:
            series: Data presentation series object.
            theme: Styling variables to apply.
            filepath: Target file destination to write.

        Returns:
            A VisualizationResult wrapper model.
        """
        return self.render(series, ChartType.HISTOGRAM, theme, filepath)

    def heatmap(
        self,
        matrix: HeatmapMatrix,
        theme: Theme,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Convenience method rendering a heatmap grid.

        Args:
            matrix: Data presentation series object.
            theme: Styling variables to apply.
            filepath: Target file destination to write.

        Returns:
            A VisualizationResult wrapper model.
        """
        return self.render(matrix, ChartType.HEATMAP, theme, filepath)
