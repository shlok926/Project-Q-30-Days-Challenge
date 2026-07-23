"""Base exception class for the Quantum Security Toolkit (QST).

References:
    Docs/10_API_SPECIFICATION.md §6
"""


class QSTError(Exception):
    """Base exception for all QST-specific errors.

    Attributes:
        message (str): Human-readable error message.
        code (str): Programmatic error code (e.g., 'QST-VAL-001').
    """

    def __init__(self, message: str, code: str = "QST-ERR-000") -> None:
        """Initialize the base QST error.

        Args:
            message: Human-readable explanation of the error.
            code: Programmatic error code.
        """
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """Return the string representation of the exception."""
        return f"[{self.code}] {self.message}"
