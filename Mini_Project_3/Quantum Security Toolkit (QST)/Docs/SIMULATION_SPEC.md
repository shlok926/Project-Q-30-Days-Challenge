# SIMULATION_SPEC — SimulationOrchestrator Implementation Contract

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `BB84_SPEC.md`, `QBER_SPEC.md`, `../docs/07_SYSTEM_ARCHITECTURE.md`, `../docs/10_API_SPECIFICATION.md`

---

## Purpose

Defines the contract for `SimulationOrchestrator` — the composition-root class that wires together `BB84Protocol`, `Eavesdropper`, and `SecurityAnalytics` (per `../docs/07_SYSTEM_ARCHITECTURE.md` §7 Dependency Rules) into the single/batch run entrypoints exposed by the public API (`../docs/10_API_SPECIFICATION.md`).

## 1. Responsibilities

`SimulationOrchestrator` MUST:

- Validate all input parameters before invoking any protocol logic (per `../docs/05_PRODUCT_REQUIREMENTS.md` FR-13, raising `ValidationError` per `../docs/10_API_SPECIFICATION.md` §6).
- Construct and run one `BB84Protocol` instance per simulation trial, optionally wired to an `Eavesdropper` instance.
- Collect protocol output and pass it to `SecurityAnalytics` for QBER/key-rate computation (per `QBER_SPEC.md`).
- Assemble and return a `SimulationResult` (per `../docs/10_API_SPECIFICATION.md` §5) for single runs, or a collection thereof for batch runs.
- Never contain BB84 protocol logic itself — it orchestrates, it does not implement (see `../docs/07_SYSTEM_ARCHITECTURE.md` §7).

`SimulationOrchestrator` MUST NOT:

- Import from `visualization/` or `cli/` directly for its core `run()`/`run_research_batch()` logic — narration/visualization are invoked by the caller (CLI layer), not embedded inside the orchestrator's core path, to keep it usable head-lessly (e.g., from a Jupyter notebook without triggering CLI-only side effects).

## 2. Registry / Extension Point Wiring

Per `../docs/07_SYSTEM_ARCHITECTURE.md` §8, `SimulationOrchestrator` depends on `ProtocolInterface`, not `BB84Protocol` concretely. Planned wiring mechanism:

```python
# Planned reference shape — illustrative, not final code.
PROTOCOL_REGISTRY = {
    "bb84": BB84Protocol,
    # "e91": E91Protocol,  # Future
}

class SimulationOrchestrator:
    def __init__(self, protocol_name: str = "bb84", **kwargs):
        protocol_cls = PROTOCOL_REGISTRY[protocol_name]
        self._protocol = protocol_cls(**kwargs)
```

A simple dict-based registry is proposed over Python entry-point plugin discovery for v1.0, since entry-point-based plugin loading adds packaging complexity not justified until third-party protocol plugins are an actual, requested use case (see `../docs/20_FUTURE_ENHANCEMENTS.md`). This choice should be logged as an ADR in `../docs/18_DECISION_LOG.md` if/when it is deliberately finalized during implementation.

## 3. Single-Run Contract (`run_educational` / library `run()`)

| Step | Behavior |
|---|---|
| 1 | Validate parameters (§1) |
| 2 | Construct `BB84Protocol` (+ `Eavesdropper` if `eve_intercept_probability > 0`) |
| 3 | Execute the protocol per `BB84_SPEC.md` §1 |
| 4 | Pass sifted output to `SecurityAnalytics` per `QBER_SPEC.md` |
| 5 | Assemble `SimulationResult` |
| 6 | If Educational Mode: emit narration hooks at each step boundary (see §5) |
| 7 | Return `SimulationResult` to caller |

## 4. Batch-Run Contract (`run_research_batch`)

```python
# Planned reference shape — illustrative, not final code.
def run_research_batch(self, param_sweep: list[dict]) -> list[SimulationResult]:
    results = []
    for params in param_sweep:
        try:
            results.append(self.run(**params))
        except QSTError as e:
            # continue-vs-abort policy — see 07_SYSTEM_ARCHITECTURE.md §11 Failure Recovery
            results.append(self._error_result(params, e))
    return results
```

- Each parameter combination in `param_sweep` is run independently; a failure in one combination must not silently corrupt or block others (per `../docs/07_SYSTEM_ARCHITECTURE.md` §11 Failure Recovery — exact continue-vs-abort default is **To Be Implemented**, but must be a configurable flag, defaulting to "continue and record the error" for research-usability).
- Batch results feed directly into the export contract defined in `EXPORT_SPEC.md`.

## 5. Narration Hook Contract (Educational Mode)

Per `../docs/07_SYSTEM_ARCHITECTURE.md` §6 (Observer pattern), Educational Mode narration must be implemented as **hooks the orchestrator calls at defined step boundaries**, not as print statements embedded inside `BB84Protocol` itself:

| Hook | Fires After |
|---|---|
| `on_bits_generated` | Step 1-2 of `BB84_SPEC.md` |
| `on_qubits_prepared` | Step 3 |
| `on_eve_intercepted` (only if Eve enabled) | Step 4/§5 of `BB84_SPEC.md` |
| `on_measured` | Step 6 |
| `on_sifted` | Step 8 |
| `on_qber_estimated` | Step 9 / `QBER_SPEC.md` |
| `on_key_finalized` | Step 10 |

A default CLI narrator implementation subscribes to these hooks to print human-readable descriptions; a caller not interested in narration (e.g., Research Mode) simply does not attach a narrator, and the core run path executes identically either way — this is the mechanism that keeps `core/` (per `../docs/07_SYSTEM_ARCHITECTURE.md` §7) free of any UI concerns.

## 6. Determinism Contract

Given identical `(protocol_name, n_qubits, seed, eve_intercept_probability, ...)` arguments, `SimulationOrchestrator.run()` MUST return a `SimulationResult` with identical `qber`, `final_key_length`, `key_rate`, and `sifted_key` fields across repeated invocations — this is the direct implementation target for FR-12 and is verified by `test_reproducibility_with_seed` (`../docs/14_TESTING_STRATEGY.md` §3).

## 7. Validation Criteria

1. Invalid parameters raise `ValidationError` before any `BB84Protocol` object is constructed (no partial/wasted simulation work — see `../docs/07_SYSTEM_ARCHITECTURE.md` §11).
2. A batch run with one deliberately-invalid parameter set among otherwise-valid ones completes for all valid entries and records the error for the invalid one, per §4.
3. Narration hooks (§5) fire in the exact step order listed, verified by an integration test subscribing a test-double narrator and asserting call order.

## Implementation Status

| Item | Status |
|---|---|
| This specification | Current (design-complete) |
| `SimulationOrchestrator` core (`run`) | Planned |
| Batch mode (`run_research_batch`) | Planned |
| Narration hooks | Planned |
| Protocol registry mechanism | Planned (dict-based proposal; may become an ADR) |

## Future Improvements

- Migrate the protocol registry (§2) to an entry-point-based plugin system if/when third-party protocol contributions become a real, requested pattern.
