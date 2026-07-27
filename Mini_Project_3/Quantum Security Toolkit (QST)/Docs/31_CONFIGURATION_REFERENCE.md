# 31 — Configuration Reference

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `../specs/CLI_SPEC.md`, `10_API_SPECIFICATION.md`, `05_PRODUCT_REQUIREMENTS.md`

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Library API Parameters](#2-library-api-parameters)
3. [CLI Configuration](#3-cli-configuration)
4. [Environment Variables](#4-environment-variables)
5. [Validation Rules Summary](#5-validation-rules-summary)
6. [Future Configuration](#6-future-configuration)
7. [Assumptions](#7-assumptions)
8. [Scope](#8-scope)
9. [References](#9-references)

---

## 1. Purpose

A single consolidated reference for every configurable parameter across the library API and CLI, so a user or contributor doesn't need to cross-reference three documents to find every default value and valid range in one place. This document does not redefine validation logic — it indexes the authoritative definitions already in `10_API_SPECIFICATION.md` and `../specs/CLI_SPEC.md`.

## 2. Library API Parameters

> Canonically defined in `10_API_SPECIFICATION.md` §3, §5; reproduced here as a consolidated index only.

| Parameter | Type | Default | Allowed Range | Defined In |
|---|---|---|---|---|
| `n_qubits` | int | Required (no default) | Positive integer; practical ceiling pending benchmarking (`05_PRODUCT_REQUIREMENTS.md` EC-6) | `10_API_SPECIFICATION.md` §3 |
| `seed` | int | Random if omitted | Any integer; exact negative/non-integer handling **To Be Implemented** (`05_PRODUCT_REQUIREMENTS.md` EC-7) | `10_API_SPECIFICATION.md` §3 |
| `eve_intercept_probability` | float | `0.0` | `[0.0, 1.0]` inclusive | `10_API_SPECIFICATION.md` §3 |
| `protocol_name` | str | `"bb84"` | Any key in `PROTOCOL_REGISTRY` (`../specs/SIMULATION_SPEC.md` §2) — only `"bb84"` exists for v1.0 | `../specs/SIMULATION_SPEC.md` §2 |

## 3. CLI Configuration

> Canonically defined in `../specs/CLI_SPEC.md` §2–§3; reproduced here as a consolidated index only.

| Flag | Command(s) | Type | Default |
|---|---|---|---|
| `--qubits` | `simulate`, `batch` | int | Required |
| `--seed` | `simulate`, `batch` | int | Random per run (single run reused across sweep for `batch`) |
| `--eve-prob` | `simulate` | float | `0.0` |
| `--eve-prob-range` | `batch` | string (`start:stop:step`) | Required for a sweep |
| `--mode` | `simulate` | choice: `educational`, `research` | `educational` |
| `--output` | `simulate`, `batch` | path | None (stdout) for `simulate`; required for `batch` |
| `--format` | `simulate`, `batch` | choice: `json`, `csv` | `json` (`simulate`), `csv` (`batch`) |
| `--include-key` | `simulate`, `batch` | flag | Off |
| `--quiet` | `simulate` | flag | Off |
| `--on-error` | `batch` | choice: `continue`, `abort` | `continue` |
| `--verbose` / `-v` | all | flag | Off (see `30_OBSERVABILITY.md` §2) |
| `--diagnose` | all | flag | Off (see `30_OBSERVABILITY.md` §8) |
| `--trace` | all | flag | Off — **Future** (see `30_OBSERVABILITY.md` §4) |

## 4. Environment Variables

**None required for core functionality**, consistent with `13_DEPLOYMENT.md` §5 and the zero-network-dependency design (`11_SECURITY_ARCHITECTURE.md` §6).

| Variable | Purpose | Status |
|---|---|---|
| `QST_LOG_LEVEL` | Override default logging verbosity without a CLI flag (useful for library/notebook use where CLI flags don't apply) | Planned |
| `QST_AI_TUTOR_API_KEY` | Would supply API credentials for the optional Future AI Tutor feature | Future — not applicable until `08_AI_ARCHITECTURE.md`'s AI Tutor is built; no such feature exists today |

## 5. Validation Rules Summary

All parameters are validated at the API boundary before any simulation work begins (`../specs/SIMULATION_SPEC.md` §1, `05_PRODUCT_REQUIREMENTS.md` §7 Error States) — invalid values raise `ValidationError` (`10_API_SPECIFICATION.md` §6) rather than being silently clamped or coerced. This document does not restate the full validation logic; see `05_PRODUCT_REQUIREMENTS.md` §6–§7 and `../specs/CLI_SPEC.md` §6 for the authoritative rules and edge cases.

## 6. Future Configuration

- A configuration file (e.g., `qst.toml` or `.qstrc`) allowing default parameter values to be set once rather than repeated on every CLI invocation — **Future**, not required for v1.0 given the CLI's relatively small flag surface (§3).
- Per-protocol configuration schemas once additional protocols (E91, B92) are added (`20_FUTURE_ENHANCEMENTS.md`) — each protocol may eventually need its own parameter subset beyond the shared `n_qubits`/`seed` core.

## 7. Assumptions

- No configuration parameter is ever read from an implicit, undocumented source (e.g., a hidden dotfile) — every configuration surface is either an explicit function/CLI argument or a documented environment variable (§4), consistent with `00_PROJECT_CONSTITUTION.md`'s no-hidden-behavior principle.

## 8. Scope

Indexes configuration surfaces only. Authoritative validation logic and error behavior remain owned by `10_API_SPECIFICATION.md`, `../specs/CLI_SPEC.md`, and `05_PRODUCT_REQUIREMENTS.md`.

## 9. References

- `10_API_SPECIFICATION.md`
- `../specs/CLI_SPEC.md`
- `05_PRODUCT_REQUIREMENTS.md`
- `13_DEPLOYMENT.md` §5
- `30_OBSERVABILITY.md`

---

## Implementation Status

| Item | Status |
|---|---|
| Library API parameters (§2) | Planned |
| CLI flags (§3) | Planned |
| `QST_LOG_LEVEL` | Planned |
| `QST_AI_TUTOR_API_KEY` | Future |
| Configuration file support | Future |

## Future Improvements

- Add a configuration-file format once CLI flag repetition becomes a genuine user pain point (evidence-driven, not speculative).

## Document Improvements

This is a new document (v0.1.0), created in Phase 3. It consolidates configuration surfaces already individually defined in `10_API_SPECIFICATION.md` and `../specs/CLI_SPEC.md` into one indexed reference, without redefining or duplicating their validation logic — each row points back to its authoritative source.
