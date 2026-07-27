---
name: Bug Report
about: Report unexpected or incorrect behavior
title: "[Bug] "
labels: bug
assignees: ''
---

## Description

A clear, concise description of what went wrong.

## Reproduction

**Please include the exact parameters used, per `docs/../specs/SIMULATION_SPEC.md` §6's Determinism Contract — a bug report without a seed is much harder to reproduce.**

```python
# Example:
from qst.orchestration import SimulationOrchestrator

orchestrator = SimulationOrchestrator(
    n_qubits=...,
    seed=...,
    eve_intercept_probability=...,
)
result = orchestrator.run()
```

Or, if using the CLI:

```bash
qst simulate --qubits ... --seed ... --eve-prob ...
```

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened. Include the full error message/traceback if applicable.

## Diagnostic Info

If possible, run with `--diagnose` (see `docs/30_OBSERVABILITY.md` §8) and paste the output here:

```
(paste --diagnose output)
```

Otherwise, please provide manually:

- QST version:
- Qiskit version:
- Python version:
- OS:

## Additional Context

Anything else relevant — e.g., does this affect `core/` (BB84Protocol/Eavesdropper)? If so, please flag this explicitly, since core-logic bugs are treated as highest priority (see `docs/29_THREAT_MODEL.md` §11).
