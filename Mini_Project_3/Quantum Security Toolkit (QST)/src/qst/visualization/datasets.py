"""Visualization presentation models and image format definitions.

References:
    Docs/VISUALIZATION_SPEC.md §2
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

from dataclasses import dataclass
from enum import Enum

from qst.exceptions.validation import ValidationError


class ImageFormat(Enum):
    """Enumeration of supported exported chart image formats."""

    PNG = "PNG"
    SVG = "SVG"
    PDF = "PDF"


@dataclass(frozen=True)
class LineSeries:
    """Immutable dataset model representing a line graph series."""

    label: str
    x_values: tuple[float, ...]
    y_values: tuple[float, ...]

    def __post_init__(self) -> None:
        """Validate alignment of coordinates."""
        if not self.x_values or not self.y_values:
            raise ValidationError(
                "Dataset must not be empty.",
                code="QST-VAL-705",
            )
        if len(self.x_values) != len(self.y_values):
            raise ValidationError(
                f"LineSeries x_values size ({len(self.x_values)}) must match y_values size ({len(self.y_values)}).",
                code="QST-VAL-701",
            )


@dataclass(frozen=True)
class ScatterSeries:
    """Immutable dataset model representing a scatter plot series."""

    label: str
    x_values: tuple[float, ...]
    y_values: tuple[float, ...]

    def __post_init__(self) -> None:
        """Validate alignment of coordinates."""
        if not self.x_values or not self.y_values:
            raise ValidationError(
                "Dataset must not be empty.",
                code="QST-VAL-705",
            )
        if len(self.x_values) != len(self.y_values):
            raise ValidationError(
                f"ScatterSeries x_values size ({len(self.x_values)}) must match y_values size ({len(self.y_values)}).",
                code="QST-VAL-701",
            )


@dataclass(frozen=True)
class HistogramSeries:
    """Immutable dataset model representing histogram bin distributions."""

    label: str
    values: tuple[float, ...]
    bin_edges: tuple[float, ...]
    bin_counts: tuple[int, ...]

    def __post_init__(self) -> None:
        """Validate histogram bins alignment."""
        if not self.values or not self.bin_edges or not self.bin_counts:
            raise ValidationError(
                "Dataset must not be empty.",
                code="QST-VAL-705",
            )
        if len(self.bin_edges) != len(self.bin_counts) + 1:
            raise ValidationError(
                f"HistogramSeries bin_edges size ({len(self.bin_edges)}) must equal bin_counts size ({len(self.bin_counts)}) + 1.",
                code="QST-VAL-702",
            )


@dataclass(frozen=True)
class HeatmapMatrix:
    """Immutable dataset model representing a two-dimensional heatmap matrix."""

    label: str
    x_labels: tuple[str, ...]
    y_labels: tuple[str, ...]
    matrix: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        """Validate matrix axes mapping dimensions."""
        if not self.x_labels or not self.y_labels or not self.matrix:
            raise ValidationError(
                "Dataset must not be empty.",
                code="QST-VAL-705",
            )
        if len(self.matrix) != len(self.y_labels):
            raise ValidationError(
                f"HeatmapMatrix rows ({len(self.matrix)}) must match y_labels ({len(self.y_labels)}).",
                code="QST-VAL-703",
            )
        for idx, row in enumerate(self.matrix):
            if len(row) != len(self.x_labels):
                raise ValidationError(
                    f"HeatmapMatrix row {idx} size ({len(row)}) must match x_labels ({len(self.x_labels)}).",
                    code="QST-VAL-704",
                )
