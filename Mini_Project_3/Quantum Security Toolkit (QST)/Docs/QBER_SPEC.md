# QBER_SPEC — Quantum Bit Error Rate Computation Contract

**Version:** 0.1.0 | **Last Updated:** 2026-07-22 | **Author:** ParaDise
**Status:** Planned (Pre-Development) | **References:** `BB84_SPEC.md`, `../docs/11_SECURITY_ARCHITECTURE.md`, `../docs/14_TESTING_STRATEGY.md`

---

## Purpose

Defines exactly how QBER (Quantum Bit Error Rate) and related security metrics are computed, so `SecurityAnalytics.compute_qber()` has a single unambiguous mathematical definition to implement against — this is the metric the entire pedagogical claim of the toolkit rests on (`../docs/11_SECURITY_ARCHITECTURE.md` §4).

## 1. Mathematical Definition

Given a sifted key of length `m` (post basis-reconciliation, per `BB84_SPEC.md` step 8), and a publicly-compared sample of size `k ≤ m`:

```
QBER = (number of mismatched bits in the sample) / k
```

Where a "mismatched bit" is an index `i` in the sample where `alice_bits[i] != bob_bits[i]`, after sifting has already restricted attention to indices where `alice_bases[i] == bob_bases[i]`.

## 2. Sample Selection

- The sample used to estimate QBER (step 9 of `BB84_SPEC.md`) MUST be selected uniformly at random from the sifted key, using the same seeded random source as the rest of the run (see `BB84_SPEC.md` §4), to keep the estimate unbiased and the whole run reproducible.
- **Sample size (`k`):** must be large enough for a statistically meaningful estimate but small enough to preserve most of the sifted key for the final shared key. A common convention is roughly half the sifted key, or a fixed absolute count with a floor (e.g., `min(m // 2, some_reasonable_cap)`) — the exact split ratio is **To Be Implemented/decided** during Phase 1 and must be documented as a named constant per `../docs/16_CODING_STANDARDS.md` §8 ("no magic numbers").
- The sampled bits are always discarded from the final key (per `BB84_SPEC.md` step 10) — they must never be reused as part of the final shared key, since they have been revealed over the public channel.

## 3. Key Rate Definition

```
key_rate = final_key_length / n_qubits
```

Where `final_key_length` is the sifted key length minus the sample size `k` used for QBER estimation (assuming the run is *not* aborted for excessive QBER — see §4).

## 4. Detection / Abort Threshold

- **Theoretical basis:** an intercept-resend eavesdropper capturing 100% of qubits introduces ~25% QBER (see `BB84_SPEC.md` §5, `../docs/11_SECURITY_ARCHITECTURE.md` §4). Real BB84 deployments typically define an abort threshold well below this (commonly cited in the literature in the low single-digit percent range to account for natural channel noise) above which the key exchange is aborted as compromised.
- **QST's stance:** for v1.0, QST computes and reports QBER and a `detection_probability` estimate (statistical confidence that observed QBER indicates eavesdropping vs. natural noise) but does **not** hard-code a specific literature abort-threshold percentage as a fixed constant, since QST uses an idealized/noiseless simulator baseline (no real channel noise) rather than a real fiber-optic channel with characterized background error rates. Implementing a literal "abort at X%" behavior with a specific numeric literature threshold would be presenting a borrowed number without QST-specific empirical grounding — a violation of `../docs/00_PROJECT_CONSTITUTION.md`'s no-fabrication principle if stated as if derived from QST's own validation.
- Instead: `SimulationResult` (see `../docs/10_API_SPECIFICATION.md` §5) surfaces the raw `qber` value and lets the caller (CLI, Educational Mode narration) apply and clearly attribute any illustrative threshold, explicitly labeled as an illustrative reference value rather than a QST-validated cutoff, pending real calibration (see `../docs/14_TESTING_STRATEGY.md` §9).

## 5. Detection Probability (Statistical Confidence)

`detection_probability` (per `../docs/07_SYSTEM_ARCHITECTURE.md` module diagram, `SecurityAnalytics.detection_probability()`) is planned to be computed via a standard statistical test comparing observed QBER against the no-eavesdropper baseline distribution (e.g., a binomial-proportion confidence interval or hypothesis test over the sample), rather than a fixed lookup table. Exact statistical test choice is **To Be Implemented** — candidates include a Wilson score interval or a simple one-sided binomial test against the expected noise-floor QBER.

## 6. Numerical Edge Cases

| Case | Required Behavior |
|---|---|
| `k = 0` (empty sample — e.g., sifted key too short) | `compute_qber()` must not divide by zero; returns `qber = None` or `0.0` with a `warning` (see `../docs/05_PRODUCT_REQUIREMENTS.md` EC-5) — exact choice between `None` and `0.0` is **To Be Implemented**, but must be consistent and documented in `../docs/10_API_SPECIFICATION.md` §5 once decided |
| `m = 0` (no sifted bits at all) | `key_rate = 0.0`; `final_key_length = 0`; a `warning` entry is added to `SimulationResult.warnings` |
| All sampled bits match (QBER = 0.0 exactly) | Valid, expected result when Eve is absent — must not be treated as an error |

## 7. Validation Criteria

1. `0.0 <= qber <= 1.0` always holds (property-based test target, `../docs/14_TESTING_STRATEGY.md` §5).
2. `key_rate` is always `<= 0.5` in expectation (since sifting alone discards ~50% of raw qubits before any QBER-sample discarding) — used as a property-based sanity check, not an exact bound.
3. QBER computed via §1's formula matches an independently hand-computed value for a small fixed example (e.g., `n=20`, fixed seed) — this fixed example becomes part of the Golden Dataset (`../docs/14_TESTING_STRATEGY.md` §8).

## Implementation Status

| Item | Status |
|---|---|
| This specification | Current (design-complete) |
| `compute_qber()`, `compute_key_rate()` | Planned |
| `detection_probability()` statistical method | Planned, exact test **To Be Implemented** |
| Abort-threshold behavior | Deliberately not hard-coded for v1.0 — see §4 |

## Future Improvements

- Calibrate and publish an empirically-derived (not borrowed) recommended abort threshold once enough simulated trial data exists to characterize QST's own noise floor (see §4).
