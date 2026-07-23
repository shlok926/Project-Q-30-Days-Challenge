"""Unit tests for Bob's QST MeasurementBuilder components.

References:
    Docs/BB84_SPEC.md §1 Steps 5-6
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest
from qiskit import QuantumCircuit

from qst.core.bb84.circuit_builder import GateApplier
from qst.core.bb84.measurement import MeasurementBasisGenerator, MeasurementBuilder
from qst.core.shared.random.random_provider import NumpyRandomProvider
from qst.exceptions.validation import ValidationError


@pytest.mark.unit
def test_measurement_basis_generator() -> None:
    """Verify measurement basis generator creates correct random basis widths."""
    prov = NumpyRandomProvider(seed=42)
    generator = MeasurementBasisGenerator(prov)

    bases = generator.generate_bases(50)
    assert len(bases) == 50
    assert all(b in ("Z", "X") for b in bases)


@pytest.mark.unit
def test_measurement_builder_valid() -> None:
    """Verify measurement builder appends correct basis rotations and measurement gates."""
    applier = GateApplier()
    builder = MeasurementBuilder(applier)

    # 2 qubits circuit
    qc = QuantumCircuit(2, 2)
    bob_bases = ("Z", "X")
    measured_qc = builder.apply_measurement(qc, bob_bases)

    # Qiskit circuit data should contain: h rotation on qubit 1 (since basis X),
    # followed by measurement gates on qubits 0 and 1.
    gates = [instr.operation.name for instr in measured_qc.data]
    assert "h" in gates
    assert gates.count("measure") == 2


@pytest.mark.unit
def test_measurement_builder_invalid() -> None:
    """Verify measurement builder raises ValidationError on mismatched circuit configurations."""
    applier = GateApplier()
    builder = MeasurementBuilder(applier)

    # 1 qubit circuit, but requesting 2 measurements bases
    qc = QuantumCircuit(1, 1)
    bob_bases = ("Z", "X")

    with pytest.raises(ValidationError) as exc:
        builder.apply_measurement(qc, bob_bases)
    assert "QST-VAL-605" in str(exc.value)
