"""Configuration management layer for the Quantum Security Toolkit (QST).

Supports loading environment variables and provides package-wide constants.

References:
    Docs/31_CONFIGURATION_REFERENCE.md
    Docs/10_API_SPECIFICATION.md §6
"""

import os

from qst.exceptions.configuration import ConfigurationError

# Package-wide constants
QST_VERSION = "0.1.0"
DEFAULT_EVE_INTERCEPT_PROBABILITY = 0.0


class Configuration:
    """Consolidated configuration manager for library runtime parameters.

    Reads configuration from environment variables and provides defaults.
    """

    def __init__(self) -> None:
        """Initialize and validate configuration from the environment."""
        self._log_level: str = self._load_log_level()

    def _load_log_level(self) -> str:
        """Load and validate the log level from environment variables.

        Returns:
            The validated logging level string.

        Raises:
            ConfigurationError: If the log level is not a recognized string.
        """
        level = os.getenv("QST_LOG_LEVEL", "INFO").upper()
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level not in valid_levels:
            raise ConfigurationError(
                f"Invalid QST_LOG_LEVEL environment variable value: '{level}'. "
                f"Must be one of {valid_levels}",
                code="QST-CFG-101",
            )
        return level

    @property
    def log_level(self) -> str:
        """Return the running logging level configuration."""
        return self._log_level

    @property
    def version(self) -> str:
        """Return the current package version."""
        return QST_VERSION
