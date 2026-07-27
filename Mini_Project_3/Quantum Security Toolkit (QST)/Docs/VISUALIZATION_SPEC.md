# VISUALIZATION_SPEC — Visualizer Implementation Contract

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `QBER_SPEC.md`, `../docs/12_UI_UX_DESIGN.md`, `../docs/07_SYSTEM_ARCHITECTURE.md`

---

## Purpose

Defines the exact inputs, outputs, and rendering contract for `Visualizer`, so plots are reproducible, accessible (per `../docs/12_UI_UX_DESIGN.md` §4), and decoupled from `SecurityAnalytics`'s internal data structures (per `../docs/07_SYSTEM_ARCHITECTURE.md` §7 Dependency Rules — `visualization/` depends on `analytics/` output, never on `core/` internals directly).

## 1. Required Visualizations (v1.0)

| Visualization | Input | Output |
|---|---|---|
| Basis/measurement table | `alice_bases`, `bob_bases`, `alice_bits`, `bob_bits`, sifted mask (from `BB84Protocol` output, passed through `SimulationResult`) | A rendered table (CLI text table or `matplotlib` table) showing per-qubit basis match/mismatch |
| QBER vs. interception-probability chart | A list of `(eve_intercept_probability, qber)` pairs, typically from a batch run (`SIMULATION_SPEC.md` §4) | A line/scatter chart with interception probability on the x-axis and QBER on the y-axis |

## 2. Data Contract

`Visualizer` functions MUST accept only the public fields of `SimulationResult` (`../docs/10_API_SPECIFICATION.md` §5) or an explicit list thereof (for the sweep chart) — never `BB84Protocol` or `Eavesdropper` internal objects directly. This is the concrete mechanism enforcing the "Facade"/"Dependency Rules" architecture decisions in `../docs/07_SYSTEM_ARCHITECTURE.md` §6–7.

```python
# Planned reference signatures — illustrative, not final code.
def render_basis_table(result: SimulationResult) -> str: ...
def plot_qber_vs_interception(results: list[SimulationResult]) -> "matplotlib.figure.Figure": ...
```

## 3. Accessibility Requirements (Normative)

Per `../docs/12_UI_UX_DESIGN.md` §4:

- Charts MUST include descriptive titles and axis labels sufficient to be understood without color (e.g., "QBER vs. Eve Interception Probability", x-axis "Interception Probability (0.0–1.0)", y-axis "QBER (%)").
- Any pass/fail or threshold indication (e.g., "likely eavesdropping detected") MUST use a text label in addition to color, never color alone.
- CLI-rendered tables MUST remain legible in a non-color terminal — no reliance on ANSI color codes to convey the only copy of essential information.

## 4. Reproducibility of Plots

Given the same `SimulationResult` (or list thereof), `Visualizer` functions MUST produce visually identical output (same data plotted the same way) — visualization introduces no additional randomness of its own. Any illustrative annotation (e.g., a reference line at the theoretical 25% QBER value) must be clearly labeled as a reference/illustrative marker, not implied to be an empirically-derived QST threshold (see `QBER_SPEC.md` §4 on avoiding borrowed, unlabeled thresholds).

## 5. Output Formats

| Context | Format |
|---|---|
| CLI (Educational Mode) | Text-rendered table (basis table) + optionally saved static image (chart) if `--output-dir` is specified |
| Notebook/library use | Native `matplotlib`/`plotly` figure objects returned directly for further manipulation by the user |
| Batch export | Charts are not embedded in CSV/JSON export (see `EXPORT_SPEC.md`) — export is data-only; regenerating a chart from exported data is left to the user's own tooling, keeping `EXPORT_SPEC.md` and this spec cleanly separated |

## 6. Validation Criteria

1. `render_basis_table()` output row count equals `n_qubits` (or is clearly truncated with an explicit "... N more rows" indicator for very large `n_qubits`, to avoid unusably long CLI output — exact truncation threshold **To Be Implemented**).
2. `plot_qber_vs_interception()` renders one point per input `SimulationResult`, with x-values matching each result's `eve_intercept_probability` field exactly.
3. No `Visualizer` function raises an exception for a valid `SimulationResult` with `warnings` set (e.g., an empty-key result per `QBER_SPEC.md` §6) — it must render a valid, if visually sparse, output rather than crashing.

## Implementation Status

| Item | Status |
|---|---|
| This specification | Current (design-complete) |
| `render_basis_table()` | Planned |
| `plot_qber_vs_interception()` | Planned |
| Bloch-sphere visualization | Future (per `../docs/12_UI_UX_DESIGN.md` §6) |

## Future Improvements

- Add an interactive Bloch-sphere visualization spec once that Future UI feature (`../docs/12_UI_UX_DESIGN.md` §6, `../docs/20_FUTURE_ENHANCEMENTS.md`) is prioritized.
