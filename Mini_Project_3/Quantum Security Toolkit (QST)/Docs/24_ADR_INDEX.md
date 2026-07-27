# 24 — ADR Index

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Living Document (master index — individual ADRs remain owned by `18_DECISION_LOG.md`) | **References:** `18_DECISION_LOG.md`

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Master ADR Index](#2-master-adr-index)
3. [Assumptions](#3-assumptions)
4. [Scope](#4-scope)
5. [References](#5-references)

---

## 1. Purpose

`18_DECISION_LOG.md` contains the full detail (Context, Problem, Decision, Alternatives, Pros, Cons, Consequences, Future Review Date) for every ADR, per its standard template. This document is a **master index only** — a single scannable table for quickly finding which ADR governs what, without opening the full log. Nothing here duplicates the ADR content itself; every field below either restates a short label or a fact not already itemized in `18_DECISION_LOG.md`'s per-ADR sections (e.g., which *other* documents an ADR's decision touches).

## 2. Master ADR Index

| ADR | Status | Owner | Decision (short) | Related Documents | Review Date | Dependencies | Impact |
|---|---|---|---|---|---|---|---|
| ADR-001 | Accepted | ParaDise | Python + Qiskit as core stack | `06_TECHNICAL_REQUIREMENTS.md`, `22_MATHEMATICAL_FOUNDATION.md`, `../specs/BB84_SPEC.md` | On breaking Qiskit change or v2.0 planning | None (foundational — no prior ADR) | High — determines entire implementation language/SDK surface |
| ADR-002 | Accepted | ParaDise | Library/CLI-first, no web service for v1.0 | `09_DATABASE_DESIGN.md`, `13_DEPLOYMENT.md`, `../specs/CLI_SPEC.md`, `12_UI_UX_DESIGN.md` | At v2.0 planning if web dashboard prioritized | Depends on ADR-001 (Python packaging assumptions) | Medium — shapes distribution and deployment strategy, not core protocol correctness |
| ADR-003 | Accepted | ParaDise | No AI/ML in core simulation path | `08_AI_ARCHITECTURE.md`, `20_FUTURE_ENHANCEMENTS.md` | Once Educational Mode ships + user feedback exists | Independent of ADR-001/002 | Low-Medium — bounds scope of Future features only, does not affect core v1.0 delivery |
| ADR-004 (candidate, not yet formalized) | Proposed | ParaDise | `ProtocolInterface` extension-point design (Strategy pattern for pluggable QKD protocols) | `07_SYSTEM_ARCHITECTURE.md` §8–§9, `../specs/SIMULATION_SPEC.md` §2 | To be formalized when the registry mechanism (dict vs. entry-points) is finalized during Phase 1 | Depends on ADR-001 | Medium — determines how extensible Phase 3+ protocol additions will be |

## 3. Assumptions

- ADR-004 is listed here as a **candidate** because `07_SYSTEM_ARCHITECTURE.md` §9 and `../specs/SIMULATION_SPEC.md` §2 already flag the registry-mechanism choice as "may become an ADR" — this index surfaces that forward pointer in one place rather than leaving it buried in two separate documents. It should be promoted to a fully-specified ADR in `18_DECISION_LOG.md` (using the standard template) once the decision is actually finalized during implementation, not before.

## 4. Scope

Index only — full ADR content is exclusively owned by `18_DECISION_LOG.md`. If this index and `18_DECISION_LOG.md` ever disagree on an ADR's status, `18_DECISION_LOG.md` is authoritative and this index should be corrected to match.

## 5. References

- `18_DECISION_LOG.md`
- `07_SYSTEM_ARCHITECTURE.md` §9 (Architecture Decision Mapping — the reverse view: architecture element → governing ADR)

---

## Implementation Status

| Item | Status |
|---|---|
| ADR-001, 002, 003 (indexed) | Current — matches `18_DECISION_LOG.md` |
| ADR-004 (candidate) | Proposed, not yet formalized |

## Future Improvements

- Promote ADR-004 to a full entry in `18_DECISION_LOG.md` once the `ProtocolInterface` registry mechanism decision is finalized, then update this index's Status column accordingly.

## Document Improvements

This is a new document (v0.1.0), created in Phase 3, providing a single-table master index over `18_DECISION_LOG.md`'s ADRs plus their footprint across the rest of the documentation suite (Related Documents, Dependencies, Impact) — information that existed only implicitly (scattered across `07_SYSTEM_ARCHITECTURE.md` §9 and individual ADR "Consequences" fields) before this index consolidated it.
