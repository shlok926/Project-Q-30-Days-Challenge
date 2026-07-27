# Security Policy

This file operationalizes the Responsible Disclosure Workflow already designed in [`docs/11_SECURITY_ARCHITECTURE.md`](docs/11_SECURITY_ARCHITECTURE.md) §11. See that document for the full rationale; this file is the actionable, repo-root version GitHub and security researchers look for by convention.

## Supported Versions

QST is currently pre-development (see [`docs/01_REPOSITORY_AUDIT.md`](docs/01_REPOSITORY_AUDIT.md)) — no versions have been released yet. Once released, supported versions will follow the policy in [`docs/06_TECHNICAL_REQUIREMENTS.md`](docs/06_TECHNICAL_REQUIREMENTS.md) §8 (a rolling two-minor-version support window).

| Version | Supported |
|---|---|
| Pre-release / unreleased | N/A — no public release exists yet |

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead:

1. Report privately via a [GitHub Security Advisory](../../security/advisories/new) on this repository, or by emailing the maintainer (contact to be published once the repository is live).
2. Include, if possible: the affected version/commit, a description of the vulnerability, and reproduction steps.
3. Given QST's architecture (an offline, local Python library with no network component — see [`docs/11_SECURITY_ARCHITECTURE.md`](docs/11_SECURITY_ARCHITECTURE.md) §6 STRIDE analysis), realistic vulnerability classes are expected to be **dependency-related** (a CVE in Qiskit or a transitive dependency) or **resource-exhaustion** (unbounded qubit-count inputs) rather than data breaches — but all reports are welcome.

## Response Targets

As a solo-maintainer project (see [`docs/17_RISK_REGISTER.md`](docs/17_RISK_REGISTER.md) P-1), response times are best-effort:

- Acknowledgment: best-effort within 7 days.
- Fix or mitigation plan: timeline communicated after initial triage, depending on severity.

## Disclosure Process

1. Report received and acknowledged privately.
2. Vulnerability confirmed and a fix developed.
3. Fix released as a patch version.
4. A GitHub Security Advisory is published describing the issue, with credit to the reporter (unless anonymity is requested) — following standard coordinated disclosure norms.

## Supply Chain Security

QST's dependency-scanning approach (`pip-audit` in CI, pinned versions, SBOM publication alongside releases) is described in [`docs/11_SECURITY_ARCHITECTURE.md`](docs/11_SECURITY_ARCHITECTURE.md) §10. If you discover a vulnerability in a QST dependency rather than in QST itself, please still report it here so we can assess and respond (e.g., by pinning to a patched version) even if the fix originates upstream.

## Scope Note

QST is an educational/research simulator, not a production key-distribution system (see [`docs/11_SECURITY_ARCHITECTURE.md`](docs/11_SECURITY_ARCHITECTURE.md) §12). It does not handle real cryptographic keys or sensitive user data. Please keep this scope in mind when assessing severity.
