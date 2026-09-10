"""Unit tests for CSVExporter and CSVFlattener.

References:
    Docs/EXPORT_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import os
from unittest import mock

import pytest

from qst.exceptions.export import ExportError
from qst.exceptions.validation import ValidationError
from qst.reporting.exporters.csv_exporter import CSVExporter, CSVFlattener


@pytest.fixture
def sample_serialized_simulation() -> dict:
    return {
        "qber": 0.05,
        "n_qubits": 100,
        "warnings": ["low key rate"],
        "alice_bits": (0, 1, 1),
        "reconciliation": {
            "matching_count": 8,
            "matching_bases": ("Z", "X"),
        },
        "sifted_keys": None,
    }


@pytest.fixture
def sample_serialized_experiment(sample_serialized_simulation) -> dict:
    return {
        "simulations": [sample_serialized_simulation, sample_serialized_simulation],
        "average_qber": 0.05,
        "average_key_rate": 0.45,
        "secure_runs": 2,
        "warning_runs": 0,
        "compromised_runs": 0,
        "metrics": {
            "execution_time": 0.25,
            "throughput": 800.0,
        },
        "metadata": {
            "protocol": "BB84",
            "repetitions": 2,
        },
    }


@pytest.fixture
def sample_serialized_sweep(sample_serialized_experiment) -> dict:
    return {
        "experiments": [sample_serialized_experiment],
        "total_experiments": 1,
        "sweep_dimensions": {
            "qubit_counts": (100,),
            "interception_probabilities": (0.0,),
        },
        "metadata": {
            "protocol": "BB84",
        },
    }


@pytest.mark.unit
def test_csv_flattener_simulation(sample_serialized_simulation) -> None:
    """Verify CSVFlattener flattens nested simulation dictionaries correctly."""
    flattener = CSVFlattener()
    rows = flattener.flatten(
        sample_serialized_simulation, metadata={"generator": "test"}
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["generator"] == "test"
    assert row["qber"] == 0.05
    assert row["n_qubits"] == 100
    assert row["warnings"] == "low key rate"
    assert row["alice_bits"] == "0,1,1"
    assert row["reconciliation_matching_count"] == 8
    assert row["reconciliation_matching_bases"] == "Z,X"
    assert row["sifted_keys"] == ""


@pytest.mark.unit
def test_csv_flattener_experiment(sample_serialized_experiment) -> None:
    """Verify CSVFlattener flattens experiment dictionaries into individual rows."""
    flattener = CSVFlattener()
    rows = flattener.flatten(
        sample_serialized_experiment, metadata={"generator": "test"}
    )

    # Repetitions is 2, so should yield 2 rows
    assert len(rows) == 2
    for row in rows:
        assert row["generator"] == "test"
        assert row["experiment_average_qber"] == 0.05
        assert row["experiment_metrics_throughput"] == 800.0
        assert row["experiment_metadata_protocol"] == "BB84"
        assert row["qber"] == 0.05
        assert row["reconciliation_matching_count"] == 8


@pytest.mark.unit
def test_csv_flattener_sweep(sample_serialized_sweep) -> None:
    """Verify CSVFlattener flattens parameter sweep experiments structure."""
    flattener = CSVFlattener()
    rows = flattener.flatten(sample_serialized_sweep, metadata={"generator": "test"})

    assert len(rows) == 2  # 1 experiment with 2 simulations
    for row in rows:
        assert row["generator"] == "test"
        assert row["sweep_total_experiments"] == 1
        assert row["sweep_sweep_dimensions_qubit_counts"] == "100"
        assert row["experiment_metadata_protocol"] == "BB84"
        assert row["qber"] == 0.05


@pytest.mark.unit
def test_csv_exporter_success(tmp_path, sample_serialized_simulation) -> None:
    """Verify CSVExporter writes flat rows to target CSV file successfully."""
    filepath = os.path.join(tmp_path, "export.csv")
    exporter = CSVExporter()

    exporter.export(filepath, sample_serialized_simulation, {"generator": "test"})
    assert os.path.exists(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        assert "qber" in content
        assert "generator" in content
        assert "0.05" in content


@pytest.mark.unit
def test_csv_exporter_validations(tmp_path) -> None:
    """Verify CSVExporter checks empty filepaths and bad types."""
    exporter = CSVExporter()

    with pytest.raises(ValidationError) as exc:
        exporter.export("", {}, {})
    assert "QST-VAL-401" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        exporter.export("file.csv", "not-a-dict", {})  # type: ignore
    assert "QST-VAL-404" in str(exc.value)

    # Overwrite protection check
    filepath = os.path.join(tmp_path, "exist.csv")
    with open(filepath, "w") as f:
        f.write("text")

    exporter_prot = CSVExporter(overwrite_protection=True)
    with pytest.raises(ValidationError) as exc:
        exporter_prot.export(filepath, {}, {})
    assert "QST-VAL-402" in str(exc.value)


@pytest.mark.unit
def test_csv_exporter_os_errors() -> None:
    """Verify CSVExporter raises ExportError if directory creation fails."""
    exporter = CSVExporter()
    with mock.patch("os.makedirs", side_effect=OSError("Perm Denied")):
        with pytest.raises(ExportError) as exc:
            exporter.export("/invalid-dir/file.csv", {}, {})
        assert "QST-EXP-401" in str(exc.value)


@pytest.mark.unit
def test_csv_exporter_file_write_error(tmp_path) -> None:
    """Verify CSVExporter raises ExportError if writing to file throws OSError."""
    filepath = os.path.join(tmp_path, "write_error.csv")
    exporter = CSVExporter()

    with mock.patch("builtins.open", side_effect=PermissionError("Mock Unwritable")):
        with pytest.raises(ExportError) as exc:
            exporter.export(filepath, {}, {})
        assert "QST-EXP-001" in str(exc.value)


@pytest.mark.unit
def test_csv_exporter_parent_is_not_dir(tmp_path) -> None:
    """Verify CSVExporter raises ValidationError if parent path exists but is not a directory."""
    parent_file = os.path.join(tmp_path, "not_a_dir")
    with open(parent_file, "w") as f:
        f.write("text")

    filepath = os.path.join(parent_file, "file.csv")
    exporter = CSVExporter()
    with mock.patch("os.makedirs"):
        with pytest.raises(ValidationError) as exc:
            exporter.export(filepath, {}, {})
        assert "QST-VAL-403" in str(exc.value)


@pytest.mark.unit
def test_csv_exporter_path_traversal_blocked(tmp_path) -> None:
    """Verify CSVExporter blocks writing outside allowed_base_dir."""
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()
    exporter = CSVExporter(allowed_base_dir=allowed_dir)

    outside_file = tmp_path / "outside.csv"
    with pytest.raises(ValidationError) as exc:
        exporter.export(outside_file, {"test": 1}, {})
    assert "QST-VAL-405" in str(exc.value)
    assert "Path traversal detected" in str(exc.value)


@pytest.mark.unit
def test_csv_exporter_null_byte_rejected() -> None:
    """Verify CSVExporter blocks filepaths containing null bytes."""
    exporter = CSVExporter()
    with pytest.raises(ValidationError) as exc:
        exporter.export("output\0.csv", {}, {})
    assert "QST-VAL-401" in str(exc.value)

