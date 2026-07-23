"""Core package initialization exposing sub-packages and stubs.

References:
    Docs/07_SYSTEM_ARCHITECTURE.md §5
"""

from qst.core.bb84.protocol import BB84Protocol
from qst.core.eavesdropper import Eavesdropper

__all__ = ["BB84Protocol", "Eavesdropper"]
