# EXPORT_SPEC — Data Export Implementation Contract

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `SIMULATION_SPEC.md`, `../docs/10_API_SPECIFICATION.md`, `../docs/11_SECURITY_ARCHITECTURE.md`

---

## Purpose

Defines the exact CSV/JSON schema for exported simulation results (FR-9, `../docs/05_PRODUCT_REQUIREMENTS.md`), so Research Mode output is stable, documented, and safely parseable by external tools (pandas, R, Excel) without ambiguity.

## 1. JSON Schema (Single Run)

```json
{
  "n_qubits": 1000,
  "seed": 42,
  "eve_intercept_probability": 0.0,
  "qber": 0.012,
  "final_key_length": 481,
  "key_rate": 0.481,
  "warnings": [],
  "metadata": {
    "qst_version": "0.1.0",
    "qiskit_version": "TBD - captured at runtime",
    "simulation_duration_seconds": 0.42
  }
}
```

This mirrors `SimulationResult` (`../docs/10_API_SPECIFICATION.md` §5) field-for-field — the export format is a direct serialization of the public API's return object, not a separate ad hoc schema, to avoid two divergent contracts for the same data.

**Notably excluded by default:** the full `sifted_key` bit list is **not** included in the default JSON export, to keep exported files small and avoid implying the sifted key is a security artifact worth protecting (see `../docs/11_SECURITY_ARCHITECTURE.md` §6 STRIDE "Information Disclosure" row). An explicit `--include-key` CLI flag (Planned) opts into full key export for users who specifically need it for further analysis.

## 2. JSON Schema (Batch Run)

```json
{
  "run_count": 20,
  "results": [
    { "...single-run object as in §1..." }
  ]
}
```

## 3. CSV Schema (Batch Run)

| Column | Type | Notes |
|---|---|---|
| `run_index` | int | 0-based index within the batch |
| `n_qubits` | int | |
| `seed` | int | |
| `eve_intercept_probability` | float | |
| `qber` | float | |
| `final_key_length` | int | |
| `key_rate` | float | |
| `warnings` | string | Semicolon-joined if multiple; empty string if none |

CSV intentionally flattens `metadata` and omits `sifted_key` by default (same rationale as §1) — a CSV column per metadata key is **To Be Implemented** if/when metadata fields stabilize enough to warrant fixed columns; until then, CSV export is the flat, analysis-ready subset and full-fidelity export should use JSON (§2).

## 4. Serialization Requirements

- Export MUST use `json.dumps`/`csv.writer` (standard library, safe) — never `pickle` or `eval`-based serialization, per `../docs/11_SECURITY_ARCHITECTURE.md` §8 secure coding principles.
- Floats are serialized at full precision (no arbitrary rounding) so downstream statistical analysis is not silently degraded — any display-only rounding happens in the CLI/Visualizer layer, never in the exported data itself.
- Export failures (disk full, permission denied) raise `ExportError` (`../docs/10_API_SPECIFICATION.md` §6) with the target file path included in the message.

## 5. Versioning of the Export Schema

- The `metadata.qst_version` field allows a consumer (or QST itself, on re-import) to detect which schema version produced a given export file.
- Any future breaking change to the export schema (field renamed/removed) is treated the same as a public API breaking change (`../docs/10_API_SPECIFICATION.md` §9 Stability Policy) — additive fields are minor-version-safe, removals/renames require a major version bump.

## 6. Validation Criteria

1. Round-trip test: export a `SimulationResult` to JSON, re-parse it, and confirm all fields (except intentionally-excluded `sifted_key`) match the original object exactly.
2. CSV export of a batch run produces exactly `run_count` data rows plus one header row.
3. Attempting export to a non-writable path raises `ExportError` rather than an unhandled `OSError` (per `../docs/07_SYSTEM_ARCHITECTURE.md` §11 Failure Recovery).

## Implementation Status

| Item | Status |
|---|---|
| This specification | Current (design-complete) |
| JSON export | Planned |
| CSV export | Planned |
| `--include-key` flag | Planned |
| Metadata-to-CSV-column expansion | Future / To Be Implemented if needed |

## Future Improvements

- Add Parquet export for large batch runs once research users request more efficient columnar storage (see `../docs/07_SYSTEM_ARCHITECTURE.md` §8 Extension Points — "Export format plugins").
