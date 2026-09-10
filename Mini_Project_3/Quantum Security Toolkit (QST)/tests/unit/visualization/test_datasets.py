"""Unit tests for visualization presentation datasets.

References:
    Docs/VISUALIZATION_SPEC.md §2
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.exceptions.validation import ValidationError
from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    LineSeries,
    ScatterSeries,
)


@pytest.mark.unit
def test_line_series_validations() -> None:
    """Verify LineSeries dimension matching and non-empty validation rules."""
    # Valid single-point chart (supported boundary check)
    ls_single = LineSeries("Single Point", (1.0,), (1.0,))
    assert ls_single.x_values == (1.0,)

    # Mismatched sizes
    with pytest.raises(ValidationError) as exc:
        LineSeries("Mismatch", (1.0, 2.0), (1.0,))
    assert "QST-VAL-701" in str(exc.value)

    # Empty check
    with pytest.raises(ValidationError) as exc:
        LineSeries("Empty", (), ())
    assert "QST-VAL-705" in str(exc.value)


@pytest.mark.unit
def test_scatter_series_validations() -> None:
    """Verify ScatterSeries dimension matching and non-empty validation rules."""
    # Valid
    ss = ScatterSeries("Scatter", (1.0, 2.0), (3.0, 4.0))
    assert ss.label == "Scatter"

    # Mismatched sizes
    with pytest.raises(ValidationError) as exc:
        ScatterSeries("Mismatch", (1.0,), (1.0, 2.0))
    assert "QST-VAL-701" in str(exc.value)

    # Empty check
    with pytest.raises(ValidationError) as exc:
        ScatterSeries("Empty", (), ())
    assert "QST-VAL-705" in str(exc.value)


@pytest.mark.unit
def test_histogram_series_validations() -> None:
    """Verify HistogramSeries bin-edges and non-empty validation rules."""
    # Valid
    hs = HistogramSeries("Histogram", (1.0, 2.0), (0.0, 1.0, 2.0), (10, 20))
    assert hs.values == (1.0, 2.0)

    # Mismatched bin counts vs edges: bin_edges size must equal bin_counts size + 1
    with pytest.raises(ValidationError) as exc:
        HistogramSeries("Mismatch", (1.0,), (0.0, 1.0), (5, 10))
    assert "QST-VAL-702" in str(exc.value)

    # Empty check
    with pytest.raises(ValidationError) as exc:
        HistogramSeries("Empty", (), (), ())
    assert "QST-VAL-705" in str(exc.value)


@pytest.mark.unit
def test_heatmap_matrix_validations() -> None:
    """Verify HeatmapMatrix dimensions, row lengths, and non-empty checks."""
    # Valid
    hm = HeatmapMatrix(
        "Heatmap",
        ("X1", "X2"),
        ("Y1",),
        ((1.0, 2.0),),
    )
    assert hm.x_labels == ("X1", "X2")

    # Mismatched row count vs y_labels
    with pytest.raises(ValidationError) as exc:
        HeatmapMatrix("Mismatch Rows", ("X1",), ("Y1", "Y2"), ((1.0,),))
    assert "QST-VAL-703" in str(exc.value)

    # Mismatched column length within row vs x_labels
    with pytest.raises(ValidationError) as exc:
        HeatmapMatrix("Mismatch Cols", ("X1", "X2"), ("Y1",), ((1.0,),))
    assert "QST-VAL-704" in str(exc.value)

    # Empty check
    with pytest.raises(ValidationError) as exc:
        HeatmapMatrix("Empty", (), (), ())
    assert "QST-VAL-705" in str(exc.value)
