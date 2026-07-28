# QST FAQ Guide

Common questions about the Quantum Security Toolkit (QST).

## General Questions

### What is the primary purpose of QST?
QST is an educational and scientific simulation framework to demonstrate, analyze, and research the BB84 Quantum Key Distribution protocol. It implements all post-sifting processing steps (Cascade Error Correction, universal Toeplitz Privacy Amplification) to model end-to-end security pipelines.

### Does QST execute on physical quantum computers?
Yes. QST provides integration with IBM Quantum systems using the Qiskit Runtime Service. You can run simulations on remote QPUs by supplying your API token or local saved accounts.

### What are the limits of local simulation sizes?
Local statevector simulation via `AerSimulator` is bounded by your machine's CPU/memory and the target backend's transpiler coupling maps (typically bounded to 29 qubits on standard simulators). We recommend using sizes $N \le 25$ for local trials.

### Can I add other error correction or hashing algorithms?
Yes. QST uses extensible abstraction interfaces. You can implement the `HashAlgorithm` interface to introduce alternative hashing families or add other error correction backends.

---

## 🔗 Quick Links
* 📂 **[Home (README)](../README.md)**
* 📖 **[User Guide](./User_Guide.md)** | **[Architecture Guide](./Architecture.md)** | **[API Reference](./API_Reference.md)**
* 🛠️ **[Troubleshooting](./Troubleshooting.md)** | **[FAQ](./FAQ.md)**
* 📈 **[Benchmark Report](./Benchmark_Report.md)** | **[Roadmap](./Roadmap.md)**
* 💻 **[Developer Guide](./Developer_Guide.md)**
