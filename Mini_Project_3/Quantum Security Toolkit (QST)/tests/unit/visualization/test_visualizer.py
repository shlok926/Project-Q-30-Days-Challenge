"""Unit tests for the Visualizer dispatcher and VisualizationBackendRegistry.

References:
    Docs/VISUALIZATION_SPEC.md §1, §3
    Docs/14_TESTING_STRATEGY.md §3
"""

from typing import Any, Optional

import pytest

from qst.models.results import SimulationResult
from qst.visualization.backend import (
    ChartType,
    VisualizationBackend,
    VisualizationResult,
)
from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)
from qst.visualization.registry import VisualizationBackendRegistry
from qst.visualization.styles import Theme
from qst.visualization.visualizer import Visualizer


class FakeBackend(VisualizationBackend):
    """Fake visualization backend mapping datasets to stub figures."""

    def render(
        self,
        dataset: Any,
        chart_type: ChartType,
        theme: Theme,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Render fake visualization dataset."""
        super().render(dataset, chart_type, theme, filepath)
        return VisualizationResult(
            figure="stub-fig",
            filepath=filepath,
            width=theme.figure.width,
            height=theme.figure.height,
            dpi=theme.figure.dpi,
            format="PNG" if filepath else None,
        )


@pytest.mark.unit
def test_visualizer_dispatch() -> None:
    """Verify Visualizer dispatches render requests to backend correctly."""
    backend = FakeBackend()
    visualizer = Visualizer(backend)

    # Line chart dispatch
    line = LineSeries("Line", (1.0,), (1.0,))
    res_line = visualizer.line_chart(line)
    assert res_line.figure == "stub-fig"
    assert res_line.width == 8.0

    # Scatter chart dispatch
    scatter = ScatterSeries("Scatter", (1.0,), (1.0,))
    res_scatter = visualizer.scatter_chart(scatter, "plot.png")
    assert res_scatter.filepath == "plot.png"

    # Histogram dispatch
    hist = HistogramSeries("Hist", (1.0,), (0.0, 2.0), (1,))
    res_hist = visualizer.histogram(hist)
    assert res_hist.figure == "stub-fig"

    # Heatmap dispatch
    heat = HeatmapMatrix("Heat", ("X",), ("Y",), ((1.0,),))
    res_heat = visualizer.heatmap(heat)
    assert res_heat.figure == "stub-fig"


@pytest.mark.unit
def test_visualizer_render_basis_table() -> None:
    """Verify text basis table matches format string outcomes."""
    # Complete bases matching
    res = SimulationResult(
        qber=0.0,
        final_key_length=2,
        key_rate=0.5,
        sifted_key=[],
        n_qubits=2,
        seed=1,
        eve_intercept_probability=0.0,
        alice_bases=("Z", "X"),
        bob_bases=("Z", "Z"),
    )

    table = Visualizer.render_basis_table(res)
    assert "Alice Bases: Z X" in table
    assert "Bob Bases:   Z Z" in table
    assert "Matches:     ✔ ✘" in table

    # Empty bases check
    res_empty = SimulationResult(None, 0, 0.0, [], 10, None, 0.0)
    assert Visualizer.render_basis_table(res_empty) == "No bases to compare."


@pytest.mark.unit
def test_backend_registry_flows() -> None:
    """Verify custom backend registration and get instantiations."""
    VisualizationBackendRegistry.register("fake", FakeBackend)

    # Get backend instance
    backend = VisualizationBackendRegistry.get("fake")
    assert isinstance(backend, FakeBackend)

    # Unregistered check
    with pytest.raises(KeyError):
        VisualizationBackendRegistry.get("unregistered-backend")
