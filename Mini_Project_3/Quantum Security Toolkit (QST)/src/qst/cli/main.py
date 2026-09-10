"""Command Line Interface (CLI) dispatcher and main execution entry point.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/07_SYSTEM_ARCHITECTURE.md §5, §11
"""

import argparse
import json
import os
import sys
from typing import Any, Optional, Sequence

import numpy as np

from qst.config.settings import QST_VERSION
from qst.exceptions.base import QSTError
from qst.exceptions.validation import ValidationError
from qst.models.config import ProtocolType, SimulationConfig
from qst.models.results import SweepDimensions
from qst.orchestration.orchestrator import SimulationOrchestrator
from qst.orchestration.sweep_generator import ParameterSweepGenerator
from qst.privacy.models import PrivacyAmplificationConfiguration
from qst.reporting.exporters.csv_exporter import CSVExporter
from qst.reporting.exporters.json_exporter import JSONExporter
from qst.reporting.serializers.serializers import (
    ExperimentSerializer,
    ParameterSweepSerializer,
)
from qst.visualization.datasets import (
    HeatmapMatrix,
    HistogramSeries,
    ScatterSeries,
)
from qst.visualization.matplotlib_backend import MatplotlibBackend
from qst.visualization.styles import DarkTheme, LightTheme, ScientificTheme, Theme
from qst.visualization.visualizer import Visualizer


def load_sweep_result_from_dict(d: dict[str, Any]) -> Any:
    """Helper deserializing a sweep nested dictionary back into domain models.

    Args:
        d: Serialized sweep dictionary.

    Returns:
        A ParameterSweepResult instance.
    """
    from qst.models.results import (
        ExecutionMetrics,
        ExperimentMetadata,
        ExperimentResult,
        ParameterSweepResult,
        SecurityMetrics,
        SecurityStatus,
        SimulationResult,
        SweepDimensions,
    )

    experiments = []
    for exp_d in d.get("experiments", []):
        sims = []
        for sim_d in exp_d.get("simulations", []):
            sec_met_d = sim_d.get("security_metrics")
            sec_met = None
            if sec_met_d:
                sec_met = SecurityMetrics(
                    key_rate=sec_met_d.get("key_rate", 0.0),
                    discard_rate=sec_met_d.get("discard_rate", 0.0),
                    error_rate=sec_met_d.get("error_rate", 0.0),
                    status=SecurityStatus(sec_met_d.get("status", "SECURE")),
                )
            sim = SimulationResult(
                qber=sim_d.get("qber"),
                final_key_length=(
                    sim_d.get("final_key_length", 0)
                    if sim_d.get("final_key_length") is not None
                    else 0
                ),
                key_rate=(
                    sim_d.get("key_rate", 0.0)
                    if sim_d.get("key_rate") is not None
                    else 0.0
                ),
                sifted_key=(
                    list(sim_d.get("sifted_key", []))
                    if sim_d.get("sifted_key") is not None
                    else []
                ),
                n_qubits=(
                    sim_d.get("n_qubits", 0) if sim_d.get("n_qubits") is not None else 0
                ),
                seed=sim_d.get("seed"),
                eve_intercept_probability=(
                    sim_d.get(
                        "eve_intercept_probability",
                        sim_d.get("interception_probability", 0.0),
                    )
                    if sim_d.get("eve_intercept_probability") is not None
                    else sim_d.get("interception_probability", 0.0)
                ),
                interception_probability=sim_d.get("interception_probability", 0.0),
                alice_bases=(
                    tuple(sim_d.get("alice_bases", ()))
                    if sim_d.get("alice_bases")
                    else None
                ),
                bob_bases=(
                    tuple(sim_d.get("bob_bases", ()))
                    if sim_d.get("bob_bases")
                    else None
                ),
                security_metrics=sec_met,
            )
            sims.append(sim)

        met_d = exp_d.get("metrics", {})
        metrics = ExecutionMetrics(
            execution_time=met_d.get("execution_time", 0.0),
            average_simulation_time=met_d.get("average_simulation_time", 0.0),
            throughput=met_d.get("throughput", 0.0),
            simulations_per_second=met_d.get("simulations_per_second", 0.0),
        )

        meta_d = exp_d.get("metadata", {})
        metadata = ExperimentMetadata(
            protocol=meta_d.get("protocol", "BB84"),
            timestamp=meta_d.get("timestamp", ""),
            qiskit_version=meta_d.get("qiskit_version", ""),
            repetitions=meta_d.get("repetitions", 1),
            seed_strategy=meta_d.get("seed_strategy", ""),
        )

        exp = ExperimentResult(
            simulations=tuple(sims),
            average_qber=exp_d.get("average_qber", 0.0),
            average_key_rate=exp_d.get("average_key_rate", 0.0),
            secure_runs=exp_d.get("secure_runs", 0),
            warning_runs=exp_d.get("warning_runs", 0),
            compromised_runs=exp_d.get("compromised_runs", 0),
            metrics=metrics,
            metadata=metadata,
        )
        experiments.append(exp)

    sweep_dim_d = d.get("sweep_dimensions", {})
    sweep_dimensions = SweepDimensions(
        qubit_counts=tuple(sweep_dim_d.get("qubit_counts", ())),
        interception_probabilities=tuple(
            sweep_dim_d.get("interception_probabilities", ())
        ),
        seeds=tuple(sweep_dim_d.get("seeds", ())),
    )

    meta_d = d.get("metadata", {})
    metadata = ExperimentMetadata(
        protocol=meta_d.get("protocol", "BB84"),
        timestamp=meta_d.get("timestamp", ""),
        qiskit_version=meta_d.get("qiskit_version", ""),
        repetitions=meta_d.get("repetitions", 1),
        seed_strategy=meta_d.get("seed_strategy", ""),
    )

    return ParameterSweepResult(
        experiments=tuple(experiments),
        total_experiments=d.get("total_experiments", 0),
        sweep_dimensions=sweep_dimensions,
        metadata=metadata,
    )


def get_parser() -> argparse.ArgumentParser:
    """Create parser setup for QST commands.

    Returns:
        An argparse.ArgumentParser.
    """
    parser = argparse.ArgumentParser(
        prog="qst", description="Quantum Security Toolkit (QST) CLI Adapter"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # qst simulate
    sim_p = subparsers.add_parser("simulate", help="Run a single simulation")
    sim_p.add_argument("--qubits", type=int, default=20, help="Qubit count (positive)")
    sim_p.add_argument("--seed", type=int, default=None, help="Random seed")
    sim_p.add_argument(
        "--interception-probability",
        type=float,
        default=0.0,
        help="Eve's interception probability [0.0, 1.0]",
    )
    sim_p.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output save path (JSON extension required)",
    )
    sim_p.add_argument(
        "--error-correction",
        action="store_true",
        default=False,
        help="Enable Cascade error correction",
    )
    sim_p.add_argument(
        "--privacy-amplification",
        action="store_true",
        default=False,
        help="Enable privacy amplification",
    )
    sim_p.add_argument(
        "--privacy-algorithm",
        type=str,
        default="toeplitz",
        choices=["toeplitz", "universal_hash", "TOEPLITZ", "UNIVERSAL_HASH"],
        help="Privacy amplification hash family",
    )
    sim_p.add_argument(
        "--compression-ratio",
        type=float,
        default=0.5,
        help="Privacy amplification compression ratio (0.0, 1.0]",
    )

    # qst sweep
    sweep_p = subparsers.add_parser("sweep", help="Run parameter sweeps")
    sweep_p.add_argument(
        "--qubits",
        type=str,
        default="10,20,50",
        help="Comma-separated integers list",
    )
    sweep_p.add_argument(
        "--probabilities",
        type=str,
        default="0.0,0.1,0.5",
        help="Comma-separated floats list",
    )
    sweep_p.add_argument(
        "--repetitions",
        type=int,
        default=10,
        help="Simulations per combination coordinate",
    )
    sweep_p.add_argument(
        "--export",
        type=str,
        default=None,
        help="Output save path (JSON extension required)",
    )
    sweep_p.add_argument(
        "--error-correction",
        action="store_true",
        default=False,
        help="Enable Cascade error correction across sweep",
    )
    sweep_p.add_argument(
        "--privacy-amplification",
        action="store_true",
        default=False,
        help="Enable privacy amplification across sweep",
    )
    sweep_p.add_argument(
        "--privacy-algorithm",
        type=str,
        default="toeplitz",
        choices=["toeplitz", "universal_hash", "TOEPLITZ", "UNIVERSAL_HASH"],
        help="Privacy amplification hash family",
    )
    sweep_p.add_argument(
        "--compression-ratio",
        type=float,
        default=0.5,
        help="Privacy amplification compression ratio (0.0, 1.0]",
    )

    # qst export
    export_p = subparsers.add_parser("export", help="Export existing results")
    export_p.add_argument("filepath", type=str, help="Input JSON file path")
    export_p.add_argument(
        "--format",
        type=str,
        required=True,
        choices=["JSON", "CSV", "json", "csv"],
        help="Target format to export",
    )
    export_p.add_argument(
        "--output", type=str, required=True, help="Destination save path"
    )

    # qst visualize
    vis_p = subparsers.add_parser("visualize", help="Generate plots from results")
    vis_p.add_argument("filepath", type=str, help="Input sweep JSON file path")
    vis_p.add_argument(
        "--type",
        type=str,
        required=True,
        choices=[
            "LINE",
            "SCATTER",
            "HISTOGRAM",
            "HEATMAP",
            "line",
            "scatter",
            "histogram",
            "heatmap",
        ],
        help="Plot chart format type",
    )
    vis_p.add_argument(
        "--format",
        type=str,
        default="PNG",
        choices=["PNG", "SVG", "PDF", "png", "svg", "pdf"],
        help="Export image format suffix",
    )
    vis_p.add_argument(
        "--output", type=str, required=True, help="Destination image file path"
    )
    vis_p.add_argument(
        "--theme",
        type=str,
        default="LIGHT",
        choices=[
            "LIGHT",
            "DARK",
            "SCIENTIFIC",
            "light",
            "dark",
            "scientific",
        ],
        help="Theme colors and styling preset",
    )

    # qst info
    subparsers.add_parser("info", help="Display toolkit details")

    # qst version
    subparsers.add_parser("version", help="Display version")

    return parser


def handle_simulate(args: argparse.Namespace) -> None:
    """Execute simulate parser flow.

    Args:
        args: Parsed commands namespace.
    """
    if args.qubits <= 0:
        raise ValidationError(
            f"Qubit count must be positive, got {args.qubits}.",
            code="QST-VAL-101",
        )
    if not (0.0 <= args.interception_probability <= 1.0):
        raise ValidationError(
            f"Interception probability must be in range [0.0, 1.0], got {args.interception_probability}.",
            code="QST-VAL-102",
        )

    privacy_cfg = None
    if getattr(args, "privacy_amplification", False):
        privacy_cfg = PrivacyAmplificationConfiguration(
            compression_ratio=getattr(args, "compression_ratio", 0.5),
            hash_algorithm=getattr(args, "privacy_algorithm", "toeplitz").lower(),
            seed=args.seed or 42,
        )

    config = SimulationConfig(
        n_qubits=args.qubits,
        seed=args.seed,
        interception_probability=args.interception_probability,
        repetitions=1,
        protocol=ProtocolType.BB84,
        run_error_correction=getattr(args, "error_correction", False),
        run_privacy_amplification=getattr(args, "privacy_amplification", False),
        privacy_configuration=privacy_cfg,
    )
    orchestrator = SimulationOrchestrator()
    res = orchestrator.run_once(config)

    # Output if requested
    if args.output:
        # File suffix validation
        suffix = os.path.splitext(args.output)[1].lower()
        if suffix != ".json":
            raise ValidationError(
                f"Simulate output must be in JSON format, got {suffix}.",
                code="QST-VAL-404",
            )
        serialized = ExperimentSerializer().serialize(res)
        JSONExporter(overwrite_protection=False).export(
            filepath=args.output,
            data=serialized,
            metadata=serialized.get("metadata", {}),
        )

    # Print summary
    sys.stdout.write("Simulation completed successfully.\n")
    sys.stdout.write(f"Average QBER: {res.average_qber:.4f}\n")
    sys.stdout.write(f"Average Key Rate: {res.average_key_rate:.4f}\n")
    sys.stdout.write(f"Secure runs: {res.secure_runs}/{res.metadata.repetitions}\n")


def handle_sweep(args: argparse.Namespace) -> None:
    """Execute parameter sweep flow.

    Args:
        args: Parsed commands namespace.
    """
    if args.export:
        suffix = os.path.splitext(args.export)[1].lower()
        if suffix != ".json":
            raise ValidationError(
                f"Sweep export must be in JSON format, got {suffix}.",
                code="QST-VAL-404",
            )

    try:
        qubit_counts = [int(q.strip()) for q in args.qubits.split(",")]
    except ValueError:
        raise ValidationError(
            f"Invalid qubits format: {args.qubits}.", code="QST-VAL-103"
        )

    try:
        probabilities = [float(p.strip()) for p in args.probabilities.split(",")]
    except ValueError:
        raise ValidationError(
            f"Invalid probabilities format: {args.probabilities}.",
            code="QST-VAL-104",
        )

    if args.repetitions <= 0:
        raise ValidationError(
            f"Repetitions count must be positive, got {args.repetitions}.",
            code="QST-VAL-105",
        )

    privacy_cfg = None
    if getattr(args, "privacy_amplification", False):
        privacy_cfg = PrivacyAmplificationConfiguration(
            compression_ratio=getattr(args, "compression_ratio", 0.5),
            hash_algorithm=getattr(args, "privacy_algorithm", "toeplitz").lower(),
            seed=42,
        )

    # Generate configs and dimensions
    configs = ParameterSweepGenerator.generate_configs(
        qubit_counts=qubit_counts,
        interception_probabilities=probabilities,
        seeds=[None],
        repetitions=args.repetitions,
        run_error_correction=getattr(args, "error_correction", False),
        run_privacy_amplification=getattr(args, "privacy_amplification", False),
        privacy_configuration=privacy_cfg,
    )
    sweep_dimensions = SweepDimensions(
        qubit_counts=tuple(qubit_counts),
        interception_probabilities=tuple(probabilities),
        seeds=(None,),
    )

    orchestrator = SimulationOrchestrator()
    res = orchestrator.run_parameter_sweep(configs, sweep_dimensions)

    if args.export:
        serialized = ParameterSweepSerializer().serialize(res)
        JSONExporter(overwrite_protection=False).export(
            filepath=args.export,
            data=serialized,
            metadata=serialized.get("metadata", {}),
        )

    sys.stdout.write("Parameter sweep execution completed successfully.\n")
    sys.stdout.write(f"Total experiments executed: {res.total_experiments}\n")


def handle_export(args: argparse.Namespace) -> None:
    """Execute results exporter.

    Args:
        args: Parsed commands namespace.
    """
    if not os.path.exists(args.filepath):
        raise FileNotFoundError(f"Input file not found at: {args.filepath}")

    with open(args.filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    input_metadata = data.get("metadata", {})
    if not isinstance(input_metadata, dict):
        input_metadata = {"exporter": "QST CLI"}

    fmt = args.format.upper()
    if fmt == "JSON":
        JSONExporter(overwrite_protection=False).export(
            filepath=args.output,
            data=data,
            metadata=input_metadata,
        )
    elif fmt == "CSV":
        CSVExporter(overwrite_protection=False).export(
            filepath=args.output,
            data=data,
            metadata=input_metadata,
        )


def handle_visualize(args: argparse.Namespace) -> None:
    """Execute charts visualization.

    Args:
        args: Parsed commands namespace.
    """
    if not os.path.exists(args.filepath):
        raise FileNotFoundError(f"Input file not found at: {args.filepath}")

    with open(args.filepath, "r", encoding="utf-8") as f:
        raw_dict = json.load(f)

    # Heatmap requires sweep result. Other types also work best on sweep results.
    data_dict = raw_dict.get("data", raw_dict)
    sweep_result = load_sweep_result_from_dict(data_dict)

    # 1. Parse chart type
    c_type = args.type.upper()

    # 2. Select dataset
    from qst.analysis.trends.trends import TrendAnalysisService

    trend_service = TrendAnalysisService()
    dataset: Any

    if c_type == "LINE":
        # Select appropriate line trend
        if len(sweep_result.sweep_dimensions.interception_probabilities) > 1:
            dataset = trend_service.analyze_qber_vs_interception(sweep_result)
        elif len(sweep_result.sweep_dimensions.qubit_counts) > 1:
            dataset = trend_service.analyze_key_rate_vs_qubits(sweep_result)
        else:
            dataset = trend_service.analyze_throughput_vs_repetitions(sweep_result)

    elif c_type == "SCATTER":
        x_vals = []
        y_vals = []
        for exp in sweep_result.experiments:
            x_vals.append(exp.average_qber)
            y_vals.append(exp.average_key_rate)
        dataset = ScatterSeries(
            "QBER vs Key Rate Scatter", tuple(x_vals), tuple(y_vals)
        )

    elif c_type == "HISTOGRAM":
        qbers = []
        for exp in sweep_result.experiments:
            for sim in exp.simulations:
                if sim.qber is not None:
                    qbers.append(sim.qber)
        if not qbers:
            raise ValidationError(
                "No QBER results available for histogram plotting.",
                code="QST-VAL-710",
            )
        counts, edges = np.histogram(qbers, bins=10)
        dataset = HistogramSeries(
            "QBER Histogram Distribution",
            tuple(qbers),
            tuple(float(e) for e in edges),
            tuple(int(c) for c in counts),
        )

    elif c_type == "HEATMAP":
        qubits = sorted(list(set(sweep_result.sweep_dimensions.qubit_counts)))
        probs = sorted(
            list(set(sweep_result.sweep_dimensions.interception_probabilities))
        )
        if len(qubits) <= 1 or len(probs) <= 1:
            raise ValidationError(
                "HEATMAP requires a 2D parameter sweep grid (multiple qubit counts and probabilities).",
                code="QST-VAL-711",
            )

        matrix = [[0.0 for _ in range(len(qubits))] for _ in range(len(probs))]
        for exp in sweep_result.experiments:
            if not exp.simulations:
                continue
            q = exp.simulations[0].n_qubits
            p = exp.simulations[0].interception_probability
            if q in qubits and p in probs:
                q_idx = qubits.index(q)
                p_idx = probs.index(p)
                matrix[p_idx][q_idx] = exp.average_qber

        dataset = HeatmapMatrix(
            "QBER Sweep Heatmap",
            tuple(f"Q{q}" for q in qubits),
            tuple(f"P{p:.2f}" for p in probs),
            tuple(tuple(row) for row in matrix),
        )
    else:
        raise ValidationError(f"Unsupported chart type: {c_type}", code="QST-VAL-712")

    # 3. Resolve theme
    t_name = args.theme.upper()
    theme: Theme
    if t_name == "LIGHT":
        theme = LightTheme()
    elif t_name == "DARK":
        theme = DarkTheme()
    elif t_name == "SCIENTIFIC":
        theme = ScientificTheme()
    else:
        theme = LightTheme()

    # 4. Render
    backend = MatplotlibBackend(overwrite_protection=False)
    visualizer = Visualizer(backend, theme)

    if c_type == "LINE":
        visualizer.line_chart(dataset, args.output)
    elif c_type == "SCATTER":
        visualizer.scatter_chart(dataset, args.output)
    elif c_type == "HISTOGRAM":
        visualizer.histogram(dataset, args.output)
    elif c_type == "HEATMAP":
        visualizer.heatmap(dataset, args.output)

    sys.stdout.write(f"Chart successfully saved to path: {args.output}\n")


def main(args: Optional[Sequence[str]] = None) -> int:
    """CLI execution dispatcher entry point.

    Args:
        args: List of command arguments. Defaults to sys.argv[1:].

    Returns:
        Integer exit status code (0 for success, 1 for errors).
    """
    if args is None:
        args = sys.argv[1:]

    # Special handling for --version if passed directly (or single help triggers)
    if len(args) == 1 and args[0] in ["--version", "-v"]:
        sys.stdout.write(f"QST Version: {QST_VERSION}\n")
        return 0

    try:
        try:
            parser = get_parser()
            parsed_args = parser.parse_args(args)
        except SystemExit as e:
            return e.code if isinstance(e.code, int) else 1

        if parsed_args.command == "version":
            sys.stdout.write(f"QST Version: {QST_VERSION}\n")
            return 0

        elif parsed_args.command == "info":
            sys.stdout.write("Quantum Security Toolkit (QST) Library\n")
            sys.stdout.write("Developed by Lead Quantum Software Engineers\n")
            sys.stdout.write("Supported Protocols: BB84\n")
            sys.stdout.write("Version: 0.1.0\n")
            return 0

        elif parsed_args.command == "simulate":
            handle_simulate(parsed_args)
            return 0

        elif parsed_args.command == "sweep":
            handle_sweep(parsed_args)
            return 0

        elif parsed_args.command == "export":
            handle_export(parsed_args)
            return 0

        elif parsed_args.command == "visualize":
            handle_visualize(parsed_args)
            return 0

        return 0

    except (ValidationError, QSTError) as e:
        sys.stderr.write(f"Validation Error: {str(e)}\n")
        return 1
    except FileNotFoundError as e:
        sys.stderr.write(f"File Error: {str(e)}\n")
        return 1
    except Exception as e:
        sys.stderr.write(f"Execution Error: {str(e)}\n")
        return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
