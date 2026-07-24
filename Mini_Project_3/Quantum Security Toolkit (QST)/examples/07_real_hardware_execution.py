"""Example 07: IBM Quantum Runtime Real Hardware Execution.

================================================================================
META INFORMATION
================================================================================
Difficulty Level: Intermediate
Estimated Completion Time: 3 minutes
Concepts Demonstrated:
  - Setting up QST SimulationConfig with IBM Quantum Runtime options
  - Performing credentials authentication and QPU backend selection
  - Executing quantum key distribution on physical IBM Quantum QPUs
  - Retrieving and evaluating execution results
  - Verifying graceful fallback to the Aer Simulator on connection/auth errors

================================================================================
REQUIREMENTS
================================================================================
  - Python 3.10+
  - qiskit >= 1.0.0
  - qiskit-ibm-runtime >= 0.20.0
  - Quantum Security Toolkit (QST) installed or in python path

================================================================================
COMMON TROUBLESHOOTING
================================================================================
  - Missing token: Ensure the `QISKIT_IBM_TOKEN` environment variable is set or configure a token explicitly.
  - Device queues: Physical hardware backends may have long queue wait times. Configure `noise_aware_local=True` to run noise-aware simulations locally instead.
"""

import os
import sys
from pathlib import Path

# Ensure the package is importable if running directly from the root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.exceptions.base import QSTError


def main() -> None:
    """Demonstrates BB84 execution on IBM Quantum Runtime with automatic fallback."""
    # Define outputs paths using pathlib
    base_dir = Path(__file__).resolve().parent
    logs_dir = base_dir / "outputs" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "07_real_hardware.log"

    print("--- Example 07: IBM Quantum Runtime Execution ---")
    print(f"Logging setup path: {log_file}\n")

    # Load IBM Quantum Token from environment variables
    token = os.environ.get("QISKIT_IBM_TOKEN") or os.environ.get("IBM_QUANTUM_TOKEN")

    if not token:
        print("[Notice] No IBM Quantum Token found in environment variables (QISKIT_IBM_TOKEN).")
        print("This run will demonstrate QST's graceful fallback behavior to Qiskit Aer Simulator.\n")

    try:
        # Initialize simulation configuration for IBM Quantum Runtime
        config = SimulationConfig(
            n_qubits=10,
            seed=42,
            interception_probability=0.0,
            repetitions=1,
            protocol=ProtocolType.BB84,
            use_ibm_runtime=True,
            backend_name="best",  # Select least busy operational hardware backend
            ibm_token=token,
            noise_aware_local=False,  # Set to True to build local noise-aware simulator from QPU profile
            fallback_to_aer=True,  # Automatically fall back to Aer simulator on connection/auth failure
        )

        print("Executing simulation orchestrator...")
        orchestrator = SimulationOrchestrator()
        experiment_result = orchestrator.run_once(config)
        trial = experiment_result.simulations[0]

        # Display result telemetry
        print("\n--- Simulation Complete. Metrics: ---")
        print(f"Sifted Key Length: {trial.final_key_length} bits")
        print(f"Key Rate:          {trial.key_rate:.4f}")
        print(f"QBER (Error Rate): {trial.qber:.4f}")
        print(f"Security Status:   {trial.security_metrics.status.value}")

        # Save execution log status
        with open(log_file, "w", encoding="utf-8") as lf:
            lf.write(
                f"QST Example 07 IBM Runtime Execution\n"
                f"QBER: {trial.qber}\n"
                f"Status: {trial.security_metrics.status.value}\n"
            )

    except QSTError as e:
        print(f"\n[QST Validation Error]: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[System Error]: Unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

# ================================================================================
# EXPECTED OUTPUT (Without Token - Fallback Active)
# ================================================================================
# --- Example 07: IBM Quantum Runtime Execution ---
# Logging setup path: .../examples/outputs/logs/07_real_hardware.log
#
# [Notice] No IBM Quantum Token found in environment variables (QISKIT_IBM_TOKEN).
# This run will demonstrate QST's graceful fallback behavior to Qiskit Aer Simulator.
#
# Executing simulation orchestrator...
# [Warning] Fallback to AerExecutor triggered due to IBM Quantum Runtime error: ...
#
# --- Simulation Complete. Metrics: ---
# Sifted Key Length: 5 bits
# Key Rate:          0.3333
# QBER (Error Rate): 0.0000
# Security Status:   SECURE
