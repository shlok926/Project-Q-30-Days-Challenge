# 32 — Component Specification

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `07_SYSTEM_ARCHITECTURE.md`, all `../specs/*.md`

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Component: BB84Protocol](#2-component-bb84protocol)
3. [Component: Eavesdropper](#3-component-eavesdropper)
4. [Component: SecurityAnalytics](#4-component-securityanalytics)
5. [Component: Visualizer](#5-component-visualizer)
6. [Component: SimulationOrchestrator](#6-component-simulationorchestrator)
7. [Component: CLI](#7-component-cli)
8. [Assumptions](#8-assumptions)
9. [Scope](#9-scope)
10. [References](#10-references)

---

## 1. Purpose

Provides one standardized, per-module summary (Purpose, Responsibilities, Dependencies, Inputs, Outputs, Extension Points, Failure Modes, Testing Strategy) across every module named in `07_SYSTEM_ARCHITECTURE.md` §5's module diagram. This is a **summary index**, not a replacement for the detailed `../specs/*.md` files — every field below links to the spec section that defines it in full.

## 2. Component: BB84Protocol

| Field | Detail |
|---|---|
| **Purpose** | Implements the core BB84 key-exchange algorithm (bit/basis generation, qubit prep, measurement, sifting) |
| **Responsibilities** | Steps 1–3, 5–6, 8 of `../specs/BB84_SPEC.md` §1 |
| **Dependencies** | Qiskit, Qiskit Aer (`06_TECHNICAL_REQUIREMENTS.md` §2); no dependency on `analytics/`, `visualization/`, `cli/` (`07_SYSTEM_ARCHITECTURE.md` §7) |
| **Inputs** | `n_qubits`, `seed` (`10_API_SPECIFICATION.md` §3) |
| **Outputs** | `alice_bits`, `alice_bases`, `bob_bits`, `bob_bases`, sifted-index mask (internal; surfaced to caller via `SimulationResult`, `10_API_SPECIFICATION.md` §5) |
| **Extension Points** | `ProtocolInterface` (`07_SYSTEM_ARCHITECTURE.md` §8) — `BB84Protocol` is one concrete implementation; Future `E91Protocol`, `B92Protocol` implement the same interface |
| **Failure Modes** | Backend (Qiskit/Aer) exceptions → wrapped as `SimulationError` (`10_API_SPECIFICATION.md` §6); invalid inputs are rejected before this component is even constructed (`../specs/SIMULATION_SPEC.md` §1) |
| **Testing Strategy** | Unit tests `test_bit_basis_generation_length`, `test_reproducibility_with_seed`, `test_sifting_discards_mismatched_bases`; golden dataset (`14_TESTING_STRATEGY.md` §3, §8) |
| **Full Spec** | `../specs/BB84_SPEC.md` |

## 3. Component: Eavesdropper

| Field | Detail |
|---|---|
| **Purpose** | Models an intercept-resend eavesdropping attack against qubits in transit |
| **Responsibilities** | Steps E1–E5 of `../specs/BB84_SPEC.md` §5 |
| **Dependencies** | Same qubit-preparation primitives as `BB84Protocol`; no dependency on `analytics/`, `visualization/`, `cli/` |
| **Inputs** | `eve_intercept_probability`, in-transit qubit stream |
| **Outputs** | Modified (or passed-through) qubit stream forwarded to Bob |
| **Extension Points** | `AttackModelInterface` (Future, `07_SYSTEM_ARCHITECTURE.md` §8) would generalize beyond intercept-resend to other attack strategies |
| **Failure Modes** | Same backend-exception wrapping as `BB84Protocol`; a logic bug here is the single highest-priority threat in the entire suite (`29_THREAT_MODEL.md` §7.1, §11) |
| **Testing Strategy** | `test_qber_zero_eve`, `test_qber_full_eve`, statistical validation (`14_TESTING_STRATEGY.md` §3, §9) — **critical, blocking** tests per `11_SECURITY_ARCHITECTURE.md` §4 |
| **Full Spec** | `../specs/BB84_SPEC.md` §5 |

## 4. Component: SecurityAnalytics

| Field | Detail |
|---|---|
| **Purpose** | Computes QBER, key rate, and detection probability from sifted protocol output |
| **Responsibilities** | `../specs/QBER_SPEC.md` §1–§5 |
| **Dependencies** | `BB84Protocol`/`Eavesdropper` output only (never the reverse — `07_SYSTEM_ARCHITECTURE.md` §7) |
| **Inputs** | Sifted key, public sample (`../specs/QBER_SPEC.md` §2) |
| **Outputs** | `qber`, `key_rate`, `detection_probability` fields of `SimulationResult` |
| **Extension Points** | None currently planned — this component is intentionally narrow/single-purpose (Single Responsibility, `16_CODING_STANDARDS.md` §7) |
| **Failure Modes** | Division-by-zero on empty sifted key — explicitly handled per `../specs/QBER_SPEC.md` §6, not an unhandled crash |
| **Testing Strategy** | Property-based tests (QBER bounds, monotonicity — `14_TESTING_STRATEGY.md` §5); fixed hand-computed example in golden dataset (`../specs/QBER_SPEC.md` §7) |
| **Full Spec** | `../specs/QBER_SPEC.md` |

## 5. Component: Visualizer

| Field | Detail |
|---|---|
| **Purpose** | Renders basis tables and QBER-vs-interception charts |
| **Responsibilities** | `../specs/VISUALIZATION_SPEC.md` §1 |
| **Dependencies** | `matplotlib`/`plotly` (optional extra, `06_TECHNICAL_REQUIREMENTS.md` §3); depends on `analytics/` output shape (`SimulationResult`), never on `core/` internals directly (`07_SYSTEM_ARCHITECTURE.md` §7) |
| **Inputs** | `SimulationResult` or `list[SimulationResult]` (`../specs/VISUALIZATION_SPEC.md` §2) |
| **Outputs** | Rendered CLI table (str) or `matplotlib`/`plotly` figure object |
| **Extension Points** | Bloch-sphere visualization (Future, `12_UI_UX_DESIGN.md` §6) |
| **Failure Modes** | Must render gracefully even for a `warnings`-flagged empty-key result (`../specs/VISUALIZATION_SPEC.md` §6) — never raises for a valid-but-sparse result |
| **Testing Strategy** | Lower coverage target (≥60%, `14_TESTING_STRATEGY.md` §12) reflecting presentation-layer, non-security-critical status |
| **Full Spec** | `../specs/VISUALIZATION_SPEC.md` |

## 6. Component: SimulationOrchestrator

| Field | Detail |
|---|---|
| **Purpose** | Composition root coordinating protocol, attack, and analytics modules into single/batch run entrypoints |
| **Responsibilities** | `../specs/SIMULATION_SPEC.md` §1, §3–§4 |
| **Dependencies** | `core/`, `analytics/`, `visualization/` (the only layer allowed to depend on all three — `07_SYSTEM_ARCHITECTURE.md` §7) |
| **Inputs** | All public API parameters (`10_API_SPECIFICATION.md` §3), or a `param_sweep` list for batch mode |
| **Outputs** | `SimulationResult` (single) or `list[SimulationResult]` (batch) |
| **Extension Points** | `PROTOCOL_REGISTRY` (`../specs/SIMULATION_SPEC.md` §2) — the mechanism through which new protocols are wired in without modifying the orchestrator itself |
| **Failure Modes** | Validates before constructing any protocol object (fail-fast, `07_SYSTEM_ARCHITECTURE.md` §11); batch mode isolates per-trial failures per the `--on-error` policy (`../specs/SIMULATION_SPEC.md` §4, `../specs/CLI_SPEC.md` §3) |
| **Testing Strategy** | Integration tests (`14_TESTING_STRATEGY.md` §4); narration-hook call-order test (`../specs/SIMULATION_SPEC.md` §7 point 3) |
| **Full Spec** | `../specs/SIMULATION_SPEC.md` |

## 7. Component: CLI

| Field | Detail |
|---|---|
| **Purpose** | Thin command-line entrypoint over `SimulationOrchestrator` |
| **Responsibilities** | `../specs/CLI_SPEC.md` §1–§5 |
| **Dependencies** | `orchestration/` only, never `core/` directly (`07_SYSTEM_ARCHITECTURE.md` §7) |
| **Inputs** | Command-line flags (`31_CONFIGURATION_REFERENCE.md` §3) |
| **Outputs** | stdout narration/summary, stderr errors, exit codes (`../specs/CLI_SPEC.md` §4), optional export file (`../specs/EXPORT_SPEC.md`) |
| **Extension Points** | New subcommands (e.g., a Future `qst compare`, `../specs/CLI_SPEC.md` Future Improvements) |
| **Failure Modes** | Exit-code contract (`../specs/CLI_SPEC.md` §4) maps every exception type to a distinct, scriptable exit code |
| **Testing Strategy** | Integration tests covering argument parsing, exit codes, and range-parsing correctness (`../specs/CLI_SPEC.md` §6) |
| **Full Spec** | `../specs/CLI_SPEC.md` |

## 8. Assumptions

- Every component listed above corresponds exactly to a node in `07_SYSTEM_ARCHITECTURE.md` §5's module diagram — this document introduces no new component that isn't already architecturally scoped.

## 9. Scope

Per-module summary index only. Full behavioral contracts remain owned by the respective `../specs/*.md` files linked in each section.

## 10. References

- `07_SYSTEM_ARCHITECTURE.md` §5
- `../specs/BB84_SPEC.md`
- `../specs/QBER_SPEC.md`
- `../specs/SIMULATION_SPEC.md`
- `../specs/VISUALIZATION_SPEC.md`
- `../specs/EXPORT_SPEC.md`
- `../specs/CLI_SPEC.md`
- `29_THREAT_MODEL.md`

---

## Implementation Status

| Component | Status |
|---|---|
| BB84Protocol | Planned |
| Eavesdropper | Planned |
| SecurityAnalytics | Planned |
| Visualizer | Planned |
| SimulationOrchestrator | Planned |
| CLI | Planned |

## Future Improvements

- Add a `Future E91Protocol` row once that component is prioritized (`20_FUTURE_ENHANCEMENTS.md`).

## Document Improvements

This is a new document (v0.1.0), created in Phase 3. It provides the single standardized per-module summary table format across all six components that `07_SYSTEM_ARCHITECTURE.md`'s module diagram names — previously, per-module detail existed only within each `../specs/*.md` file with no consolidated cross-module comparison view.
