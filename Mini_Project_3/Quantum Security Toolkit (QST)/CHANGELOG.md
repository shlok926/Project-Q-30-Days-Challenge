# Changelog

All notable changes to the Quantum Security Toolkit (QST) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-07-28

### Added
- **Core BB84 Simulation Engine:** Polarization encoding/measurement, quantum state collapse, and local Aer/QPU execution routing.
- **Eve Interception Layer:** Simulation of eavesdropping collapse with custom probabilities and base measurement intercepts.
- **Sifting & Reconciliation:** Basis reconciliation, sifted key generation, and QBER estimation.
- **Cascade Error Correction (Phase 13A):** Recursive multi-pass Cascade error correction protocol to reconcile transmission errors without altering original key data structures.
- **Privacy Amplification (Phase 13B):** 2-universal Toeplitz matrix hashing to compress corrected keys and calculate mathematical Min-Entropy ($H_{\infty}$) bounds.
- **Metrics & Summaries (Phase 13C):** Dedicated `SecretMetricsCalculator` and `ProtocolSummaryBuilder` classes compiling final key rates, protocol losses, and configurable security level classifications.
- **IBM Quantum Runtime Integration (Phase 12):** Execute BB84 simulations on real remote physical QPUs with Aer executor fallback capabilities.
- **Scientific Visualization:** Custom light, dark, and scientific themes supporting PNG, SVG, and PDF exports.
- **CLI Engine:** Executables to simulate, sweep, visualize, and export trial batches.

### Changed
- Standardized file path parsing using `pathlib` across all executors and exporters.
- Decoupled business logic calculations from `SimulationOrchestrator` using service abstractions.

### Migration Notes
- Initial stable production release. No migration required from previous versions.
