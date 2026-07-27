# 18 — Decision Log

**Version:** 0.2.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Living Document | **References:** `00_PROJECT_CONSTITUTION.md`

---

## Table of Contents
1. [How to Use This Log](#1-how-to-use-this-log)
2. [Standard ADR Template](#2-standard-adr-template)
3. [Decisions](#3-decisions)
4. [Assumptions](#4-assumptions)
5. [Scope](#5-scope)
6. [References](#6-references)

---

## 1. How to Use This Log

Every architecturally significant decision (technology choice, major trade-off) is recorded here with its rationale and alternatives considered, so future-you or future contributors understand *why*, not just *what*. All ADRs from this revision onward follow the standard template in §2 for consistency; ADR-001 through ADR-003 have been reformatted (content preserved, structure standardized) to match.

## 2. Standard ADR Template

Every ADR in this log follows this structure:

```
### ADR-XXX: <Title>

- Status: Proposed | Accepted | Superseded by ADR-YYY
- Context: What situation/problem prompted this decision?
- Problem: What specific question does this decision answer?
- Decision: What was decided?
- Alternatives: What else was considered?
- Pros: Advantages of the chosen option
- Cons: Drawbacks/trade-offs accepted
- Consequences: Downstream effects on architecture, roadmap, or risk
- Future Review Date: When should this decision be revisited? (or "None scheduled" if open-ended)
```

## 3. Decisions

### ADR-001: Python + Qiskit as the core technology stack

- **Status:** Accepted
- **Context:** Need a language/framework combination for quantum circuit simulation that is widely taught, well-documented, and has a strong open-source simulator (Aer).
- **Problem:** Which language/quantum-SDK combination should QST build on?
- **Decision:** Python + Qiskit (+ Qiskit Aer for simulation).
- **Alternatives:** Cirq (Google), PennyLane. Not evaluated in depth for this decision — Qiskit chosen primarily due to its dominant position in academic BB84 tutorials and the project owner's existing familiarity, which supports faster, more reliable delivery.
- **Pros:** Strong academic/tutorial ecosystem already uses Qiskit for BB84-style demos, easing onboarding for the target student/researcher audience; project owner's existing familiarity speeds delivery; Aer provides a mature, well-supported simulator backend.
- **Cons:** Ties the project to a single vendor's SDK and release cadence; Cirq/PennyLane were not rigorously benchmarked against Qiskit for this use case, so the choice rests partly on familiarity rather than exhaustive comparison.
- **Consequences:** Ties the project to Qiskit's release cadence and breaking-change risk (see `17_RISK_REGISTER.md` T-1).
- **Future Review Date:** Revisit if Qiskit introduces a breaking change that would require significant rework, or at the v2.0 planning milestone (`19_RELEASE_PLAN.md`).

### ADR-002: Library/CLI-first, no web service for v1.0

- **Status:** Accepted
- **Context:** Target users (students, researchers) commonly work in local Python/Jupyter environments; a hosted web service adds infrastructure cost/complexity without clear v1.0 benefit.
- **Problem:** Should QST ship as a hosted web service/API, or as a locally-run library/CLI?
- **Decision:** Ship as a pip-installable Python package + CLI; defer any web dashboard to Future.
- **Alternatives:** A hosted Streamlit/Flask dashboard as the primary interface from day one; a REST API with a thin client.
- **Pros:** Zero hosting cost/maintenance burden for a solo maintainer; no database or auth surface needed (see `09_DATABASE_DESIGN.md`, `11_SECURITY_ARCHITECTURE.md` §6); matches how the target audience already works (local Python/notebooks).
- **Cons:** Higher barrier to entry for users who would prefer a no-install, point-and-click experience; no built-in way to showcase the tool via a public demo link without the user installing it first.
- **Consequences:** No database or hosting needed for v1.0 (see `09_DATABASE_DESIGN.md`, `13_DEPLOYMENT.md`).
- **Future Review Date:** Revisit at v2.0 planning if a web dashboard is prioritized from `20_FUTURE_ENHANCEMENTS.md`.

### ADR-003: No AI/ML in the core simulation path

- **Status:** Accepted
- **Context:** Core value is transparent, inspectable protocol simulation.
- **Problem:** Should any AI/ML component be part of the core BB84 simulation, attack modeling, or analytics logic?
- **Decision:** AI features (e.g., AI Tutor) are optional, Future, and never required for core functionality.
- **Alternatives:** Building an LLM-based explanation layer into the core `SimulationOrchestrator` from the start.
- **Pros:** Keeps the core simulation fully transparent, deterministic, and auditable — critical given the project's educational-correctness mission (`00_PROJECT_CONSTITUTION.md` Core Principles); avoids any hard dependency on external AI APIs or associated cost/network requirements.
- **Cons:** Defers a potentially valuable learning-aid feature (natural-language explanation of results) to an unspecified future date.
- **Consequences:** See `08_AI_ARCHITECTURE.md`.
- **Future Review Date:** Revisit once Educational Mode (core, non-AI) ships and user feedback indicates demand (see `08_AI_ARCHITECTURE.md` Future Improvements).

### ADR-004: Composable Protocol Engine Architecture

- **Status:** Accepted
- **Context:** Need to lay down a solid protocol design supporting future protocols (E91, B92) and isolate Qiskit dependencies to reduce version friction on the wider application stack.
- **Problem:** How should the protocol engines be structured to ensure extensibility, SOLID compatibility, and Qiskit API change isolation?
- **Decision:** Scaffold a `qst.core.shared` package separating random generators (`RandomProvider`) and executors (`ExecutorInterface`). Refactor BB84 to live in a dedicated subpackage (`qst.core.bb84`) where circuit construction is broken into single-responsibility classes (`RegisterAllocator`, `GateApplier`, `StateEncoder`, `CircuitBuilder`, `MeasurementBuilder`).
- **Alternatives:**
  - A monolithic, single-class BB84 implementation doing random generation, circuit build, and simulator execution.
  - Allowing Qiskit imports globally throughout the codebase.
- **Pros:**
  - Standardized random and execution providers are reusable directly by E91 and B92.
  - Localizes Qiskit library version shifts entirely to `executor.py` and circuit builders.
  - Independent unit testing is simplified since builders and state preparers can be mocked.
- **Cons:**
  - Multiplies the file count and increases object-composition verbosity in the protocol engine.
- **Consequences:** All future protocols must follow the interface contracts and register stubs without editing shared core.
- **Future Review Date:** None scheduled.

## 4. Assumptions

- Decisions recorded here reflect the project owner's reasoning at time of writing and may be revisited as an ADR update (never silently overwritten — a superseded decision is marked "Superseded by ADR-XXX," not deleted).
- The standardized template (§2) applies retroactively to ADR-001–003 for consistency; no factual content in those decisions was altered, only reformatted into the common structure.

## 5. Scope

Architecturally significant decisions only — not every implementation detail.

## 6. References

- `00_PROJECT_CONSTITUTION.md`
- `06_TECHNICAL_REQUIREMENTS.md`
- `08_AI_ARCHITECTURE.md`
- `07_SYSTEM_ARCHITECTURE.md` (§9 Architecture Decision Mapping references these ADRs)

---

## Implementation Status

| Item | Status |
|---|---|
| ADR-001, 002, 003, 004 | Current (decisions made; implemented in code) |
| Standard ADR template (§2) | Current (adopted this revision, applied retroactively) |

## Future Improvements

- Add new ADRs as further architectural decisions are made during implementation.

## Document Improvements

This revision (0.2.0) added: a Standard ADR Template (§2) with Context, Problem, Decision, Alternatives, Pros, Cons, Consequences, and Future Review Date fields, and reformatted ADR-001 through ADR-003 into this consistent structure — adding explicit Problem, Pros, Cons, and Future Review Date fields that were previously implicit or absent. No original decision content, rationale, or consequence was removed or altered in meaning.
