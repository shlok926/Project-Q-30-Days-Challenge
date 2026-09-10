"""End-to-End Command Line Interface (CLI) Pipeline tests.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md
"""

import os

import pytest

from qst.cli.main import main


@pytest.mark.e2e
def test_cli_pipeline_simulate_command(tmp_path, capsys) -> None:
    """Verify 'qst simulate' command executes successfully with spaced and relative paths."""
    out_dir = os.path.join(tmp_path, "spaced folder name")
    os.makedirs(out_dir, exist_ok=True)
    out_json = os.path.join(out_dir, "simulation_results.json")

    # Spaced path check
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
            out_json,
        ]
    )
    assert code == 0
    out, err = capsys.readouterr()
    assert "Simulation completed successfully" in out
    assert "Average QBER" in out
    assert os.path.exists(out_json)

    # Relative path check (clean up after run)
    rel_json = "rel_simulation.json"
    if os.path.exists(rel_json):
        os.remove(rel_json)

    try:
        code_rel = main(
            [
                "simulate",
                "--qubits",
                "10",
                "--seed",
                "42",
                "--interception-probability",
                "0.1",
                "--output",
                rel_json,
            ]
        )
        assert code_rel == 0
        out_rel, _ = capsys.readouterr()
        assert "Simulation completed successfully" in out_rel
        assert os.path.exists(rel_json)
    finally:
        if os.path.exists(rel_json):
            os.remove(rel_json)


@pytest.mark.e2e
def test_cli_pipeline_sweep_and_visualize_paths(tmp_path, capsys) -> None:
    """Verify 'qst sweep' and 'qst visualize' work with cross-platform and spaced separators."""
    # Create output paths using Windows and POSIX separators
    out_sweep_win = os.path.join(
        tmp_path, "spaced sweep folder", "sweep_win.json"
    ).replace("/", "\\")
    out_sweep_posix = os.path.join(
        tmp_path, "spaced sweep folder", "sweep_posix.json"
    ).replace("\\", "/")

    # Ensure parent dir exists
    os.makedirs(os.path.dirname(out_sweep_win), exist_ok=True)

    # Exec qst sweep (Windows separators)
    code_win = main(
        [
            "sweep",
            "--qubits",
            "10,20",
            "--probabilities",
            "0.0,0.5",
            "--repetitions",
            "2",
            "--export",
            out_sweep_win,
        ]
    )
    assert code_win == 0
    out_win, _ = capsys.readouterr()
    assert "Parameter sweep execution completed successfully" in out_win
    assert os.path.exists(out_sweep_win)

    # Exec qst sweep (POSIX separators)
    code_posix = main(
        [
            "sweep",
            "--qubits",
            "10,20",
            "--probabilities",
            "0.0,0.5",
            "--repetitions",
            "2",
            "--export",
            out_sweep_posix,
        ]
    )
    assert code_posix == 0
    assert os.path.exists(out_sweep_posix)

    # Visualize LINE chart (Windows path)
    out_plot_win = os.path.join(tmp_path, "plots", "line_chart.png").replace("/", "\\")
    code_vis_win = main(
        [
            "visualize",
            out_sweep_win,
            "--type",
            "line",
            "--output",
            out_plot_win,
        ]
    )
    assert code_vis_win == 0
    out_vis, _ = capsys.readouterr()
    assert "Chart successfully saved to path" in out_vis
    assert os.path.exists(out_plot_win)


@pytest.mark.e2e
def test_cli_pipeline_export_command(tmp_path, capsys) -> None:
    """Verify 'qst export' command correctly translates files and raises helpful validation errors."""
    in_json = os.path.join(tmp_path, "simulate_source.json")
    code_sim = main(
        [
            "simulate",
            "--qubits",
            "10",
            "--output",
            in_json,
        ]
    )
    assert code_sim == 0
    capsys.readouterr()

    # Valid export CSV
    out_csv = os.path.join(tmp_path, "export_dest.csv")
    code_exp = main(
        [
            "export",
            in_json,
            "--format",
            "csv",
            "--output",
            out_csv,
        ]
    )
    assert code_exp == 0
    assert os.path.exists(out_csv)

    # Validation Error Check (invalid command arguments or parameters)
    code_err = main(
        [
            "simulate",
            "--qubits",
            "-5",
        ]
    )
    assert code_err == 1
    _, err = capsys.readouterr()
    assert "Qubit count must be positive" in err

    # File Error Check (missing file paths)
    code_missing = main(
        [
            "export",
            "nonexistent_file_path.json",
            "--format",
            "json",
            "--output",
            "dest.json",
        ]
    )
    assert code_missing == 1
    _, err_missing = capsys.readouterr()
    assert "File Error: Input file not found" in err_missing
