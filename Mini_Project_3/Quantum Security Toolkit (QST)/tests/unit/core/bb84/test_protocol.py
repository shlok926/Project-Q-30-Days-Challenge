"""Unit tests for QST BB84Protocol composition.

References:
    Docs/BB84_SPEC.md §1, §6
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.core.bb84.protocol import BB84Protocol
from qst.exceptions.validation import ValidationError


@pytest.mark.unit
def test_bb84_protocol_orchestrated_flow() -> None:
    """Verify BB84Protocol runs Alice prep, builder compiling, and Bob execution."""
    protocol = BB84Protocol()

    # 1. Initialize
    protocol.initialize(n_qubits=10, seed=42)
    assert len(protocol.alice_bits) == 10
    assert len(protocol.alice_bases) == 10
    assert len(protocol.bob_bases) == 10

    # 2. Execute Alice
    protocol.execute()
    assert protocol.prepared_circuit is not None

    # 3. Measure Bob
    protocol.measure()
    assert protocol.measured_circuit is not None
    assert len(protocol.bob_bits) == 10

    # Test Bob measured bits values.
    # Since it's single shot execution, every bit must be in (0, 1)
    assert all(b in (0, 1) for b in protocol.bob_bits)

    # 4. Export
    exp = protocol.export()
    assert exp["n_qubits"] == 10
    assert exp["seed"] == 42
    assert exp["alice_bits"] == protocol.alice_bits
    assert exp["bob_bits"] == protocol.bob_bits

    # Verify that Bob's bits match Alice's bits wherever bases match!
    # (Since there is no eavesdropper, mismatched bases produce 50% error,
    # but matched bases must produce 0% error, i.e. 100% correct match!)
    for i in range(10):
        if protocol.alice_bases[i] == protocol.bob_bases[i]:
            assert protocol.alice_bits[i] == protocol.bob_bits[i]

    # 5. Reset
    protocol.reset()
    assert len(protocol.alice_bits) == 0
    assert protocol.prepared_circuit is None


@pytest.mark.unit
def test_bb84_protocol_determinism() -> None:
    """Verify BB84Protocol runs identically for identical seeds."""
    p1 = BB84Protocol()
    p1.initialize(n_qubits=20, seed=12345)
    p1.execute()
    p1.measure()

    p2 = BB84Protocol()
    p2.initialize(n_qubits=20, seed=12345)
    p2.execute()
    p2.measure()

    assert p1.alice_bits == p2.alice_bits
    assert p1.alice_bases == p2.alice_bases
    assert p1.bob_bases == p2.bob_bases
    assert p1.bob_bits == p2.bob_bits


@pytest.mark.unit
def test_bb84_protocol_measure_without_execute() -> None:
    """Verify calling measure before execute raises ValueError."""
    protocol = BB84Protocol()
    protocol.initialize(n_qubits=10, seed=42)
    with pytest.raises(ValueError):
        protocol.measure()


@pytest.mark.unit
def test_bb84_protocol_validation_error() -> None:
    """Verify validation checking raises ValidationError on invalid parameters."""
    protocol = BB84Protocol()
    with pytest.raises(ValidationError):
        protocol.initialize(n_qubits=-5, seed=42)


@pytest.mark.unit
def test_bb84_protocol_bob_bases_mismatch() -> None:
    """Verify validation checking raises ValidationError on Bob bases size mismatch."""
    protocol = BB84Protocol()
    protocol.initialize(n_qubits=5, seed=42)
    # Manually corrupt Bob's bases to trigger a mismatch
    protocol._bob_bases = ("Z", "X")
    with pytest.raises(ValidationError) as exc:
        protocol.validate()
    assert "QST-VAL-701" in str(exc.value)
