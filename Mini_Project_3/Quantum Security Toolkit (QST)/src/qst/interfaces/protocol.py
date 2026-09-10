"""ProtocolInterface abstract base class for QST.

All quantum key distribution protocols (e.g. BB84, E91, B92) must implement
this interface.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md §8
    Docs/BB84_SPEC.md §1
"""

import abc
from typing import Any, Optional


class ProtocolInterface(abc.ABC):
    """Abstract Base Class defining the contract for QKD protocols.

    Every protocol implementation is responsible for qubit preparation,
    transmission, eavesdropper interaction handling, measurement, sifting,
    and output formatting.
    """

    @abc.abstractmethod
    def initialize(
        self,
        n_qubits: int,
        seed: Optional[int] = None,
        eve_intercept_probability: float = 0.0,
    ) -> None:
        """Initialize the protocol state and random generators.

        Args:
            n_qubits: The number of qubits to process in the simulation.
            seed: An optional seed for reproducible randomness.
            eve_intercept_probability: Optional eavesdropper intercept probability.

        Raises:
            ValidationError: If n_qubits, seed, or interception probability are invalid.
        """
        pass

    @abc.abstractmethod
    def execute(self) -> None:
        """Execute the qubit preparation and channel transmission steps.

        This includes applying any quantum gates, encoding classical bits
        in specific bases, and sending qubits through the quantum channel.
        """
        pass

    @abc.abstractmethod
    def measure(self) -> None:
        """Perform basis measurement on Bob's side.

        Measures the received qubits in randomly selected bases.
        """
        pass

    @abc.abstractmethod
    def validate(self) -> None:
        """Execute validation checks on the protocol parameter settings.

        Ensures all initialized values satisfy boundary requirements.
        """
        pass

    @abc.abstractmethod
    def reset(self) -> None:
        """Reset the internal protocol state, clearing generated keys and bits."""
        pass

    @abc.abstractmethod
    def export(self) -> Any:
        """Export the final results of the key exchange.

        Returns:
            The protocol simulation output data structure.
        """
        pass
