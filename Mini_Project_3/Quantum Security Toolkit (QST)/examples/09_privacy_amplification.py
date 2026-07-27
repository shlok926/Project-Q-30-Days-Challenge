"""Example 09: Privacy Amplification compression on corrected keys.

================================================================================
META INFORMATION
================================================================================
Difficulty Level: Intermediate
Estimated Completion Time: 3 minutes
Concepts Demonstrated:
  - Activating Privacy Amplification in QST SimulationConfig
  - Compressing keys using deterministic Toeplitz Hashing algorithm
  - Analyzing Min-Entropy and Shannon Entropy statistical bounds
  - Comparing corrected key and secret key metrics

================================================================================
REQUIREMENTS
================================================================================
  - Python 3.10+
  - Quantum Security Toolkit (QST) installed or in python path

================================================================================
COMMON TROUBLESHOOTING
================================================================================
  - Empty corrected key: If error correction fails to run or sifting results in
    no common bits, privacy amplification raises custom validators exceptions.
"""

import sys
from pathlib import Path

# Ensure the package is importable if running directly from the root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.privacy.models import PrivacyAmplificationConfiguration
from qst.exceptions.base import QSTError


def main() -> None:
    """Demonstrates BB84 simulation, error correction, and Privacy Amplification."""
    print("--- Example 09: Privacy Amplification ---")

    try:
        # 1. Define configuration with Cascade error correction and Privacy Amplification
        config = SimulationConfig(
            n_qubits=25,
            seed=42,
            interception_probability=0.1,  # Noise / Eavesdropper
            repetitions=1,
            protocol=ProtocolType.BB84,
            run_error_correction=True,
            run_privacy_amplification=True,
            privacy_configuration=PrivacyAmplificationConfiguration(
                compression_ratio=0.6,
                hash_algorithm="toeplitz",
                seed=99,
            ),
        )

        # 2. Run simulation orchestrator
        orchestrator = SimulationOrchestrator()
        experiment_result = orchestrator.run_once(config)
        trial = experiment_result.simulations[0]

        # 3. Retrieve corrected key and amplified secret key details
        bob_corrected = trial.corrected_key
        secret_key_obj = trial.final_secret_key
        priv_res = trial.privacy_result

        # 4. Print results
        print("\n--- Key Processing Stages ---")
        if bob_corrected is not None:
            print(f"Corrected Shared Key (Input):  {list(bob_corrected)}")
        if secret_key_obj is not None:
            print(f"Final Secret Key (Output):     {list(secret_key_obj.key_bits)}")

        print("\n--- Privacy Amplification Telemetry ---")
        print(f"Input Key Length:              {priv_res.input_key_length} bits")
        print(f"Output Key Length:             {priv_res.output_key_length} bits")
        print(
            f"Discarded Bits:                {priv_res.statistics.discarded_bits} bits"
        )
        print(
            f"Compression Percentage:        {priv_res.statistics.compression_percentage:.2f}%"
        )
        print(
            f"Effective Key Rate (Ratio):    {priv_res.statistics.effective_key_rate:.4f}"
        )
        print(f"Hash Hashing Algorithm:        {priv_res.hash_algorithm.upper()}")
        print(
            f"Estimated Security Parameter:  {priv_res.statistics.estimated_security_parameter:.4f}"
        )
        print(
            f"Estimated Eve Information:     {priv_res.estimated_eve_information:.4f} bits"
        )
        print(
            f"Shannon Entropy Estimate:      {secret_key_obj.shannon_entropy_estimate:.4f}"
        )
        print(
            f"Min-Entropy (H_infinity):      {secret_key_obj.min_entropy_estimate:.4f}"
        )
        print(f"Execution Duration:            {priv_res.execution_time * 1000:.3f} ms")

        # 5. Verify compression matches target configuration
        expected_len = int(len(bob_corrected) * 0.6)
        if len(secret_key_obj.key_bits) == expected_len:
            print(
                "\nPrivacy Amplification SUCCESSFUL! Outputs matches target compression."
            )
        else:
            print("\nPrivacy Amplification size mismatch.")

    except QSTError as e:
        print(f"\n[QST Error]: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n[System Error]: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
