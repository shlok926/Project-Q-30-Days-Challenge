"""Concrete Matplotlib plotting backend.

References:
    Docs/VISUALIZATION_SPEC.md §3, §4
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

import os
from typing import Any, Optional

try:
    from matplotlib.figure import Figure

    HAS_MATPLOTLIB = True
except ImportError:
    Figure = Any  # type: ignore
    HAS_MATPLOTLIB = False

import numpy as np

from qst.exceptions.export import ExportError
from qst.exceptions.validation import ValidationError
from qst.exceptions.visualization import VisualizationError
from qst.visualization.backend import (
    ChartType,
    VisualizationBackend,
    VisualizationResult,
)
from qst.visualization.datasets import (
    ImageFormat,
    LineSeries,
    ScatterSeries,
    HistogramSeries,
    HeatmapMatrix,
)
from qst.visualization.styles import Theme


class MatplotlibBackend(VisualizationBackend):
    """Concrete visualization backend utilizing Matplotlib."""

    def __init__(self, overwrite_protection: bool = True) -> None:
        """Initialize MatplotlibBackend.

        Args:
            overwrite_protection: If True, blocks overwriting existing files.
        """
        self.overwrite_protection = overwrite_protection

    def render(
        self,
        dataset: Any,
        chart_type: ChartType,
        theme: Theme,
        filepath: Optional[str] = None,
    ) -> VisualizationResult:
        """Render a dataset onto a Matplotlib Figure and optionally save to disk.

        Args:
            dataset: The LineSeries, ScatterSeries, HistogramSeries, or HeatmapMatrix object.
            chart_type: The enum ChartType category of the chart.
            theme: The styling Theme to apply.
            filepath: Optional destination path to write the output image.

        Returns:
            A VisualizationResult payload wrapper.
        """
        if not HAS_MATPLOTLIB:
            raise VisualizationError(
                "Matplotlib is not installed. Install with optional dependencies 'pip install \"qst[viz]\"' to enable plotting.",
                code="QST-VIS-701",
            )

        # Validate format beforehand if filepath is supplied
        fmt = None
        if filepath is not None:
            if not filepath.strip():
                raise ValidationError("Filepath must not be empty.", code="QST-VAL-401")
            suffix = os.path.splitext(filepath)[1].upper().replace(".", "")
            if suffix not in [f.value for f in ImageFormat]:
                raise ValidationError(
                    f"Unsupported image format: {suffix}",
                    code="QST-VAL-709",
                )
            fmt = suffix

            # Validate directory structure
            parent_dir = os.path.dirname(filepath)
            if parent_dir:
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                except OSError as e:
                    raise ExportError(
                        f"Failed to create directory {parent_dir}: {str(e)}",
                        code="QST-EXP-401",
                    )
                if not os.path.isdir(parent_dir):
                    raise ValidationError(
                        f"Parent path {parent_dir} is not a directory.",
                        code="QST-VAL-403",
                    )

            # Overwrite protection check
            if self.overwrite_protection and os.path.exists(filepath):
                raise ValidationError(
                    f"File already exists at {filepath} and overwrite protection is active.",
                    code="QST-VAL-402",
                )

        # Create Matplotlib Figure
        fig = Figure(
            figsize=(theme.figure.width, theme.figure.height),
            dpi=theme.figure.dpi,
        )
        fig.patch.set_facecolor(theme.colors.background_color)

        ax = fig.subplots()
        ax.set_facecolor(theme.colors.background_color)

        # Theme color for labels and titles
        text_color = "white" if theme.name == "dark" else "black"

        # Apply grid style
        ax.grid(
            visible=theme.grid.grid_visible,
            color=theme.grid.grid_color,
            linewidth=theme.grid.grid_line_width,
        )

        # Dispatch chart generation
        if chart_type == ChartType.LINE:
            if not isinstance(dataset, LineSeries):
                raise TypeError("LINE chart requires a LineSeries dataset.")
            ax.plot(
                dataset.x_values,
                dataset.y_values,
                label=dataset.label,
                color=theme.colors.primary_color,
            )
            ax.set_title(
                dataset.label,
                fontsize=theme.typography.title_size,
                color=text_color,
                family=theme.typography.font_family,
            )

        elif chart_type == ChartType.SCATTER:
            if not isinstance(dataset, ScatterSeries):
                raise TypeError("SCATTER chart requires a ScatterSeries dataset.")
            ax.scatter(
                dataset.x_values,
                dataset.y_values,
                label=dataset.label,
                color=theme.colors.accent_color,
            )
            ax.set_title(
                dataset.label,
                fontsize=theme.typography.title_size,
                color=text_color,
                family=theme.typography.font_family,
            )

        elif chart_type == ChartType.HISTOGRAM:
            if not isinstance(dataset, HistogramSeries):
                raise TypeError("HISTOGRAM chart requires a HistogramSeries dataset.")
            widths = np.diff(dataset.bin_edges)
            ax.bar(
                dataset.bin_edges[:-1],
                dataset.bin_counts,
                width=widths,
                align="edge",
                color=theme.colors.primary_color,
                edgecolor=theme.colors.background_color,
            )
            ax.set_title(
                dataset.label,
                fontsize=theme.typography.title_size,
                color=text_color,
                family=theme.typography.font_family,
            )

        elif chart_type == ChartType.HEATMAP:
            if not isinstance(dataset, HeatmapMatrix):
                raise TypeError("HEATMAP chart requires a HeatmapMatrix dataset.")
            matrix_data = np.array(dataset.matrix)
            im = ax.imshow(matrix_data, cmap=theme.colors.colormap)
            fig.colorbar(im, ax=ax)

            # Configure tick labels mapping
            ax.set_xticks(range(len(dataset.x_labels)))
            ax.set_xticklabels(
                dataset.x_labels, rotation=45, ha="right", color=text_color
            )
            ax.set_yticks(range(len(dataset.y_labels)))
            ax.set_yticklabels(dataset.y_labels, color=text_color)
            ax.set_title(
                dataset.label,
                fontsize=theme.typography.title_size,
                color=text_color,
                family=theme.typography.font_family,
            )

        # Apply tick sizes and label colors
        ax.tick_params(colors=text_color, labelsize=theme.typography.font_size)

        # Save to file if path is provided
        if filepath is not None:
            try:
                fig.savefig(
                    filepath,
                    dpi=theme.figure.dpi,
                    bbox_inches="tight",
                    facecolor=fig.get_facecolor(),
                    edgecolor="none",
                )
            except (OSError, PermissionError) as e:
                raise ExportError(
                    f"Failed to save plot to file {filepath}: {str(e)}",
                    code="QST-EXP-001",
                )

        return VisualizationResult(
            figure=fig,
            filepath=filepath,
            width=theme.figure.width,
            height=theme.figure.height,
            dpi=theme.figure.dpi,
            format=fmt,
        )
