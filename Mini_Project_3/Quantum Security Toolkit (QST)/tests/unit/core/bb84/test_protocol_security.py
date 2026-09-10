"""Unit tests validating the complete QKD BB84 Protocol integration with eavesdropping, QBER, and security metrics.

References:
    Docs/BB84_SPEC.md §1, §5
    Docs/10_API_SPECIFICATION.md §5
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.core.bb84.protocol import BB84Protocol
from qst.models.results import SecurityStatus, SimulationResult


@pytest.mark.unit
def test_bb84_protocol_no_eavesdropping() -> None:
    """Verify QKD simulation runs with no eavesdropper (interception = 0.0).

    Should yield QBER ≈ 0.0 and secure status.
    """
    protocol = BB84Protocol()
    protocol.initialize(n_qubits=20, seed=123, eve_intercept_probability=0.0)
    protocol.execute()
    protocol.measure()

    res = protocol.export()
    assert isinstance(res, SimulationResult)
    assert res.eve_intercept_probability == 0.0
    assert res.interception_probability == 0.0
    assert res.eve_simulation is None
    assert res.qber_result is not None
    assert res.qber_result.qber == 0.0
    assert res.qber_result.error_count == 0
    assert res.security_metrics is not None
    assert res.security_metrics.status == SecurityStatus.SECURE
    assert res.qber == 0.0

    # Alice's sifted key matches Bob's sifted key perfectly
    assert res.sifted_keys is not None
    assert res.sifted_keys.alice_key == res.sifted_keys.bob_key

    # Assert getters on protocol directly
    assert protocol.eve_intercept_probability == 0.0
    assert protocol.eve_simulation is None
    assert protocol.qber_result is not None
    assert protocol.security_metrics is not None


@pytest.mark.unit
def test_bb84_protocol_full_eavesdropping() -> None:
    """Verify QKD simulation runs under complete eavesdropper attack (interception = 1.0).

    Under intercept-resend, Eve measures every qubit.
    For matching bases (Z/Z or X/X), Alice and Bob only match if Alice-Eve match and Eve-Bob match,
    or Alice-Eve mismatch and Eve-Bob mismatch.
    This creates an expected QBER of ≈ 25% on the reconciled key, yielding a Compromised status.
    """
    protocol = BB84Protocol()
    protocol.initialize(n_qubits=20, seed=42, eve_intercept_probability=1.0)
    protocol.execute()
    protocol.measure()

    res = protocol.export()
    assert res.eve_intercept_probability == 1.0
    assert res.eve_simulation is not None
    assert all(res.eve_simulation.intercepted_mask)

    assert res.qber_result is not None
    # QBER should be around 25%. For n_qubits=20, with seed=42, let's verify it exceeds secure bounds (QBER > 11%)
    assert res.qber_result.qber > 0.11
    assert res.security_metrics is not None
    assert res.security_metrics.status == SecurityStatus.COMPROMISED


@pytest.mark.unit
def test_bb84_protocol_partial_eavesdropping() -> None:
    """Verify simulation behavior under partial interception probability (interception = 0.5)."""
    protocol = BB84Protocol()
    protocol.initialize(n_qubits=16, seed=999, eve_intercept_probability=0.5)
    protocol.execute()
    protocol.measure()

    res = protocol.export()
    assert res.eve_intercept_probability == 0.5
    assert res.eve_simulation is not None
    # Some qubits should be intercepted, some not
    assert any(res.eve_simulation.intercepted_mask)
    assert not all(res.eve_simulation.intercepted_mask)


@pytest.mark.unit
def test_bb84_protocol_security_determinism() -> None:
    """Verify that runs with the same configuration and seed yield identical result contents."""
    p1 = BB84Protocol()
    p1.initialize(n_qubits=25, seed=12345, eve_intercept_probability=0.6)
    p1.execute()
    p1.measure()
    res1 = p1.export()

    p2 = BB84Protocol()
    p2.initialize(n_qubits=25, seed=12345, eve_intercept_probability=0.6)
    p2.execute()
    p2.measure()
    res2 = p2.export()

    # Verify identical values are reconstructed and sifted
    assert res1.alice_bits == res2.alice_bits
    assert res1.bob_bits == res2.bob_bits
    assert res1.sifted_key == res2.sifted_key
    assert res1.qber == res2.qber
    assert res1.security_metrics == res2.security_metrics
    assert res1.eve_simulation.intercepted_mask == res2.eve_simulation.intercepted_mask
