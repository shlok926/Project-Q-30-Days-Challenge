"""Unit tests for QST validation utilities.

References:
    Docs/05_PRODUCT_REQUIREMENTS.md §7
    Docs/14_TESTING_STRATEGY.md §3
"""

from pathlib import Path

import pytest

from qst.exceptions.validation import ValidationError
from qst.utils.validation import (
    validate_output_directory,
    validate_probability,
    validate_qubit_count,
    validate_seed,
)


@pytest.mark.unit
def test_validate_qubit_count_valid() -> None:
    """Verify validate_qubit_count accepts positive integers."""
    assert validate_qubit_count(100) == 100
    assert validate_qubit_count(1) == 1


@pytest.mark.unit
def test_validate_qubit_count_invalid() -> None:
    """Verify validate_qubit_count rejects negative, zero, and non-integer values."""
    with pytest.raises(ValidationError) as exc:
        validate_qubit_count(0)
    assert "QST-VAL-102" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_qubit_count(-5)
    assert "QST-VAL-102" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_qubit_count(10.5)
    assert "QST-VAL-101" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_qubit_count("100")
    assert "QST-VAL-101" in str(exc.value)

    # Boolean values subclass int but should be rejected
    with pytest.raises(ValidationError) as exc:
        validate_qubit_count(True)
    assert "QST-VAL-101" in str(exc.value)

    # Exceeding default ceiling of 2048
    with pytest.raises(ValidationError) as exc:
        validate_qubit_count(2049)
    assert "QST-VAL-103" in str(exc.value)

    # Exceeding custom configured ceiling
    with pytest.raises(ValidationError) as exc:
        validate_qubit_count(64, max_qubits=32)
    assert "QST-VAL-103" in str(exc.value)

    # Statevector memory explosion guard
    with pytest.raises(ValidationError) as exc:
        validate_qubit_count(35, simulation_method="statevector")
    assert "QST-VAL-104" in str(exc.value)



@pytest.mark.unit
def test_validate_probability_valid() -> None:
    """Verify validate_probability accepts values in range [0.0, 1.0]."""
    assert validate_probability(0.0) == 0.0
    assert validate_probability(0.5) == 0.5
    assert validate_probability(1.0) == 1.0


@pytest.mark.unit
def test_validate_probability_invalid() -> None:
    """Verify validate_probability rejects out-of-range or non-numeric values."""
    with pytest.raises(ValidationError) as exc:
        validate_probability(-0.1)
    assert "QST-VAL-202" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_probability(1.1)
    assert "QST-VAL-202" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_probability("0.5")
    assert "QST-VAL-201" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_probability(False)
    assert "QST-VAL-201" in str(exc.value)


@pytest.mark.unit
def test_validate_seed_valid() -> None:
    """Verify validate_seed accepts integers and None."""
    assert validate_seed(42) == 42
    assert validate_seed(0) == 0
    assert validate_seed(None) is None


@pytest.mark.unit
def test_validate_seed_invalid() -> None:
    """Verify validate_seed rejects non-integers."""
    with pytest.raises(ValidationError) as exc:
        validate_seed(12.34)
    assert "QST-VAL-301" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_seed("seed")
    assert "QST-VAL-301" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        validate_seed(True)
    assert "QST-VAL-301" in str(exc.value)


@pytest.mark.unit
def test_validate_output_directory_valid(tmp_path: Path) -> None:
    """Verify validate_output_directory accepts and returns valid Path objects."""
    assert validate_output_directory(tmp_path) == tmp_path
    new_dir = tmp_path / "new_dir"
    assert validate_output_directory(new_dir) == new_dir
    assert new_dir.exists()


@pytest.mark.unit
def test_validate_output_directory_invalid() -> None:
    """Verify validate_output_directory rejects non-path types."""
    with pytest.raises(ValidationError) as exc:
        validate_output_directory(123)
    assert "QST-VAL-401" in str(exc.value)
