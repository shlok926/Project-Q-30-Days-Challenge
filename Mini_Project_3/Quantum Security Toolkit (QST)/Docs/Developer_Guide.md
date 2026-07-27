# QST Developer Guide

This document describes conventions, formatting, testing, and contribution policies for developers extending QST.

## API Stability Policy
QST adheres to [Semantic Versioning (SemVer)](https://semver.org/). We divide our code surfaces into distinct categories to preserve API compatibility:

* **Stable APIs (`qst.core.*`, `qst.orchestration.*`, `qst.models.*`, `qst.secret.*`, `qst.privacy.*`):**
  - Guaranteed backward compatibility across all `v1.x` release cycles.
  - Breaking changes are strictly forbidden in minor/patch releases and will only occur at major version bumps (e.g. `v2.0.0`).
* **Experimental APIs (marked with `@experimental` docstring):**
  - Exposed for early feature trials or research feedback.
  - May modify signature, parameters, or behaviors in minor releases.
* **Internal APIs (`qst.core.shared.*`):**
  - Exclusively for internal execution, testing, or code sharing.
  - No backward compatibility guarantees.

## Coding Style & Format
We enforce automated code styling to maintain repository consistency:
- **Formatter:** `black`
- **Linter:** `ruff`
- **Type Checker:** `mypy`

Command execution:
```bash
black src/ tests/
ruff check src/
mypy src/
```

## Testing Requirements
All commits must maintain or exceed test coverage targets ($\ge 95\%$ aggregate coverage).
Ensure you run and pass all test suites before raising a Pull Request:
```bash
python -m pytest
```
Tests are structured under `tests/` into `unit/`, `integration/`, `property/`, and `performance/` suites.
