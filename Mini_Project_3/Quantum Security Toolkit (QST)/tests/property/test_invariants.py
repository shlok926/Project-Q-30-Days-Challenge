"""Property-based testing of BB84 physical and mathematical invariants.

References:
    Docs/00_PROJECT_CONSTITUTION.md
    Docs/14_TESTING_STRATEGY.md
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qst.models.config import ProtocolType, SimulationConfig
from qst.orchestration.orchestrator import SimulationOrchestrator


@pytest.mark.property
@settings(max_examples=15, deadline=None)
@given(
    n_qubits=st.integers(min_value=10, max_value=25),
    prob=st.floats(min_value=0.0, max_value=0.999),
    seed=st.integers(min_value=1, max_value=100000),
)
def test_bb84_mathematical_invariants(n_qubits: int, prob: float, seed: int) -> None:
    """Verify that key rate and discard rate sum to 1.0 across random configurations."""
    orchestrator = SimulationOrchestrator()
    config = SimulationConfig(
        n_qubits=n_qubits,
        seed=seed,
        interception_probability=prob,
        repetitions=1,
        protocol=ProtocolType.BB84,
    )
    res = orchestrator.run_once(config)
    sim = res.simulations[0]

    # Invariant 1: Key rate and discard rate must sum to exactly 1.0
    assert (
        pytest.approx(sim.key_rate + sim.security_metrics.discard_rate, abs=1e-9)
        == 1.0
    )

    # Invariant 2: Rates must fall between 0.0 and 1.0 inclusive
    assert 0.0 <= sim.key_rate <= 1.0
    assert 0.0 <= sim.security_metrics.discard_rate <= 1.0
    assert 0.0 <= sim.security_metrics.key_rate <= 1.0
    assert 0.0 <= sim.security_metrics.error_rate <= 1.0


@pytest.mark.property
@settings(max_examples=10, deadline=None)
@given(
    n_qubits=st.integers(min_value=10, max_value=25),
    seed=st.integers(min_value=1, max_value=100000),
)
def test_bb84_zero_eavesdropper_property(n_qubits: int, seed: int) -> None:
    """Verify that zero eavesdropper interception guarantees exactly zero QBER."""
    orchestrator = SimulationOrchestrator()
    config = SimulationConfig(
        n_qubits=n_qubits,
        seed=seed,
        interception_probability=0.0,
        repetitions=1,
        protocol=ProtocolType.BB84,
    )
    res = orchestrator.run_once(config)
    sim = res.simulations[0]

    # Invariant 3: Zero interception probability => exactly 0.0 QBER
    assert sim.qber == 0.0
    assert sim.security_metrics.error_rate == 0.0


@pytest.mark.property
def test_bb84_full_intercept_resend_qber_convergence() -> None:
    """Verify QBER converges to the theoretical 25% range under 100% intercept-resend attack."""
    orchestrator = SimulationOrchestrator()

    # Execute multiple combined repetitions to ensure statistical bounds without exceeding qubit limits
    config = SimulationConfig(
        n_qubits=25,
        seed=8888,
        interception_probability=1.0,
        repetitions=50,
        protocol=ProtocolType.BB84,
    )
    res = orchestrator.run_many(config)

    # Invariant 4: Average QBER under full intercept-resend attack converges to [0.23, 0.27]
    assert 0.23 <= res.average_qber <= 0.27

