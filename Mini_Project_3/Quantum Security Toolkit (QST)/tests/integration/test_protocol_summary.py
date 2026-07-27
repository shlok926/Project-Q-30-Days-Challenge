"""Integration tests verifying ProtocolSummary and final secret key metrics in orchestration.

References:
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from qst.models.config import SimulationConfig, ProtocolType
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.correction.models import CascadeConfiguration
from qst.privacy.models import PrivacyAmplificationConfiguration


@pytest.mark.integration
def test_orchestration_summary_and_metrics_full_run() -> None:
    """Verify orchestrator runs all BB84 stages and populates final summary & metrics."""
    config = SimulationConfig(
        n_qubits=20,
        seed=42,
        interception_probability=0.05,
        repetitions=1,
        protocol=ProtocolType.BB84,
        run_error_correction=True,
        cascade_configuration=CascadeConfiguration(num_passes=2, block_sizes=(4,)),
        run_privacy_amplification=True,
        privacy_configuration=PrivacyAmplificationConfiguration(compression_ratio=0.5),
    )

    orchestrator = SimulationOrchestrator()
    result = orchestrator.run_once(config)
    trial = result.simulations[0]

    # Verify that the final summary exists and values are populated
    summary = trial.protocol_summary
    assert summary is not None
    assert summary.raw_key_length > 0
    assert summary.sifted_key_length > 0
    assert summary.corrected_key_length > 0
    assert summary.final_key_length > 0
    assert summary.correction_enabled is True
    assert summary.privacy_enabled is True
    assert summary.overall_success is True
    assert summary.execution_mode == "Local Aer"
    assert summary.protocol_name == "BB84"

    # Verify key metrics
    metrics = trial.secret_key_metrics
    assert metrics is not None
    assert metrics.raw_key_rate == 1.0
    assert metrics.sifted_key_rate > 0.0
    assert metrics.final_secret_key_rate > 0.0
    assert metrics.compression_ratio == 0.5
    assert metrics.overall_efficiency == metrics.final_secret_key_rate
    assert metrics.total_protocol_loss > 0.0

    # Verify security level exists
    assert trial.security_level is not None
