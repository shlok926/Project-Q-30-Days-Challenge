"""Core protocol constants for BB84 key agreement.

References:
    Docs/BB84_SPEC.md §2
"""

# BB84 encoding bases
BASIS_Z = "Z"  # Rectilinear basis
BASIS_X = "X"  # Diagonal basis

SUPPORTED_BASES = (BASIS_Z, BASIS_X)

# Binary bit values
BIT_0 = 0
BIT_1 = 1

SUPPORTED_BITS = (BIT_0, BIT_1)
