"""Typography, Colors, GridStyle, and FigureStyle theme presets.

References:
    Docs/VISUALIZATION_SPEC.md §3
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

from dataclasses import dataclass, field

from qst.exceptions.validation import ValidationError


@dataclass(frozen=True)
class Typography:
    """Typography settings for plot fonts."""

    font_size: int = 10
    title_size: int = 14
    font_family: str = "sans-serif"

    def __post_init__(self) -> None:
        """Validate typography sizes."""
        if self.font_size <= 0 or self.title_size <= 0:
            raise ValidationError(
                "Typography sizes must be positive.",
                code="QST-VAL-706",
            )


@dataclass(frozen=True)
class Colors:
    """Color palette specifications for graphs canvas and series."""

    background_color: str
    primary_color: str
    accent_color: str
    colormap: str = "viridis"


@dataclass(frozen=True)
class GridStyle:
    """Style configuration properties for grid lines visibility."""

    grid_visible: bool = True
    grid_color: str = "#cccccc"
    grid_line_width: float = 0.5


@dataclass(frozen=True)
class FigureStyle:
    """Dimensions and pixel density settings for canvas plotting."""

    width: float = 8.0
    height: float = 6.0
    dpi: int = 100

    def __post_init__(self) -> None:
        """Validate figure dimensions bounds."""
        if self.width <= 0.0 or self.height <= 0.0:
            raise ValidationError(
                "Figure dimensions must be positive.",
                code="QST-VAL-707",
            )
        if not (50 <= self.dpi <= 600):
            raise ValidationError(
                f"DPI must be between 50 and 600, got {self.dpi}.",
                code="QST-VAL-708",
            )


@dataclass(frozen=True)
class Theme:
    """Composition object mapping theme details to render styles."""

    name: str
    typography: Typography = field(default_factory=Typography)
    colors: Colors = field(
        default_factory=lambda: Colors(
            background_color="#ffffff",
            primary_color="#1f77b4",
            accent_color="#ff7f0e",
            colormap="viridis",
        )
    )
    grid: GridStyle = field(default_factory=GridStyle)
    figure: FigureStyle = field(default_factory=FigureStyle)


class LightTheme(Theme):
    """Preset theme optimized for documents and screen viewing in bright rooms."""

    def __init__(self, dpi: int = 100) -> None:
        """Initialize the LightTheme."""
        super().__init__(
            name="light",
            typography=Typography(font_size=10, title_size=14),
            colors=Colors(
                background_color="#ffffff",
                primary_color="#0066cc",
                accent_color="#ff9900",
                colormap="viridis",
            ),
            grid=GridStyle(grid_visible=True, grid_color="#e0e0e0"),
            figure=FigureStyle(width=8.0, height=6.0, dpi=dpi),
        )


class DarkTheme(Theme):
    """Preset theme optimized for dark mode user interfaces."""

    def __init__(self, dpi: int = 100) -> None:
        """Initialize the DarkTheme."""
        super().__init__(
            name="dark",
            typography=Typography(font_size=10, title_size=14),
            colors=Colors(
                background_color="#121212",
                primary_color="#00ddff",
                accent_color="#ff0077",
                colormap="magma",
            ),
            grid=GridStyle(grid_visible=True, grid_color="#333333"),
            figure=FigureStyle(width=8.0, height=6.0, dpi=dpi),
        )


class ScientificTheme(Theme):
    """Preset theme optimized for journal articles and academic prints."""

    def __init__(self, dpi: int = 100) -> None:
        """Initialize the ScientificTheme."""
        super().__init__(
            name="scientific",
            typography=Typography(font_size=8, title_size=10, font_family="serif"),
            colors=Colors(
                background_color="#ffffff",
                primary_color="#000000",
                accent_color="#555555",
                colormap="gray",
            ),
            grid=GridStyle(
                grid_visible=False, grid_color="#000000", grid_line_width=0.3
            ),
            figure=FigureStyle(width=5.5, height=4.0, dpi=dpi),
        )
