# QST Architecture Guide

This document describes the software design and protocol pipeline of the Quantum Security Toolkit (QST) v1.0.0.

## Complete Protocol Pipeline Flow
The execution flow from raw quantum transmission to a verified shared key:

```
        Alice (Sender)                      Bob (Receiver)
              │                                    │
              ▼                                    ▼
       Polarization Bases ──────────────────► Polarization Measurement
              │                                    │
              ▼                                    ▼
      [Basis Reconciliation] ◄──────────────► [Basis Reconciliation]
              │                                    │
              ▼                                    ▼
         Sifted Keys ◄────────────────────────► Sifted Keys
              │                                    │
              ▼                                    ▼
        QBER Estimation ◄────────────────────► QBER Estimation
              │                                    │
              ▼                                    ▼
     Cascade Error Correction ◄──────────────► Cascade Error Correction
              │                                    │
              ▼                                    ▼
        Corrected Key                        Corrected Key
              │                                    │
              ▼                                    ▼
     Privacy Amplification ────────────────► Privacy Amplification
              │                                    │
              ▼                                    ▼
        Final Secret Key                     Final Secret Key
```

## Module Responsibilities
* **`qst.core`**: Quantum circuit builders, eavesdropping simulation, basis reconciliation, and key sifting.
* **`qst.correction`**: Parity calculations, block partitioning, binary search, and recursive Cascade feedback reconciliation loops.
* **`qst.privacy`**: Extensible universal hashing algorithms interface, Toeplitz diagonal generation, and Min-Entropy estimations.
* **`qst.secret`**: Rate/loss benchmarks, security level classifiers, and protocol summaries builders.
* **`qst.orchestration`**: Coordination of executors, sweep generators, and batch simulations.
* **`qst.reporting`**: Serialization formatters, CSV/JSON file exporters.
* **`qst.visualization`**: Custom plot styling backend registry and multi-format exporters.
* **`qst.cli`**: Command Line Interface commands entrypoint.
