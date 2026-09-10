"""Key Sifting Service component for BB84.

References:
    Docs/BB84_SPEC.md §1 Step 8
    Docs/07_SYSTEM_ARCHITECTURE.md §5
"""

from typing import Sequence

from qst.core.bb84.validators import validate_bb84_bits
from qst.exceptions.validation import ValidationError
from qst.models.results import ReconciliationResult, SiftedKeyResult


class KeySiftingService:
    """Discards bits where Alice and Bob bases differed to generate keys."""

    def sift_keys(
        self,
        alice_raw_key: Sequence[int],
        bob_raw_key: Sequence[int],
        reconciliation_result: ReconciliationResult,
    ) -> SiftedKeyResult:
        """Sift key bits for Alice and Bob using matched basis indices.

        Args:
            alice_raw_key: Alice's raw bits sequence.
            bob_raw_key: Bob's raw measured bits sequence.
            reconciliation_result: Reconciled basis information.

        Returns:
            A SiftedKeyResult containing the secret keys.

        Raises:
            ValidationError: If raw keys mismatch or indices are out of bounds.
        """
        validate_bb84_bits(alice_raw_key)
        validate_bb84_bits(bob_raw_key)

        if len(alice_raw_key) != len(bob_raw_key):
            raise ValidationError(
                f"Alice raw key length ({len(alice_raw_key)}) does not match "
                f"Bob raw key length ({len(bob_raw_key)}).",
                code="QST-VAL-802",
            )

        if len(alice_raw_key) != reconciliation_result.total_bits:
            raise ValidationError(
                f"Key length ({len(alice_raw_key)}) does not match "
                f"reconciliation total bits ({reconciliation_result.total_bits}).",
                code="QST-VAL-803",
            )

        alice_sifted_list: list[int] = []
        bob_sifted_list: list[int] = []

        for idx in reconciliation_result.matching_indices:
            alice_sifted_list.append(alice_raw_key[idx])
            bob_sifted_list.append(bob_raw_key[idx])

        alice_sifted = tuple(alice_sifted_list)
        bob_sifted = tuple(bob_sifted_list)
        key_length = len(alice_sifted)

        return SiftedKeyResult(
            alice_key=alice_sifted,
            bob_key=bob_sifted,
            key_length=key_length,
        )
