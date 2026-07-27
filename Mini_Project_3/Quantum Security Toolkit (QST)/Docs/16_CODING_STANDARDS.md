# 16 — Coding Standards

**Version:** 0.2.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Design (Pre-Development — to be enforced from first commit) | **References:** `00_PROJECT_CONSTITUTION.md`

---

## Table of Contents
1. [Naming Conventions](#1-naming-conventions)
2. [Naming Exceptions](#2-naming-exceptions)
3. [Formatting](#3-formatting)
4. [File Size Limits](#4-file-size-limits)
5. [Function Complexity Rules](#5-function-complexity-rules)
6. [Architecture Rules](#6-architecture-rules)
7. [SOLID Application](#7-solid-application)
8. [Clean Code Practices](#8-clean-code-practices)
9. [Documentation Rules](#9-documentation-rules)
10. [Code Review Checklist](#10-code-review-checklist)
11. [Commit Conventions](#11-commit-conventions)
12. [Branch Strategy](#12-branch-strategy)
13. [Assumptions](#13-assumptions)
14. [Scope](#14-scope)
15. [References](#15-references)

---

## 1. Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Modules/files | `snake_case` | `bb84_protocol.py` |
| Classes | `PascalCase` | `BB84Protocol` |
| Functions/variables | `snake_case` | `compute_qber()` |
| Constants | `UPPER_SNAKE_CASE` | `DEFAULT_QUBIT_COUNT` |
| Private members | leading underscore | `_internal_state` |

## 2. Naming Exceptions

- **Physics/protocol-standard abbreviations are exempt from full-word expansion**, since they are more readable and universally recognized in their standard short form: `qber` (not `quantum_bit_error_rate` in variable names — though the latter is fine as a docstring term), `bb84`, `n_qubits` (not `number_of_qubits`), `eve`/`alice`/`bob` as conventional named-actor identifiers in cryptography, retained even though they are proper-noun-style names rather than descriptive ones.
- **Single-letter variables are acceptable only** inside tight, obviously-scoped loops over qubit indices (e.g., `for i in range(n_qubits):`) — never for anything crossing a function boundary.
- **Acronym casing:** acronyms inside `PascalCase` class names stay fully capitalized when they are exactly the conventional term (`BB84Protocol`, not `Bb84Protocol`), but follow normal casing when part of a longer compound word (`QberCalculator` is preferred over `QBERCalculator` if such a class is ever introduced, for readability) — exact casing call is made per-symbol at introduction and then must stay consistent for that symbol's lifetime.

## 3. Formatting

- **Formatter:** `black` (default settings).
- **Linter:** `ruff`.
- **Line length:** 88 characters (black default).
- **Docstrings:** Google-style, required on all public classes/functions.

## 4. File Size Limits

**Planned guideline** (to be enforced via review, not yet via automated tooling — automated enforcement is a Future CI addition):

| File Type | Soft Limit | Hard Limit | Rationale |
|---|---|---|---|
| Core domain module (`core/*.py`) | 300 lines | 500 lines | Keeps security-critical modules (`11_SECURITY_ARCHITECTURE.md` §4) small enough to be reviewed in full during a single PR review pass |
| Other modules (`analytics/`, `visualization/`, `orchestration/`, `cli/`) | 400 lines | 600 lines | Slightly more headroom for orchestration/glue code |
| Test files | No hard limit | — | Thorough test files are encouraged to grow; split by concern (e.g., `test_bb84_core.py` vs. `test_bb84_edge_cases.py`) rather than capped arbitrarily |

Exceeding the hard limit should trigger a refactor-or-justify discussion in the PR, not an automatic block, at the project's current single-maintainer scale.

## 5. Function Complexity Rules

**Planned guideline:**

- Target cyclomatic complexity ≤ 10 per function, measured via `ruff`'s complexity checks (or `radon` as a supplementary tool) once CI exists (`13_DEPLOYMENT.md`).
- Functions in `core/` implementing protocol steps (`prepare_qubits()`, `measure_qubits()`, `sift()`) should be simple enough that their control flow can be manually traced against the BB84 protocol description in `specs/BB84_SPEC.md` (once that spec exists) line-by-line — high complexity in these functions is treated as a security-review red flag, not just a style nit, given `11_SECURITY_ARCHITECTURE.md` §4's critical-correctness note.
- Prefer extracting a named helper function over adding another branch/nesting level once a function exceeds ~4 levels of nested control flow.

## 6. Architecture Rules

- Core domain logic (`core/`) must not import from `visualization/` or `cli/` — dependencies flow one direction only (per the layered architecture in `07_SYSTEM_ARCHITECTURE.md`).
- `analytics/` may depend on `core/`, but not vice versa.
- No module may perform network I/O except an explicitly isolated Future AI integration module (see `08_AI_ARCHITECTURE.md`), which must remain optional and disabled by default.
- These rules mirror and are owned canonically by `07_SYSTEM_ARCHITECTURE.md` §7 (Dependency Rules) — this section restates them here as an enforceable coding standard, not a second independent design decision.

## 7. SOLID Application

| Principle | Applied As |
|---|---|
| Single Responsibility | `BB84Protocol` handles protocol steps only; `SecurityAnalytics` handles metrics only |
| Open/Closed | New protocols (E91, B92 — Future) should be addable via a shared interface without modifying `BB84Protocol` |
| Liskov Substitution | Any future alternate protocol implementation must be substitutable behind a common `Protocol` interface |
| Interface Segregation | `Visualizer` should not require analytics internals it doesn't use |
| Dependency Inversion | `SimulationOrchestrator` depends on abstractions (protocol interface), not concrete `BB84Protocol` directly, to support future protocol plugins |

## 8. Clean Code Practices

- Functions should do one thing; prefer composing small functions over long procedural blocks, especially in `core/` where correctness review matters most (per `11_SECURITY_ARCHITECTURE.md`).
- No magic numbers — protocol constants (e.g., theoretical 25% QBER threshold) must be named constants with a comment referencing the theory.
- Every public function touching security-relevant logic must have a docstring explaining its role in the protocol, not just its parameters.

## 9. Documentation Rules

- Every public class/function requires a Google-style docstring (§3) covering: purpose, parameters, return value, and raised exceptions (cross-referencing `10_API_SPECIFICATION.md` §6 exception types where relevant).
- Any function implementing a specific step of the BB84 protocol must reference the corresponding section of `specs/BB84_SPEC.md` (once created) in its docstring, so a reviewer can check implementation against specification without leaving the code.
- Inline comments should explain **why**, not **what** — the code itself should make the "what" clear; comments earn their place only when the reasoning isn't obvious from the code (e.g., "resend probability is 0.5 here because an intercepted qubit measured in the wrong basis has a 50% chance of being reprepared incorrectly — see 11_SECURITY_ARCHITECTURE.md §4").
- Any change to a module's public interface must be accompanied by a corresponding update to `10_API_SPECIFICATION.md` in the same PR — stale API docs are treated as a review-blocking issue per `00_PROJECT_CONSTITUTION.md` §6.

## 10. Code Review Checklist

**Planned** — self-review checklist at the current single-maintainer stage (per `00_PROJECT_CONSTITUTION.md` §7), to become a PR template once external contributors are onboarded:

- [ ] Does this change keep `core/` free of `visualization/`/`cli/` imports (§6)?
- [ ] Are all new public functions documented per §9?
- [ ] If this touches `BB84Protocol` or `Eavesdropper`, have the §4 regression tests (`11_SECURITY_ARCHITECTURE.md`, `14_TESTING_STRATEGY.md` §3) been run and do they still pass?
- [ ] Are new dependencies pinned and justified (`06_TECHNICAL_REQUIREMENTS.md` §10)?
- [ ] Is test coverage for changed code at or above the relevant target in `14_TESTING_STRATEGY.md` §12?
- [ ] Has any relevant `docs/` file been updated to match this change (no stale documentation, per NFR-4)?
- [ ] Does this introduce any new `TODO`/shortcut that should instead be logged in `15_ROADMAP.md` §8 Technical Debt Backlog?

## 11. Commit Conventions

Conventional Commits format:

```
feat(core): implement BB84 sifting logic
fix(analytics): correct QBER sample-size edge case
docs(11): update threat model after Eve model change
test(core): add QBER regression test for full interception
```

## 12. Branch Strategy

- `main` — always releasable.
- `feature/<short-description>` — feature branches off `main`.
- PRs required before merge; at minimum, self-review checklist (§10) against `00_PROJECT_CONSTITUTION.md` §8 Definition of Done, since the project currently has a single maintainer.

## 13. Assumptions

- Google-style docstrings and Conventional Commits are adopted without further debate, as reasonable, widely-used defaults (see `18_DECISION_LOG.md` if changed).
- File size and complexity limits (§4, §5) are guidelines enforced by review at current scale, becoming automated CI checks only once bandwidth allows building that tooling.

## 14. Scope

Code-level conventions only; process/governance is in `00_PROJECT_CONSTITUTION.md` §7–9.

## 15. References

- `00_PROJECT_CONSTITUTION.md`
- `07_SYSTEM_ARCHITECTURE.md`
- `10_API_SPECIFICATION.md`
- `11_SECURITY_ARCHITECTURE.md`
- `14_TESTING_STRATEGY.md`
- `15_ROADMAP.md`

---

## Implementation Status

| Item | Status |
|---|---|
| Formatter/linter config | To Be Implemented |
| Pre-commit hooks | Planned |
| File size / complexity automated enforcement | Future (manual review for now) |
| Code review checklist | Planned (self-review today; PR template once contributors join) |

## Future Improvements

- Add `pre-commit` hook automation once repository exists.
- Automate file-size/complexity checks in CI once bandwidth allows.

## Document Improvements

This revision (0.2.0) added: Naming Exceptions for physics/protocol terminology (§2), File Size Limits (§4), Function Complexity Rules (§5), Documentation Rules (§9), and a Code Review Checklist (§10). All original content (Naming Conventions, Formatting, Architecture Rules, SOLID, Clean Code, Commit Conventions, Branch Strategy, Assumptions, Scope, References) is preserved unchanged; Architecture Rules (§6) now explicitly notes it mirrors `07_SYSTEM_ARCHITECTURE.md` §7 to avoid duplicated ownership of that decision.
