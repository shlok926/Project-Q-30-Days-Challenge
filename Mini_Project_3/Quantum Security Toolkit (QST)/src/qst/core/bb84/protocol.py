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
from qst.models.results import (
    SimulationResult,
    ReconciliationResult,
    SiftedKeyResult,
    EveSimulationResult,
    QBERResult,
    SecurityMetrics,
)
from qst.core.bb84.reconciliation import BasisReconciliationService
from qst.core.bb84.sifting import KeySiftingService
from qst.core.bb84.eavesdropper import InterceptResendChannel
from qst.core.bb84.qber import QBERService
from qst.core.bb84.metrics import SecurityMetricsService


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
        self._reconciliation_service = BasisReconciliationService()
        self._sifting_service = KeySiftingService()
        self._eve_channel = InterceptResendChannel(self._random_provider)
        self._qber_service = QBERService()
        self._security_metrics_service = SecurityMetricsService()

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
        self._reconciliation: Optional[ReconciliationResult] = None
        self._sifted_keys: Optional[SiftedKeyResult] = None
        self._eve_intercept_probability: float = 0.0
        self._eve_result: Optional[EveSimulationResult] = None
        self._qber_result: Optional[QBERResult] = None
        self._security_metrics: Optional[SecurityMetrics] = None
        self._reconstructed_bits: tuple[int, ...] = ()
        self._reconstructed_bases: tuple[str, ...] = ()

    def initialize(
        self,
        n_qubits: int,
        seed: Optional[int] = None,
        eve_intercept_probability: float = 0.0,
    ) -> None:
        """Initialize simulation parameters and prepare Alice, Eve, and Bob states.

        Args:
            n_qubits: Number of qubits to simulate.
            seed: Reproducible generator seed.
            eve_intercept_probability: Configured probability of Eve interception.

        Raises:
            ValidationError: If inputs are invalid.
        """
        self.reset()
        self._n_qubits = n_qubits
        self._seed = seed
        self._eve_intercept_probability = eve_intercept_probability

        # Configure numpy seed if default NumpyRandomProvider is used
        if isinstance(self._random_provider, NumpyRandomProvider):
            self._random_provider = NumpyRandomProvider(seed)
            self._preparer = AliceStatePreparer(self._random_provider)
            self._meas_generator = MeasurementBasisGenerator(self._random_provider)
            self._eve_channel = InterceptResendChannel(self._random_provider)

        # Generate Alice's prepared states and Bob's measurement bases
        self._alice_bits, self._alice_bases = self._preparer.prepare_state(n_qubits)
        self._bob_bases = self._meas_generator.generate_bases(n_qubits)

        # Simulate Eve's Intercept-Resend attack during transit
        if self._eve_intercept_probability > 0.0:
            self._eve_result = self._eve_channel.intercept_and_resend(
                self._alice_bits,
                self._alice_bases,
                self._eve_intercept_probability,
            )
            self._reconstructed_bits = self._eve_result.reconstructed_bits
            self._reconstructed_bases = self._eve_result.reconstructed_bases
        else:
            self._eve_result = None
            self._reconstructed_bits = self._alice_bits
            self._reconstructed_bases = self._alice_bases

    def execute(self) -> None:
        """Construct Alice's/Eve's state preparation QuantumCircuit for Bob."""
        self.validate()
        self._prepared_circuit = self._builder.build_circuit(
            self._reconstructed_bits, self._reconstructed_bases
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

        # Perform basis reconciliation and sifting
        self._reconciliation = self._reconciliation_service.reconcile(
            self._alice_bases, self._bob_bases
        )
        self._sifted_keys = self._sifting_service.sift_keys(
            self._alice_bits, self._bob_bits, self._reconciliation
        )

        # Calculate QBER and security metrics
        self._qber_result = self._qber_service.calculate_qber(
            self._sifted_keys.alice_key, self._sifted_keys.bob_key
        )
        self._security_metrics = self._security_metrics_service.compute_metrics(
            self._n_qubits, self._reconciliation, self._qber_result
        )

    def validate(self) -> None:
        """Verify internal consistency of states and parameters.

        Raises:
            ValidationError: If internal parameters differ or are out of bounds.
        """
        validate_bb84_inputs(self._alice_bits, self._alice_bases)
        from qst.utils.validation import validate_probability

        validate_probability(
            self._eve_intercept_probability, name="eve_intercept_probability"
        )
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
        self._reconciliation = None
        self._sifted_keys = None
        self._eve_intercept_probability = 0.0
        self._eve_result = None
        self._qber_result = None
        self._security_metrics = None
        self._reconstructed_bits = ()
        self._reconstructed_bases = ()

    def export(self) -> SimulationResult:
        """Export the final SimulationResult representation of the run.

        Returns:
            The immutable SimulationResult payload.
        """
        final_key_len = self._sifted_keys.key_length if self._sifted_keys else 0
        key_rate = float(final_key_len / self._n_qubits) if self._n_qubits > 0 else 0.0
        sifted_key_list = list(self._sifted_keys.alice_key) if self._sifted_keys else []
        qber = self._qber_result.qber if self._qber_result else None

        return SimulationResult(
            qber=qber,
            final_key_length=final_key_len,
            key_rate=key_rate,
            sifted_key=sifted_key_list,
            n_qubits=self._n_qubits,
            seed=self._seed,
            eve_intercept_probability=self._eve_intercept_probability,
            warnings=[],
            metadata={"raw_counts": self._raw_counts},
            alice_bits=self._alice_bits,
            bob_bits=self._bob_bits,
            alice_bases=self._alice_bases,
            bob_bases=self._bob_bases,
            reconciliation=self._reconciliation,
            sifted_keys=self._sifted_keys,
            interception_probability=self._eve_intercept_probability,
            eve_simulation=self._eve_result,
            qber_result=self._qber_result,
            security_metrics=self._security_metrics,
            privacy_amplification=None,
            error_correction=None,
            entropy_analysis=None,
            raw_key=list(self._alice_bits) if self._alice_bits else None,
        )

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

    @property
    def reconciliation(self) -> Optional[ReconciliationResult]:
        """Return the basis reconciliation result."""
        return self._reconciliation

    @property
    def sifted_keys(self) -> Optional[SiftedKeyResult]:
        """Return the key sifting result."""
        return self._sifted_keys

    @property
    def eve_intercept_probability(self) -> float:
        """Return the eavesdropper interception probability."""
        return self._eve_intercept_probability

    @property
    def eve_simulation(self) -> Optional[EveSimulationResult]:
        """Return the eavesdropper simulation results."""
        return self._eve_result

    @property
    def qber_result(self) -> Optional[QBERResult]:
        """Return the calculated QBER results."""
        return self._qber_result

    @property
    def security_metrics(self) -> Optional[SecurityMetrics]:
        """Return the calculated security metrics."""
        return self._security_metrics
