"""Cascade Error Correction package initialization.

References:
    Docs/10_API_SPECIFICATION.md
"""

from qst.correction.exceptions import CorrectionError
from qst.correction.models import (
    CascadeConfiguration,
    CorrectedKey,
    CorrectionStatistics,
    CorrectionResult,
)
from qst.correction.validators import validate_keys, validate_cascade_config
from qst.correction.parity import calculate_parity
from qst.correction.block import generate_blocks, KeyBlock
from qst.correction.binary_search import perform_binary_search
from qst.correction.cascade import CascadeReconciler

__all__ = [
    "CorrectionError",
    "CascadeConfiguration",
    "CorrectedKey",
    "CorrectionStatistics",
    "CorrectionResult",
    "validate_keys",
    "validate_cascade_config",
    "calculate_parity",
    "generate_blocks",
    "KeyBlock",
    "perform_binary_search",
    "CascadeReconciler",
]
