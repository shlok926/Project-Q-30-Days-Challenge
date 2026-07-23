"""Intercept-Resend Eavesdropper (Eve) model implementation class stub.

References:
    Docs/BB84_SPEC.md §5
    Docs/11_SECURITY_ARCHITECTURE.md §3, §4
"""

from typing import Any, Optional


class Eavesdropper:
    """Simulates an active eavesdropper (Eve) attacking the quantum channel.

    Applies intercept-resend measurements to qubits during transit based on the
    configured probability metrics.
    """

    def __init__(
        self, intercept_probability: float = 0.0, seed: Optional[int] = None
    ) -> None:
        """Initialize the Eavesdropper model.

        Args:
            intercept_probability: Probability of Eve intercepting each qubit.
            seed: Seed for local random decisions.
        """
        # TODO: Setup random state generator. Ref: BB84_SPEC.md §5
        self.intercept_probability = intercept_probability
        self.seed = seed

    def intercept_and_resend(self, qubit_index: int, qubit_circuit: Any) -> Any:
        """Intercept the qubit, measure in a random basis, and re-prepare.

        Args:
            qubit_index: Index of the qubit in transit.
            qubit_circuit: The current Qiskit circuit representing the qubit.

        Returns:
            The modified Qiskit circuit representing the resubmitted qubit.
        """
        # TODO: Apply random measurement and reconstruct state vector. Ref: BB84_SPEC.md §5
        raise NotImplementedError(
            "Eavesdropper.intercept_and_resend is not yet implemented."
        )
