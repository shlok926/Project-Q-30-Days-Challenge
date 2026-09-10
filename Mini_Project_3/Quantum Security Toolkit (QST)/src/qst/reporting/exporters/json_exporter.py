"""JSON Exporter implementation.

References:
    Docs/EXPORT_SPEC.md §1
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

from qst.exceptions.export import ExportError
from qst.exceptions.validation import ValidationError


class JSONExporter:
    """Exporter for saving normalized representations to deterministic JSON format with atomic writes."""

    def __init__(
        self,
        overwrite_protection: bool = True,
        allowed_base_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        """Initialize JSONExporter.

        Args:
            overwrite_protection: If True, blocks overwriting existing files.
            allowed_base_dir: If provided, restricts file exports to this base directory.
        """
        self.overwrite_protection = overwrite_protection
        self.allowed_base_dir = (
            Path(allowed_base_dir).resolve() if allowed_base_dir is not None else None
        )

    def export(
        self,
        filepath: Union[str, Path],
        data: dict[str, Any],
        metadata: dict[str, Any],
    ) -> None:
        """Serialize and export data to a JSON file safely and atomically.

        Args:
            filepath: Path to the target file.
            data: Normalized dictionary containing domain metrics.
            metadata: Structured dictionary of export metadata attributes.

        Raises:
            ValidationError: For invalid filenames, path traversal, existing files, or unsupported types.
            ExportError: For file-system or OS write permission errors.
        """
        if not filepath:
            raise ValidationError("Filepath must not be empty.", code="QST-VAL-401")

        if "\0" in str(filepath):
            raise ValidationError("Invalid null byte in filepath.", code="QST-VAL-401")

        if not isinstance(data, dict):
            raise ValidationError(
                f"JSONExporter only supports dictionary inputs, got {type(data)}",
                code="QST-VAL-404",
            )

        # 1. Normalize and resolve canonical path
        target_path = Path(filepath).resolve()

        # 2. Path traversal security check against allowed_base_dir
        if self.allowed_base_dir is not None:
            if not target_path.is_relative_to(self.allowed_base_dir):
                raise ValidationError(
                    f"Path traversal detected: '{filepath}' resolves outside allowed directory '{self.allowed_base_dir}'.",
                    code="QST-VAL-405",
                )

        # 3. Overwrite protection check
        if self.overwrite_protection and target_path.exists():
            raise ValidationError(
                f"File already exists at {target_path} and overwrite protection is active.",
                code="QST-VAL-402",
            )

        # 4. Directory validation & creation
        parent_dir = target_path.parent
        if parent_dir.exists() and not parent_dir.is_dir():
            raise ValidationError(
                f"Parent path {parent_dir} is not a directory.",
                code="QST-VAL-403",
            )

        try:
            os.makedirs(parent_dir, exist_ok=True)
        except OSError as e:
            raise ExportError(
                f"Failed to create directory {parent_dir}: {str(e)}",
                code="QST-EXP-401",
            )

        # Re-check parent directory after creation
        if not parent_dir.is_dir():
            raise ValidationError(
                f"Parent path {parent_dir} is not a directory.",
                code="QST-VAL-403",
            )

        # Wrap content inside metadata envelope
        payload = {
            "schema_version": metadata.get("schema_version", "1.0.0"),
            "metadata": metadata,
            "data": data,
        }

        # 5. Safe atomic write (tempfile in target directory -> fsync -> os.replace)
        temp_fd = None
        temp_path: Optional[Path] = None
        fd_closed = False
        try:
            temp_fd, temp_path_str = tempfile.mkstemp(
                dir=str(parent_dir),
                prefix=f".tmp_{target_path.stem}_",
                suffix=target_path.suffix,
            )
            temp_path = Path(temp_path_str)
            try:
                f = open(temp_fd, "w", encoding="utf-8")
            except Exception:
                os.close(temp_fd)
                fd_closed = True
                raise

            with f:
                json.dump(payload, f, indent=4, sort_keys=True)
                f.flush()
                os.fsync(f.fileno())

            os.replace(temp_path, target_path)
        except (OSError, PermissionError) as e:
            if temp_fd is not None and not fd_closed:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass
            if temp_path is not None and temp_path.exists():
                try:
                    temp_path.unlink()
                except OSError:
                    pass
            raise ExportError(
                f"Failed to write to file {filepath}: {str(e)}",
                code="QST-EXP-001",
            )

