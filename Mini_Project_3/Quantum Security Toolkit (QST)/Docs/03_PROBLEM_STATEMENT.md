# 03 — Problem Statement

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Design (Pre-Development) | **References:** `02_PRODUCT_BLUEPRINT.md`

---

## Table of Contents
1. [Problem](#1-problem)
2. [Pain Points](#2-pain-points)
3. [Current Solutions](#3-current-solutions)
4. [Limitations of Current Solutions](#4-limitations-of-current-solutions)
5. [Why Quantum](#5-why-quantum)
6. [Expected Impact](#6-expected-impact)
7. [Assumptions](#7-assumptions)
8. [Scope](#8-scope)
9. [References](#9-references)

---

## 1. Problem

Quantum key distribution — and BB84 specifically — is widely taught conceptually (bits, bases, measurement) but rarely experienced interactively by students and early researchers. Most coursework relies on static diagrams and hand-worked examples rather than runnable, inspectable simulations that show *why* an eavesdropper is detectable.

## 2. Pain Points

- Static textbook explanations don't let a learner change parameters (e.g., eavesdropping probability) and observe the resulting QBER change.
- Existing single-purpose demo scripts (where they exist) typically simulate BB84 without also modeling an attacker or producing structured analytics.
- Security engineers with a classical-crypto background often lack an intuitive, hands-on bridge into quantum security concepts.
- There is no widely known single toolkit combining simulation + attack modeling + visualization + analytics in one coherent, well-documented package (see `04_MARKET_RESEARCH.md` for the competitive landscape).

## 3. Current Solutions

- **Academic lecture slides and textbook walkthroughs** — conceptually correct but non-interactive.
- **Individual Qiskit tutorial notebooks** (from IBM and community authors) — useful but typically narrow in scope (protocol only, no attack modeling or analytics layer).
- **General-purpose quantum simulators** (Qiskit Aer, Cirq, etc.) — powerful, but not packaged as an educational BB84-specific toolkit.

## 4. Limitations of Current Solutions

| Limitation | Impact |
|---|---|
| No integrated eavesdropper simulation | Learners can't see the security *proof in action* |
| No analytics layer (QBER, key rate) | Hard to reason quantitatively about security margins |
| No visualization layer | Abstract math stays abstract |
| Fragmented across notebooks/scripts | No single trusted, versioned, tested toolkit to point students to |

## 5. Why Quantum

Quantum key distribution's security guarantee comes from physics (no-cloning theorem, measurement disturbance) rather than computational hardness assumptions — which is precisely why it's a compelling teaching subject in an era where classical public-key cryptography faces long-term quantum threats. A toolkit that lets learners *empirically observe* this physical security guarantee (via QBER spikes under eavesdropping) makes an abstract theorem tangible.

## 6. Expected Impact

- Faster, more intuitive learning curve for BB84 and QKD concepts.
- A reusable research base for students/researchers wanting to experiment with noise models or alternate protocols without building simulation infrastructure from scratch.
- A visible, well-documented open-source project supporting the maintainer's research/security engineering track record.

## 7. Assumptions

- The primary gap is pedagogical/tooling, not theoretical — BB84 itself is well-understood in the literature; the gap is in accessible, integrated tooling.

## 8. Scope

This document covers the problem/motivation only. Feature-level response to this problem is in `02_PRODUCT_BLUEPRINT.md` and `05_PRODUCT_REQUIREMENTS.md`.

## 9. References

- `02_PRODUCT_BLUEPRINT.md`
- `04_MARKET_RESEARCH.md`

---

## Implementation Status

| Item | Status |
|---|---|
| Problem validated via literature/landscape review | Current (desk research, not user studies) |
| User studies / learner testing | To Be Implemented |

## Future Improvements

- Validate pain points with actual student/researcher user testing once a prototype exists.
