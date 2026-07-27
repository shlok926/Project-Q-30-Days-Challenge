"""Privacy Amplification custom exceptions.

References:
    Docs/10_API_SPECIFICATION.md §6
"""

from qst.exceptions.base import QSTError


class PrivacyAmplificationError(QSTError):
    """Exception raised when Privacy Amplification fails or configuration is invalid."""

    def __init__(self, message: str, code: str = "QST-PRIV-001") -> None:
        """Initialize the privacy amplification exception.

        Args:
            message: Details of the failure.
            code: Unique error code registry.
        """
        super().__init__(message, code)
