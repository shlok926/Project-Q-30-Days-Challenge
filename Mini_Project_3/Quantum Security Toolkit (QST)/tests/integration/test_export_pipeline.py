"""Integration tests for the reporting and export pipeline.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md
"""

import csv
import json
import os

import pytest

from qst.models.config import SimulationConfig
from qst.models.results import SweepDimensions
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.orchestration.sweep_generator import ParameterSweepGenerator
from qst.reporting.exporters.csv_exporter import CSVExporter
from qst.reporting.exporters.json_exporter import JSONExporter
from qst.reporting.serializers.serializers import (
    ExperimentSerializer,
    ParameterSweepSerializer,
    SimulationSerializer,
)


def _scrub_dynamic_fields(data: dict) -> dict:
    """Recursively scrubs volatile metadata to ensure test stability."""
    if "metadata" in data and isinstance(data["metadata"], dict):
        data["metadata"]["timestamp"] = "2026-07-24T17:15:00"
        data["metadata"]["qiskit_version"] = "2.0.0"
    if "simulations" in data and isinstance(data["simulations"], list):
        for sim in data["simulations"]:
            _scrub_dynamic_fields(sim)
    if "experiments" in data and isinstance(data["experiments"], list):
        for exp in data["experiments"]:
            _scrub_dynamic_fields(exp)
    if "metrics" in data and isinstance(data["metrics"], dict):
        data["metrics"]["execution_time"] = 0.1
        data["metrics"]["average_simulation_time"] = 0.05
        data["metrics"]["throughput"] = 100.0
        data["metrics"]["simulations_per_second"] = 10.0
    return data


@pytest.mark.integration
def test_export_data_integrity_json_roundtrip(tmp_path) -> None:
    """Verify that exporting to JSON and reloading preserves data, metadata, and schemas."""
    config = SimulationConfig(
        n_qubits=10, seed=42, interception_probability=0.5, repetitions=1
    )
    orchestrator = SimulationOrchestrator()
    exp_res = orchestrator.run_once(config)
    serialized = ExperimentSerializer().serialize(exp_res)

    out_path = os.path.join(tmp_path, "export.json")
    JSONExporter(overwrite_protection=False).export(
        filepath=out_path,
        data=serialized,
        metadata={"timestamp": "2026-07-24T17:15:00", "qiskit_version": "2.0.0"},
    )

    assert os.path.exists(out_path)

    # Read back and verify roundtrip data integrity
    with open(out_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)

    assert loaded["schema_version"] == "1.0.0"
    assert loaded["metadata"]["timestamp"] == "2026-07-24T17:15:00"
    assert len(loaded["data"]["simulations"]) == 1
    assert loaded["data"]["average_key_rate"] == exp_res.average_key_rate
    assert loaded["data"]["average_qber"] == exp_res.average_qber


@pytest.mark.integration
def test_export_csv_columns_integrity(tmp_path) -> None:
    """Verify that CSV exports generate matching columns, and keys are preserved in rows."""
    config = SimulationConfig(
        n_qubits=10, seed=42, interception_probability=0.5, repetitions=1
    )
    orchestrator = SimulationOrchestrator()
    exp_res = orchestrator.run_once(config)
    serialized = ExperimentSerializer().serialize(exp_res)

    out_path = os.path.join(tmp_path, "export.csv")
    CSVExporter(overwrite_protection=False).export(
        filepath=out_path,
        data=serialized,
        metadata={"timestamp": "2026-07-24T17:15:00", "qiskit_version": "2.0.0"},
    )

    assert os.path.exists(out_path)

    # Verify CSV structure
    with open(out_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert "experiment_average_qber" in reader.fieldnames
    assert "experiment_average_key_rate" in reader.fieldnames
    assert "timestamp" in reader.fieldnames


@pytest.mark.integration
def test_export_golden_reference_comparisons(tmp_path) -> None:
    """Compare freshly generated exports against pre-loaded Golden reference baseline files."""
    golden_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../fixtures/golden")
    )

    # Initialize simulation configs corresponding to golden baselines
    config = SimulationConfig(
        n_qubits=10, seed=42, interception_probability=0.5, repetitions=1
    )
    orchestrator = SimulationOrchestrator()
    exp_res = orchestrator.run_once(config)
    sim_res = exp_res.simulations[0]

    sim_serialized = SimulationSerializer().serialize(sim_res)
    exp_serialized = ExperimentSerializer().serialize(exp_res)

    # Param sweep configs corresponding to golden sweep
    configs = ParameterSweepGenerator.generate_configs(
        qubit_counts=[10, 20],
        interception_probabilities=[0.0, 0.5],
        seeds=[42],
        repetitions=2,
    )
    sweep_dims = SweepDimensions(
        qubit_counts=(10, 20), interception_probabilities=(0.0, 0.5), seeds=(42,)
    )
    sweep_res = orchestrator.run_parameter_sweep(configs, sweep_dims)
    sweep_serialized = ParameterSweepSerializer().serialize(sweep_res)

    # Scrub dynamic values
    clean_sim = json.loads(json.dumps(_scrub_dynamic_fields(sim_serialized)))
    clean_exp = json.loads(json.dumps(_scrub_dynamic_fields(exp_serialized)))
    clean_sweep = json.loads(json.dumps(_scrub_dynamic_fields(sweep_serialized)))

    # 1. Compare Simulation JSON
    golden_sim_path = os.path.join(golden_dir, "golden_simulation.json")
    with open(golden_sim_path, "r", encoding="utf-8") as f:
        golden_sim = json.load(f)
    assert clean_sim == golden_sim

    # 2. Compare Experiment JSON
    golden_exp_path = os.path.join(golden_dir, "golden_experiment.json")
    with open(golden_exp_path, "r", encoding="utf-8") as f:
        golden_exp = json.load(f)
    assert clean_exp == golden_exp

    # 3. Compare Sweep JSON
    golden_sweep_path = os.path.join(golden_dir, "golden_sweep.json")
    with open(golden_sweep_path, "r", encoding="utf-8") as f:
        golden_sweep = json.load(f)
    assert clean_sweep == golden_sweep
