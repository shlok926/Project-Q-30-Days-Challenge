# 23 — References

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Reference | **References:** `22_MATHEMATICAL_FOUNDATION.md`, `11_SECURITY_ARCHITECTURE.md`

---

## Table of Contents
1. [Purpose](#1-purpose)
2. [Books](#2-books)
3. [Research Papers](#3-research-papers)
4. [IBM Quantum & Qiskit Documentation](#4-ibm-quantum--qiskit-documentation)
5. [Standards Bodies (NIST, ETSI, IEEE, RFC)](#5-standards-bodies-nist-etsi-ieee-rfc)
6. [arXiv Preprints](#6-arxiv-preprints)
7. [Assumptions](#7-assumptions)
8. [Scope](#8-scope)

---

## 1. Purpose

Central citation registry for the whole documentation suite. Every reference used anywhere in `docs/` or `specs/` should be listed exactly once here, with full bibliographic detail — other documents cite it by short label (e.g., "[1] Nielsen & Chuang") and link back here, rather than repeating full citation metadata.

> **Note on verification:** Bibliographic details below (author names, years, DOIs) reflect well-established, canonical works in quantum computing/QKD. Exact page numbers, edition numbers, and DOIs should be verified against the physical/digital source at time of actual citation in a publication — this registry is a documentation aid, not a legally verified citation database, and any DOI/URL should be re-checked before external publication use.

## 2. Books

### [1] Nielsen & Chuang — *Quantum Computation and Quantum Information*

- **APA:** Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information* (10th Anniversary ed.). Cambridge University Press.
- **BibTeX:**
```bibtex
@book{nielsen2010quantum,
  title={Quantum Computation and Quantum Information},
  author={Nielsen, Michael A. and Chuang, Isaac L.},
  edition={10th Anniversary},
  year={2010},
  publisher={Cambridge University Press}
}
```
- **Purpose:** The standard graduate-level reference for the linear algebra, Dirac notation, and measurement postulates underlying QST's simulation.
- **Used in:** `22_MATHEMATICAL_FOUNDATION.md` §2–§11.

## 3. Research Papers

### [2] Shor & Preskill — Simple Proof of Security of the BB84 QKD Protocol

- **APA:** Shor, P. W., & Preskill, J. (2000). Simple proof of security of the BB84 quantum key distribution protocol. *Physical Review Letters*, 85(2), 441–444.
- **DOI:** 10.1103/PhysRevLett.85.441
- **BibTeX:**
```bibtex
@article{shor2000simple,
  title={Simple proof of security of the {BB84} quantum key distribution protocol},
  author={Shor, Peter W. and Preskill, John},
  journal={Physical Review Letters},
  volume={85},
  number={2},
  pages={441--444},
  year={2000}
}
```
- **Purpose:** Canonical unconditional-security proof for BB84.
- **Used in:** `22_MATHEMATICAL_FOUNDATION.md` §13, §19.

### [3] Wootters & Zurek — A Single Quantum Cannot Be Cloned

- **APA:** Wootters, W. K., & Zurek, W. H. (1982). A single quantum cannot be cloned. *Nature*, 299(5886), 802–803.
- **DOI:** 10.1038/299802a0
- **Purpose:** Original statement of the no-cloning theorem, the physical basis for BB84's eavesdropper-detectability claim.
- **Used in:** `22_MATHEMATICAL_FOUNDATION.md` §13; `11_SECURITY_ARCHITECTURE.md` §4.

### [4] Impagliazzo, Levin & Luby — Pseudo-random Generation from One-way Functions (Leftover Hash Lemma origin)

- **APA:** Impagliazzo, R., Levin, L. A., & Luby, M. (1989). Pseudo-random generation from one-way functions. *Proceedings of the 21st Annual ACM Symposium on Theory of Computing*, 12–24.
- **DOI:** 10.1145/73007.73009
- **Purpose:** Foundational leftover hash lemma underlying privacy amplification.
- **Used in:** `22_MATHEMATICAL_FOUNDATION.md` §17.

### [5] Mayers — Unconditional Security in Quantum Cryptography

- **APA:** Mayers, D. (2001). Unconditional security in quantum cryptography. *Journal of the ACM*, 48(3), 351–406.
- **DOI:** 10.1145/382780.382781
- **Purpose:** First complete unconditional-security proof of BB84.
- **Used in:** `22_MATHEMATICAL_FOUNDATION.md` §19.

### [6] Renner — Security of Quantum Key Distribution

- **APA:** Renner, R. (2005). *Security of quantum key distribution* [Doctoral dissertation, ETH Zurich]. arXiv:quant-ph/0512258.
- **arXiv:** quant-ph/0512258
- **Purpose:** Modern security-proof framework via smooth min-entropy, standard reference for privacy amplification bounds.
- **Used in:** `22_MATHEMATICAL_FOUNDATION.md` §17, §19.

### [7] Bennett & Brassard — Quantum Cryptography: Public Key Distribution and Coin Tossing

- **APA:** Bennett, C. H., & Brassard, G. (1984). Quantum cryptography: Public key distribution and coin tossing. *Proceedings of IEEE International Conference on Computers, Systems and Signal Processing*, 175–179.
- **Purpose:** The original BB84 paper — foundational primary source for the entire protocol QST simulates.
- **Used in:** `00_PROJECT_CONSTITUTION.md` (glossary "BB84"), `../specs/BB84_SPEC.md`, `22_MATHEMATICAL_FOUNDATION.md`.

## 4. IBM Quantum & Qiskit Documentation

### [8] Qiskit Documentation

- **APA:** IBM Quantum. (n.d.). *Qiskit documentation*. Retrieved 2026, from https://docs.quantum.ibm.com
- **Purpose:** Primary reference for the Qiskit/Qiskit Aer API surface QST's `core/` module targets.
- **Used in:** `06_TECHNICAL_REQUIREMENTS.md`, `../specs/BB84_SPEC.md` §3.
- **Verification note:** Exact API signatures referenced in `../specs/BB84_SPEC.md` §3 are marked "To Be Verified" against the pinned Qiskit version at implementation time — this reference should be re-checked against the live docs at that point, since Qiskit's API surface evolves across versions (see `06_TECHNICAL_REQUIREMENTS.md` §7 Compatibility Matrix).

## 5. Standards Bodies (NIST, ETSI, IEEE, RFC)

> **Status: Contextual/Future.** QST does not currently implement or claim conformance to any of the standards below — they are listed as landscape context relevant to `04_MARKET_RESEARCH.md` and as forward references for Future work (e.g., if QST ever adds post-quantum cryptography comparison content, per `20_FUTURE_ENHANCEMENTS.md`).

| Body | Relevant Work | Relevance to QST |
|---|---|---|
| NIST | Post-Quantum Cryptography Standardization Project | Adjacent, complementary domain (classical PQC, not QKD) — noted in `04_MARKET_RESEARCH.md` §2 as a distinct but related trend; no direct dependency |
| ETSI | ETSI GS QKD specifications (QKD system/interface standards) | Relevant to *real-hardware* QKD deployment, not to QST's simulator-only v1.0 scope (`06_TECHNICAL_REQUIREMENTS.md` §4) — Future reference if real-hardware execution is added |
| IEEE | General quantum computing standardization efforts (e.g., IEEE P7130 series) | Contextual only — QST does not currently target conformance with any specific IEEE standard |
| RFC | No directly applicable RFC identified for BB84/QKD specifically (RFCs govern classical network protocols, not the quantum layer) | Not applicable to QST's core scope |

Exact document numbers/titles for the above should be looked up and cited precisely (with DOI/URL) at the time any Future feature actually depends on them — placeholder-level detail here is intentional, per the "no fabrication" principle, rather than inventing precise citation numbers not yet verified.

## 6. arXiv Preprints

See [6] Renner above (quant-ph/0512258). Additional arXiv preprints should be added here as they are actually cited in future revisions of `22_MATHEMATICAL_FOUNDATION.md` or elsewhere — this section is intentionally not pre-populated with speculative citations.

## 7. Assumptions

- Citation details (author names, years, journal/volume info) reflect standard, well-known bibliographic facts about foundational quantum computing literature. DOIs are included where confidently known and should be spot-checked before external/formal publication use.

## 8. Scope

Bibliographic reference only. Does not constitute legal citation advice or a substitute for verifying exact publication details before formal academic use.

---

## Implementation Status

| Item | Status |
|---|---|
| Reference registry (this document) | Current |
| Standards-body conformance claims | Not applicable — contextual only, no conformance claimed |

## Future Improvements

- Add specific NIST/ETSI document numbers with verified DOIs if/when a Future feature (e.g., PQC comparison content, real-hardware QKD execution) actually depends on them.

## Document Improvements

This is a new document (v0.1.0), created in Phase 3. It centralizes citation metadata that `22_MATHEMATICAL_FOUNDATION.md` references by short label, avoiding duplicated bibliographic detail across documents.
