"""Unit tests for JSONExporter.

References:
    Docs/EXPORT_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import os
from unittest import mock

import pytest

from qst.exceptions.export import ExportError
from qst.exceptions.validation import ValidationError
from qst.reporting.exporters.json_exporter import JSONExporter


@pytest.mark.unit
def test_json_exporter_success(tmp_path) -> None:
    """Verify JSONExporter successfully exports serialized dict representation to filepath."""
    filepath = os.path.join(tmp_path, "subdir", "results.json")
    exporter = JSONExporter(overwrite_protection=True)

    data = {"key_rate": 0.5, "warnings": []}
    metadata = {"schema_version": "1.0.0", "generator": "test"}

    # Parent directory "subdir" should be auto-created
    exporter.export(filepath, data, metadata)

    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        import json

        loaded = json.load(f)
        assert loaded["schema_version"] == "1.0.0"
        assert loaded["data"]["key_rate"] == 0.5


@pytest.mark.unit
def test_json_exporter_empty_filepath() -> None:
    """Verify JSONExporter rejects empty filepaths."""
    exporter = JSONExporter()
    with pytest.raises(ValidationError) as exc:
        exporter.export("", {}, {})
    assert "QST-VAL-401" in str(exc.value)


@pytest.mark.unit
def test_json_exporter_non_dict_data() -> None:
    """Verify JSONExporter rejects non-dictionary data structures."""
    exporter = JSONExporter()
    with pytest.raises(ValidationError) as exc:
        exporter.export("file.json", "not-a-dict", {})  # type: ignore
    assert "QST-VAL-404" in str(exc.value)


@pytest.mark.unit
def test_json_exporter_overwrite_protection(tmp_path) -> None:
    """Verify JSONExporter blocks overwriting existing files when protection is enabled."""
    filepath = os.path.join(tmp_path, "exists.json")
    with open(filepath, "w") as f:
        f.write("{}")

    exporter = JSONExporter(overwrite_protection=True)
    with pytest.raises(ValidationError) as exc:
        exporter.export(filepath, {}, {})
    assert "QST-VAL-402" in str(exc.value)

    # Disable overwrite protection, should write successfully
    exporter_force = JSONExporter(overwrite_protection=False)
    exporter_force.export(filepath, {"val": 1}, {})
    assert os.path.exists(filepath)


@pytest.mark.unit
def test_json_exporter_directory_creation_failure() -> None:
    """Verify JSONExporter raises ExportError if directory creation fails."""
    exporter = JSONExporter()
    with mock.patch("os.makedirs", side_effect=OSError("Permission Denied")):
        with pytest.raises(ExportError) as exc:
            exporter.export("/invalid-dir/file.json", {}, {})
        assert "QST-EXP-401" in str(exc.value)


@pytest.mark.unit
def test_json_exporter_parent_is_not_dir(tmp_path) -> None:
    """Verify JSONExporter raises ValidationError if parent path exists but is not a directory."""
    parent_file = os.path.join(tmp_path, "not_a_dir")
    with open(parent_file, "w") as f:
        f.write("text")

    filepath = os.path.join(parent_file, "file.json")
    exporter = JSONExporter()
    # We patch os.makedirs to prevent OS error throwing
    with mock.patch("os.makedirs"):
        with pytest.raises(ValidationError) as exc:
            exporter.export(filepath, {}, {})
        assert "QST-VAL-403" in str(exc.value)


@pytest.mark.unit
def test_json_exporter_write_file_error(tmp_path) -> None:
    """Verify JSONExporter raises ExportError if file writing fails."""
    filepath = os.path.join(tmp_path, "unwritable.json")
    exporter = JSONExporter()

    # Mock open to raise PermissionError
    with mock.patch(
        "builtins.open", side_effect=PermissionError("Mock Permission Denied")
    ):
        with pytest.raises(ExportError) as exc:
            exporter.export(filepath, {}, {})
        assert "QST-EXP-001" in str(exc.value)


@pytest.mark.unit
def test_json_exporter_path_traversal_blocked(tmp_path) -> None:
    """Verify JSONExporter blocks writing outside allowed_base_dir."""
    allowed_dir = tmp_path / "allowed"
    allowed_dir.mkdir()
    exporter = JSONExporter(allowed_base_dir=allowed_dir)

    outside_file = tmp_path / "outside.json"
    with pytest.raises(ValidationError) as exc:
        exporter.export(outside_file, {"test": 1}, {})
    assert "QST-VAL-405" in str(exc.value)
    assert "Path traversal detected" in str(exc.value)


@pytest.mark.unit
def test_json_exporter_null_byte_rejected() -> None:
    """Verify JSONExporter blocks filepaths containing null bytes."""
    exporter = JSONExporter()
    with pytest.raises(ValidationError) as exc:
        exporter.export("output\0.json", {}, {})
    assert "QST-VAL-401" in str(exc.value)

