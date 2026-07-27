# 19 — Release Plan

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `15_ROADMAP.md`

---

## Table of Contents
1. [Versioning Scheme](#1-versioning-scheme)
2. [v0.1 — Internal Core](#2-v01--internal-core)
3. [v0.5 — Feature Complete Pre-Release](#3-v05--feature-complete-pre-release)
4. [v1.0 — Public Release](#4-v10--public-release)
5. [v2.0 — Extended Toolkit](#5-v20--extended-toolkit)
6. [Assumptions](#6-assumptions)
7. [Scope](#7-scope)
8. [References](#8-references)

---

## 1. Versioning Scheme

Semantic Versioning (`MAJOR.MINOR.PATCH`), standard for Python packages.

## 2. v0.1 — Internal Core

- Maps to Roadmap Phase 1 (`15_ROADMAP.md` §2).
- Not published to PyPI — dev/internal only.
- **Features:** `BB84Protocol`, `Eavesdropper`, `SecurityAnalytics` core.

## 3. v0.5 — Feature Complete Pre-Release

- Maps to Roadmap Phase 2.
- **Features:** Visualization, Educational Mode.
- Distributed as a GitHub pre-release / TestPyPI for early feedback.

## 4. v1.0 — Public Release

- Maps to Roadmap Phase 3.
- **Features:** Research/Batch Mode, CI/CD, PyPI publication.
- **Definition of "done" for v1.0:** All Must/Should FRs in `05_PRODUCT_REQUIREMENTS.md` implemented and tested; documentation suite (this `docs/` folder) updated to reflect actual implementation, replacing "Planned" statuses with "Current" where true.

## 5. v2.0 — Extended Toolkit

- Scope drawn from `20_FUTURE_ENHANCEMENTS.md`: additional protocols (E91, B92), optional AI Tutor, web dashboard.
- Not committed — contingent on v1.0 adoption and maintainer bandwidth (`17_RISK_REGISTER.md` P-1).

## 6. Assumptions

- No fixed calendar dates are committed, consistent with a solo-maintainer, non-commercial project.

## 7. Scope

Release contents and sequencing only; day-to-day task sequencing is in `15_ROADMAP.md`.

## 8. References

- `15_ROADMAP.md`
- `20_FUTURE_ENHANCEMENTS.md`
- `05_PRODUCT_REQUIREMENTS.md`

---

## Implementation Status

| Version | Status |
|---|---|
| v0.1 | Not started |
| v0.5 | Not started |
| v1.0 | Not started |
| v2.0 | Future |

## Future Improvements

- Add calendar-based release cadence once v0.1 velocity is known.
