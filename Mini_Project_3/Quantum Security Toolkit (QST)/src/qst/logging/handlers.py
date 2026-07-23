"""Custom handlers for QST logging.

Provides standard StreamHandler and optional FileHandler.

References:
    Docs/30_OBSERVABILITY.md
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def get_console_handler(structured: bool = False) -> logging.Handler:
    """Create and configure a standard output stream handler.

    Args:
        structured: If True, uses StructuredJSONFormatter. Otherwise standard.

    Returns:
        The configured console logging Handler.
    """
    handler = logging.StreamHandler(sys.stdout)
    if structured:
        from qst.logging.formatters import StructuredJSONFormatter

        handler.setFormatter(StructuredJSONFormatter())
    else:
        from qst.logging.formatters import StandardFormatter

        handler.setFormatter(StandardFormatter())
    return handler


def get_file_handler(
    file_path: Path, structured: bool = True
) -> Optional[logging.Handler]:
    """Create and configure a file handler for logging to a file.

    Args:
        file_path: Path to the log file.
        structured: If True, uses StructuredJSONFormatter. Otherwise standard.

    Returns:
        The configured file logging Handler, or None if path cannot be created.
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(file_path, encoding="utf-8")
        if structured:
            from qst.logging.formatters import StructuredJSONFormatter

            handler.setFormatter(StructuredJSONFormatter())
        else:
            from qst.logging.formatters import StandardFormatter

            handler.setFormatter(StandardFormatter())
        return handler
    except OSError:
        # Fallback if file directory is non-writable
        return None
