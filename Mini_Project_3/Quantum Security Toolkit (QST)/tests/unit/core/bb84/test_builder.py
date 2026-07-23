"""Unit tests for the QST CircuitBuilder and allocation components.

References:
    Docs/BB84_SPEC.md §3
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest
from qiskit import QuantumCircuit

from qst.core.bb84.circuit_builder import (
    CircuitBuilder,
    GateApplier,
    RegisterAllocator,
    StateEncoder,
)
from qst.exceptions.validation import ValidationError


@pytest.mark.unit
def test_register_allocator() -> None:
    """Verify register allocator sets up correct register widths."""
    allocator = RegisterAllocator()
    qr, cr = allocator.allocate(5)
    assert qr.size == 5
    assert cr.size == 5


@pytest.mark.unit
def test_gate_applier() -> None:
    """Verify gate applier executes basic rotations on QuantumCircuit."""
    applier = GateApplier()
    qc = QuantumCircuit(1)
    applier.apply_x(qc, 0)
    applier.apply_h(qc, 0)

    # Qiskit circuit data contains gates: x, then h
    gates = [instr.operation.name for instr in qc.data]
    assert gates == ["x", "h"]


@pytest.mark.unit
def test_state_encoder() -> None:
    """Verify state encoder maps bits and bases to quantum gates correctly."""
    applier = GateApplier()
    encoder = StateEncoder(applier)

    # |0> rectilinear (bit 0, basis Z): No gates
    qc1 = QuantumCircuit(1)
    encoder.encode(qc1, 0, bit=0, basis="Z")
    assert len(qc1.data) == 0

    # |1> rectilinear (bit 1, basis Z): X gate
    qc2 = QuantumCircuit(1)
    encoder.encode(qc2, 0, bit=1, basis="Z")
    assert qc2.data[0].operation.name == "x"

    # |+> diagonal (bit 0, basis X): H gate
    qc3 = QuantumCircuit(1)
    encoder.encode(qc3, 0, bit=0, basis="X")
    assert qc3.data[0].operation.name == "h"

    # |-> diagonal (bit 1, basis X): X then H gates
    qc4 = QuantumCircuit(1)
    encoder.encode(qc4, 0, bit=1, basis="X")
    gates = [instr.operation.name for instr in qc4.data]
    assert gates == ["x", "h"]


@pytest.mark.unit
def test_circuit_builder_valid() -> None:
    """Verify circuit builder compiles complete, valid QuantumCircuit."""
    allocator = RegisterAllocator()
    applier = GateApplier()
    encoder = StateEncoder(applier)
    builder = CircuitBuilder(allocator, encoder)

    bits = (0, 1, 0, 1)
    bases = ("Z", "Z", "X", "X")
    qc = builder.build_circuit(bits, bases)

    assert qc.num_qubits == 4
    assert qc.num_clbits == 4


@pytest.mark.unit
def test_circuit_builder_invalid() -> None:
    """Verify circuit builder raises ValidationError on mismatched inputs."""
    allocator = RegisterAllocator()
    applier = GateApplier()
    encoder = StateEncoder(applier)
    builder = CircuitBuilder(allocator, encoder)

    # Length mismatch
    with pytest.raises(ValidationError) as exc:
        builder.build_circuit((0, 1), ("Z",))
    assert "QST-VAL-603" in str(exc.value)

    # Invalid bit values
    with pytest.raises(ValidationError) as exc:
        builder.build_circuit((0, 2), ("Z", "Z"))
    assert "QST-VAL-601" in str(exc.value)

    # Invalid basis values
    with pytest.raises(ValidationError) as exc:
        builder.build_circuit((0, 1), ("Z", "Y"))
    assert "QST-VAL-602" in str(exc.value)


@pytest.mark.unit
def test_validate_circuit_registers_failures() -> None:
    """Verify validate_circuit_registers raises ValidationError for mismatched widths."""
    from qst.core.shared.validation.validators import validate_circuit_registers

    # None check
    with pytest.raises(ValidationError) as exc:
        validate_circuit_registers(None, 1, 1)
    assert "QST-VAL-604" in str(exc.value)

    # Qubit size mismatch
    qc1 = QuantumCircuit(2, 2)
    with pytest.raises(ValidationError) as exc:
        validate_circuit_registers(qc1, 1, 2)
    assert "QST-VAL-605" in str(exc.value)

    # Classical bit size mismatch
    qc2 = QuantumCircuit(2, 1)
    with pytest.raises(ValidationError) as exc:
        validate_circuit_registers(qc2, 2, 2)
    assert "QST-VAL-606" in str(exc.value)
