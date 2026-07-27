# 28 — Performance Benchmark Plan

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development — no benchmarks have been run; no code exists) | **References:** `05_PRODUCT_REQUIREMENTS.md` NFR-1, `14_TESTING_STRATEGY.md` §11, `06_TECHNICAL_REQUIREMENTS.md` §5

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Benchmark Methodology](#2-benchmark-methodology)
3. [Performance Metrics](#3-performance-metrics)
4. [Memory Metrics](#4-memory-metrics)
5. [CPU Metrics](#5-cpu-metrics)
6. [Scaling Metrics](#6-scaling-metrics)
7. [Benchmark Hardware](#7-benchmark-hardware)
8. [Acceptance Thresholds](#8-acceptance-thresholds)
9. [Reporting Tables & Charts (Template)](#9-reporting-tables--charts-template)
10. [Future Benchmark Reporting](#10-future-benchmark-reporting)
11. [Assumptions](#11-assumptions)
12. [Scope](#12-scope)
13. [References](#13-references)

---

## 1. Purpose

Defines *how* QST's performance will be measured once Phase 1 exists, so `05_PRODUCT_REQUIREMENTS.md` NFR-1 ("target, not yet benchmarked") gets a concrete, repeatable measurement methodology rather than remaining an open-ended promise. **No benchmark data exists in this document** — everything below is a plan to execute, not a report of results.

## 2. Benchmark Methodology

1. Run `SimulationOrchestrator.run()` (or its future benchmark-harness wrapper) for a fixed matrix of `n_qubits` values (see §6) at a fixed seed, on the benchmark hardware profile (§7).
2. Repeat each configuration a minimum of 5 times and report median + interquartile range (not just a single run), since Python/OS scheduling jitter can meaningfully skew a single measurement.
3. Measure wall-clock time, peak memory (via `tracemalloc` or `memory_profiler`), and CPU utilization separately (§3–§5) rather than a single conflated number.
4. Record the exact Qiskit/Qiskit Aer version alongside every result (per `06_TECHNICAL_REQUIREMENTS.md` §7 Compatibility Matrix), since simulator performance can change across Qiskit releases.
5. Commit raw benchmark output (not just summary tables) to a `benchmarks/results/` directory (Planned, to be created alongside `tests/` once the repository is scaffolded) so historical comparisons are possible across QST versions.

## 3. Performance Metrics

| Metric | Definition | Tooling (Planned) |
|---|---|---|
| Wall-clock time per run | End-to-end time from `run()` call to `SimulationResult` return | Python's `time.perf_counter()` |
| Time per qubit | Wall-clock time ÷ `n_qubits` | Derived |
| Throughput | Qubits simulated per second | Derived |

## 4. Memory Metrics

| Metric | Definition | Tooling (Planned) |
|---|---|---|
| Peak resident memory | Maximum memory used during a single run | `tracemalloc` (stdlib) or `memory_profiler` |
| Memory per qubit | Peak memory ÷ `n_qubits` | Derived — expected to reveal whether QST's per-qubit-independent simulation strategy (`06_TECHNICAL_REQUIREMENTS.md` §5) actually achieves near-linear (not exponential) scaling in practice |

## 5. CPU Metrics

| Metric | Definition | Tooling (Planned) |
|---|---|---|
| CPU utilization | % CPU time used during simulation (single-core baseline, since no parallelism is assumed for v1.0) | `psutil` or OS-level `time` command |
| Multi-core scaling (Future) | Whether/how much batch runs (`../specs/SIMULATION_SPEC.md` §4) benefit from parallelizing independent trials across cores | Future — not required for v1.0 since Research Mode's per-trial independence makes this a natural, low-risk future optimization, not a v1.0 requirement |

## 6. Scaling Metrics

**Planned benchmark matrix:**

| `n_qubits` | Purpose |
|---|---|
| 10 | Baseline/sanity — should be near-instant |
| 100 | Typical Educational Mode usage |
| 1,000 | Typical Research Mode single-trial usage |
| 10,000 | NFR-1's stated target ceiling |
| 100,000 | Stress test — beyond NFR-1's stated target, to characterize behavior past the "documented recommended maximum" (`05_PRODUCT_REQUIREMENTS.md` EC-6) |

Results across this matrix should be plotted (time/memory vs. `n_qubits`) to visually confirm whether scaling is linear (expected, per `06_TECHNICAL_REQUIREMENTS.md` §5's per-qubit-independent design rationale) or reveals unexpected super-linear behavior requiring architectural attention.

## 7. Benchmark Hardware

**Planned disclosure requirement:** every published benchmark result must state:

- CPU model and core count
- RAM amount
- OS and Python version
- Qiskit/Qiskit Aer version (per §2 step 4)

No specific hardware has been selected yet, since no benchmarks have been run — NFR-1's "standard laptop CPU" phrasing is intentionally vague pending an actual reference machine being chosen at Phase 1 benchmark time. **This is an open placeholder, not an omission to be filled with an invented spec.**

## 8. Acceptance Thresholds

- NFR-1's target ("10,000 qubits in under 30 seconds") is the only threshold currently stated anywhere in the documentation suite, and it is explicitly marked as an estimate pending validation (`05_PRODUCT_REQUIREMENTS.md` NFR-1).
- No other numeric acceptance threshold (e.g., specific memory ceiling) is set in this document, consistent with the "no fabrication" principle — thresholds will be set from the first real benchmark run's baseline, then tracked for regression in subsequent releases (a threshold like "no more than 10% slower than the previous release's median" is a reasonable Planned regression-detection policy once a first baseline exists).

## 9. Reporting Tables & Charts (Template)

**Planned report table shape** (to be populated with real data once Phase 1 benchmarks run):

| `n_qubits` | Median Time (s) | IQR (s) | Peak Memory (MB) | CPU Util (%) | Qiskit Version |
|---|---|---|---|---|---|
| 10 | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| 100 | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| 1,000 | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| 10,000 | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |
| 100,000 | _TBD_ | _TBD_ | _TBD_ | _TBD_ | _TBD_ |

**Planned chart:** a simple line chart, `n_qubits` (log scale) on the x-axis, time and memory as two separate y-axis series, generated via the same `Visualizer` machinery already specified in `../specs/VISUALIZATION_SPEC.md` (benchmark charts should reuse existing plotting infrastructure rather than introducing a parallel, one-off charting mechanism).

## 10. Future Benchmark Reporting

- Once CI exists (`13_DEPLOYMENT.md`), a scheduled (not per-PR, to control CI cost) benchmark job could run this matrix and flag regressions automatically — Future, contingent on the acceptance-threshold policy (§8) being established first from real baseline data.
- Historical benchmark results (§2 step 5) should be published alongside release notes once a benchmark history exists, so users can see documented performance characteristics per QST version rather than only the latest.

## 11. Assumptions

- No GPU-accelerated benchmarking is planned for v1.0, consistent with `06_TECHNICAL_REQUIREMENTS.md` §5's CPU-only baseline.
- Benchmark hardware (§7) will be whatever the project owner's development machine is at Phase 1 completion, disclosed transparently rather than presented as a rigorous multi-machine study — a rigorous multi-machine benchmark suite is a reasonable Future enhancement once community interest justifies the added effort.

## 12. Scope

Methodology and planned matrix only — contains no actual benchmark results, since none exist yet (see `01_REPOSITORY_AUDIT.md`).

## 13. References

- `05_PRODUCT_REQUIREMENTS.md` (NFR-1)
- `06_TECHNICAL_REQUIREMENTS.md` §5 (Hardware Constraints)
- `14_TESTING_STRATEGY.md` §11 (Performance Testing)
- `../specs/VISUALIZATION_SPEC.md`

---

## Implementation Status

| Item | Status |
|---|---|
| Benchmark methodology (this document) | Current (design-complete) |
| Any actual benchmark data | Not available — To Be Implemented at Phase 1 completion |
| CI-integrated regression benchmarking | Future |

## Future Improvements

- Populate §9's report template with real data after the first Phase 1 benchmark run.
- Establish a concrete regression-detection policy (§8) once a baseline exists.

## Document Improvements

This is a new document (v0.1.0), created in Phase 3. It elevates the previously brief, single-paragraph performance-testing mention in `14_TESTING_STRATEGY.md` §11 into a full methodology, without duplicating that section — `14_TESTING_STRATEGY.md` retains ownership of *when in the test pyramid* performance testing runs; this document owns *how* it's measured and reported.
