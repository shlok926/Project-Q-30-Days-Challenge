"""Privacy Amplification package initialization.

References:
    Docs/10_API_SPECIFICATION.md
"""

from qst.privacy.amplifier import PrivacyAmplifier
from qst.privacy.exceptions import PrivacyAmplificationError
from qst.privacy.interfaces import HashAlgorithm
from qst.privacy.models import (
    FinalSecretKey,
    PrivacyAmplificationConfiguration,
    PrivacyAmplificationResult,
    PrivacyStatistics,
)
from qst.privacy.validators import (
    validate_dimensions,
    validate_key,
    validate_privacy_config,
)

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
