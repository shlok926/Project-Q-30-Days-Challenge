"""Parameter Sweep Configuration Generator.

References:
    Docs/SIMULATION_SPEC.md §4
    Docs/07_SYSTEM_ARCHITECTURE.md §11
"""

from itertools import product
from typing import Optional, Sequence

from qst.exceptions.validation import ValidationError
from qst.models.config import ProtocolType, SecurityThresholds, SimulationConfig
from qst.utils.validation import (
    validate_probability,
    validate_qubit_count,
    validate_seed,
)


class ParameterSweepGenerator:
    """Generates Cartesian product configurations for protocol parameter sweeps."""

    @staticmethod
    def generate_configs(
        qubit_counts: Sequence[int],
        interception_probabilities: Sequence[float],
        seeds: Sequence[Optional[int]],
        repetitions: int = 1,
        security_thresholds: Optional[SecurityThresholds] = None,
        protocol: ProtocolType = ProtocolType.BB84,
    ) -> list[SimulationConfig]:
        """Validate inputs and generate a Cartesian product of simulation configs.

        Args:
            qubit_counts: Sequence of varied qubit sizes.
            interception_probabilities: Sequence of eavesdropping rates tested.
            seeds: Sequence of random generator seeds.
            repetitions: Execution loop iterations for each combination.
            security_thresholds: Security status classification limits.
            protocol: Protocol variant target.

        Returns:
            A list of SimulationConfig configuration objects.

        Raises:
            ValidationError: If any of the sweep parameters violate range checks.
        """
        if repetitions <= 0:
            raise ValidationError(
                f"Repetitions must be greater than zero, got {repetitions}.",
                code="QST-VAL-303",
            )

        if not qubit_counts or not interception_probabilities or not seeds:
            raise ValidationError(
                "Qubit counts, interception probabilities, and seeds lists must not be empty.",
                code="QST-VAL-304",
            )

        # Validate each coordinate element
        for count in qubit_counts:
            validate_qubit_count(count)
        for prob in interception_probabilities:
            validate_probability(prob, name="interception_probability")
        for s in seeds:
            validate_seed(s)

        thresholds = security_thresholds or SecurityThresholds()

        # Build Cartesian product configurations list
        configs = []
        for count, prob, s in product(qubit_counts, interception_probabilities, seeds):
            configs.append(
                SimulationConfig(
                    n_qubits=count,
                    seed=s,
                    interception_probability=prob,
                    repetitions=repetitions,
                    security_thresholds=thresholds,
                    protocol=protocol,
                )
            )

        return configs
