"""Integration tests verifying Privacy Amplification inside the QST orchestration run loop.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.models.config import SimulationConfig
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.privacy.models import PrivacyAmplificationConfiguration


@pytest.mark.integration
def test_pipeline_with_privacy_amplification_active() -> None:
    """Verify orchestrator runs Privacy Amplification on the corrected key when enabled."""
    config = SimulationConfig(
        n_qubits=20,
        seed=42,
        repetitions=1,
        run_error_correction=True,
        run_privacy_amplification=True,
        privacy_configuration=PrivacyAmplificationConfiguration(
            compression_ratio=0.5,
            seed=99,
        ),
    )

    orchestrator = SimulationOrchestrator()
    result = orchestrator.run_once(config)
    trial = result.simulations[0]

    # Verify key results exist
    assert trial.corrected_key is not None
    assert trial.error_correction is not None
    assert trial.privacy_result is not None
    assert trial.final_secret_key is not None

    # Check length compression matches
    assert trial.final_key_length == len(trial.final_secret_key.key_bits)
    assert trial.final_key_length == int(len(trial.corrected_key) * 0.5)


@pytest.mark.integration
def test_pipeline_with_privacy_only_reconciled_fallback() -> None:
    """Verify that if error correction is disabled, privacy amplification runs on the sifted key."""
    config = SimulationConfig(
        n_qubits=20,
        seed=101,
        repetitions=1,
        run_error_correction=False,
        run_privacy_amplification=True,
        privacy_configuration=PrivacyAmplificationConfiguration(
            compression_ratio=0.6,
        ),
    )

    orchestrator = SimulationOrchestrator()
    result = orchestrator.run_once(config)
    trial = result.simulations[0]

    # Checks
    assert trial.corrected_key is None
    assert trial.error_correction is None
    assert trial.privacy_result is not None
    assert trial.final_secret_key is not None
    assert trial.final_key_length == int(len(trial.sifted_key) * 0.6)


@pytest.mark.integration
def test_pipeline_privacy_backward_compatibility() -> None:
    """Verify backward compatibility: privacy results remain Null by default."""
    config = SimulationConfig(
        n_qubits=15,
        seed=42,
        repetitions=1,
    )

    orchestrator = SimulationOrchestrator()
    result = orchestrator.run_once(config)
    trial = result.simulations[0]

    assert trial.privacy_result is None
    assert trial.final_secret_key is None
