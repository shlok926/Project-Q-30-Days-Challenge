"""Intercept-Resend Eavesdropper (Eve) model implementation for BB84.

References:
    Docs/BB84_SPEC.md §5
    Docs/11_SECURITY_ARCHITECTURE.md §3, §4
"""


from typing import Optional

from qst.core.shared.random.random_provider import RandomProvider
from qst.exceptions.validation import ValidationError
from qst.models.results import EveSimulationResult


class InterceptResendChannel:
    """Simulates an active intercept-resend eavesdropper (Eve) on a QKD channel."""

    def __init__(self, random_provider: RandomProvider) -> None:
        """Initialize the InterceptResendChannel.

        Args:
            random_provider: Seeded random source for deterministic decisions.
        """
        self._random_provider = random_provider

    def intercept_and_resend(
        self,
        alice_bits: tuple[int, ...],
        alice_bases: tuple[str, ...],
        interception_probability: float,
    ) -> EveSimulationResult:
        """Intercept qubits, measure them in random bases, and resend reconstructed states.

        Args:
            alice_bits: Secret bit sequence prepared by Alice.
            alice_bases: Basis choices selected by Alice.
            interception_probability: Probability that Eve intercepts each qubit.

        Returns:
            An EveSimulationResult capturing the attack details.

        Raises:
            ValidationError: If inputs are invalid or mismatch in size.
        """
        from qst.utils.validation import validate_probability

        validate_probability(interception_probability, name="interception_probability")

        length = len(alice_bits)
        if len(alice_bases) != length:
            raise ValidationError(
                f"Alice bits length ({length}) does not match bases length ({len(alice_bases)}).",
                code="QST-VAL-804",
            )

        # Decide which qubits are intercepted
        probs = self._random_provider.generate_probabilities(length)
        intercepted_mask_list = [
            probs[i] < interception_probability for i in range(length)
        ]

        # Generate Eve's basis choices for all positions
        eve_bases_choice = self._random_provider.generate_bases(length, ["Z", "X"])
        eve_bases_list = []
        eve_measurements_list: list[Optional[int]] = []
        reconstructed_bits_list = []
        reconstructed_bases_list = []

        # Iterate and simulate mid-channel measurements and qubit reconstructions
        for i in range(length):
            if intercepted_mask_list[i]:
                basis = eve_bases_choice[i]
                eve_bases_list.append(basis)
                # Eve measures the state
                if basis == alice_bases[i]:
                    # Basis matches: measurement is deterministic
                    measured_bit = alice_bits[i]
                else:
                    # Basis mismatches: measurement collapses state to 50/50 probability
                    measured_bit = self._random_provider.generate_bits(1)[0]

                eve_measurements_list.append(measured_bit)
                reconstructed_bits_list.append(measured_bit)
                reconstructed_bases_list.append(basis)
            else:
                eve_bases_list.append("")
                eve_measurements_list.append(None)
                reconstructed_bits_list.append(alice_bits[i])
                reconstructed_bases_list.append(alice_bases[i])

        return EveSimulationResult(
            intercepted_mask=tuple(intercepted_mask_list),
            eve_bases=tuple(eve_bases_list),
            eve_measurements=tuple(eve_measurements_list),
            reconstructed_bits=tuple(reconstructed_bits_list),
            reconstructed_bases=tuple(reconstructed_bases_list),
        )
