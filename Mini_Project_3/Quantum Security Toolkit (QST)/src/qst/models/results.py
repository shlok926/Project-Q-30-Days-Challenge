"""Simulation result model and batch result domain definitions.

References:
    Docs/10_API_SPECIFICATION.md §5
    Docs/EXPORT_SPEC.md §1, §2
    Docs/QBER_SPEC.md §6
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional

from qst.exceptions.validation import ValidationError
from qst.models.metadata import SimulationMetadata


class SecurityStatus(Enum):
    """Enumeration representing the secure state classification of a QKD run."""

    SECURE = "SECURE"
    WARNING = "WARNING"
    COMPROMISED = "COMPROMISED"


@dataclass(frozen=True)
class EveSimulationResult:
    """Immutable domain model representing the eavesdropping intercept-resend simulation.

    Attributes:
        intercepted_mask: Tuple of booleans flagging intercepted qubit indices.
        eve_bases: Tuple of basis choices selected by Eve (empty string if not intercepted).
        eve_measurements: Tuple of measurement outcomes obtained by Eve (None if not intercepted).
        reconstructed_bits: Tuple of bits prepared by Eve for transmission to Bob.
        reconstructed_bases: Tuple of bases chosen by Eve for transmission to Bob.
    """

    intercepted_mask: tuple[bool, ...]
    eve_bases: tuple[str, ...]
    eve_measurements: tuple[Optional[int], ...]
    reconstructed_bits: tuple[int, ...]
    reconstructed_bases: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate input mask and parameter lengths."""
        length = len(self.intercepted_mask)
        if (
            len(self.eve_bases) != length
            or len(self.eve_measurements) != length
            or len(self.reconstructed_bits) != length
            or len(self.reconstructed_bases) != length
        ):
            raise ValidationError(
                "All tuple attributes in EveSimulationResult must have identical length.",
                code="QST-VAL-514",
            )


@dataclass(frozen=True)
class QBERResult:
    """Immutable domain model representing the calculated QBER telemetry.

    Attributes:
        error_count: Number of differing bits between Alice and Bob's keys.
        sifted_key_length: Size of keys compared.
        qber: Estimated Quantum Bit Error Rate fraction.
        confidence_notes: Diagnostic notes detailing metrics context.
    """

    error_count: int
    sifted_key_length: int
    qber: float
    confidence_notes: str

    def __post_init__(self) -> None:
        """Validate QBER and error count bounds."""
        if not (0.0 <= self.qber <= 1.0):
            raise ValidationError(
                f"QBER must be between 0.0 and 1.0, got {self.qber}",
                code="QST-VAL-501",
            )
        if self.error_count < 0:
            raise ValidationError(
                f"Error count must be non-negative, got {self.error_count}",
                code="QST-VAL-515",
            )
        if self.sifted_key_length < 0:
            raise ValidationError(
                f"Sifted key length must be non-negative, got {self.sifted_key_length}",
                code="QST-VAL-503",
            )


@dataclass(frozen=True)
class SecurityMetrics:
    """Immutable domain model representing security statistics and decisions.

    Attributes:
        key_rate: Ratio of final key length to total raw qubits simulated.
        discard_rate: Ratio of discarded bits to total raw qubits simulated.
        error_rate: QBER rate or channel error fraction.
        status: Secure classification flag (SECURE, WARNING, COMPROMISED).
    """

    key_rate: float
    discard_rate: float
    error_rate: float
    status: SecurityStatus

    def __post_init__(self) -> None:
        """Validate rates and status bounds."""
        if not (0.0 <= self.key_rate <= 1.0):
            raise ValidationError(
                f"Key rate must be between 0.0 and 1.0, got {self.key_rate}",
                code="QST-VAL-502",
            )
        if not (0.0 <= self.discard_rate <= 1.0):
            raise ValidationError(
                f"Discard rate must be between 0.0 and 1.0, got {self.discard_rate}",
                code="QST-VAL-516",
            )
        if not (0.0 <= self.error_rate <= 1.0):
            raise ValidationError(
                f"Error rate must be between 0.0 and 1.0, got {self.error_rate}",
                code="QST-VAL-517",
            )


@dataclass(frozen=True)
class ReconciliationResult:
    """Immutable domain model representing the result of basis reconciliation.

    Attributes:
        matching_indices: Sorted sequence of indices where bases matched.
        discarded_indices: Sequence of indices where bases mismatched.
        matching_bases: Sequence of basis strings that matched.
        total_bits: Total bits processed.
        matching_count: Total count of matching indices.
        match_rate: Ratio of matching bits to total bits.
    """

    matching_indices: tuple[int, ...]
    discarded_indices: tuple[int, ...]
    matching_bases: tuple[str, ...]
    total_bits: int
    matching_count: int
    match_rate: float

    def __post_init__(self) -> None:
        """Validate reconciliation properties post initialization."""
        if list(self.matching_indices) != sorted(self.matching_indices):
            raise ValidationError(
                "Matching indices must be sorted.",
                code="QST-VAL-505",
            )
        if len(set(self.matching_indices)) != len(self.matching_indices):
            raise ValidationError(
                "Matching indices must be unique.",
                code="QST-VAL-506",
            )
        if self.total_bits < 0:
            raise ValidationError(
                f"Total bits must be non-negative, got {self.total_bits}",
                code="QST-VAL-513",
            )
        for idx in self.matching_indices:
            if not (0 <= idx < self.total_bits):
                raise ValidationError(
                    f"Matching index {idx} out of bounds for total_bits {self.total_bits}.",
                    code="QST-VAL-507",
                )
        for idx in self.discarded_indices:
            if not (0 <= idx < self.total_bits):
                raise ValidationError(
                    f"Discarded index {idx} out of bounds for total_bits {self.total_bits}.",
                    code="QST-VAL-508",
                )
        if self.matching_count != len(self.matching_indices):
            raise ValidationError(
                f"Matching count ({self.matching_count}) must equal matching indices size ({len(self.matching_indices)}).",
                code="QST-VAL-509",
            )
        if not (0.0 <= self.match_rate <= 1.0):
            raise ValidationError(
                f"Match rate must be between 0.0 and 1.0, got {self.match_rate}",
                code="QST-VAL-510",
            )


@dataclass(frozen=True)
class SiftedKeyResult:
    """Immutable domain model representing the keys generated after sifting.

    Attributes:
        alice_key: Sequence of bits representing Alice's sifted key.
        bob_key: Sequence of bits representing Bob's sifted key.
        key_length: Size of the secret sifted keys.
    """

    alice_key: tuple[int, ...]
    bob_key: tuple[int, ...]
    key_length: int

    def __post_init__(self) -> None:
        """Validate key sifting properties post initialization."""
        if len(self.alice_key) != len(self.bob_key):
            raise ValidationError(
                f"Alice and Bob sifted keys must have equal lengths, got {len(self.alice_key)} and {len(self.bob_key)}.",
                code="QST-VAL-511",
            )
        if self.key_length != len(self.alice_key):
            raise ValidationError(
                f"Key length ({self.key_length}) must match alice_key size ({len(self.alice_key)}).",
                code="QST-VAL-512",
            )


@dataclass(frozen=True)
class SimulationResult:
    """The canonical output payload representing a single key-exchange simulation.

    Attributes:
        qber: Estimated Quantum Bit Error Rate, or None if no bits sifted.
        final_key_length: Size of final sifted and checked key.
        key_rate: Ratio of final key length to total raw qubits simulated.
        sifted_key: List of resulting shared secret key bits.
        n_qubits: Total qubits processed.
        seed: Random seed used in the run.
        eve_intercept_probability: Configured probability of interception.
        warnings: List of warnings raised during execution.
        metadata: Serialization-ready diagnostic metadata.
        alice_bits: Alice's generated bits.
        bob_bits: Bob's measured bits.
        alice_bases: Alice's encoding bases.
        bob_bases: Bob's measurement bases.
        reconciliation: Basis reconciliation results.
        sifted_keys: Sifted keys results.
    """

    qber: Optional[float]
    final_key_length: int
    key_rate: float
    sifted_key: list[int]
    n_qubits: int
    seed: Optional[int]
    eve_intercept_probability: float
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    alice_bits: Optional[tuple[int, ...]] = None
    bob_bits: Optional[tuple[int, ...]] = None
    alice_bases: Optional[tuple[str, ...]] = None
    bob_bases: Optional[tuple[str, ...]] = None
    reconciliation: Optional[ReconciliationResult] = None
    sifted_keys: Optional[SiftedKeyResult] = None
    interception_probability: float = 0.0
    eve_simulation: Optional[EveSimulationResult] = None
    qber_result: Optional[QBERResult] = None
    security_metrics: Optional[SecurityMetrics] = None
    privacy_amplification: Optional[Any] = None
    error_correction: Optional[Any] = None
    entropy_analysis: Optional[Any] = None

    def __post_init__(self) -> None:
        """Validate output properties post initialization."""
        if self.qber is not None and not (0.0 <= self.qber <= 1.0):
            raise ValidationError(
                f"QBER must be between 0.0 and 1.0, got {self.qber}",
                code="QST-VAL-501",
            )
        if not (0.0 <= self.key_rate <= 1.0):
            raise ValidationError(
                f"Key rate must be between 0.0 and 1.0, got {self.key_rate}",
                code="QST-VAL-502",
            )
        if self.final_key_length < 0:
            raise ValidationError(
                f"Final key length must be non-negative, got {self.final_key_length}",
                code="QST-VAL-503",
            )
        if not (0.0 <= self.interception_probability <= 1.0):
            raise ValidationError(
                f"Interception probability must be between 0.0 and 1.0, got {self.interception_probability}",
                code="QST-VAL-202",
            )


@dataclass(frozen=True)
class BatchResult:
    """Aggregated output containing multiple simulation run outcomes.

    Attributes:
        run_count: Total sweep run trials executed.
        results: Collection of individual SimulationResult objects.
    """

    run_count: int
    results: list[SimulationResult]

    def __post_init__(self) -> None:
        """Verify run count matches internal collection size."""
        if self.run_count != len(self.results):
            raise ValidationError(
                f"Run count ({self.run_count}) does not match results size ({len(self.results)})",
                code="QST-VAL-504",
            )


@dataclass(frozen=True)
class ExportMetadata:
    """Serialization formatting properties for exports.

    Attributes:
        format_type: Serialization codec identifier (e.g. 'json', 'csv').
        export_path: Output target file destination.
    """

    format_type: str
    export_path: str


@dataclass(frozen=True)
class ValidationResult:
    """Encapsulation representing validation check statuses.

    Attributes:
        is_valid: True if parameters successfully pass validators.
        error_message: Detailed message if parameters are invalid.
    """

    is_valid: bool
    error_message: Optional[str] = None


@dataclass(frozen=True)
class ExperimentMetadata:
    """Immutable metadata tracking experiment execution details.

    Attributes:
        protocol: Name/identifier of the protocol (e.g. 'BB84').
        timestamp: ISO-8601 formatted execution timestamp.
        qiskit_version: Loaded Qiskit package version.
        repetitions: Configured execution iterations.
        seed_strategy: Description of seed distribution (e.g. 'seeded-generator').
    """

    protocol: str
    timestamp: str
    qiskit_version: str
    repetitions: int
    seed_strategy: str


@dataclass(frozen=True)
class ExecutionMetrics:
    """Immutable performance metrics for simulation executions.

    Attributes:
        execution_time: Total elapsed runtime in seconds.
        average_simulation_time: Mean simulation step duration.
        throughput: Qubits simulated per second.
        simulations_per_second: Executed trial loops per second.
    """

    execution_time: float
    average_simulation_time: float
    throughput: float
    simulations_per_second: float


@dataclass(frozen=True)
class ExperimentResult:
    """Immutable domain model containing aggregated outcomes of a simulation run repetitions.

    Attributes:
        simulations: Sequence of individual simulation results.
        average_qber: Average QBER rate computed across the sweep.
        average_key_rate: Average key rate achieved.
        secure_runs: Number of runs classified as SECURE.
        warning_runs: Number of runs classified as WARNING.
        compromised_runs: Number of runs classified as COMPROMISED.
        metrics: Performance profiling execution details.
        metadata: Audit metadata tracking environment context.
    """

    simulations: tuple[SimulationResult, ...]
    average_qber: float
    average_key_rate: float
    secure_runs: int
    warning_runs: int
    compromised_runs: int
    metrics: ExecutionMetrics
    metadata: ExperimentMetadata


@dataclass(frozen=True)
class SweepDimensions:
    """Immutable sweep coordinates specifying varied parameter grids.

    Attributes:
        qubit_counts: Sequence of varied qubit sizes.
        interception_probabilities: Sequence of eavesdropping rates tested.
        seeds: Sequence of random generator seeds.
    """

    qubit_counts: tuple[int, ...]
    interception_probabilities: tuple[float, ...]
    seeds: tuple[Optional[int], ...]


@dataclass(frozen=True)
class ParameterSweepResult:
    """Immutable domain model holding parameter sweep execution outcomes.

    Attributes:
        experiments: Sequence of completed ExperimentResult sets.
        total_experiments: Count of distinct sweeps completed.
        sweep_dimensions: Varied bounds defining configuration loops.
        metadata: Global sweep execution context attributes.
    """

    experiments: tuple[ExperimentResult, ...]
    total_experiments: int
    sweep_dimensions: SweepDimensions
    metadata: ExperimentMetadata


@dataclass(frozen=True)
class StatisticsResult:
    """Immutable statistical metrics summary wrapper.

    Attributes:
        mean: Standard average calculated across the sample.
        median: Midpoint value in sorted sequence.
        variance: Sample variance representing spread.
        standard_deviation: Sample standard deviation.
        confidence_interval: 95% confidence interval boundaries.
    """

    mean: float
    median: float
    variance: float
    standard_deviation: float
    confidence_interval: tuple[float, float]
