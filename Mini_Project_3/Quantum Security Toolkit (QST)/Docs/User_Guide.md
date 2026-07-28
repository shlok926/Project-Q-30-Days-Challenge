# QST User Guide

Welcome to the Quantum Security Toolkit (QST) User Guide. QST is designed to help researchers, students, and software engineers understand and simulate Quantum Key Distribution (QKD) BB84 protocols.

## Installation

Install QST directly using `pip` from the local workspace:
```bash
pip install .
```
Or install with plotting/visualization dependencies:
```bash
pip install ".[viz]"
```

## Quick Start Configuration
Create a script to run a noise-free BB84 simulation:

```python
from qst.models.config import SimulationConfig
from qst.orchestration.orchestrator import SimulationOrchestrator

# Configure the protocol settings
config = SimulationConfig(
    n_qubits=20,
    seed=42,
    repetitions=1
)

# Run orchestration execution
orchestrator = SimulationOrchestrator()
result = orchestrator.run_once(config)
trial = result.simulations[0]

print("Sifted Key length:", trial.sifted_key_length)
```

## Advanced Execution
To enable Error Correction and Privacy Amplification:

```python
from qst.models.config import SimulationConfig
from qst.correction.models import CascadeConfiguration
from qst.privacy.models import PrivacyAmplificationConfiguration

config = SimulationConfig(
    n_qubits=30,
    run_error_correction=True,
    cascade_configuration=CascadeConfiguration(block_sizes=(8, 16)),
    run_privacy_amplification=True,
    privacy_configuration=PrivacyAmplificationConfiguration(compression_ratio=0.5)
)
```
Check our `examples/` directory for full examples from basic simulation to QPU execution and final metrics summaries.

---

## 🔗 Quick Links
* 📂 **[Home (README)](../README.md)**
* 📖 **[User Guide](./User_Guide.md)** | **[Architecture Guide](./Architecture.md)** | **[API Reference](./API_Reference.md)**
* 🛠️ **[Troubleshooting](./Troubleshooting.md)** | **[FAQ](./FAQ.md)**
* 📈 **[Benchmark Report](./Benchmark_Report.md)** | **[Roadmap](./Roadmap.md)**
* 💻 **[Developer Guide](./Developer_Guide.md)**
