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
| [`01_basic_bb84.py`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/examples/01_basic_bb84.py) | Beginner | 2 mins | Configuration initialization, orchestrator run_once, console reporting |
| [`02_eavesdropper_demo.py`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/examples/02_eavesdropper_demo.py) | Intermediate | 3 mins | Eavesdropping intercepts, quantum state collapse explanation, QBER rise |
| [`03_parameter_sweep.py`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/examples/03_parameter_sweep.py) | Intermediate | 4 mins | Config sweeps generation, sweeps execution, statistical aggregations |
| [`04_export_results.py`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/examples/04_export_results.py) | Intermediate | 3 mins | Serializers, JSONExporter, CSVExporter, schema load verification |
| [`05_visualization.py`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/examples/05_visualization.py) | Intermediate | 4 mins | Visualizer, MatplotlibBackend, themes (Light, Dark, Scientific), multi-format plots (PNG, SVG, PDF) |
| [`06_complete_pipeline.py`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/examples/06_complete_pipeline.py) | Advanced | 5 mins | E2E sweeps, trend analysis, scientific plotting, serialization, JSON/CSV exports |
| [`07_real_hardware_execution.py`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/examples/07_real_hardware_execution.py) | Intermediate | 3 mins | IBM Quantum Runtime execution, backend discovery/selection, and Aer fallback |

---

## 📓 Jupyter Notebooks

For interactive, visual tutorials, navigate to the `notebooks/` directory:

1. **[`BB84_Introduction.ipynb`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/notebooks/BB84_Introduction.ipynb):** Introduces Quantum Key Distribution (QKD), BB84 steps (Alice/Bob polarization encoding/measurement, sifting, error estimation), and runs a basic noise-free simulation.
2. **[`Security_Analysis.ipynb`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/notebooks/Security_Analysis.ipynb):** Explains how Eve's intercept-resend attack projects state collapses, causes QBER to increase up to 25%, and graphs QBER vs. Interception Probability.
3. **[`Parameter_Sweeps.ipynb`](file:///d:/Downloads/Project%20-%20Q%2030%20%28Day%29/Mini_Project_3/Quantum%20Security%20Toolkit%20%28QST%29/notebooks/Parameter_Sweeps.ipynb):** Demonstrates sweeping parameter grids, running aggregators, performing trend analysis, and saving charts to disk.

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
5. **Looking Ahead:** Run `07_real_hardware_execution.py` to test physical QPU execution and see graceful fallbacks in action.

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
* **[x] Examples & Tutorials:** 7 python example scripts, 3 Jupyter notebooks, output auto-routing.
* **[x] IBM Quantum Runtime Integration (Phase 12):** Real physical QPU execution support, least-busy selection, noise-aware simulation, and automatic Aer fallbacks.

### Future Roadmap (Coming Soon)
* **[ ] Privacy Amplification (Phase 13):** Toeplitz matrix hashing and hashing extraction algorithms for secure key distillation.
* **[ ] Error Correction (Phase 13):** Cascade and LDPC reconciliation coding to correct channel noise.
* **[ ] Secure Key Generation (Phase 13):** Production-ready symmetric key exports.
* **[ ] Release & Packaging (Phase 14):** PyPI package deployment, public GitHub releases, and production v1.0.0 tag.
