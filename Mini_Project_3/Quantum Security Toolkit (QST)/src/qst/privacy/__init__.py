"""Privacy Amplification package initialization.

References:
    Docs/10_API_SPECIFICATION.md
"""

from qst.privacy.exceptions import PrivacyAmplificationError
from qst.privacy.models import (
    PrivacyAmplificationConfiguration,
    FinalSecretKey,
    PrivacyStatistics,
    PrivacyAmplificationResult,
)
from qst.privacy.validators import (
    validate_key,
    validate_privacy_config,
    validate_dimensions,
)
from qst.privacy.interfaces import HashAlgorithm
from qst.privacy.amplifier import PrivacyAmplifier

__all__ = [
    "PrivacyAmplificationError",
    "PrivacyAmplificationConfiguration",
    "FinalSecretKey",
    "PrivacyStatistics",
    "PrivacyAmplificationResult",
    "validate_key",
    "validate_privacy_config",
    "validate_dimensions",
    "HashAlgorithm",
    "PrivacyAmplifier",
]
