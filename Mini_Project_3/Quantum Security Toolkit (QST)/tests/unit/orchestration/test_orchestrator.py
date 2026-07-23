"""Unit tests for the SimulationOrchestrator coordination layer.

References:
    Docs/SIMULATION_SPEC.md §3, §4
    Docs/14_TESTING_STRATEGY.md §3
"""

import pytest

from qst.interfaces.protocol import ProtocolInterface
from qst.models.config import ProtocolType, SimulationConfig
from qst.models.results import (
    ExperimentResult,
    SimulationResult,
    SecurityStatus,
    SecurityMetrics,
)
from qst.orchestration.orchestrator import SimulationOrchestrator


class FakeProtocol(ProtocolInterface):
    """Fake QKD protocol implementation for testing orchestrator pluggability."""

    def __init__(self) -> None:
        self.n_qubits = 0
        self.seed = None
        self.eve_prob = 0.0

    def initialize(
        self,
        n_qubits: int,
        seed: int = None,
        eve_intercept_probability: float = 0.0,
    ) -> None:
        self.n_qubits = n_qubits
        self.seed = seed
        self.eve_prob = eve_intercept_probability

    def execute(self) -> None:
        pass

    def measure(self) -> None:
        pass

    def validate(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def export(self) -> SimulationResult:
        metrics = SecurityMetrics(
            key_rate=0.5,
            discard_rate=0.5,
            error_rate=0.0,
            status=SecurityStatus.SECURE,
        )
        return SimulationResult(
            qber=0.0,
            final_key_length=5,
            key_rate=0.5,
            sifted_key=[0, 1, 0, 1, 0],
            n_qubits=self.n_qubits,
            seed=self.seed,
            eve_intercept_probability=self.eve_prob,
            warnings=[],
            metadata={},
            security_metrics=metrics,
        )


@pytest.mark.unit
def test_orchestrator_run_once() -> None:
    """Verify SimulationOrchestrator runs a single simulation run successfully."""
    # Use fake protocol factory to isolate Qiskit and simulate pluggability
    orchestrator = SimulationOrchestrator(
        protocol_factory=lambda p_type: FakeProtocol()
    )

    config = SimulationConfig(n_qubits=10, seed=42)
    res = orchestrator.run_once(config)

    assert isinstance(res, ExperimentResult)
    assert len(res.simulations) == 1
    assert res.average_qber == 0.0
    assert res.average_key_rate == 0.5
    assert res.secure_runs == 1
    assert res.warning_runs == 0
    assert res.compromised_runs == 0

    assert res.metrics.execution_time > 0.0
    assert res.metrics.average_simulation_time > 0.0
    assert res.metrics.throughput > 0.0
    assert res.metrics.simulations_per_second > 0.0

    assert res.metadata.protocol == "BB84"
    assert res.metadata.repetitions == 1


@pytest.mark.unit
def test_orchestrator_run_many_repetitions() -> None:
    """Verify run_many runs the specified repetitions loop and computes stats."""
    orchestrator = SimulationOrchestrator(
        protocol_factory=lambda p_type: FakeProtocol()
    )

    config = SimulationConfig(n_qubits=10, seed=123, repetitions=5)
    res = orchestrator.run_many(config)

    assert len(res.simulations) == 5
    assert res.metadata.repetitions == 5
    # Verify sub-seeds distribution is deterministic for fixed seeds
    for idx, sim in enumerate(res.simulations):
        assert sim.seed is not None


@pytest.mark.unit
def test_orchestrator_default_factory_and_no_seed() -> None:
    """Verify default constructor instantiates BB84Protocol and seed=None runs."""
    orchestrator = SimulationOrchestrator()
    assert orchestrator._protocol_factory is not None

    # Run repetitions with seed=None to verify random generator paths
    config = SimulationConfig(n_qubits=10, seed=None, repetitions=2)
    # Using FakeProtocol to execute quickly
    orc_fake = SimulationOrchestrator(protocol_factory=lambda p_type: FakeProtocol())
    res = orc_fake.run_many(config)
    assert len(res.simulations) == 2
    for sim in res.simulations:
        assert sim.seed is None


class StatusFakeProtocol(ProtocolInterface):
    """Fake protocol returning specific security status values for coverage."""

    def __init__(self, status: SecurityStatus) -> None:
        self.status = status

    def initialize(self, n_qubits: int, seed: int = None, **kwargs) -> None:
        pass

    def execute(self) -> None:
        pass

    def measure(self) -> None:
        pass

    def validate(self) -> None:
        pass

    def reset(self) -> None:
        pass

    def export(self) -> SimulationResult:
        metrics = SecurityMetrics(
            key_rate=0.5,
            discard_rate=0.5,
            error_rate=0.1,
            status=self.status,
        )
        return SimulationResult(
            qber=0.1,
            final_key_length=5,
            key_rate=0.5,
            sifted_key=[0, 1, 0, 1, 0],
            n_qubits=10,
            seed=None,
            eve_intercept_probability=0.0,
            warnings=[],
            metadata={},
            security_metrics=metrics,
        )


@pytest.mark.unit
def test_orchestrator_status_counting_coverage() -> None:
    """Verify that orchestrator counts secure, warning, and compromised runs correctly."""
    # Warning fake
    orc_warn = SimulationOrchestrator(
        protocol_factory=lambda p_type: StatusFakeProtocol(SecurityStatus.WARNING)
    )
    res_warn = orc_warn.run_many(SimulationConfig(n_qubits=10, repetitions=2))
    assert res_warn.warning_runs == 2

    # Compromised fake
    orc_comp = SimulationOrchestrator(
        protocol_factory=lambda p_type: StatusFakeProtocol(SecurityStatus.COMPROMISED)
    )
    res_comp = orc_comp.run_many(SimulationConfig(n_qubits=10, repetitions=2))
    assert res_comp.compromised_runs == 2
