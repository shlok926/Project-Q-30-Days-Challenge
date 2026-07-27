# 26 — Project Glossary

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Reference (consolidates, does not replace, per-document scoped glossaries) | **References:** All documents in `docs/` and `specs/`

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Glossary](#2-glossary)
3. [Assumptions](#3-assumptions)
4. [Scope](#4-scope)

---

## 1. Purpose

Several documents (`00`, `02`, `05`, `07`, `11`, `22`) already carry their own scoped glossary covering terms relevant to that document. This document consolidates **every** technical term used anywhere in the suite into one alphabetized reference, per `21_DOCUMENTATION_QUALITY_REPORT.md` Round 2's R2.5/R2.6 recommendation. Per-document glossaries are **not removed** (they remain useful for reading a document standalone) — this file is an additional, complete index, not a replacement.

## 2. Glossary

| Term | Definition | Context | Related Documents |
|---|---|---|---|
| **Alice** | The conventional name for the sender in a cryptographic protocol description; in BB84, the party who generates and prepares qubits. | Protocol actor | `../specs/BB84_SPEC.md`, `22_MATHEMATICAL_FOUNDATION.md` |
| **Basis** | A choice of measurement/preparation reference frame for a qubit — BB84 uses two: computational (Z) and Hadamard (X). | Quantum mechanics | `../specs/BB84_SPEC.md` §2, `22_MATHEMATICAL_FOUNDATION.md` §9 |
| **BB84** | The first quantum key distribution protocol, proposed by Bennett and Brassard in 1984. | Protocol | `00_PROJECT_CONSTITUTION.md`, `../specs/BB84_SPEC.md`, `23_REFERENCES.md` [7] |
| **Bob** | The conventional name for the receiver in a cryptographic protocol description; in BB84, the party who measures incoming qubits. | Protocol actor | `../specs/BB84_SPEC.md` |
| **Bloch Sphere** | A geometric representation of a single qubit's state as a point on/in a unit sphere. | Visualization / QM | `22_MATHEMATICAL_FOUNDATION.md` §6, `../specs/VISUALIZATION_SPEC.md` |
| **Born Rule** | The postulate that measurement probabilities equal the squared magnitude of the corresponding quantum amplitude. | Quantum mechanics | `22_MATHEMATICAL_FOUNDATION.md` §8 |
| **Density Matrix** | A generalization of the state vector representation that can describe mixed (statistically uncertain) quantum states, not just pure states. QST's v1.0 scope uses pure-state vectors only (see `22_MATHEMATICAL_FOUNDATION.md` §5 Assumptions); density matrices are not required for the core simulation but are standard vocabulary a contributor extending to noisy/mixed-state simulation (per `20_FUTURE_ENHANCEMENTS.md` noise models) will encounter. | Quantum mechanics (Future relevance) | `22_MATHEMATICAL_FOUNDATION.md`, `20_FUTURE_ENHANCEMENTS.md` |
| **Detection Probability** | A statistical confidence estimate that observed QBER indicates eavesdropping rather than natural noise. | Analytics | `../specs/QBER_SPEC.md` §5 |
| **Eavesdropper (Eve)** | The conventional name for an adversary attempting to intercept and learn the key in a cryptographic protocol; in BB84, modeled via the intercept-resend attack. | Protocol actor / threat model | `../specs/BB84_SPEC.md` §5, `11_SECURITY_ARCHITECTURE.md`, `29_THREAT_MODEL.md` |
| **Entanglement** | A quantum correlation between two or more qubits such that their combined state cannot be described as a product of individual qubit states. Not used in QST's core BB84 simulation (per `22_MATHEMATICAL_FOUNDATION.md` §5) — relevant to Future entanglement-based protocols like E91. | Quantum mechanics (Future relevance) | `22_MATHEMATICAL_FOUNDATION.md` §5, `20_FUTURE_ENHANCEMENTS.md` |
| **Error Correction** | Classical post-processing step reconciling small key mismatches due to channel noise, distinct from QBER sampling. Future scope for QST. | Protocol (Future) | `22_MATHEMATICAL_FOUNDATION.md` §18, `11_SECURITY_ARCHITECTURE.md` §7 |
| **Hilbert Space** | The complex vector space (with inner product) in which quantum states live; a single qubit's Hilbert space is $\mathbb{C}^2$. | Quantum mechanics | `22_MATHEMATICAL_FOUNDATION.md` §5 |
| **Information Leakage** | The amount of information about the final key an eavesdropper could plausibly have gained, bounded via mutual information. | Security theory | `22_MATHEMATICAL_FOUNDATION.md` §16 |
| **Intercept-Resend** | An eavesdropping strategy where Eve measures a qubit and retransmits a newly-prepared qubit based on her measurement outcome, introducing detectable errors. | Attack model | `../specs/BB84_SPEC.md` §5, `11_SECURITY_ARCHITECTURE.md` §3 |
| **Key Rate** | The fraction of raw transmitted qubits that survive to become part of the final shared key. | Analytics | `../specs/QBER_SPEC.md` §3 |
| **Mutual Information** | An information-theoretic measure of shared information between two random variables (e.g., Alice's key and Eve's knowledge of it). | Information theory | `22_MATHEMATICAL_FOUNDATION.md` §16 |
| **No-Cloning Theorem** | A fundamental quantum mechanics result stating an unknown quantum state cannot be copied exactly — the physical basis for BB84's security. | Quantum mechanics | `11_SECURITY_ARCHITECTURE.md` §4, `22_MATHEMATICAL_FOUNDATION.md` §13, `23_REFERENCES.md` [3] |
| **Privacy Amplification** | A classical post-processing step that compresses a partially-known key into a shorter, information-theoretically secret one. Future scope for QST. | Protocol (Future) | `22_MATHEMATICAL_FOUNDATION.md` §17, `11_SECURITY_ARCHITECTURE.md` §7 |
| **QBER (Quantum Bit Error Rate)** | The fraction of sampled sifted-key bits that differ between Alice and Bob, used to detect eavesdropping. | Analytics / security metric | `../specs/QBER_SPEC.md`, `11_SECURITY_ARCHITECTURE.md` §4, `22_MATHEMATICAL_FOUNDATION.md` §14 |
| **Qiskit** | IBM's open-source Python SDK for programming and simulating quantum computers. | Technology | `06_TECHNICAL_REQUIREMENTS.md`, `23_REFERENCES.md` [8] |
| **QKD (Quantum Key Distribution)** | Using quantum mechanics to securely distribute a cryptographic key between two parties. | Protocol category | `00_PROJECT_CONSTITUTION.md` |
| **Qubit** | The fundamental unit of quantum information, a 2-level quantum system capable of superposition. | Quantum mechanics | `22_MATHEMATICAL_FOUNDATION.md` §6 |
| **Shannon Entropy** | A measure of uncertainty/information content in a random variable, foundational to mutual information and privacy amplification calculations. | Information theory | `22_MATHEMATICAL_FOUNDATION.md` §15 |
| **Sifting** | The BB84 step where sender and receiver discard bits measured in mismatched bases, keeping only matched-basis results. | Protocol step | `../specs/BB84_SPEC.md` §1 step 8, `02_PRODUCT_BLUEPRINT.md` §16 |
| **Simulation** | The classical computational modeling of a quantum system's behavior (as opposed to running on real quantum hardware). | Technology | `06_TECHNICAL_REQUIREMENTS.md` §4 |
| **SimulationResult** | QST's canonical return-object type encapsulating a run's outcome (QBER, key rate, final key, etc.). | API contract | `10_API_SPECIFICATION.md` §5, `../specs/EXPORT_SPEC.md` |
| **Statevector** | A complex vector fully describing a pure quantum state; the representation Qiskit Aer's statevector simulator method computes. | Quantum mechanics / simulation | `06_TECHNICAL_REQUIREMENTS.md` §5, `22_MATHEMATICAL_FOUNDATION.md` §6 |
| **Superposition** | A quantum state that is a linear combination of two or more basis states, not definitely any single one until measured. | Quantum mechanics | `22_MATHEMATICAL_FOUNDATION.md` §7 |

## 3. Assumptions

- This glossary is a living document — as `27_CONTRIBUTOR_GUIDE.md` §"How documentation should be updated" specifies, any new technical term introduced in a future PR must be added here in the same PR, not deferred.

## 4. Scope

Terminology reference only. Does not replace the scoped, in-context glossaries already present in `00`, `02`, `05`, `07`, `11`, `22` — this file is the complete cross-document index those partial glossaries feed into.

---

## Implementation Status

| Item | Status |
|---|---|
| This glossary | Current (reflects design-stage terminology; will grow as implementation introduces new terms) |

## Future Improvements

- Auto-generate a linked/cross-referenced HTML version once the documentation is published (e.g., via a static site generator), so each glossary entry links directly to its source document section.

## Document Improvements

This is a new document (v0.1.0), created in Phase 3, consolidating every technical term across the entire suite (previously scattered across five separate per-document glossaries with no single complete index) into one alphabetized reference, per the Round 2 audit's recommendation in `21_DOCUMENTATION_QUALITY_REPORT.md`.
