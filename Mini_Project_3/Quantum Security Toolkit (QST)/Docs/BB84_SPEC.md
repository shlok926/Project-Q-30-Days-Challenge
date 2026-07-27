# BB84_SPEC — BB84 Protocol Implementation Contract

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `../docs/07_SYSTEM_ARCHITECTURE.md`, `../docs/11_SECURITY_ARCHITECTURE.md`

---

## Purpose

This is the **implementation contract** for `BB84Protocol` — precise enough that a contributor could implement it without needing to re-derive the protocol from a textbook, and precise enough that a reviewer can check an implementation against it line-by-line. It is more granular than `docs/07_SYSTEM_ARCHITECTURE.md` (which covers module boundaries) and more implementation-focused than `docs/11_SECURITY_ARCHITECTURE.md` (which covers the security properties, not the step-by-step algorithm).

## Scope

Covers the core BB84 key-exchange algorithm only (Alice/Bob, no eavesdropper). Eavesdropper behavior is specified separately in this same document's §5 for cohesion, since it operates directly on the qubits mid-protocol; QBER computation is owned by `QBER_SPEC.md`.

## 1. Protocol Steps (Normative)

| Step | Actor | Operation |
|---|---|---|
| 1 | Alice | Generate `n` random classical bits: `alice_bits[i] ∈ {0, 1}` |
| 2 | Alice | Generate `n` random bases: `alice_bases[i] ∈ {Z, X}` (rectilinear/diagonal) |
| 3 | Alice | Prepare qubit `i` by encoding `alice_bits[i]` in `alice_bases[i]` |
| 4 | (Eve, optional) | See §5 |
| 5 | Bob | Generate `n` random bases: `bob_bases[i] ∈ {Z, X}` |
| 6 | Bob | Measure qubit `i` in `bob_bases[i]`, record `bob_bits[i]` |
| 7 | Alice & Bob | Publicly compare `alice_bases` and `bob_bases` (classical channel, assumed authenticated per `docs/11_SECURITY_ARCHITECTURE.md` §3) |
| 8 | Alice & Bob | Sift: keep only indices where `alice_bases[i] == bob_bases[i]` |
| 9 | Alice & Bob | Sample a subset of the sifted key to publicly compare and estimate QBER (see `QBER_SPEC.md`) |
| 10 | Alice & Bob | Discard the sampled/compared bits; remaining bits form the final key |

## 2. Qubit Encoding Convention

| Basis | Bit 0 | Bit 1 |
|---|---|---|
| Z (rectilinear) | `\|0⟩` | `\|1⟩` |
| X (diagonal) | `\|+⟩ = (\|0⟩+\|1⟩)/√2` | `\|-⟩ = (\|0⟩-\|1⟩)/√2` |

Implementation must use this exact encoding so that basis mismatch produces the standard 50% measurement-disturbance probability required by `docs/11_SECURITY_ARCHITECTURE.md` §4.

## 3. Qiskit Circuit Construction (Reference Pseudocode)

```python
# Planned reference implementation shape — illustrative, not final code.
from qiskit import QuantumCircuit

def prepare_qubit(bit: int, basis: str) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    if bit == 1:
        qc.x(0)
    if basis == "X":
        qc.h(0)
    return qc

def measure_qubit(qc: QuantumCircuit, basis: str) -> QuantumCircuit:
    if basis == "X":
        qc.h(0)  # rotate back to computational basis before measuring
    qc.measure(0, 0)
    return qc
```

This is illustrative and must be validated against Qiskit's actual API surface at implementation time (exact method signatures are **To Be Verified** against the pinned Qiskit version, per `docs/06_TECHNICAL_REQUIREMENTS.md` §8).

## 4. Randomness Requirements

- All random bit/basis generation MUST accept an optional `seed` parameter (per `docs/05_PRODUCT_REQUIREMENTS.md` FR-12) and MUST use a single, consistently-seeded random source per simulation run (e.g., a `numpy.random.Generator` instance, not the global `numpy.random` state) — using the global state risks cross-run/cross-test contamination and non-reproducibility, which would silently violate FR-12's acceptance criteria.
- Basis choice and bit choice must be independently random (uniform, unbiased) — a biased basis choice would distort the expected ~50% sifting rate and confound QBER interpretation.

## 5. Eavesdropper (Eve) Behavior — Intercept-Resend Model

| Step | Operation |
|---|---|
| E1 | For each qubit in transit, with probability `eve_intercept_probability`, Eve intercepts it |
| E2 | If intercepted: Eve generates her own random basis `eve_basis[i] ∈ {Z, X}` |
| E3 | Eve measures the qubit in `eve_basis[i]`, obtaining a classical bit `eve_bit[i]` |
| E4 | Eve re-prepares a new qubit encoding `eve_bit[i]` in `eve_basis[i]` and forwards it to Bob |
| E5 | If not intercepted: the original qubit passes to Bob unmodified |

**Critical correctness requirement:** Step E4 must re-prepare the qubit based on Eve's *own* measurement outcome and basis — NOT pass through Alice's original qubit unchanged, and NOT use Alice's original bit/basis (which Eve does not have access to). This is what correctly introduces the ~25% QBER on intercepted qubits when Eve's basis differs from Alice's (50% of the time), each contributing a 50% chance of Bob observing a flipped bit relative to Alice's original — the source of the theoretical ~25% aggregate QBER referenced in `docs/11_SECURITY_ARCHITECTURE.md` §4 and `docs/05_PRODUCT_REQUIREMENTS.md` §10.

## 6. Validation Criteria

An implementation is considered spec-compliant when:

1. With `eve_intercept_probability = 0.0`, sifted-key QBER (before intentional test corruption) is near the simulator's numerical noise floor across repeated seeded trials.
2. With `eve_intercept_probability = 1.0`, mean sifted-key QBER across many trials falls within statistical tolerance of 25% (see `docs/14_TESTING_STRATEGY.md` §9 for the validation methodology).
3. Sifted key length, in expectation, is approximately `n/2` (since Alice/Bob bases match independently with 50% probability) — exact tolerance is a statistical check, not an exact-equality check, per `docs/14_TESTING_STRATEGY.md` §5.
4. Given identical `(n_qubits, seed, eve_intercept_probability)`, two runs produce bit-identical output (FR-12 reproducibility).

## 7. Edge Cases (Protocol-Specific)

See `docs/05_PRODUCT_REQUIREMENTS.md` §6 for the full edge-case list (EC-1 through EC-7); this spec adds one protocol-specific note:

- **EC-8 (new):** If `eve_intercept_probability` is strictly between 0 and 1, Eve's interception decision per-qubit must be independently random (not, e.g., "intercept exactly the first `p*n` qubits") — a deterministic subset would not correctly model a probabilistic eavesdropper and would bias QBER estimation if the sample (step 9) happens to overlap non-uniformly with intercepted qubits.

## Implementation Status

| Item | Status |
|---|---|
| This specification | Current (design-complete) |
| `BB84Protocol` implementation | Planned |
| Validation against §6 criteria | To Be Implemented |

## Future Improvements

- Extend this spec with an `E91Protocol` sibling document once entanglement-based QKD is prioritized (see `../docs/20_FUTURE_ENHANCEMENTS.md`).
