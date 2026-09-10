"""Integration tests for the visualization pipeline.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md
"""

import os

import pytest

from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)
from qst.visualization.matplotlib_backend import MatplotlibBackend
from qst.visualization.styles import DarkTheme, LightTheme, ScientificTheme
from qst.visualization.visualizer import Visualizer


@pytest.mark.integration
@pytest.mark.parametrize("file_format", ["png", "svg", "pdf"])
def test_visualization_formats_and_dimensions(tmp_path, file_format) -> None:
    """Verify that all chart types generate files of non-zero size for various file suffixes."""
    backend = MatplotlibBackend(overwrite_protection=False)
    visualizer_light = Visualizer(backend, LightTheme())
    visualizer_dark = Visualizer(backend, DarkTheme())
    visualizer_sci = Visualizer(backend, ScientificTheme())

    # Line Chart
    line_data = LineSeries("Line Trend", (1.0, 2.0, 3.0), (10.0, 15.0, 12.0))
    line_path = os.path.join(tmp_path, f"line.{file_format}")
    res = visualizer_light.line_chart(line_data, line_path)
    assert os.path.exists(line_path)
    assert os.path.getsize(line_path) > 0
    assert res.format == file_format.upper()

    # Scatter Chart
    scatter_data = ScatterSeries("Scatter points", (1.0, 2.0), (5.0, 8.0))
    scatter_path = os.path.join(tmp_path, f"scatter.{file_format}")
    res = visualizer_dark.scatter_chart(scatter_data, scatter_path)
    assert os.path.exists(scatter_path)
    assert os.path.getsize(scatter_path) > 0
    assert res.format == file_format.upper()

    # Histogram Chart
    hist_data = HistogramSeries("Hist", (1.5, 2.5), (1.0, 2.0, 3.0), (5, 10))
    hist_path = os.path.join(tmp_path, f"hist.{file_format}")
    res = visualizer_sci.histogram(hist_data, hist_path)
    assert os.path.exists(hist_path)
    assert os.path.getsize(hist_path) > 0
    assert res.format == file_format.upper()

    # Heatmap Matrix Chart
    matrix = ((1.0, 2.0), (3.0, 4.0))
    heatmap_data = HeatmapMatrix("Heatmap", ("X1", "X2"), ("Y1", "Y2"), matrix)
    heatmap_path = os.path.join(tmp_path, f"heatmap.{file_format}")
    res = visualizer_light.heatmap(heatmap_data, heatmap_path)
    assert os.path.exists(heatmap_path)
    assert os.path.getsize(heatmap_path) > 0
    assert res.format == file_format.upper()
