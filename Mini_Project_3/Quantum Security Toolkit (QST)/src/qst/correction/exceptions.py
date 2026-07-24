"""Cascade Error Correction custom exceptions.

References:
    Docs/10_API_SPECIFICATION.md §6
"""

from qst.exceptions.base import QSTError


class CorrectionError(QSTError):
    """Exception raised when Cascade Error Correction fails or configuration is invalid."""

    def __init__(self, message: str, code: str = "QST-CORR-001") -> None:
        """Initialize the error correction exception.

        Args:
            message: Details of the failure.
            code: Unique error code registry.
        """
        super().__init__(message, code)
