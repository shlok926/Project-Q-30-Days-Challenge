"""BB84 Protocol Engine composition class.

Coordinates Alice's state preparation, circuit compiling, Bob's measurement
rotation compiling, and simulator execution.

References:
    Docs/BB84_SPEC.md §1
    Docs/07_SYSTEM_ARCHITECTURE.md §5
    Docs/10_API_SPECIFICATION.md §3
"""

from typing import Any, Optional

from qst.interfaces.protocol import ProtocolInterface
from qst.core.shared.random.random_provider import NumpyRandomProvider, RandomProvider
from qst.core.shared.execution.executor import AerExecutor, ExecutorInterface
from qst.core.bb84.state_preparation import AliceStatePreparer
from qst.core.bb84.circuit_builder import (
    CircuitBuilder,
    GateApplier,
    RegisterAllocator,
    StateEncoder,
)
from qst.core.bb84.measurement import MeasurementBasisGenerator, MeasurementBuilder
from qst.core.bb84.validators import validate_bb84_inputs


class BB84Protocol(ProtocolInterface):
    """Protocol Engine orchestrating state preparation and circuit compilation.

    Composes decoupled random generators, builders, and executors.
    """

    def __init__(
        self,
        random_provider: Optional[RandomProvider] = None,
        executor: Optional[ExecutorInterface] = None,
    ) -> None:
        """Initialize the BB84 Protocol Engine.

        Args:
            random_provider: Random provider override.
            executor: Execution backend wrapper override.
        """
        self._random_provider = random_provider or NumpyRandomProvider()
        self._executor = executor or AerExecutor()

        self._gate_applier = GateApplier()
        self._preparer = AliceStatePreparer(self._random_provider)
        self._builder = CircuitBuilder(
            RegisterAllocator(), StateEncoder(self._gate_applier)
        )
        self._meas_generator = MeasurementBasisGenerator(self._random_provider)
        self._meas_builder = MeasurementBuilder(self._gate_applier)

        # Local state storage
        self._n_qubits: int = 0
        self._seed: Optional[int] = None
        self._alice_bits: tuple[int, ...] = ()
        self._alice_bases: tuple[str, ...] = ()
        self._bob_bases: tuple[str, ...] = ()
        self._bob_bits: tuple[int, ...] = ()

        self._prepared_circuit: Any = None
        self._measured_circuit: Any = None
        self._raw_counts: dict[str, int] = {}

    def initialize(self, n_qubits: int, seed: Optional[int] = None) -> None:
        """Initialize simulation parameters and prepare Alice and Bob states.

        Args:
            n_qubits: Number of qubits to simulate.
            seed: Reproducible generator seed.

        Raises:
            ValidationError: If inputs are invalid.
        """
        self.reset()
        self._n_qubits = n_qubits
        self._seed = seed

        # Configure numpy seed if default NumpyRandomProvider is used
        if isinstance(self._random_provider, NumpyRandomProvider):
            self._random_provider = NumpyRandomProvider(seed)
            self._preparer = AliceStatePreparer(self._random_provider)
            self._meas_generator = MeasurementBasisGenerator(self._random_provider)

        # Generate Alice and Bob settings
        self._alice_bits, self._alice_bases = self._preparer.prepare_state(n_qubits)
        self._bob_bases = self._meas_generator.generate_bases(n_qubits)

    def execute(self) -> None:
        """Construct Alice's state preparation QuantumCircuit."""
        self.validate()
        self._prepared_circuit = self._builder.build_circuit(
            self._alice_bits, self._alice_bases
        )

    def measure(self) -> None:
        """Build measurement circuits, run simulation, and extract Bob's outcomes."""
        if self._prepared_circuit is None:
            raise ValueError("Must run execute() before measure().")

        # Compile measured circuit
        self._measured_circuit = self._meas_builder.apply_measurement(
            self._prepared_circuit, self._bob_bases
        )

        # Run compilation sanity checks
        self._executor.validate_transpilation(self._measured_circuit)

        # Execute single-shot simulation
        counts = self._executor.execute(self._measured_circuit, self._seed)
        self._raw_counts = counts

        # Parse counts. Since we execute 1 shot, there is exactly one outcome string.
        # Qiskit outcomes represent little-endian format (0th bit rightmost).
        if counts:
            outcome_str = list(counts.keys())[0]
            self._bob_bits = tuple(int(bit) for bit in reversed(outcome_str))

    def validate(self) -> None:
        """Verify internal consistency of states and parameters.

        Raises:
            ValidationError: If internal parameters differ or are out of bounds.
        """
        validate_bb84_inputs(self._alice_bits, self._alice_bases)
        if len(self._bob_bases) != self._n_qubits:
            from qst.exceptions.validation import ValidationError

            raise ValidationError(
                "Bob bases size does not match qubit count.", code="QST-VAL-701"
            )

    def reset(self) -> None:
        """Reset internal parameters and wipe circuits."""
        self._n_qubits = 0
        self._seed = None
        self._alice_bits = ()
        self._alice_bases = ()
        self._bob_bases = ()
        self._bob_bits = ()
        self._prepared_circuit = None
        self._measured_circuit = None
        self._raw_counts = {}

    def export(self) -> dict[str, Any]:
        """Export the compiled states and outcomes (no sifting/post-processing).

        Returns:
            A dictionary containing generated states and raw counts.
        """
        return {
            "n_qubits": self._n_qubits,
            "seed": self._seed,
            "alice_bits": self._alice_bits,
            "alice_bases": self._alice_bases,
            "bob_bases": self._bob_bases,
            "bob_bits": self._bob_bits,
            "raw_counts": self._raw_counts,
        }

    # Public getters for test assertions
    @property
    def alice_bits(self) -> tuple[int, ...]:
        """Return Alice's generated bits."""
        return self._alice_bits

    @property
    def alice_bases(self) -> tuple[str, ...]:
        """Return Alice's encoding bases."""
        return self._alice_bases

    @property
    def bob_bases(self) -> tuple[str, ...]:
        """Return Bob's measurement bases."""
        return self._bob_bases

    @property
    def bob_bits(self) -> tuple[int, ...]:
        """Return Bob's measured bits."""
        return self._bob_bits

    @property
    def prepared_circuit(self) -> Any:
        """Return the compiled state preparation circuit."""
        return self._prepared_circuit

    @property
    def measured_circuit(self) -> Any:
        """Return the compiled measurement circuit."""
        return self._measured_circuit
