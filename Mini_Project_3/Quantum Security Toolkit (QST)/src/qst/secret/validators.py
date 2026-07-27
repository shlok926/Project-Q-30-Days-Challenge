"""Validation rules for secret key metrics and protocol consistency.

References:
    Docs/10_API_SPECIFICATION.md §4
"""

from typing import Optional, Dict
from qst.secret.exceptions import SecretKeyError


def validate_key_lengths(
    raw: int,
    sifted: int,
    corrected: Optional[int],
    final: int,
) -> None:
    """Validate that the key lengths are consistent across protocol stages.

    Args:
        raw: Raw key size.
        sifted: Sifted key size.
        corrected: Reconciled key size (optional).
        final: Compressed final key size.

    Raises:
        SecretKeyError: If key lengths fail monotonically decreasing constraints.
    """
    if raw < 0 or sifted < 0 or final < 0:
        raise SecretKeyError(
            f"Key lengths must be non-negative, got raw={raw}, sifted={sifted}, final={final}.",
            code="QST-SEC-701",
        )

    if raw > 0 and raw < sifted:
        raise SecretKeyError(
            f"Sifted key length ({sifted}) cannot exceed raw key length ({raw}).",
            code="QST-SEC-701",
        )

    if sifted < final:
        raise SecretKeyError(
            f"Final secret key length ({final}) cannot exceed sifted key length ({sifted}).",
            code="QST-SEC-701",
        )

    if corrected is not None and corrected > 0:
        if sifted < corrected:
            raise SecretKeyError(
                f"Corrected key length ({corrected}) cannot exceed sifted key length ({sifted}).",
                code="QST-SEC-701",
            )
        if corrected < final:
            raise SecretKeyError(
                f"Final secret key length ({final}) cannot exceed corrected key length ({corrected}).",
                code="QST-SEC-701",
            )


def validate_rates(rates: Dict[str, float]) -> None:
    """Validate that calculated rate probabilities are within boundaries [0, 1].

    Args:
        rates: Dictionary of calculated rate names and values.

    Raises:
        SecretKeyError: If any rate lies outside [0.0, 1.0].
    """
    for name, rate in rates.items():
        if not (0.0 <= rate <= 1.0):
            raise SecretKeyError(
                f"Key rate '{name}' must be between 0.0 and 1.0, got {rate}.",
                code="QST-SEC-702",
            )
