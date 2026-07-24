"""Integration tests for Cascade Error Correction orchestration pipeline.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.correction.models import CascadeConfiguration


@pytest.mark.integration
def test_pipeline_with_error_correction_active() -> None:
    """Verify that orchestrator runs error correction, populates corrected_key, and leaves sifted_key unchanged."""
    config = SimulationConfig(
        n_qubits=20,
        seed=123,
        interception_probability=0.1,  # introduces channel noise / errors
        repetitions=1,
        protocol=ProtocolType.BB84,
        run_error_correction=True,
        cascade_configuration=CascadeConfiguration(num_passes=4, block_sizes=(4, 8)),
    )

    orchestrator = SimulationOrchestrator()
    result = orchestrator.run_once(config)
    trial = result.simulations[0]

    # Verify new model fields exist
    assert trial.corrected_key is not None
    assert trial.error_correction is not None
    assert trial.raw_key is not None

    # Check key correction properties
    alice_sifted = trial.sifted_keys.alice_key
    bob_sifted = trial.sifted_keys.bob_key
    bob_corrected = trial.corrected_key

    # Bob's corrected key must match Alice's sifted key completely
    assert list(bob_corrected) == list(alice_sifted)

    # Bob's raw sifted key is unchanged (might contain errors if QBER > 0)
    assert list(trial.sifted_key) == list(bob_sifted)
    if trial.qber and trial.qber > 0.0:
        assert list(bob_sifted) != list(alice_sifted)

    # Check CorrectionResult telemetry properties
    corr_res = trial.error_correction
    assert corr_res.corrected_key.key_bits == tuple(bob_corrected)
    assert corr_res.estimated_qber_after_correction == 0.0
    assert corr_res.statistics.initial_discrepancies >= 0
    assert corr_res.statistics.execution_time > 0.0


@pytest.mark.integration
def test_pipeline_backward_compatibility() -> None:
    """Verify that by default, error correction is inactive and corrected_key is None."""
    config = SimulationConfig(
        n_qubits=20,
        seed=42,
        interception_probability=0.0,
        repetitions=1,
    )

    orchestrator = SimulationOrchestrator()
    result = orchestrator.run_once(config)
    trial = result.simulations[0]

    # Defaults check
    assert trial.corrected_key is None
    assert trial.error_correction is None
    assert trial.raw_key is not None
    assert trial.privacy_result is None
    assert trial.final_secret_key is None
