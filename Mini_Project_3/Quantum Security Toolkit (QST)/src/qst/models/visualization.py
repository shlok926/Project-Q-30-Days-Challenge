"""VisualizationResult model for QST.

References:
    Docs/VISUALIZATION_SPEC.md §2, §6
"""

from dataclasses import dataclass, field
from typing import Any

from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)


@dataclass(frozen=True)
class VisualizationResult:
    """Coordinate, styling, and text payload representing plotted data.

    Attributes:
        coordinates: List of (x, y) plot coordinates.
        title: Descriptive graph title.
        labels: Mapping of axis names to text representations.
        extra: Additional metadata or rendering config properties.
    """

    coordinates: list[tuple[float, float]]
    title: str
    labels: dict[str, str]
    extra: dict[str, Any] = field(default_factory=dict)


__all__ = [
    "VisualizationResult",
    "HeatmapMatrix",
    "HistogramSeries",
    "LineSeries",
    "ScatterSeries",
]



