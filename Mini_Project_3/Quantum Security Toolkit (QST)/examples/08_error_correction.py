"""Example 08: Cascade Error Correction for reconciled keys.

================================================================================
META INFORMATION
================================================================================
Difficulty Level: Intermediate
Estimated Completion Time: 3 minutes
Concepts Demonstrated:
  - Setting up QST SimulationConfig with Cascade Error Correction
  - Performing reconciliation on sifted keys between Alice and Bob
  - Evaluating correction efficiency and remaining post-reconciliation QBER
  - Comparing sifted key and corrected key telemetry

================================================================================
REQUIREMENTS
================================================================================
  - Python 3.10+
  - Quantum Security Toolkit (QST) installed or in python path

================================================================================
COMMON TROUBLESHOOTING
================================================================================
  - No errors in key: If the simulated transmission has 0% interception probability, QST checks early termination and skips block searches.
"""

import sys
from pathlib import Path

# Ensure the package is importable if running directly from the root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.correction.models import CascadeConfiguration
from qst.exceptions.base import QSTError


def main() -> None:
    """Demonstrates BB84 simulation followed by Cascade Error Correction reconciliation."""
    print("--- Example 08: Cascade Error Correction ---")

    try:
        # 1. Define configuration with error correction active
        config = SimulationConfig(
            n_qubits=25,
            seed=42,
            interception_probability=0.15,  # Introduce eavesdropping errors
            repetitions=1,
            protocol=ProtocolType.BB84,
            run_error_correction=True,
            cascade_configuration=CascadeConfiguration(
                num_passes=4,
                block_sizes=(4, 8),
                seed=101,
            ),
        )

        # 2. Run simulation orchestrator
        orchestrator = SimulationOrchestrator()
        experiment_result = orchestrator.run_once(config)
        trial = experiment_result.simulations[0]

        # 3. Retrieve raw, sifted, and corrected keys
        alice_sifted = trial.sifted_keys.alice_key
        bob_sifted = trial.sifted_keys.bob_key
        bob_corrected = trial.corrected_key
        corr_res = trial.error_correction

        # 4. Print results
        print("\n--- Key Comparison ---")
        print(f"Alice's Sifted Key: {list(alice_sifted)}")
        print(f"Bob's Sifted Key:   {list(bob_sifted)}")
        if bob_corrected is not None:
            print(f"Bob's Corrected Key: {list(bob_corrected)}")

        print("\n--- Telemetry & Metrics ---")
        print(
            f"Initial Key Discrepancies: {corr_res.statistics.initial_discrepancies} bits"
        )
        print(f"Initial QBER (Error Rate): {corr_res.initial_qber:.4f}")
        print(f"Bits Corrected:            {corr_res.corrected_error_count} bits")
        print(f"Corrected Bit Positions:   {list(corr_res.corrected_bit_positions)}")
        print(
            f"Remaining Estimated QBER:  {corr_res.estimated_qber_after_correction:.4f}"
        )
        print(f"Communication Rounds:      {corr_res.communication_rounds}")
        print(f"Parity Messages Exchanged: {corr_res.parity_messages_exchanged}")
        print(f"Parity Bits Disclosed:     {corr_res.bits_disclosed} bits")
        print(
            f"Correction Efficiency:     {corr_res.correction_efficiency:.4f} (theoretical limit f >= 1.0)"
        )
        print(f"Execution Duration:        {corr_res.execution_time * 1000:.3f} ms")

        # 5. Success verification check
        if list(bob_corrected) == list(alice_sifted):
            print(
                "\nReconciliation SUCCESSFUL! Bob's corrected key matches Alice's key."
            )
        else:
            print("\nReconciliation FAILED! Mismatches still remain.")

    except QSTError as e:
        print(f"\n[QST Error]: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[System Error]: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
