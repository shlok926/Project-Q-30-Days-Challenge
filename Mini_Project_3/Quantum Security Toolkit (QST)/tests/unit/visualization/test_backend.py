"""Unit tests for the Matplotlib concrete visualization backend and themes.

References:
    Docs/VISUALIZATION_SPEC.md §3, §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import os
from unittest import mock

import pytest
from matplotlib.figure import Figure

from qst.exceptions.export import ExportError
from qst.exceptions.validation import ValidationError
from qst.visualization.backend import ChartType, VisualizationResult
from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)
from qst.visualization.matplotlib_backend import MatplotlibBackend
from qst.visualization.styles import (
    DarkTheme,
    FigureStyle,
    LightTheme,
    ScientificTheme,
    Typography,
)


@pytest.fixture
def line_dataset() -> LineSeries:
    return LineSeries("Line Plot", (1.0, 2.0, 3.0), (10.0, 15.0, 12.0))


@pytest.fixture
def scatter_dataset() -> ScatterSeries:
    return ScatterSeries("Scatter Plot ⚡", (1.0, 2.0), (5.0, 8.0))


@pytest.fixture
def histogram_dataset() -> HistogramSeries:
    return HistogramSeries("Hist Plot", (1.5, 2.5), (1.0, 2.0, 3.0), (5, 10))


@pytest.fixture
def heatmap_dataset() -> HeatmapMatrix:
    # Large heatmap coordinates simulation
    matrix = tuple(tuple(float(i * j) for j in range(20)) for i in range(20))
    x_labels = tuple(f"X{i}" for i in range(20))
    y_labels = tuple(f"Y{i}" for i in range(20))
    return HeatmapMatrix("Heat Plot", x_labels, y_labels, matrix)


@pytest.mark.unit
def test_matplotlib_backend_rendering(
    tmp_path,
    line_dataset,
    scatter_dataset,
    histogram_dataset,
    heatmap_dataset,
) -> None:
    """Verify MatplotlibBackend plots all chart types successfully in different themes."""
    backend = MatplotlibBackend()

    # 1. Line chart under LightTheme
    filepath_png = os.path.join(tmp_path, "subdir", "line.png")
    res_line = backend.line_chart(line_dataset, LightTheme(), filepath_png)
    assert isinstance(res_line, VisualizationResult)
    assert isinstance(res_line.figure, Figure)
    assert res_line.filepath == filepath_png
    assert res_line.format == "PNG"
    assert os.path.exists(filepath_png)

    # 2. Scatter chart under DarkTheme (Unicode label check)
    filepath_svg = os.path.join(tmp_path, "scatter.svg")
    res_scatter = backend.scatter_chart(scatter_dataset, DarkTheme(), filepath_svg)
    assert res_scatter.format == "SVG"
    assert os.path.exists(filepath_svg)

    # 3. Histogram under ScientificTheme
    filepath_pdf = os.path.join(tmp_path, "hist.pdf")
    res_hist = backend.histogram(histogram_dataset, ScientificTheme(), filepath_pdf)
    assert res_hist.format == "PDF"
    assert os.path.exists(filepath_pdf)

    # 4. Heatmap Matrix
    res_heat = backend.heatmap(heatmap_dataset, LightTheme())
    assert isinstance(res_heat.figure, Figure)
    assert res_heat.filepath is None


@pytest.mark.unit
def test_matplotlib_backend_types_mismatch(line_dataset) -> None:
    """Verify render method rejects mismatched types."""
    backend = MatplotlibBackend()
    theme = LightTheme()

    with pytest.raises(TypeError):
        backend.render(line_dataset, ChartType.HEATMAP, theme)
    with pytest.raises(TypeError):
        backend.render(line_dataset, ChartType.HISTOGRAM, theme)
    with pytest.raises(TypeError):
        backend.render(line_dataset, ChartType.SCATTER, theme)

    scatter_dummy = ScatterSeries("Scatter", (1.0,), (1.0,))
    with pytest.raises(TypeError):
        backend.render(scatter_dummy, ChartType.LINE, theme)


@pytest.mark.unit
def test_theme_and_typography_validations() -> None:
    """Verify DPI bounds, typography limits, and figure properties assertions."""
    # Negative DPI check
    with pytest.raises(ValidationError) as exc:
        FigureStyle(dpi=20)
    assert "QST-VAL-708" in str(exc.value)

    # Too large DPI check
    with pytest.raises(ValidationError) as exc:
        FigureStyle(dpi=1000)
    assert "QST-VAL-708" in str(exc.value)

    # Negative sizes
    with pytest.raises(ValidationError) as exc:
        Typography(font_size=-5)
    assert "QST-VAL-706" in str(exc.value)

    # Negative width
    with pytest.raises(ValidationError) as exc:
        FigureStyle(width=-8.0)
    assert "QST-VAL-707" in str(exc.value)


@pytest.mark.unit
def test_matplotlib_backend_validations(tmp_path, line_dataset) -> None:
    """Verify backend checks filepaths, overwrite protection, formats, and write access."""
    backend = MatplotlibBackend(overwrite_protection=True)
    theme = LightTheme()

    # Empty filepath
    with pytest.raises(ValidationError) as exc:
        backend.line_chart(line_dataset, theme, "")
    assert "QST-VAL-401" in str(exc.value)

    # Overwrite protection
    filepath = os.path.join(tmp_path, "exist.png")
    with open(filepath, "w") as f:
        f.write("")

    with pytest.raises(ValidationError) as exc:
        backend.line_chart(line_dataset, theme, filepath)
    assert "QST-VAL-402" in str(exc.value)

    # Unsupported format
    filepath_bad = os.path.join(tmp_path, "chart.jpg")
    with pytest.raises(ValidationError) as exc:
        backend.line_chart(line_dataset, theme, filepath_bad)
    assert "QST-VAL-709" in str(exc.value)


@pytest.mark.unit
def test_matplotlib_backend_directories_errors(line_dataset) -> None:
    """Verify parent directory validations and creation OS errors propagation."""
    backend = MatplotlibBackend()
    theme = LightTheme()

    # os.makedirs OS error check
    with mock.patch("os.makedirs", side_effect=OSError("Perm Denied")):
        with pytest.raises(ExportError) as exc:
            backend.line_chart(line_dataset, theme, "/invalid/plot.png")
        assert "QST-EXP-401" in str(exc.value)

    # parent is not a directory check
    with mock.patch("os.makedirs"):
        with mock.patch("os.path.isdir", return_value=False):
            with pytest.raises(ValidationError) as exc:
                backend.line_chart(line_dataset, theme, "/invalid/plot.png")
            assert "QST-VAL-403" in str(exc.value)


@pytest.mark.unit
def test_matplotlib_backend_savefig_error(tmp_path, line_dataset) -> None:
    """Verify backend raises ExportError if Matplotlib fig.savefig throws OSError."""
    backend = MatplotlibBackend()
    theme = LightTheme()
    filepath = os.path.join(tmp_path, "plot.png")

    with mock.patch.object(
        Figure, "savefig", side_effect=PermissionError("Mock Permission Denied")
    ):
        with pytest.raises(ExportError) as exc:
            backend.line_chart(line_dataset, theme, filepath)
        assert "QST-EXP-001" in str(exc.value)


@pytest.mark.unit
def test_matplotlib_backend_figure_cleanup(tmp_path, line_dataset) -> None:
    """Verify backend closes figures to prevent memory leak in pyplot figure manager."""
    import matplotlib.pyplot as plt

    backend = MatplotlibBackend()
    theme = LightTheme()

    # Clear any preexisting figures
    plt.close("all")
    assert len(plt.get_fignums()) == 0

    # Render multiple plots to disk
    for i in range(5):
        plot_path = os.path.join(tmp_path, f"leak_test_{i}.png")
        backend.line_chart(line_dataset, theme, plot_path)
        assert os.path.exists(plot_path)

    # Verify no open figures remain in the pyplot manager
    assert len(plt.get_fignums()) == 0

