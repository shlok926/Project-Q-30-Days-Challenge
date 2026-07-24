"""Cascade block partitioning and permutation managers.

References:
    Docs/10_API_SPECIFICATION.md
"""

from typing import Any, Sequence
import numpy as np


class KeyBlock:
    """Represents a partitioned subset of sifted key bits tracking their original positions."""

    def __init__(
        self, original_indices: Sequence[int], pass_index: int, block_index: int
    ) -> None:
        """Initialize the key block.

        Args:
            original_indices: original indices inside the sifted key.
            pass_index: 1-indexed pass identifier.
            block_index: 0-indexed block identifier within that pass.
        """
        self.indices = tuple(original_indices)
        self.pass_index = pass_index
        self.block_index = block_index

    def __repr__(self) -> str:
        """Return developer-facing representation."""
        return f"KeyBlock(pass={self.pass_index}, block={self.block_index}, size={len(self.indices)})"


def generate_blocks(
    key_length: int,
    block_size: int,
    pass_index: int,
    seed: int = 42,
) -> list[KeyBlock]:
    """Partition key indices into blocks, optionally applying permutations for pass > 1.

    Args:
        key_length: The total size of the sifted key.
        block_size: Size of each partition block.
        pass_index: 1-indexed identifier of the current Cascade pass.
        seed: Configurations seed for pseudo-random permutations.

    Returns:
        A list of KeyBlock objects partitioning the key.
    """
    indices = list(range(key_length))

    if pass_index > 1:
        # Generate deterministic shuffle permutation
        rng = np.random.default_rng(seed + pass_index)
        indices = list(rng.permutation(key_length))

    blocks = []
    block_idx = 0
    for start in range(0, key_length, block_size):
        chunk = indices[start : start + block_size]
        blocks.append(KeyBlock(chunk, pass_index, block_idx))
        block_idx += 1

    return blocks
