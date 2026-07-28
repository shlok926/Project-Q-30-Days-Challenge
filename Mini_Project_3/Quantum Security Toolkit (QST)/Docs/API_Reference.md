# QST API Reference Guide

This document lists the frozen public API signatures for the v1.0.0 release of the Quantum Security Toolkit (QST).

## Core Configuration & Models
### `SimulationConfig`
Frozen configuration parameter dataclass:
* `n_qubits: int`: Number of qubits simulated.
* `seed: Optional[int]`: Pseudo-random generation seed.
* `interception_probability: float`: Probability of Eve intercepting qubits.
* `repetitions: int`: repetitions run count.
* `protocol: ProtocolType`: Protocol selector (default: `ProtocolType.BB84`).
* `use_ibm_runtime: bool`: Enable IBM QPU backend (default: `False`).
* `noise_aware_local: bool`: Run local Aer simulation with fetched hardware noise.
* `run_error_correction: bool`: Enable Cascade Error Correction.
* `cascade_configuration: Optional[CascadeConfiguration]`: Reconciler settings.
* `run_privacy_amplification: bool`: Enable Privacy Amplification.
* `privacy_configuration: Optional[PrivacyAmplificationConfiguration]`: Matrix parameters.
* `security_classification_thresholds: Optional[SecurityClassificationConfig]`: Security level classification boundaries.

### `SimulationResult`
Frozen simulation trial outcome data container:
* `raw_key: list[int]`: Bob's raw bits.
* `sifted_key: list[int]`: Sifted key bits after basis comparison.
* `corrected_key: list[int]`: Error reconciled key bits.
* `final_secret_key: FinalSecretKey`: Compressed shared secret key object.
* `protocol_summary: ProtocolSummary`: Protocol snapshot.
* `secret_key_metrics: SecretKeyMetrics`: Performance benchmarks and loss percentages.
* `security_level: SecurityLevel`: classified security classification.

## Execution Services
### `SimulationOrchestrator`
Lifecycle coordination wrapper:
* `run_once(config: SimulationConfig) -> ExperimentResult`
* `run_many(config: SimulationConfig) -> ExperimentResult`
* `run_parameter_sweep(configs: list[SimulationConfig], dimensions: SweepDimensions) -> SweepResult`

### `SecretMetricsCalculator`
* `calculate_metrics(raw_len, sifted_len, corrected_len, final_len, security_parameter) -> SecretKeyMetrics`
* `classify_security_level(security_parameter) -> SecurityLevel`

### `ProtocolSummaryBuilder`
* `build_summary(raw_len, sifted_len, corrected_len, final_len, qber, correction_enabled, privacy_enabled, overall_success, execution_mode) -> ProtocolSummary`

---

## 🔗 Quick Links
* 📂 **[Home (README)](../README.md)**
* 📖 **[User Guide](./User_Guide.md)** | **[Architecture Guide](./Architecture.md)** | **[API Reference](./API_Reference.md)**
* 🛠️ **[Troubleshooting](./Troubleshooting.md)** | **[FAQ](./FAQ.md)**
* 📈 **[Benchmark Report](./Benchmark_Report.md)** | **[Roadmap](./Roadmap.md)**
* 💻 **[Developer Guide](./Developer_Guide.md)**
