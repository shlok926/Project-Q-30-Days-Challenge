"""CSV Exporter and CSVFlattener implementations.

References:
    Docs/EXPORT_SPEC.md §2
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

import csv
import os
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

from qst.exceptions.export import ExportError
from qst.exceptions.validation import ValidationError


class CSVFlattener:
    """Flattens nested dictionary representations into relational table records."""

    def flatten(
        self,
        data: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        """Convert nested dictionary tree into a list of flat row dictionaries.

        Args:
            data: Serialized data tree.
            metadata: Global metadata fields to inject.

        Returns:
            A list of flat dictionaries (one for each row).
        """
        # Check if data is ParameterSweepResult
        if "experiments" in data:
            return self._flatten_parameter_sweep(data, metadata)
        # Check if data is ExperimentResult
        elif "simulations" in data:
            return self._flatten_experiment(data, metadata)
        # Single SimulationResult
        else:
            return self._flatten_simulation(data, metadata)

    # 1-indexed indentation fixes
    def _flatten_simulation(
        self,
        sim_data: dict[str, Any],
        metadata: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        flat_sim = self._flatten_dict(sim_data)
        if metadata:
            flat_sim = {**metadata, **flat_sim}
        return [flat_sim]

    def _flatten_experiment(
        self,
        exp_data: dict[str, Any],
        metadata: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        sims = exp_data.get("simulations", [])
        global_keys = {k: v for k, v in exp_data.items() if k != "simulations"}
        flat_global = self._flatten_dict(global_keys, prefix="experiment")

        rows = []
        for sim in sims:
            flat_sim = self._flatten_dict(sim)
            merged = {**flat_global, **flat_sim}
            if metadata:
                merged = {**metadata, **merged}
            rows.append(merged)
        return rows

    def _flatten_parameter_sweep(
        self,
        sweep_data: dict[str, Any],
        metadata: Optional[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        exps = sweep_data.get("experiments", [])
        global_keys = {k: v for k, v in sweep_data.items() if k != "experiments"}
        flat_global = self._flatten_dict(global_keys, prefix="sweep")

        rows = []
        for exp in exps:
            exp_rows = self._flatten_experiment(exp, metadata=None)
            for exp_row in exp_rows:
                merged = {**flat_global, **exp_row}
                if metadata:
                    merged = {**metadata, **merged}
                rows.append(merged)
        return rows

    def _flatten_dict(
        self,
        d: dict[str, Any],
        prefix: str = "",
    ) -> dict[str, Any]:
        items: dict[str, Any] = {}
        for k, v in d.items():
            new_key = f"{prefix}_{k}" if prefix else k
            if isinstance(v, dict):
                items.update(self._flatten_dict(v, new_key))
            elif isinstance(v, (list, tuple)):
                items[new_key] = ",".join(map(str, v)) if v else ""
            elif v is None:
                items[new_key] = ""
            else:
                items[new_key] = v
        return items


class CSVExporter:
    """Exporter for saving normalized representations to tabular CSV format with atomic writes."""

    def __init__(
        self,
        overwrite_protection: bool = True,
        allowed_base_dir: Optional[Union[str, Path]] = None,
    ) -> None:
        """Initialize CSVExporter.

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
        """Flatten and export data to a CSV file safely and atomically.

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
                f"CSVExporter only supports dictionary inputs, got {type(data)}",
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

        # Flatten records
        flattener = CSVFlattener()
        rows = flattener.flatten(data, metadata)

        headers = []
        for row in rows:
            for key in row.keys():
                if key not in headers:
                    headers.append(key)

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
                f = open(temp_fd, "w", newline="", encoding="utf-8")
            except Exception:
                os.close(temp_fd)
                fd_closed = True
                raise

            with f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)
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

