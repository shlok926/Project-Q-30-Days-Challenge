"""Visualization package initialization exposing backends, registry, themes, and datasets.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md §5, §11
"""

from qst.visualization.backend import (
    ChartType,
    VisualizationBackend,
    VisualizationResult,
)
from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    ImageFormat,
    LineSeries,
    ScatterSeries,
)
from qst.visualization.matplotlib_backend import MatplotlibBackend
from qst.visualization.registry import VisualizationBackendRegistry
from qst.visualization.styles import (
    Colors,
    DarkTheme,
    FigureStyle,
    GridStyle,
    LightTheme,
    ScientificTheme,
    Theme,
    Typography,
)
from qst.visualization.visualizer import Visualizer

__all__ = [
    "Visualizer",
    "VisualizationBackend",
    "VisualizationResult",
    "ChartType",
    "MatplotlibBackend",
    "VisualizationBackendRegistry",
    "Theme",
    "LightTheme",
    "DarkTheme",
    "ScientificTheme",
    "Typography",
    "Colors",
    "GridStyle",
    "FigureStyle",
    "ImageFormat",
    "LineSeries",
    "ScatterSeries",
    "HistogramSeries",
    "HeatmapMatrix",
]
