# 20 — Future Enhancements

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Future / Not Committed | **References:** `15_ROADMAP.md`, `19_RELEASE_PLAN.md`

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Future Modules](#2-future-modules)
3. [Research Opportunities](#3-research-opportunities)
4. [Advanced Features](#4-advanced-features)
5. [Enterprise/Institutional Roadmap](#5-enterpriseinstitutional-roadmap)
6. [Assumptions](#6-assumptions)
7. [Scope](#7-scope)
8. [References](#8-references)

---

## 1. Purpose

This document is an explicit parking lot for ideas that are **not** part of the v1.0 commitment (`19_RELEASE_PLAN.md`), so they aren't lost, but also aren't allowed to cause scope creep (see `17_RISK_REGISTER.md` P-3).

## 2. Future Modules

- **Additional QKD protocols:** E91 (entanglement-based), B92 — pluggable behind the protocol interface described in `16_CODING_STANDARDS.md` §4.
- **Noise models:** realistic hardware noise simulation (depolarizing channel, etc.) for more research-grade fidelity.
- **Web dashboard:** Streamlit or similar, per `12_UI_UX_DESIGN.md` §6.
- **AI Tutor / Anomaly Detector:** per `08_AI_ARCHITECTURE.md` §3.

## 3. Research Opportunities

- Empirical study comparing simulated QBER distributions against published theoretical bounds across different Eve strategies, potentially publishable as a small research note.
- Extension to a full privacy-amplification pipeline (`11_SECURITY_ARCHITECTURE.md` §7), turning QST into a more complete (if still educational) QKD stack.

## 4. Advanced Features

- Real IBM Quantum hardware execution path (optional, opt-in), for users who want to see real-hardware noise vs. simulator behavior.
- Guided classroom/lab-exercise mode with quiz checkpoints (extends `12_UI_UX_DESIGN.md` §6 Future UI Improvements).

## 5. Enterprise/Institutional Roadmap

Framed for potential university/institutional adoption rather than commercial enterprise sale (consistent with the project's open-source educational mission, `00_PROJECT_CONSTITUTION.md`):

- Packaged "course module" version with instructor guide.
- Optional hosted demo instance for institutions without local Python setup capability (would require revisiting `09_DATABASE_DESIGN.md` and `13_DEPLOYMENT.md`).

## 6. Assumptions

- None of the above is committed; inclusion here is not a promise, per `19_RELEASE_PLAN.md` v2.0 framing.

## 7. Scope

Speculative/backlog only — not to be treated as roadmap commitments.

## 8. References

- `15_ROADMAP.md`
- `19_RELEASE_PLAN.md`
- `08_AI_ARCHITECTURE.md`
- `12_UI_UX_DESIGN.md`

---

## Implementation Status

| Item | Status |
|---|---|
| Everything in this document | Future (not started, not committed) |

## Future Improvements

- Promote items from this backlog into `15_ROADMAP.md` only after v1.0 ships and priorities are re-evaluated.
