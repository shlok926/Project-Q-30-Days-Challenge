"""Alice state preparation component for BB84.

References:
    Docs/BB84_SPEC.md §1 Steps 1-2
    Docs/07_SYSTEM_ARCHITECTURE.md §5
"""

from typing import Any, Optional

from qst.core.bb84.constants import SUPPORTED_BASES
from qst.core.bb84.validators import validate_bb84_inputs
from qst.core.shared.random.random_provider import RandomProvider
from qst.core.shared.validation.validators import validate_qubit_count


class AliceStatePreparer:
    """Manages generation and tracking of Alice's quantum state parameters.

    Responsible for random bits and bases generation using a delegated
    random provider.
    """

    def __init__(self, random_provider: RandomProvider) -> None:
        """Initialize the AliceStatePreparer.

        Args:
            random_provider: The random source instance.
        """
        self._random_provider = random_provider
        self._bits: tuple[int, ...] = ()
        self._bases: tuple[str, ...] = ()

    def prepare_state(self, length: int) -> tuple[tuple[int, ...], tuple[str, ...]]:
        """Generate and validate random bits and bases of a specified length.

        Args:
            length: Number of states to prepare.

        Returns:
            A tuple of (bits, bases).

        Raises:
            ValidationError: If length is invalid or random values fail boundary rules.
        """
        validate_qubit_count(length)
        bits = self._random_provider.generate_bits(length)
        bases = self._random_provider.generate_bases(length, SUPPORTED_BASES)

        validate_bb84_inputs(bits, bases)

        self._bits = bits
        self._bases = bases

        return bits, bases

    @property
    def bits(self) -> tuple[int, ...]:
        """Return the generated bits sequence."""
        return self._bits

    @property
    def bases(self) -> tuple[str, ...]:
        """Return the generated bases sequence."""
        return self._bases

    @property
    def metadata(self) -> dict[str, Any]:
        """Return metadata about the prepared states."""
        return {
            "length": len(self._bits),
            "state_prepared": len(self._bits) > 0,
        }
