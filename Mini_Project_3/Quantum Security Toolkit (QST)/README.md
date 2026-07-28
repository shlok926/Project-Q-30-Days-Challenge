# Quantum Security Toolkit (QST)

The **Quantum Security Toolkit (QST)** is a modular, enterprise-grade simulation, analysis, and validation framework for Quantum Key Distribution (QKD) protocols. Built on top of IBM's Qiskit, QST allows security researchers, network engineers, and students to model quantum networks, evaluate the impact of eavesdroppers, and run statistical parameter sweeps in clean, reproducible environments.

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install the dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run a Simple Simulation
You can run a noise-free BB84 simulation trial in Python with just a few lines:
```python
from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator

config = SimulationConfig(
    n_qubits=15,
    seed=42,
    interception_probability=0.0,
    repetitions=1,
    protocol=ProtocolType.BB84
)

orchestrator = SimulationOrchestrator()
result = orchestrator.run_once(config)
trial = result.simulations[0]

print(f"Sifted Key Length: {trial.final_key_length}")
print(f"QBER (Error Rate): {trial.qber}")
print(f"Security Status:   {trial.security_metrics.status.value}")
```

### 3. Run via CLI
Alternatively, execute QST from the command line:
```bash
qst simulate --qubits 15 --seed 42 --interception-probability 0.0 --output outputs.json
```

---

## 📚 Examples & Tutorials

QST includes a set of documented example scripts located in the `examples/` directory.

### Example Feature Matrix

| Script Name | Difficulty | Est. Time | Key Concepts Demonstrated |
| :--- | :--- | :--- | :--- |
| [`01_basic_bb84.py`](./examples/01_basic_bb84.py) | Beginner | 2 mins | Configuration initialization, orchestrator run_once, console reporting |
| [`02_eavesdropper_demo.py`](./examples/02_eavesdropper_demo.py) | Intermediate | 3 mins | Eavesdropping intercepts, quantum state collapse explanation, QBER rise |
| [`03_parameter_sweep.py`](./examples/03_parameter_sweep.py) | Intermediate | 4 mins | Config sweeps generation, sweeps execution, statistical aggregations |
| [`04_export_results.py`](./examples/04_export_results.py) | Intermediate | 3 mins | Serializers, JSONExporter, CSVExporter, schema load verification |
| [`05_visualization.py`](./examples/05_visualization.py) | Intermediate | 4 mins | Visualizer, MatplotlibBackend, themes (Light, Dark, Scientific), multi-format plots (PNG, SVG, PDF) |
| [`06_complete_pipeline.py`](./examples/06_complete_pipeline.py) | Advanced | 5 mins | E2E sweeps, trend analysis, scientific plotting, serialization, JSON/CSV exports |
| [`07_real_hardware_execution.py`](./examples/07_real_hardware_execution.py) | Intermediate | 3 mins | IBM Quantum Runtime execution, backend discovery/selection, and Aer fallback |
| [`08_error_correction.py`](./examples/08_error_correction.py) | Intermediate | 3 mins | Cascade Error Correction integration, key reconciliation metrics, telemetry |
| [`09_privacy_amplification.py`](./examples/09_privacy_amplification.py) | Intermediate | 3 mins | Privacy Amplification, key compression ratio metrics, Min/Shannon Entropy |
| [`10_protocol_summary.py`](./examples/10_protocol_summary.py) | Intermediate | 3 mins | Protocol Finalization, E2E key rates summary, classification levels, and losses |

---

## 📓 Jupyter Notebooks

For interactive, visual tutorials, navigate to the `notebooks/` directory:

1. **[`BB84_Introduction.ipynb`](./notebooks/BB84_Introduction.ipynb):** Introduces Quantum Key Distribution (QKD), BB84 steps (Alice/Bob polarization encoding/measurement, sifting, error estimation), and runs a basic noise-free simulation.
2. **[`Security_Analysis.ipynb`](./notebooks/Security_Analysis.ipynb):** Explains how Eve's intercept-resend attack projects state collapses, causes QBER to increase up to 25%, and graphs QBER vs. Interception Probability.
3. **[`Parameter_Sweeps.ipynb`](./notebooks/Parameter_Sweeps.ipynb):** Demonstrates sweeping parameter grids, running aggregators, performing trend analysis, and saving charts to disk.

To open the notebooks:
```bash
jupyter notebook notebooks/
```

---

## 📂 Expected Output Directory Structure

Examples that generate output files will automatically write to the following relative subfolders inside the `examples/` directory:

```
examples/
├── outputs/
│   ├── csv/          <- Flattened CSV reports (.csv)
│   ├── figures/      <- Generated charts (.png, .svg, .pdf)
│   ├── json/         <- Serialized nested result files (.json)
│   └── logs/         <- Diagnostics execution logs (.log)
```

---

## 🗺️ Recommended Learning Path

To master the QST framework, we recommend developers follow this step-by-step path (approx. 20 minutes total):
1. **BB84 Foundations (5 mins):** Read the `BB84_Introduction.ipynb` notebook and execute `01_basic_bb84.py`.
2. **Security & Eavesdropping (5 mins):** Go through the `Security_Analysis.ipynb` notebook and run `02_eavesdropper_demo.py` to see the effect of measurement collapse on QBER.
3. **Aggregations & Sweps (5 mins):** Run `03_parameter_sweep.py` and review `Parameter_Sweeps.ipynb` to understand multi-trial simulation aggregations.
4. **Production Pipelines & Outputs (5 mins):** Study `04_export_results.py`, `05_visualization.py`, and run the comprehensive script `06_complete_pipeline.py`.
5. **Error Correction (3 mins):** Run `08_error_correction.py` to reconcile keys via Cascade error correction and observe telemetry.
6. **Privacy Amplification (3 mins):** Run `09_privacy_amplification.py` to compress keys and estimate security parameters/entropy.
7. **Protocol Finalization (3 mins):** Run `10_protocol_summary.py` to generate complete protocol summaries and benchmarking losses.
8. **Physical Execution:** Run `07_real_hardware_execution.py` to test physical QPU execution and see graceful fallbacks in action.


## 🛡️ Cascade Error Correction (Phase 13A)

QST includes Phase 13A Cascade Error Correction support. It reconciles transmission noise and eavesdropping errors between Alice's and Bob's sifted keys without compromising raw key data structures.

### Protocol Flow Diagram

```
      Alice
        │
        ▼
  Quantum Transmission
        │
        ▼
       Bob
        │
        ▼
Basis Reconciliation
        │
        ▼
   Key Sifting
        │
        ▼
 QBER Estimation
        │
        ▼
Cascade Error Correction (Phase 13A)
        │
        ▼
Privacy Amplification (Phase 13B)
        │
        ▼
Secret Key Metrics & Summary (Phase 13C)
        │
        ▼
  Final Shared Secret Key
```

### Configuration & Settings
Configure via `SimulationConfig`:
* `run_error_correction` (bool): Activates the reconciler stages when set to `True`.
* `cascade_configuration` (CascadeConfiguration): Overrides default options (block sizes, passes, and seeds):
  ```python
  from qst.correction.models import CascadeConfiguration
  config.cascade_configuration = CascadeConfiguration(
      block_sizes=(4, 8, 16),
      num_passes=4,
      seed=42
  )
  ```

### Reconciled Metrics
The `SimulationResult` exposes metrics in the `error_correction` field:
* `corrected_key`: The finalized, matching binary key.
* `initial_qber`: The raw QBER before error correction.
* `estimated_qber_after_correction`: The remaining error rate (usually `0.0` after Cascade).
* `correction_efficiency`: The ratio of bits disclosed relative to the theoretical Shannon entropy limit.
* `parity_messages_exchanged`: Total messages sent during parity exchanges.
* `communication_rounds`: Communication rounds performed.


## 🔒 Privacy Amplification (Phase 13B)

QST includes Phase 13B Privacy Amplification support. It distills the corrected or sifted key into a cryptographically stronger, shorter final secret key, eliminating any potential information leaked to Eve.

### Extensible Hashing Architecture
Privacy Amplification uses an extensible design:
* **`HashAlgorithm` Interface:** A generic interface defining the contract for hash families.
* **`ToeplitzHasher`:** The default 2-universal hash family implementation. It generates a deterministic $(N \times M)$ Toeplitz matrix from a configured seed to perform modulo-2 matrix multiplication.

### Input Key Routing
Privacy Amplification automatically routes the input key:
1. **Corrected Key (Recommended):** If Cascade Error Correction is enabled (`run_error_correction=True`), the reconciler's corrected output key is processed.
2. **Sifted Key (Fallback):** If Cascade is disabled, it operates directly on the sifted key.

### Configuration & Settings
Configure via `SimulationConfig`:
* `run_privacy_amplification` (bool): Activates the privacy stage when set to `True`.
* `privacy_configuration` (PrivacyAmplificationConfiguration): Configures compression and seed options:
  ```python
  from qst.privacy.models import PrivacyAmplificationConfiguration
  config.privacy_configuration = PrivacyAmplificationConfiguration(
      compression_ratio=0.5,
      hash_algorithm="toeplitz",
      seed=42
  )
  ```

### Cryptographic Telemetry
The final execution metrics are populated on `SimulationResult` under `privacy_result` and `final_secret_key`:
* `final_secret_key.key_bits`: The compressed shared secret key.
* `final_secret_key.min_entropy_estimate` ($H_{\infty}$): Standard metric in QKD security analysis representing the adversary's maximum information capability.
* `final_secret_key.shannon_entropy_estimate`: Standard sample Shannon entropy.
* `statistics.discarded_bits`: Count of bits removed during compression.
* `statistics.compression_percentage`: Key length reduction ratio.
* `statistics.effective_key_rate`: The final compression efficiency.
* `statistics.estimated_security_parameter`: Quantifies trace distance upper bound bounds ($s = \text{discard} - \text{leak}$).


## 📊 Secret Key Metrics & Protocol Finalization (Phase 13C)

QST includes Phase 13C Secret Key Metrics & Protocol Finalization. This stage aggregates metrics from previous protocol stages using dedicated calculators and builders without modifying intermediate key arrays, providing complete execution transparency and benchmark-ready telemetry.

### Metrics & Builders Abstraction
* **`SecretMetricsCalculator`:** A service class that computes key rates and protocol loss parameters relative to raw key size, and classifies the final security level.
* **`ProtocolSummaryBuilder`:** A service class that constructs a summary containing key lengths, execution modes, and success flags.

### Configurable Security Levels
Security levels (`LOW`, `MEDIUM`, `HIGH`) are classified based on the computed trace distance security parameter and configurable thresholds:
* **`SecurityClassificationConfig`:** Configure custom classification boundaries via `SimulationConfig`:
  ```python
  from qst.secret.models import SecurityClassificationConfig
  config.security_classification_thresholds = SecurityClassificationConfig(
      high_threshold=12.0,
      medium_threshold=6.0
  )
  ```

### Metric Calculations
The `SimulationResult` exposes metrics under `protocol_summary`, `secret_key_metrics`, and `security_level`:
* **Rates & Efficiency:**
  - `raw_key_rate`: $1.0$ (or $0.0$ if no raw key populated).
  - `sifted_key_rate`: $\frac{N_{\text{sifted}}}{N_{\text{raw}}}$.
  - `corrected_key_rate`: $\frac{N_{\text{corrected}}}{N_{\text{raw}}}$.
  - `final_secret_key_rate`: $\frac{N_{\text{final}}}{N_{\text{raw}}}$.
  - `overall_efficiency`: Equivalent to the final secret key rate.
* **Loss Benchmarks:**
  - `error_correction_loss`: Disclosed parity bits fraction $\frac{N_{\text{sifted}} - N_{\text{corrected}}}{N_{\text{raw}}}$.
  - `privacy_amplification_loss`: Hashing compression fraction $\frac{N_{\text{corrected}} - N_{\text{final}}}{N_{\text{raw}}}$.
  - `total_protocol_loss`: Total key reduction fraction $\frac{N_{\text{raw}} - N_{\text{final}}}{N_{\text{raw}}}$.

### Sample Console Output
```text
Protocol Summary
------------------------
Raw Key Length:          20
  v
Sifted Key Length:       8
  v
Corrected Key Length:    8
  v
Final Secret Key Length: 4
------------------------
Raw Key Rate:            1.0000
  v
Sifted Key Rate:         0.4000
  v
Corrected Key Rate:      0.4000
  v
Final Key Rate:          0.2000
------------------------
QBER:                    0.0000
Security Parameter:      4.0000
Security Level:          MEDIUM
Execution Backend:       Local Aer
Overall Success:         True
------------------------
```

---

## 🌐 IBM Quantum Runtime Integration

QST includes Phase 12 integration allowing seamless execution on physical IBM Quantum QPUs or remote simulators using Qiskit Runtime Service.

### Authentication Guide
Authenticate by passing your token via configuration parameters or setting up system environment variables:
```bash
# Save to environment variables
export QISKIT_IBM_TOKEN="your_ibm_api_token"
```
QST automatically scans for `QISKIT_IBM_TOKEN` or `IBM_QUANTUM_TOKEN`, falling back to previously saved accounts on the local system if no environment token is supplied.

### Backend Selection
Select the execution target using `SimulationConfig` backend attributes:
* `"best"`: Automatically discovers and routes execution to the least busy operational physical QPU backend on your account.
* `"simulator"`: Routes execution to IBM's remote qasm simulator.
* Explicit Backend Name: Pass a specific backend string (e.g., `backend_name="ibm_brisbane"`).

### Supported Execution Modes
Configured via `SimulationConfig`:
1. **Ideal Simulation (Local):** `use_ibm_runtime=False` (default, executes locally on AerSimulator).
2. **Real Hardware Execution (QPU):** `use_ibm_runtime=True`, `noise_aware_local=False` (transpiles and sends job queues to remote QPU).
3. **Noise-Aware Local Simulation:** `use_ibm_runtime=True`, `noise_aware_local=True` (fetches the physical QPU noise properties and runs a local noise-aware Aer simulation).

### Troubleshooting Common Runtime Errors
* **QST-SIM-301 (Authentication Denied):** Your credentials token is invalid, or the channel cannot be resolved. Check your environment setup.
* **QST-SIM-303 (Backend Selection Error):** The requested device backend is inactive or unauthorized.
* **QST-SIM-304 (QPU execution timeout/cancelled):** Job timed out or was cancelled by the remote queue scheduler. Configure `fallback_to_aer=True` to recover gracefully.
---

## 📖 Documentation

Detailed guides and specifications are available under the `Docs/` directory:
* 📖 **[User Guide](./Docs/User_Guide.md)** — Installation methods, configuration settings, and quick start scripts.
* 📐 **[Architecture Guide](./Docs/Architecture.md)** — Core module designs and end-to-end QKD pipeline data flows.
* 📝 **[API Reference](./Docs/API_Reference.md)** — Configuration dataclasses and orchestrator/service method signatures.
* 🛠️ **[Troubleshooting](./Docs/Troubleshooting.md)** — Diagnostic steps for `QST-VAL-*` and `QST-SIM-*` error codes.
* 📊 **[Benchmark Report](./Docs/Benchmark_Report.md)** — Execution timings, memory usage statistics, and reproducibility baselines.
* 📅 **[Future Roadmap](./Docs/Roadmap.md)** — Completed phases milestones and target feature roadmap for subsequent versions.
* ❓ **[FAQ](./Docs/FAQ.md)** — Frequently asked questions regarding local simulator bounds and customization plugins.

---

## 🛠️ Common Troubleshooting

* **Qiskit Aer Simulator crash:**
  - *Cause:* `qiskit-aer` is missing or binary compilation is incompatible with your system configuration.
  - *Resolution:* Install qiskit-aer via `pip install qiskit-aer` or verify setup by executing `import qiskit_aer` in a python shell.
* **Validation Error (QST-VAL-101):**
  - *Cause:* Qubit count count is set to zero or a negative number.
  - *Resolution:* Double-check the parameter and pass positive integers for qubit sizes (e.g. `n_qubits=20`).
* **Overwrite Protection Error (QST-VAL-402 or QST-VAL-602):**
  - *Cause:* Exporters reject writing files if output paths already have content.
  - *Resolution:* Pass `overwrite_protection=False` to the exporter initialization (e.g., `JSONExporter(overwrite_protection=False)`).
* **Missing PDF or SVG backends:**
  - *Cause:* Local Matplotlib library doesn't contain dependencies for vectorial exports.
  - *Resolution:* Upgrade matplotlib via `pip install --upgrade matplotlib`.

---

## 📅 Project Roadmap

Below is a summary of the completed development milestones and the target roadmap for upcoming releases:

### Completed Milestones
* **[x] Core Framework:** Immutable domain results models, configuration validators, and exception hierarchies.
* **[x] BB84 Protocol:** Alice/Bob states preparation, basis reconciliation, key sifting, QBER estimation.
* **[x] CLI Engine:** simulate, sweep, export, and visualize subcommands execution.
* **[x] Visualization:** Custom styling themes (Light, Dark, Scientific) and MatplotlibBackend.
* **[x] Integration & E2E Testing:** Deterministic golden schema checks, math invariants property tests, regression performance benchmarks.
* **[x] Examples & Tutorials:** 10 python example scripts, 3 Jupyter notebooks, output auto-routing.
* **[x] IBM Quantum Runtime Integration (Phase 12):** Real physical QPU execution support, least-busy selection, noise-aware simulation, and automatic Aer fallbacks.
* **[x] Cascade Error Correction (Phase 13A):** Recursive Cascade parity reconciliation algorithm.
* **[x] Privacy Amplification (Phase 13B):** Extensible 2-universal hashing with Toeplitz algorithm and entropy bounds calculations.
* **[x] Secret Key Metrics & Protocol Finalization (Phase 13C):** Multi-stage calculators and summary builders, configurable classification levels, and benchmarking losses.

### Future Roadmap (Coming Soon)
* **[ ] Release & Packaging (Phase 14):** PyPI package deployment, public GitHub releases, and production v1.0.0 tag.

---

## 🤝 Contributing

We welcome contributions to the Quantum Security Toolkit! Please read our [Contributing Guide](./CONTRIBUTING.md) and [Code of Conduct](./CODE_OF_CONDUCT.md) for details on our code style, formatting, testing requirements, and pull request submission process.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🏷️ Citation

If you use QST in your research, please cite the toolkit using the citation metadata defined in [CITATION.cff](./CITATION.cff).
