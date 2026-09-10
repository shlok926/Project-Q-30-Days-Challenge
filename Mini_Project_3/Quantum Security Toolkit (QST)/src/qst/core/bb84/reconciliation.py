"""Basis Reconciliation Service and Statistics helper components.

References:
    Docs/BB84_SPEC.md §1 Step 7
    Docs/07_SYSTEM_ARCHITECTURE.md §5
"""

from typing import Sequence

from qst.core.bb84.validators import validate_bb84_bases
from qst.exceptions.validation import ValidationError
from qst.models.results import ReconciliationResult


class ReconciliationStatistics:
    """Computes statistical metrics for basis reconciliation."""

    @staticmethod
    def match_rate(matching_count: int, total_bits: int) -> float:
        """Calculate the ratio of matching bits to total bits.

        Args:
            matching_count: Total matching index positions.
            total_bits: Total qubits processed.

        Returns:
            The match rate as a float between 0.0 and 1.0.
        """
        if total_bits <= 0:
            return 0.0
        return float(matching_count / total_bits)

    @staticmethod
    def discard_count(total_bits: int, matching_count: int) -> int:
        """Calculate mismatched index positions.

        Args:
            total_bits: Total qubits processed.
            matching_count: Total matching index positions.

        Returns:
            The count of discarded bits.
        """
        return max(0, total_bits - matching_count)

    @staticmethod
    def discard_rate(discard_count: int, total_bits: int) -> float:
        """Calculate the ratio of discarded bits to total bits.

        Args:
            discard_count: Discarded mismatching count.
            total_bits: Total qubits processed.

        Returns:
            The discard rate as a float between 0.0 and 1.0.
        """
        if total_bits <= 0:
            return 0.0
        return float(discard_count / total_bits)


class BasisReconciliationService:
    """Performs Bob and Alice basis comparison and purges mismatches."""

    def reconcile(
        self, alice_bases: Sequence[str], bob_bases: Sequence[str]
    ) -> ReconciliationResult:
        """Reconcile Alice's and Bob's basis choices.

        Args:
            alice_bases: Bases used by Alice for state preparation.
            bob_bases: Bases used by Bob for state measurements.

        Returns:
            A ReconciliationResult containing matching positions.

        Raises:
            ValidationError: If bases lists contain invalid elements or mismatch in size.
        """
        validate_bb84_bases(alice_bases)
        validate_bb84_bases(bob_bases)

        if len(alice_bases) != len(bob_bases):
            raise ValidationError(
                f"Alice bases length ({len(alice_bases)}) does not match "
                f"Bob bases length ({len(bob_bases)}).",
                code="QST-VAL-801",
            )

        total_bits = len(alice_bases)
        matching_indices_list: list[int] = []
        discarded_indices_list: list[int] = []
        matching_bases_list: list[str] = []

        for idx in range(total_bits):
            if alice_bases[idx] == bob_bases[idx]:
                matching_indices_list.append(idx)
                matching_bases_list.append(alice_bases[idx])
            else:
                discarded_indices_list.append(idx)

        matching_indices = tuple(matching_indices_list)
        discarded_indices = tuple(discarded_indices_list)
        matching_bases = tuple(matching_bases_list)
        matching_count = len(matching_indices)

        match_rate = ReconciliationStatistics.match_rate(matching_count, total_bits)

        return ReconciliationResult(
            matching_indices=matching_indices,
            discarded_indices=discarded_indices,
            matching_bases=matching_bases,
            total_bits=total_bits,
            matching_count=matching_count,
            match_rate=match_rate,
        )
