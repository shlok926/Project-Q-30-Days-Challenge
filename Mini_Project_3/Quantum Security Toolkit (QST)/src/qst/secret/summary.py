"""ProtocolSummaryBuilder aggregating keys sizes and protocol outcomes.

References:
    Docs/10_API_SPECIFICATION.md
"""

from typing import Optional
from qst.secret.models import ProtocolSummary
from qst.secret.validators import validate_key_lengths


class ProtocolSummaryBuilder:
    """Builder class for constructing ProtocolSummary snapshots."""

    def build_summary(
        self,
        raw_len: int,
        sifted_len: int,
        corrected_len: Optional[int],
        final_len: int,
        qber: float,
        correction_enabled: bool,
        privacy_enabled: bool,
        overall_success: bool,
        execution_mode: str,
    ) -> ProtocolSummary:
        """Aggregate protocol dimensions into a final summary model.

        Args:
            raw_len: Raw key size.
            sifted_len: Sifted key size.
            corrected_len: Reconciled key size.
            final_len: Compressed final key size.
            qber: Quantified error rate.
            correction_enabled: Whether error correction ran.
            privacy_enabled: Whether privacy amplification ran.
            overall_success: True if the protocol completed without critical error.
            execution_mode: Mode under which the executors ran.

        Returns:
            The ProtocolSummary dataclass.
        """
        validate_key_lengths(raw_len, sifted_len, corrected_len, final_len)

        corr_len_val = corrected_len if corrected_len is not None else 0

        return ProtocolSummary(
            raw_key_length=raw_len,
            sifted_key_length=sifted_len,
            corrected_key_length=corr_len_val,
            final_key_length=final_len,
            qber=qber,
            correction_enabled=correction_enabled,
            privacy_enabled=privacy_enabled,
            overall_success=overall_success,
            execution_mode=execution_mode,
        )
