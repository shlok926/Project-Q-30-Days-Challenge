"""Secret key custom exceptions.

References:
    Docs/10_API_SPECIFICATION.md §6
"""

from qst.exceptions.base import QSTError


class SecretKeyError(QSTError):
    """Exception raised when secret key metrics calculation or validation fails."""

    def __init__(self, message: str, code: str = "QST-SEC-001") -> None:
        """Initialize the secret key exceptions.

        Args:
            message: Details of the failure.
            code: Unique error code registry.
        """
        super().__init__(message, code)
