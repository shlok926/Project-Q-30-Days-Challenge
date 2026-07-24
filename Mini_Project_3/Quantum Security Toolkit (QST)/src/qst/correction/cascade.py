"""Cascade Error Correction reconciler execution service.

References:
    Docs/10_API_SPECIFICATION.md
"""

import time
import math
from typing import Sequence
from qst.correction.exceptions import CorrectionError
from qst.correction.validators import validate_keys, validate_cascade_config
from qst.correction.parity import calculate_parity
from qst.correction.block import generate_blocks
from qst.correction.binary_search import perform_binary_search
from qst.correction.models import (
    CascadeConfiguration,
    CorrectedKey,
    CorrectionStatistics,
    CorrectionResult,
)


class CascadeReconciler:
    """Orchestrates interactive Cascade Error Correction stages between Alice and Bob."""

    def __init__(self, config: CascadeConfiguration) -> None:
        """Initialize the reconciler with a configuration.

        Args:
            config: Configurations details for blocks, passes, and seeds.
        """
        validate_cascade_config(config)
        self.config = config

    def reconcile(
        self,
        alice_key: Sequence[int],
        bob_key: Sequence[int],
    ) -> CorrectionResult:
        """Reconcile Bob's sifted key to match Alice's sifted key.

        Args:
            alice_key: Alice's sifted key bits sequence.
            bob_key: Bob's sifted key bits sequence.

        Returns:
            An immutable CorrectionResult containing the reconciled key and telemetry.

        Raises:
            CorrectionError: If validation fails.
        """
        validate_keys(alice_key, bob_key)

        alice_key_bits = list(alice_key)
        bob_key_bits = list(bob_key)
        N = len(alice_key_bits)

        corrected_positions = []
        messages = 0
        rounds = 0
        disclosed = 0
        passes_completed = 0

        # Initial discrepancies
        initial_discrepancies = sum(
            1 for a, b in zip(alice_key_bits, bob_key_bits) if a != b
        )
        initial_qber = initial_discrepancies / N if N > 0 else 0.0

        t_start = time.perf_counter()

        # Track blocks by pass number
        blocks_by_pass = {}

        corrected_in_chain = set()

        def cascade_feedback(error_idx: int, current_pass: int) -> None:
            """Recursively resolves parity mismatches in all shuffles up to current_pass."""
            nonlocal messages, rounds, disclosed
            for prev_pass in range(1, current_pass + 1):
                prev_blocks = blocks_by_pass[prev_pass]
                target_block = None
                for b in prev_blocks:
                    if error_idx in b.indices:
                        target_block = b
                        break

                if target_block is None:
                    continue

                # Verify if this block now has an odd parity error
                a_parity = calculate_parity(
                    [alice_key_bits[idx] for idx in target_block.indices]
                )
                b_parity = calculate_parity(
                    [bob_key_bits[idx] for idx in target_block.indices]
                )
                messages += 1
                disclosed += 1

                if a_parity != b_parity:
                    # Resolve recursively using BINARY search
                    new_err_idx, BS_msg, BS_rnd, BS_disc = perform_binary_search(
                        target_block, alice_key_bits, bob_key_bits
                    )
                    messages += BS_msg
                    rounds += BS_rnd
                    disclosed += BS_disc

                    if new_err_idx in corrected_in_chain:
                        continue

                    corrected_in_chain.add(new_err_idx)

                    # Flip Bob's bit
                    bob_key_bits[new_err_idx] = 1 - bob_key_bits[new_err_idx]
                    corrected_positions.append(new_err_idx)

                    # Propagate changes up to current_pass
                    cascade_feedback(new_err_idx, current_pass)

        # Execute passes
        for p in range(1, self.config.num_passes + 1):
            # Early termination check
            if alice_key_bits == bob_key_bits:
                break

            # Block size routing
            if p - 1 < len(self.config.block_sizes):
                block_size = self.config.block_sizes[p - 1]
            else:
                block_size = self.config.block_sizes[-1] * (
                    2 ** (p - len(self.config.block_sizes))
                )

            # Partition key indices into blocks
            blocks = generate_blocks(N, block_size, p, self.config.seed)
            blocks_by_pass[p] = blocks

            # One round for all block check comparisons in this pass
            rounds += 1

            mismatches = []
            for b in blocks:
                a_parity = calculate_parity([alice_key_bits[idx] for idx in b.indices])
                b_parity = calculate_parity([bob_key_bits[idx] for idx in b.indices])
                messages += 1
                disclosed += 1
                if a_parity != b_parity:
                    mismatches.append(b)

            # Reconcile each mismatch block
            for block in mismatches:
                # Verify if this block still has mismatched parity
                a_parity = calculate_parity(
                    [alice_key_bits[idx] for idx in block.indices]
                )
                b_parity = calculate_parity(
                    [bob_key_bits[idx] for idx in block.indices]
                )
                messages += 1
                disclosed += 1
                if a_parity == b_parity:
                    continue  # already corrected by previous cascade cascades

                # Run BINARY search
                err_idx, BS_msg, BS_rnd, BS_disc = perform_binary_search(
                    block, alice_key_bits, bob_key_bits
                )
                messages += BS_msg
                rounds += BS_rnd
                disclosed += BS_disc

                # Correct the bit
                bob_key_bits[err_idx] = 1 - bob_key_bits[err_idx]
                corrected_positions.append(err_idx)

                corrected_in_chain.clear()
                corrected_in_chain.add(err_idx)

                # Propagate cascade corrections
                cascade_feedback(err_idx, p)

            passes_completed = p

        t_elapsed = time.perf_counter() - t_start

        # Calculate final metrics
        final_discrepancies = sum(
            1 for a, b in zip(alice_key_bits, bob_key_bits) if a != b
        )
        estimated_qber_after_correction = final_discrepancies / N if N > 0 else 0.0

        # Shannon entropy limit
        e = initial_qber
        if e <= 0.0 or e >= 1.0:
            shannon_limit = 0.0
        else:
            h_e = -e * math.log2(e) - (1 - e) * math.log2(1 - e)
            shannon_limit = N * h_e

        if shannon_limit > 0.0:
            efficiency = disclosed / shannon_limit
        else:
            efficiency = 1.0

        stats = CorrectionStatistics(
            initial_discrepancies=initial_discrepancies,
            corrected_bit_positions=tuple(corrected_positions),
            parity_exchanges=messages,
            communication_rounds=rounds,
            bits_disclosed=disclosed,
            execution_time=t_elapsed,
        )

        return CorrectionResult(
            corrected_key=CorrectedKey(tuple(bob_key_bits)),
            corrected_error_count=len(corrected_positions),
            corrected_bit_positions=tuple(corrected_positions),
            initial_qber=initial_qber,
            estimated_qber_after_correction=estimated_qber_after_correction,
            correction_efficiency=efficiency,
            parity_messages_exchanged=messages,
            communication_rounds=rounds,
            bits_disclosed=disclosed,
            passes_completed=passes_completed,
            execution_time=t_elapsed,
            statistics=stats,
        )
