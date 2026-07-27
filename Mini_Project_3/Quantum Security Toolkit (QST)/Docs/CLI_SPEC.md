# CLI_SPEC — Command-Line Interface Implementation Contract

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `SIMULATION_SPEC.md`, `EXPORT_SPEC.md`, `../docs/10_API_SPECIFICATION.md`, `../docs/12_UI_UX_DESIGN.md`

---

## Purpose

Defines the exact command structure, flags, exit codes, and output conventions for the `qst` CLI — the thin entrypoint over `SimulationOrchestrator` (per `../docs/07_SYSTEM_ARCHITECTURE.md` §7, CLI depends only on `orchestration/`).

## 1. Command Structure

```
qst <command> [options]
```

| Command | Purpose | Status |
|---|---|---|
| `qst simulate` | Run a single BB84 simulation | Planned |
| `qst batch` | Run a parameter-sweep batch simulation | Planned |
| `qst --version` | Print installed QST and Qiskit versions | Planned |
| `qst --help` | Auto-generated help (via `argparse`/`click`) | Planned |

## 2. `qst simulate` — Full Flag Reference

| Flag | Type | Default | Maps to |
|---|---|---|---|
| `--qubits` | int | Required | `n_qubits` (`../docs/10_API_SPECIFICATION.md` §3) |
| `--seed` | int | Random if omitted | `seed` |
| `--eve-prob` | float | `0.0` | `eve_intercept_probability` |
| `--mode` | choice: `educational`, `research` | `educational` | Determines narration vs. quiet+export behavior |
| `--output` | path | None (stdout only) | Export path (`EXPORT_SPEC.md`) |
| `--format` | choice: `json`, `csv` | `json` | Export format (`EXPORT_SPEC.md`) |
| `--include-key` | flag | Off | Include full `sifted_key` in export (`EXPORT_SPEC.md` §1) |
| `--quiet` | flag | Off | Suppress narration even in `educational` mode (useful for scripting) |

## 3. `qst batch` — Flag Reference

| Flag | Type | Default | Notes |
|---|---|---|---|
| `--qubits` | int | Required | Applied to every run in the sweep unless overridden per-run via a sweep-definition file |
| `--eve-prob-range` | string, e.g. `"0.0:1.0:0.1"` (start:stop:step) | Required for a sweep | Parsed into the `param_sweep` list passed to `run_research_batch` (`SIMULATION_SPEC.md` §4) |
| `--seed` | int | Random per run if omitted | If provided, the *same* seed is reused across the sweep — an explicit choice the user must make deliberately, since reusing one seed across an Eve-probability sweep is a reasonable default for isolating the effect of `eve-prob` alone from run-to-run randomness |
| `--output` | path | Required for batch (no useful stdout format for many rows) | `EXPORT_SPEC.md` |
| `--format` | choice: `json`, `csv` | `csv` | Batch defaults to CSV since it's naturally tabular |
| `--on-error` | choice: `continue`, `abort` | `continue` | Maps to the batch failure policy in `SIMULATION_SPEC.md` §4 |

## 4. Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | `ValidationError` — invalid CLI arguments/parameters |
| `2` | `SimulationError` — backend (Qiskit/Aer) failure during execution |
| `3` | `ExportError` — failure writing output file |
| `130` | Interrupted by user (SIGINT / Ctrl-C) — standard convention (128 + signal 2) |

Exit codes map directly to the exception hierarchy in `../docs/10_API_SPECIFICATION.md` §6, so scripting/CI usage of the CLI can distinguish failure classes without parsing error text.

## 5. Output Conventions

- **Educational mode, default (no `--quiet`):** narrated step-by-step text to stdout (per `SIMULATION_SPEC.md` §5 hooks), followed by a summary block (QBER, key rate, final key length).
- **Research mode / `--quiet`:** no narration; only a final summary line to stdout (or fully silent if `--output` is set and the user redirects stdout), with full results in the exported file.
- **Errors:** written to stderr, not stdout, so piping stdout to a file doesn't capture error text; the underlying exception's `.code` (per `../docs/10_API_SPECIFICATION.md` §6) is included in the printed message for grep-ability.
- **No color-only signaling** — consistent with `../docs/12_UI_UX_DESIGN.md` §4 accessibility requirements; any "eavesdropping likely detected"-style message is plain text, optionally colored as a *supplement*, never color-only.

## 6. Validation Criteria

1. `qst simulate --qubits -5` exits with code `1` and a stderr message matching the `ValidationError` text from the underlying API call (no CLI-specific duplicate error message text that could drift out of sync with the library's own validation message).
2. `qst batch --eve-prob-range "0.0:1.0:0.25"` produces exactly 5 sweep points (0.0, 0.25, 0.5, 0.75, 1.0) — an off-by-one in range parsing (4 vs. 5 points) would silently produce misleading sweep coverage, so this is a required unit test.
3. `qst --version` output includes both the QST package version and the installed Qiskit version, to aid bug reports (a report saying "QBER looks wrong" is far more actionable with both versions attached).

## Implementation Status

| Item | Status |
|---|---|
| This specification | Current (design-complete) |
| `qst simulate` | Planned |
| `qst batch` | Planned |
| Exit code contract | Planned |

## Future Improvements

- Add a `qst compare` command for side-by-side comparison of two prior export files, once batch/export usage patterns from real users are observed.
