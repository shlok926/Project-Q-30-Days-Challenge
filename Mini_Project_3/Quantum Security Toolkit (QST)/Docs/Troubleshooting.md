# QST Troubleshooting Guide

This guide describes common error codes in QST and steps to resolve them.

## Validation Errors (QST-VAL-*)

### QST-VAL-101 (Invalid Qubits Count)
* **Cause:** The parameter `n_qubits` is negative, zero, or not an integer.
* **Resolution:** Set `n_qubits` to a positive integer (e.g. `n_qubits=20`).

### QST-VAL-402 / QST-VAL-602 (Overwrite Protection Error)
* **Cause:** File exporters reject writing JSON or CSV files if the destination file already exists.
* **Resolution:** Pass `overwrite_protection=False` to the exporter instance.

## Simulation Errors (QST-SIM-*)

### QST-SIM-102 (Transpilation Check Failed)
* **Cause:** The circuit is too wide or has invalid mapping for the backend coupling map.
* **Resolution:** Reduce `n_qubits` to match backend limits (e.g. $N \le 25$).

### QST-SIM-301 (IBM Authentication Denied)
* **Cause:** The provided API token is invalid or unauthorized.
* **Resolution:** Verify your Qiskit API token or configure the environment variable `QISKIT_IBM_TOKEN`.

### QST-SIM-304 (QPU Execution Timeout)
* **Cause:** Physical queue scheduling wait time exceeded target limit.
* **Resolution:** Set `fallback_to_aer=True` to run locally on Aer if the remote physical queue is overloaded.
