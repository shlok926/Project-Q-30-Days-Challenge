"""Unit tests for the QST Random Provider architecture.

References:
    Docs/BB84_SPEC.md §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.core.shared.random.random_provider import NumpyRandomProvider, RandomProvider


@pytest.mark.unit
def test_random_provider_interface() -> None:
    """Verify that RandomProvider is an abstract base class."""
    with pytest.raises(TypeError):
        # Can't instantiate abstract class directly
        RandomProvider()  # type: ignore[abstract]


@pytest.mark.unit
def test_numpy_random_provider_determinism() -> None:
    """Verify NumpyRandomProvider outputs are deterministic for the same seed."""
    prov1 = NumpyRandomProvider(seed=42)
    prov2 = NumpyRandomProvider(seed=42)

    bits1 = prov1.generate_bits(50)
    bits2 = prov2.generate_bits(50)
    assert bits1 == bits2

    bases1 = prov1.generate_bases(50, allowed_bases=("Z", "X"))
    bases2 = prov2.generate_bases(50, allowed_bases=("Z", "X"))
    assert bases1 == bases2


@pytest.mark.unit
def test_numpy_random_provider_types_and_bounds() -> None:
    """Verify generated outputs adhere to bit and basis specification bounds."""
    prov = NumpyRandomProvider(seed=123)

    # Empty requests
    assert prov.generate_bits(0) == ()
    assert prov.generate_bits(-10) == ()
    assert prov.generate_bases(0, ("Z", "X")) == ()
    assert prov.generate_bases(-5, ("Z", "X")) == ()

    # Bit values logic
    bits = prov.generate_bits(100)
    assert len(bits) == 100
    assert all(b in (0, 1) for b in bits)

    # Basis choices logic
    bases = prov.generate_bases(100, allowed_bases=("Z", "X"))
    assert len(bases) == 100
    assert all(b in ("Z", "X") for b in bases)


@pytest.mark.unit
def test_abstract_random_provider() -> None:
    """Verify abstract methods can be compiled and called using super()."""
    from typing import Sequence

    class MockRandomProvider(RandomProvider):
        def generate_bits(self, length: int) -> tuple[int, ...]:
            return super().generate_bits(length)  # type: ignore[return-value]

        def generate_bases(
            self, length: int, allowed_bases: Sequence[str]
        ) -> tuple[str, ...]:
            return super().generate_bases(length, allowed_bases)  # type: ignore[return-value]

    prov = MockRandomProvider()
    assert prov.generate_bits(5) is None
    assert prov.generate_bases(5, ("Z", "X")) is None
