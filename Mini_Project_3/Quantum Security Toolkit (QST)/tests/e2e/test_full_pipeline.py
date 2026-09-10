"""End-to-End Pipeline test.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md
"""

import json
import os

import pytest

from qst.analysis.trends.trends import TrendAnalysisService
from qst.models.config import ProtocolType, SimulationConfig
from qst.models.results import SweepDimensions
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.orchestration.sweep_generator import ParameterSweepGenerator
from qst.reporting.exporters.json_exporter import JSONExporter
from qst.reporting.serializers.serializers import ParameterSweepSerializer
from qst.visualization.matplotlib_backend import MatplotlibBackend
from qst.visualization.styles import LightTheme
from qst.visualization.visualizer import Visualizer


@pytest.mark.e2e
def test_full_pipeline_e2e(tmp_path) -> None:
    """Verify end-to-end execution flow of QST pipeline from simulation to plotting."""
    # 1. Run simulation sweep
    qubit_counts = [10, 20]
    probabilities = [0.0, 0.5]
    seeds = [42]
    repetitions = 2

    configs = ParameterSweepGenerator.generate_configs(
        qubit_counts=qubit_counts,
        interception_probabilities=probabilities,
        seeds=seeds,
        repetitions=repetitions,
    )
    sweep_dims = SweepDimensions(
        qubit_counts=tuple(qubit_counts),
        interception_probabilities=tuple(probabilities),
        seeds=tuple(seeds),
    )

    orchestrator = SimulationOrchestrator()
    sweep_res = orchestrator.run_parameter_sweep(configs, sweep_dims)

    # 2. Assert statistics
    assert sweep_res.total_experiments == 4
    assert sweep_res.experiments[0].secure_runs == 2  # No interception
    exp_interception = sweep_res.experiments[1]
    assert exp_interception.secure_runs + exp_interception.warning_runs + exp_interception.compromised_runs == 2

    # 3. Analyze trends
    trend_service = TrendAnalysisService()
    line_series = trend_service.analyze_qber_vs_interception(sweep_res)

    assert line_series.label == "QBER vs Interception Probability"
    assert line_series.x_values == (0.0, 0.5)
    # Average QBER under 0 interception must be 0
    assert line_series.y_values[0] == 0.0
    # Average QBER under 0.5 interception must be positive
    assert line_series.y_values[1] > 0.0

    # 4. Serialize and Export
    serialized = ParameterSweepSerializer().serialize(sweep_res)
    json_path = os.path.join(tmp_path, "sweep_result.json")
    JSONExporter(overwrite_protection=False).export(
        filepath=json_path,
        data=serialized,
        metadata=serialized.get("metadata", {}),
    )

    assert os.path.exists(json_path)

    # 5. Visualize and render figure
    backend = MatplotlibBackend(overwrite_protection=False)
    theme = LightTheme()
    visualizer = Visualizer(backend, theme)

    plot_path = os.path.join(tmp_path, "qber_vs_interception.png")
    vis_res = visualizer.line_chart(line_series, plot_path)

    assert os.path.exists(plot_path)
    assert os.path.getsize(plot_path) > 0
    assert vis_res.format == "PNG"


@pytest.mark.e2e
def test_full_qkd_lifecycle_e2e(tmp_path) -> None:
    """Verify complete end-to-end QKD lifecycle with every stage explicitly executed.

    Stages verified:
        1. Alice: Classical bit & basis preparation
        2. Quantum transmission: Channel interaction (Eve interception)
        3. Bob: Measurement basis selection and quantum measurement
        4. Sifting: Basis reconciliation and sifted key generation
        5. QBER: Error detection and channel parameter estimation
        6. Error Correction: Cascade parity-checking and error elimination
        7. Privacy Amplification: Matrix hash compression and Eve information bound
        8. Final Secret Key: Entropy-verified distilled secret key
        9. Export: Safe atomic serialization to JSON and CSV
    """
    from qst.correction.models import CascadeConfiguration
    from qst.privacy.models import PrivacyAmplificationConfiguration
    from qst.reporting.exporters.csv_exporter import CSVExporter
    from qst.reporting.serializers.serializers import ExperimentSerializer

    n_qubits = 120
    eve_prob = 0.3
    seed = 42

    config = SimulationConfig(
        n_qubits=n_qubits,
        seed=seed,
        interception_probability=eve_prob,
        repetitions=1,
        protocol=ProtocolType.BB84,
        run_error_correction=True,
        cascade_configuration=CascadeConfiguration(),
        run_privacy_amplification=True,
        privacy_configuration=PrivacyAmplificationConfiguration(
            compression_ratio=0.5,
            hash_algorithm="toeplitz",
            seed=seed,
        ),
    )

    orchestrator = SimulationOrchestrator()
    exp_res = orchestrator.run_once(config)
    assert len(exp_res.simulations) == 1
    sim = exp_res.simulations[0]

    # STAGE 1: Alice preparation
    assert sim.alice_bits is not None
    assert len(sim.alice_bits) == n_qubits
    assert all(b in (0, 1) for b in sim.alice_bits)
    assert sim.alice_bases is not None
    assert len(sim.alice_bases) == n_qubits
    assert all(base in ("Z", "X") for base in sim.alice_bases)

    # STAGE 2: Quantum transmission & Eve interaction
    assert sim.eve_intercept_probability == eve_prob

    # STAGE 3: Bob measurement
    assert sim.bob_bits is not None
    assert len(sim.bob_bits) == n_qubits
    assert all(b in (0, 1) for b in sim.bob_bits)
    assert sim.bob_bases is not None
    assert len(sim.bob_bases) == n_qubits
    assert all(base in ("Z", "X") for base in sim.bob_bases)

    # STAGE 4: Sifting and Basis Reconciliation
    assert sim.reconciliation is not None
    assert sim.reconciliation.matching_count > 0
    assert sim.reconciliation.match_rate > 0.0
    assert sim.sifted_keys is not None
    assert len(sim.sifted_keys.alice_key) == sim.reconciliation.matching_count
    assert len(sim.sifted_keys.bob_key) == sim.reconciliation.matching_count
    assert 0.3 * n_qubits <= len(sim.sifted_keys.alice_key) <= 0.7 * n_qubits

    # STAGE 5: QBER calculation
    assert sim.qber is not None
    assert sim.qber > 0.0

    # STAGE 6: Cascade Error Correction
    assert sim.error_correction is not None
    assert sim.corrected_key is not None
    assert len(sim.corrected_key) == len(sim.sifted_keys.alice_key)
    assert sim.error_correction.passes_completed > 0
    assert sim.error_correction.estimated_qber_after_correction <= sim.qber


    # STAGE 7: Privacy Amplification
    assert sim.privacy_result is not None
    assert sim.privacy_result.hash_algorithm == "toeplitz"
    assert sim.privacy_result.compression_ratio == 0.5
    assert sim.privacy_result.output_key_length == int(len(sim.corrected_key) * 0.5)
    assert sim.privacy_result.statistics.discarded_bits > 0

    # STAGE 8: Final Secret Key
    assert sim.final_secret_key is not None
    assert len(sim.final_secret_key.key_bits) == sim.privacy_result.output_key_length
    assert sim.final_key_length == len(sim.final_secret_key.key_bits)
    assert sim.key_rate == float(sim.final_key_length / n_qubits)
    assert sim.key_rate > 0.0
    assert sim.final_secret_key.shannon_entropy_estimate > 0.0

    # STAGE 9: Safe Atomic Export (JSON and CSV)
    serializer = ExperimentSerializer()
    serialized_data = serializer.serialize(exp_res)
    metadata = serialized_data.get("metadata", {"schema_version": "1.0.0"})

    json_export_path = tmp_path / "lifecycle_export.json"
    json_exporter = JSONExporter(overwrite_protection=True, allowed_base_dir=tmp_path)
    json_exporter.export(json_export_path, serialized_data, metadata)
    assert json_export_path.exists()
    assert json_export_path.stat().st_size > 0

    with open(json_export_path, "r", encoding="utf-8") as f:
        loaded_json = json.load(f)
        assert loaded_json["data"]["simulations"][0]["final_key_length"] == sim.final_key_length

    csv_export_path = tmp_path / "lifecycle_export.csv"
    csv_exporter = CSVExporter(overwrite_protection=True, allowed_base_dir=tmp_path)
    csv_exporter.export(csv_export_path, serialized_data, metadata)
    assert csv_export_path.exists()
    assert csv_export_path.stat().st_size > 0

    with open(csv_export_path, "r", encoding="utf-8") as f:
        csv_content = f.read()
        assert "qber" in csv_content
        assert "final_key_length" in csv_content

