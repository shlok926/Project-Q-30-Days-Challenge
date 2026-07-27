"""Example 10: Complete BB84 protocol lifecycle summary and key metrics telemetry.

================================================================================
META INFORMATION
================================================================================
Difficulty Level: Intermediate
Estimated Completion Time: 3 minutes
Concepts Demonstrated:
  - Constructing a complete E2E BB84 protocol simulation pipeline
  - Reconciling keys using Cascade error correction
  - Compressing keys using Privacy Amplification (Toeplitz Hashing)
  - Extracting key rates, protocol losses, and trace distance parameter
  - Determining security classification based on thresholds

================================================================================
REQUIREMENTS
================================================================================
  - Python 3.10+
  - Quantum Security Toolkit (QST) installed or in python path

================================================================================
COMMON TROUBLESHOOTING
================================================================================
  - Empty keys: If key length constraints or parameters are invalid,
    validate_key_lengths raises SecretKeyError.
"""

import sys
from pathlib import Path

# Ensure the package is importable if running directly from the root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.correction.models import CascadeConfiguration
from qst.privacy.models import PrivacyAmplificationConfiguration
from qst.secret.models import SecurityClassificationConfig
from qst.exceptions.base import QSTError


def main() -> None:
    """Runs BB84 E2E simulation and outputs a structured protocol final summary."""
    print("--- Example 10: Protocol Summary & Finalization ---")

    try:
        # 1. Define configuration for a complete BB84 pipeline execution
        config = SimulationConfig(
            n_qubits=20,
            seed=42,
            interception_probability=0.08,  # Introduce realistic noise
            repetitions=1,
            protocol=ProtocolType.BB84,
            run_error_correction=True,
            cascade_configuration=CascadeConfiguration(
                num_passes=3,
                block_sizes=(8, 16),
                seed=99,
            ),
            run_privacy_amplification=True,
            privacy_configuration=PrivacyAmplificationConfiguration(
                compression_ratio=0.5,
                seed=101,
            ),
            security_classification_thresholds=SecurityClassificationConfig(
                high_threshold=10.0,
                medium_threshold=4.0,
            ),
        )

        # 2. Run simulation orchestrator
        orchestrator = SimulationOrchestrator()
        experiment_result = orchestrator.run_once(config)
        trial = experiment_result.simulations[0]

        summary = trial.protocol_summary
        metrics = trial.secret_key_metrics
        sec_level = trial.security_level

        if summary is None or metrics is None or sec_level is None:
            print(
                "Error: Protocol summary or metrics were not populated.",
                file=sys.stderr,
            )
            sys.exit(1)

        # 3. Print structured output matching user's exact console specifications
        print("\nProtocol Summary")
        print("------------------------")
        print(f"Raw Key Length:          {summary.raw_key_length}")
        print("  v")
        print(f"Sifted Key Length:       {summary.sifted_key_length}")
        print("  v")
        print(f"Corrected Key Length:    {summary.corrected_key_length}")
        print("  v")
        print(f"Final Secret Key Length: {summary.final_key_length}")
        print("------------------------")
        print(f"Raw Key Rate:            {metrics.raw_key_rate:.4f}")
        print("  v")
        print(f"Sifted Key Rate:         {metrics.sifted_key_rate:.4f}")
        print("  v")
        print(f"Corrected Key Rate:      {metrics.corrected_key_rate:.4f}")
        print("  v")
        print(f"Final Key Rate:          {metrics.final_secret_key_rate:.4f}")
        print("------------------------")
        print(f"QBER:                    {summary.qber:.4f}")
        print(f"Security Parameter:      {metrics.security_parameter_summary:.4f}")
        print(f"Security Level:          {sec_level.value}")
        print(f"Execution Backend:       {summary.execution_mode}")
        print(f"Overall Success:         {summary.overall_success}")
        print("------------------------")

        print("\n--- Additional Benchmarking Loss ---")
        print(f"Error Correction Loss:   {metrics.error_correction_loss:.4f}")
        print(f"Privacy Amplification Loss: {metrics.privacy_amplification_loss:.4f}")
        print(f"Total Protocol Loss:     {metrics.total_protocol_loss:.4f}")

    except QSTError as e:
        print(f"\n[QST Error]: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[System Error]: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
