# Contributing to Quantum Security Toolkit (QST)

Thanks for your interest in contributing! This is the short, practical guide to submitting a change. For the deeper engineering reasoning behind these steps, see [`docs/27_CONTRIBUTOR_GUIDE.md`](docs/27_CONTRIBUTOR_GUIDE.md) — this file is the "how," that one is the "why."

> **Project stage:** QST is currently pre-development — a complete documentation suite (`docs/00`–`32`) and implementation contracts (`specs/`) exist, but no code has been written yet (see [`docs/01_REPOSITORY_AUDIT.md`](docs/01_REPOSITORY_AUDIT.md)). Early contributions are especially valuable in shaping the first implementation against these specs.

## Before You Start

1. Read [`docs/00_PROJECT_CONSTITUTION.md`](docs/00_PROJECT_CONSTITUTION.md) — the project's core principles and Definition of Done.
2. Check the [`docs/15_ROADMAP.md`](docs/15_ROADMAP.md) to see what phase is currently active.
3. If you're implementing a spec'd component, read its corresponding `specs/*.md` file in full first — it's the contract your code should satisfy.
4. For anything not already covered by an open issue, please open one before starting significant work, so effort isn't duplicated.

## How to Contribute

1. Fork the repository and create a branch: `feature/<short-description>` (see [`docs/16_CODING_STANDARDS.md`](docs/16_CODING_STANDARDS.md) §12).
2. Make your change, following:
   - [`docs/16_CODING_STANDARDS.md`](docs/16_CODING_STANDARDS.md) for style, naming, and complexity guidelines.
   - The relevant `specs/*.md` contract if you're implementing core functionality.
3. Add or update tests per [`docs/14_TESTING_STRATEGY.md`](docs/14_TESTING_STRATEGY.md). Changes to `core/` (BB84Protocol, Eavesdropper) **require** the regression tests described in `docs/11_SECURITY_ARCHITECTURE.md` §4 to still pass — these are treated as blocking, not optional.
4. Update any `docs/` or `specs/` file affected by your change, in the same PR (see [`docs/00_PROJECT_CONSTITUTION.md`](docs/00_PROJECT_CONSTITUTION.md) §6 Documentation Standards). If nothing needs updating, say so explicitly in your PR description.
5. Run the self-review checklist in [`docs/16_CODING_STANDARDS.md`](docs/16_CODING_STANDARDS.md) §10 before opening your PR.
6. Use [Conventional Commits](https://www.conventionalcommits.org/) format (e.g., `feat(core): implement BB84 sifting logic`).
7. Open a pull request using the PR template — it will walk you through the same checklist.

## Commit & PR Conventions

See [`docs/16_CODING_STANDARDS.md`](docs/16_CODING_STANDARDS.md) §11–§12 for the authoritative commit message format and branch naming convention.

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## Reporting Security Issues

**Do not open a public issue for security vulnerabilities.** See [`SECURITY.md`](SECURITY.md) for the private reporting process.

## Questions?

Open a [GitHub Discussion](https://github.com/OWNER/quantum-security-toolkit/discussions) using the Q&A category, or use the `question` issue template if you're unsure whether something is a bug.

## A Note on Documentation Quality

This project is documentation-first by design (see [`docs/27_CONTRIBUTOR_GUIDE.md`](docs/27_CONTRIBUTOR_GUIDE.md) §2). We take "no fabricated claims" seriously — please mark anything you're not fully certain about as `Planned`/`Future`/`To Be Implemented` rather than stating it as done, consistent with the labeling convention used throughout `docs/`.
