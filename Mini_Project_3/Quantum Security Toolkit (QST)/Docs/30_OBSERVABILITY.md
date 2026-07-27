# 30 — Observability

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `07_SYSTEM_ARCHITECTURE.md`, `../specs/CLI_SPEC.md`, `11_SECURITY_ARCHITECTURE.md`

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Logging](#2-logging)
3. [Metrics](#3-metrics)
4. [Tracing](#4-tracing)
5. [Debugging](#5-debugging)
6. [Profiling](#6-profiling)
7. [Error Reporting](#7-error-reporting)
8. [Diagnostic Mode](#8-diagnostic-mode)
9. [Developer Mode](#9-developer-mode)
10. [Future Telemetry](#10-future-telemetry)
11. [Assumptions](#11-assumptions)
12. [Scope](#12-scope)
13. [References](#13-references)

---

## 1. Purpose

Defines how QST surfaces internal behavior for debugging, performance analysis, and (opt-in only) future telemetry — without introducing any unsolicited data collection, consistent with `11_SECURITY_ARCHITECTURE.md` §6's "no network I/O in core path" constraint and `00_PROJECT_CONSTITUTION.md`'s no-hidden-behavior principle.

## 2. Logging

**Planned:** Python standard library `logging` module, not a third-party logging framework, to keep the dependency footprint minimal (`06_TECHNICAL_REQUIREMENTS.md` §2).

| Log Level | Used For |
|---|---|
| `DEBUG` | Per-qubit trace detail (basis/bit choices, Eve interception decisions) — verbose, opt-in via `--verbose`/`-v` CLI flag (Planned, extends `../specs/CLI_SPEC.md`) |
| `INFO` | High-level run milestones (simulation started, sifting complete, result assembled) |
| `WARNING` | Non-fatal unusual conditions (e.g., empty sifted key — `../specs/QBER_SPEC.md` §6) |
| `ERROR` | Caught exceptions before re-raising as a QST-specific exception (`10_API_SPECIFICATION.md` §6) |

All logging goes to stderr by default (never stdout, to avoid polluting piped/redirected simulation output — consistent with `../specs/CLI_SPEC.md` §5's stdout/stderr separation) and is entirely local — no log data leaves the user's machine, ever, for any log level.

## 3. Metrics

**Planned, local-only:** QST does not run a metrics server (no such component exists in the architecture, `07_SYSTEM_ARCHITECTURE.md` §2). "Metrics" in QST's context means:

- Per-run timing/memory data already specified in `28_PERFORMANCE_BENCHMARK_PLAN.md` §3–§5, surfaced via `SimulationResult.metadata` (`10_API_SPECIFICATION.md` §5) for any caller who wants to inspect it.
- No metrics are aggregated, transmitted, or persisted beyond a single run's `SimulationResult` unless the user explicitly exports it (`../specs/EXPORT_SPEC.md`).

## 4. Tracing

**Future, optional:** distributed tracing (e.g., OpenTelemetry) is not applicable to a single-process, offline library — there is no distributed system to trace. What *is* planned is a lightweight **internal step trace**: reusing the narration hooks already specified in `../specs/SIMULATION_SPEC.md` §5 (`on_bits_generated`, `on_qubits_prepared`, etc.), a `--trace` CLI flag (Future) could dump a structured (JSON) record of every hook firing with a timestamp, useful for debugging *why* a particular run behaved unexpectedly without needing to add ad hoc print statements to `core/`.

## 5. Debugging

- Since every run is reproducible from `(n_qubits, seed, eve_intercept_probability)` (`../specs/SIMULATION_SPEC.md` §6 Determinism Contract), the primary debugging workflow is: **reproduce the exact run using the reported seed**, then step through with a standard Python debugger (`pdb`/IDE debugger) — no QST-specific debugging infrastructure is required for this most common case.
- `SimulationResult.warnings` (`10_API_SPECIFICATION.md` §5) is the first place to check for a run that produced unexpected (but not erroring) results.

## 6. Profiling

**Planned:** standard Python profiling tools (`cProfile`, `py-spy`) are sufficient and recommended over a QST-specific profiling wrapper, to avoid maintaining bespoke tooling that duplicates well-established ecosystem tools. `28_PERFORMANCE_BENCHMARK_PLAN.md` §2 step 3's benchmark methodology already specifies using `tracemalloc`/`memory_profiler` for memory profiling specifically.

## 7. Error Reporting

- QST does **not** implement any automatic error-reporting-to-maintainer mechanism (e.g., a Sentry-style crash reporter) — consistent with the zero-network-calls-in-core-path constraint (`11_SECURITY_ARCHITECTURE.md` §6) and the project's non-commercial, privacy-respecting posture.
- Users experiencing an unhandled exception are directed (via a friendly CLI error message, Planned) to file a GitHub issue using the bug report template (Phase 4, `.github/ISSUE_TEMPLATE/bug_report.md`), including the QST/Qiskit version (`../specs/CLI_SPEC.md` §6 point 3) and, ideally, the seed that reproduces the issue.

## 8. Diagnostic Mode

**Planned:** a `qst simulate --diagnose` flag (extends `../specs/CLI_SPEC.md` §2) that, on completion, prints a structured diagnostic block: QST version, Qiskit/Aer version, Python version, OS, and the full parameter set used — designed to be copy-pasted directly into a GitHub bug report, reducing the "what version are you on" back-and-forth in issue triage.

## 9. Developer Mode

**Planned:** `--verbose`/`-v` (§2) combined with `--trace` (§4, Future) constitutes QST's "developer mode" — no separate build/binary is needed since QST is a single Python package; developer-mode behavior is purely a matter of flags/log-level configuration, not a different installed artifact.

## 10. Future Telemetry

**Explicitly deferred, opt-in only if ever built:** consistent with `02_PRODUCT_BLUEPRINT.md` §3.3's Measurement Principle ("No metric requiring user data collection will be implemented without being explicitly opt-in and documented"), any future anonymous usage telemetry (e.g., anonymized feature-usage counts to inform roadmap prioritization) would require:

1. Explicit, documented opt-in (never on by default).
2. A clear, published data-handling statement (what is collected, where it goes, how to disable it).
3. No collection of simulation parameters or results themselves (only high-level feature-usage signals, if ever implemented) — collecting actual research data without explicit, separate consent would be a significant overreach beyond simple usage telemetry.

No telemetry of any kind exists today, and none is planned for v1.0.

## 11. Assumptions

- The Python standard library `logging` module is sufficient for all v1.0 observability needs; a third-party structured-logging library is not justified until a concrete need for structured (e.g., JSON) log output arises beyond what `--trace`'s dedicated JSON output (§4) already covers.

## 12. Scope

Covers developer/user-facing observability tooling only. Does not cover CI/build-pipeline observability (see `13_DEPLOYMENT.md`).

## 13. References

- `07_SYSTEM_ARCHITECTURE.md`
- `../specs/CLI_SPEC.md`
- `../specs/SIMULATION_SPEC.md` §5 (narration hooks reused for tracing)
- `10_API_SPECIFICATION.md` §5 (`SimulationResult.metadata`/`warnings`)
- `11_SECURITY_ARCHITECTURE.md` §6
- `02_PRODUCT_BLUEPRINT.md` §3.3

---

## Implementation Status

| Item | Status |
|---|---|
| Standard logging (`--verbose`) | Planned |
| Diagnostic mode (`--diagnose`) | Planned |
| Trace mode (`--trace`) | Future |
| Any telemetry | Not implemented, not planned for v1.0 — Future only, opt-in |

## Future Improvements

- Implement `--trace` once the narration-hook mechanism (`../specs/SIMULATION_SPEC.md` §5) is built and stable.
- Revisit opt-in telemetry only if roadmap-prioritization needs genuinely can't be met via GitHub-metadata-only metrics (`02_PRODUCT_BLUEPRINT.md` §3).

## Document Improvements

This is a new document (v0.1.0), created in Phase 3. It reuses (rather than duplicates) the narration-hook mechanism already specified in `../specs/SIMULATION_SPEC.md` §5 for tracing purposes, and the `SimulationResult.metadata`/`warnings` fields already specified in `10_API_SPECIFICATION.md` §5 for metrics/debugging — no new data structures were invented where existing ones already served the purpose.
