"""Reusable validation utilities for input parameters.

References:
    Docs/05_PRODUCT_REQUIREMENTS.md §7, §11
    Docs/10_API_SPECIFICATION.md §6
"""

from pathlib import Path
from typing import Any, Optional

from qst.exceptions.validation import ValidationError

DEFAULT_MAX_QUBITS: int = 2048


def estimate_simulation_memory_bytes(
    n_qubits: int, simulation_method: str = "automatic"
) -> int:
    """Estimate memory requirement in bytes for simulating n_qubits.

    Args:
        n_qubits: Number of qubits.
        simulation_method: Simulation approach ('statevector', 'density_matrix', 'stabilizer', 'automatic').

    Returns:
        Estimated required memory in bytes.
    """
    method = simulation_method.lower()
    if method == "statevector":
        if n_qubits >= 60:
            return 2**60
        return (2**n_qubits) * 16
    elif method == "density_matrix":
        if n_qubits >= 30:
            return 2**60
        return (4**n_qubits) * 16
    elif method in ("stabilizer", "extended_stabilizer"):
        return max(1024 * 1024, (2 * n_qubits * (2 * n_qubits + 1) // 8) + n_qubits * 1024)
    else:  # "automatic"
        return max(1024 * 1024, n_qubits * 16384)


def validate_qubit_count(
    value: Any,
    max_qubits: int = DEFAULT_MAX_QUBITS,
    simulation_method: str = "automatic",
) -> int:
    """Validate that the qubit count is a positive integer within safe resource bounds.

    Args:
        value: Input value to validate.
        max_qubits: Configurable maximum qubit ceiling (default 2048).
        simulation_method: Simulation method (default 'automatic').

    Returns:
        The validated qubit count as an integer.

    Raises:
        ValidationError: If qubit count is <= 0, not an integer, exceeds max_qubits,
                         or exceeds available system resources.
    """
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(
            f"Qubit count must be an integer, got {type(value).__name__}",
            code="QST-VAL-101",
        )
    if value <= 0:
        raise ValidationError(
            f"Qubit count must be a positive integer, got {value}",
            code="QST-VAL-102",
        )
    if value > max_qubits:
        raise ValidationError(
            f"Qubit count {value} exceeds maximum allowed ceiling of {max_qubits}.",
            code="QST-VAL-103",
        )

    # Conservative resource-aware memory check
    estimated_bytes = estimate_simulation_memory_bytes(value, simulation_method)
    if simulation_method.lower() == "statevector" and value > 28:
        raise ValidationError(
            f"Statevector simulation of {value} qubits requires ~{estimated_bytes / (1024**3):.1f} GB, exceeding safe limits.",
            code="QST-VAL-104",
        )

    try:
        import psutil

        available_ram = psutil.virtual_memory().available
        if estimated_bytes > available_ram * 0.8:
            raise ValidationError(
                f"Estimated simulation memory ({estimated_bytes / (1024**2):.1f} MB) exceeds available system RAM ({available_ram / (1024**2):.1f} MB).",
                code="QST-VAL-104",
            )
    except ImportError:
        pass

    return value



def validate_probability(value: Any, name: str = "Probability") -> float:
    """Validate that a probability value is a float between 0.0 and 1.0.

    Args:
        value: Input value to validate.
        name: Name of the variable being validated (for error reporting).

    Returns:
        The validated probability as a float.

    Raises:
        ValidationError: If probability is not a float or outside [0.0, 1.0].
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValidationError(
            f"{name} must be a numeric value, got {type(value).__name__}",
            code="QST-VAL-201",
        )
    val_float = float(value)
    if not (0.0 <= val_float <= 1.0):
        raise ValidationError(
            f"{name} must be between 0.0 and 1.0, got {value}",
            code="QST-VAL-202",
        )
    return val_float


def validate_seed(value: Any) -> Optional[int]:
    """Validate that the seed is a valid optional integer.

    Args:
        value: Input value to validate.

    Returns:
        The validated seed (int or None).

    Raises:
        ValidationError: If seed is not an integer and not None.
    """
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValidationError(
            f"Seed must be an integer or None, got {type(value).__name__}",
            code="QST-VAL-301",
        )
    return value


def validate_output_directory(value: Any) -> Path:
    """Validate that the output directory exists or can be created.

    Args:
        value: The path input to validate.

    Returns:
        The validated Path object.

    Raises:
        ValidationError: If directory cannot be created or is not writable.
    """
    if not isinstance(value, (str, Path)):
        raise ValidationError(
            f"Output directory must be a path or string, got {type(value).__name__}",
            code="QST-VAL-401",
        )
    path = Path(value)
    try:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        # Test write permissions by creating a temporary directory check
        test_file = path / ".qst_write_test"
        test_file.touch()
        test_file.unlink()
    except (OSError, PermissionError) as e:
        raise ValidationError(
            f"Output directory '{value}' is not writable or cannot be created. Reason: {e}",
            code="QST-VAL-402",
        ) from e
    return path
