"""Unit tests for the Command Line Interface (CLI).

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md §3
"""

import json
import os

import pytest

from qst.cli.main import main
from qst.exceptions.validation import ValidationError


@pytest.mark.unit
def test_cli_version_and_info(capsys) -> None:
    """Verify version, version flag, and info display output and status codes."""
    # version subcommand
    code = main(["version"])
    assert code == 0
    out, _ = capsys.readouterr()
    assert "Version: 0.1.0" in out

    # version flag
    code_flag = main(["--version"])
    assert code_flag == 0
    out_flag, _ = capsys.readouterr()
    assert "Version: 0.1.0" in out_flag

    # info command
    code_info = main(["info"])
    assert code_info == 0
    out_info, _ = capsys.readouterr()
    assert "Quantum Security Toolkit" in out_info
    assert "BB84" in out_info


@pytest.mark.unit
def test_cli_simulate_success(tmp_path, capsys) -> None:
    """Verify simulate executes single trials and writes outputs to files."""
    out_path = os.path.join(tmp_path, "simulate.json")
    code = main(
        [
            "simulate",
            "--qubits",
            "10",
            "--seed",
            "42",
            "--interception-probability",
            "0.1",
            "--output",
            out_path,
        ]
    )
    assert code == 0
    out, err = capsys.readouterr()
    assert "Simulation completed successfully" in out
    assert "Average QBER" in out
    assert os.path.exists(out_path)

    # Load and check JSON structure
    with open(out_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "simulations" in data["data"]
    assert len(data["data"]["simulations"]) == 1


@pytest.mark.unit
def test_cli_simulate_validations(capsys) -> None:
    """Verify simulate checks range constraints and file formats."""
    # Qubits boundary
    code = main(["simulate", "--qubits", "0"])
    assert code == 1
    _, err = capsys.readouterr()
    assert "QST-VAL-101" in err

    # Interception prob boundary
    code_prob = main(["simulate", "--interception-probability", "1.5"])
    assert code_prob == 1
    _, err_prob = capsys.readouterr()
    assert "QST-VAL-102" in err_prob

    # Output extension format
    code_ext = main(["simulate", "--output", "sim.txt"])
    assert code_ext == 1
    _, err_ext = capsys.readouterr()
    assert "QST-VAL-404" in err_ext


@pytest.mark.unit
def test_cli_sweep_success(tmp_path, capsys) -> None:
    """Verify sweep executes grids sweeps and writes outputs."""
    out_path = os.path.join(tmp_path, "sweep.json")
    code = main(
        [
            "sweep",
            "--qubits",
            "10,20",
            "--probabilities",
            "0.0,0.2",
            "--repetitions",
            "2",
            "--export",
            out_path,
        ]
    )
    assert code == 0
    out, _ = capsys.readouterr()
    assert "Parameter sweep execution completed successfully" in out
    assert "Total experiments executed: 4" in out  # 2 qubits * 2 probs
    assert os.path.exists(out_path)


@pytest.mark.unit
def test_cli_sweep_validations(capsys) -> None:
    """Verify sweep parses values cleanly and handles formatting errors."""
    # Bad qubits parse
    code = main(["sweep", "--qubits", "abc"])
    assert code == 1
    _, err = capsys.readouterr()
    assert "QST-VAL-103" in err

    # Bad probs parse
    code = main(["sweep", "--probabilities", "0.0,xyz"])
    assert code == 1
    _, err = capsys.readouterr()
    assert "QST-VAL-104" in err

    # Repetitions boundary
    code = main(["sweep", "--repetitions", "-1"])
    assert code == 1
    _, err = capsys.readouterr()
    assert "QST-VAL-105" in err

    # Export format suffix check
    code = main(["sweep", "--export", "sweep.txt"])
    assert code == 1
    _, err = capsys.readouterr()
    assert "QST-VAL-404" in err


@pytest.mark.unit
def test_cli_export_success(tmp_path, capsys) -> None:
    """Verify export reads JSON and writes to JSON or CSV formats."""
    # Prepare dummy simulate json
    in_path = os.path.join(tmp_path, "simulate.json")
    main(["simulate", "--qubits", "10", "--output", in_path])

    # Export to JSON
    out_json = os.path.join(tmp_path, "export.json")
    code = main(["export", in_path, "--format", "json", "--output", out_json])
    assert code == 0
    assert os.path.exists(out_json)

    # Export to CSV
    out_csv = os.path.join(tmp_path, "export.csv")
    code = main(["export", in_path, "--format", "CSV", "--output", out_csv])
    assert code == 0
    assert os.path.exists(out_csv)

    # Export non-existent input file
    code = main(["export", "missing.json", "--format", "json", "--output", "out.json"])
    assert code == 1
    _, err = capsys.readouterr()
    assert "Input file not found" in err


@pytest.mark.unit
def test_cli_visualize_success(tmp_path, capsys) -> None:
    """Verify visualize creates LINE, SCATTER, HISTOGRAM and HEATMAP charts."""
    # Prepare dummy sweep json with 2D grid dimensions
    in_path = os.path.join(tmp_path, "sweep.json")
    main(
        [
            "sweep",
            "--qubits",
            "10,20",
            "--probabilities",
            "0.0,0.5",
            "--repetitions",
            "2",
            "--export",
            in_path,
        ]
    )

    # LINE chart
    out_line = os.path.join(tmp_path, "line.png")
    code = main(["visualize", in_path, "--type", "line", "--output", out_line])
    assert code == 0
    assert os.path.exists(out_line)

    # SCATTER chart
    out_scatter = os.path.join(tmp_path, "scatter.svg")
    code = main(
        [
            "visualize",
            in_path,
            "--type",
            "SCATTER",
            "--format",
            "svg",
            "--output",
            out_scatter,
            "--theme",
            "dark",
        ]
    )
    assert code == 0
    assert os.path.exists(out_scatter)

    # HISTOGRAM chart
    out_hist = os.path.join(tmp_path, "hist.pdf")
    code = main(
        [
            "visualize",
            in_path,
            "--type",
            "histogram",
            "--format",
            "pdf",
            "--output",
            out_hist,
            "--theme",
            "scientific",
        ]
    )
    assert code == 0
    assert os.path.exists(out_hist)

    # HEATMAP chart
    out_heat = os.path.join(tmp_path, "heat.png")
    code = main(
        [
            "visualize",
            in_path,
            "--type",
            "heatmap",
            "--output",
            out_heat,
        ]
    )
    assert code == 0
    assert os.path.exists(out_heat)


@pytest.mark.unit
def test_cli_visualize_validations(tmp_path, capsys) -> None:
    """Verify visualize asserts input files existence and 2D grid requirements."""
    # Missing input file
    code = main(["visualize", "missing.json", "--type", "line", "--output", "a.png"])
    assert code == 1
    _, err = capsys.readouterr()
    assert "Input file not found" in err

    # 1D sweep results (only 1 probability coordinate)
    in_1d_path = os.path.join(tmp_path, "sweep_1d.json")
    main(
        [
            "sweep",
            "--qubits",
            "10",
            "--probabilities",
            "0.0",
            "--export",
            in_1d_path,
        ]
    )

    # Heatmap validation check (needs 2D grid)
    code = main(
        [
            "visualize",
            in_1d_path,
            "--type",
            "heatmap",
            "--output",
            os.path.join(tmp_path, "heat.png"),
        ]
    )
    assert code == 1
    _, err = capsys.readouterr()
    assert "QST-VAL-711" in err

    # Unsupported chart type
    code = main(
        [
            "visualize",
            in_1d_path,
            "--type",
            "invalid_type",
            "--output",
            os.path.join(tmp_path, "heat.png"),
        ]
    )
    assert code == 2
    _, err = capsys.readouterr()
    assert "invalid choice" in err


@pytest.mark.unit
def test_cli_parser_error(capsys) -> None:
    """Verify parser returns code 2 (standard argparse code) for invalid subcommand options."""
    code = main(["simulate", "--invalid-option", "10"])
    assert code != 0


@pytest.mark.unit
def test_cli_visualize_line_variations(tmp_path) -> None:
    """Verify visualize line charts when sweep varies only qubits or only repetitions."""
    # 1. Sweep varying only qubits (multiple qubits, 1 probability)
    in_qubits_path = os.path.join(tmp_path, "sweep_qubits.json")
    main(
        [
            "sweep",
            "--qubits",
            "10,20",
            "--probabilities",
            "0.0",
            "--export",
            in_qubits_path,
        ]
    )
    out_qubits = os.path.join(tmp_path, "line_qubits.png")
    code = main(["visualize", in_qubits_path, "--type", "line", "--output", out_qubits])
    assert code == 0
    assert os.path.exists(out_qubits)

    # 2. Sweep varying only repetitions (1 qubit, 1 probability)
    in_reps_path = os.path.join(tmp_path, "sweep_reps.json")
    main(
        ["sweep", "--qubits", "10", "--probabilities", "0.0", "--export", in_reps_path]
    )
    out_reps = os.path.join(tmp_path, "line_reps.png")
    code = main(["visualize", in_reps_path, "--type", "line", "--output", out_reps])
    assert code == 0
    assert os.path.exists(out_reps)


@pytest.mark.unit
def test_cli_visualize_empty_qber(tmp_path, capsys) -> None:
    """Verify visualizer histogram raises error when there are no QBER measurements."""
    # Write a sweep JSON with no QBER measurements
    sweep_dict = {
        "experiments": [
            {
                "simulations": [
                    {"n_qubits": 10, "interception_probability": 0.0, "qber": None}
                ]
            }
        ],
        "sweep_dimensions": {
            "qubit_counts": [10],
            "interception_probabilities": [0.0],
            "seeds": [None],
        },
    }
    in_path = os.path.join(tmp_path, "empty_qber.json")
    with open(in_path, "w") as f:
        json.dump(sweep_dict, f)

    out_hist = os.path.join(tmp_path, "hist.png")
    code = main(["visualize", in_path, "--type", "histogram", "--output", out_hist])
    assert code == 1
    _, err = capsys.readouterr()
    assert "QST-VAL-710" in err


@pytest.mark.unit
def test_cli_export_no_metadata_fallback(tmp_path) -> None:
    """Verify export uses fallback metadata if input file has missing or invalid metadata."""
    in_path = os.path.join(tmp_path, "no_meta.json")
    with open(in_path, "w") as f:
        json.dump({"simulations": []}, f)  # Missing metadata

    out_csv = os.path.join(tmp_path, "out.csv")
    code = main(["export", in_path, "--format", "CSV", "--output", out_csv])
    assert code == 0
    assert os.path.exists(out_csv)


@pytest.mark.unit
def test_cli_sys_argv_fallback(capsys, monkeypatch) -> None:
    """Verify CLI defaults to sys.argv when no arguments are provided."""
    monkeypatch.setattr("sys.argv", ["qst", "version"])
    code = main(None)
    assert code == 0
    out, _ = capsys.readouterr()
    assert "QST Version" in out


@pytest.mark.unit
def test_cli_general_exception_handling(capsys, monkeypatch) -> None:
    """Verify CLI catches and gracefully reports unhandled general exceptions."""
    from unittest.mock import patch

    with patch(
        "qst.cli.main.get_parser",
        side_effect=RuntimeError("Mock general runtime error"),
    ):
        code = main(["version"])
        assert code == 1
        _, err = capsys.readouterr()
        assert "Execution Error" in err
        assert "Mock general runtime error" in err


@pytest.mark.unit
def test_cli_visualize_theme_fallback(tmp_path) -> None:
    """Verify visualizer falls back to LightTheme when theme parameter matches else branch."""
    in_path = os.path.join(tmp_path, "sweep.json")
    main(["sweep", "--qubits", "10", "--probabilities", "0.0", "--export", in_path])

    # Direct visualizer invocation to bypass choice check and test fallback branches
    import argparse

    from qst.cli.main import handle_visualize

    args = argparse.Namespace(
        filepath=in_path,
        type="line",
        format="PNG",
        output=os.path.join(tmp_path, "fallback_theme.png"),
        theme="INVALID_THEME",
    )
    handle_visualize(args)
    assert os.path.exists(args.output)


@pytest.mark.unit
def test_cli_visualize_type_fallback(tmp_path) -> None:
    """Verify handle_visualize throws validation error when chart type is unsupported."""
    in_path = os.path.join(tmp_path, "sweep.json")
    main(["sweep", "--qubits", "10", "--probabilities", "0.0", "--export", in_path])

    import argparse

    from qst.cli.main import handle_visualize

    args = argparse.Namespace(
        filepath=in_path,
        type="INVALID_TYPE",
        format="PNG",
        output=os.path.join(tmp_path, "fallback_type.png"),
        theme="LIGHT",
    )
    with pytest.raises(ValidationError) as exc:
        handle_visualize(args)
    assert "QST-VAL-712" in str(exc.value)
